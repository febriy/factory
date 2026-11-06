"""Read-only GitHub adapter using the user's existing gh authentication."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import re
import subprocess

from .state import FactoryError, utc_now


STATES = ("triage", "planned", "ready", "running", "review", "done", "blocked", "cancelled")
REPOSITORY = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?/[A-Za-z0-9_.-]+\Z")


def repository_name(value):
    if not isinstance(value, str) or not REPOSITORY.fullmatch(value) or value.split("/")[1] in (".", ".."):
        raise FactoryError("Use a GitHub repository in owner/name form, for example your-account/your-project.")
    return value


class GitHubError(FactoryError):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


class GitHub:
    def __init__(self, executable="gh", timeout=45):
        self.executable = executable
        self.timeout = timeout

    def get(self, endpoint, paginate=False):
        command = [self.executable, "api", "--hostname", "github.com", "--method", "GET",
                   "-H", "Accept: application/vnd.github+json", endpoint]
        if paginate:
            command.extend(["--paginate", "--slurp"])
        try:
            result = subprocess.run(command, text=True, capture_output=True, timeout=self.timeout)
        except FileNotFoundError as exc:
            raise GitHubError("GitHub CLI is missing. Install gh and run gh auth login.") from exc
        except subprocess.TimeoutExpired as exc:
            raise GitHubError("GitHub did not respond before the request timeout. Try syncing again.") from exc
        if result.returncode:
            match = re.search(r"HTTP (\d{3})", result.stderr)
            status = int(match.group(1)) if match else None
            hints = {401: "Run gh auth login.", 403: "Check repository access or GitHub rate limits.",
                     404: "Check the repository name and access permissions."}
            # Do not persist arbitrary CLI stderr, which can contain local credentials or headers.
            raise GitHubError("GitHub read failed" + (" (HTTP %d). " % status if status else ". ")
                              + hints.get(status, "Check your connection and gh auth status."), status)
        try:
            data = json.loads(result.stdout)
        except ValueError as exc:
            raise GitHubError("GitHub returned unreadable JSON; the previous snapshot is preserved.") from exc
        if paginate:
            if not isinstance(data, list) or not all(isinstance(page, list) for page in data):
                raise GitHubError("GitHub returned an unexpected paginated response.")
            return [item for page in data for item in page]
        return data


def issue_ref(raw, repo):
    if not isinstance(raw, dict):
        raise GitHubError("GitHub returned an invalid issue record.")
    number = raw.get("number")
    title = raw.get("title")
    if not isinstance(number, int) or isinstance(number, bool) or number < 1 or not isinstance(title, str):
        raise GitHubError("GitHub returned an invalid issue record.")
    # Generate links from a verified repository and issue number, never from issue body HTML.
    raw_url = raw.get("html_url") or ""
    if not isinstance(raw_url, str):
        raise GitHubError("GitHub returned an invalid issue link.")
    match = re.fullmatch(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/issues/\d+", raw_url)
    linked_repo = repository_name(match.group(1)) if match else repo
    return {"number": number, "title": title, "url": "https://github.com/%s/issues/%d" % (linked_repo, number),
            "repository": linked_repo, "state": raw.get("state", "open")}


def normalize_issue(raw, repo):
    ref = issue_ref(raw, repo)
    if raw.get("state") not in ("open", "closed"):
        raise GitHubError("GitHub returned an invalid issue state.")
    if not isinstance(raw.get("labels", []), list) or not isinstance(raw.get("assignees", []), list):
        raise GitHubError("GitHub returned invalid issue labels or assignees.")
    if raw.get("body") is not None and not isinstance(raw["body"], str):
        raise GitHubError("GitHub returned an invalid issue description.")
    labels = [x["name"] for x in raw.get("labels", []) if isinstance(x, dict) and isinstance(x.get("name"), str)]
    reported = sorted(set(x.split(":", 1)[1] for x in labels if x.startswith("factory:") and x.split(":", 1)[1] in STATES))
    warnings = []
    if len(reported) > 1:
        status = "blocked"
        warnings.append("Conflicting factory status labels; a human needs to resolve them.")
    elif reported:
        status = reported[0]
    elif raw.get("state") == "closed":
        status = "cancelled" if raw.get("state_reason") == "not_planned" else "done"
    elif "ready-for-agent" in labels:
        status = "ready"
    elif "needs-info" in labels or "ready-for-human" in labels:
        status = "blocked"
    else:
        status = "triage"
    if raw.get("state") == "closed" and status not in ("done", "cancelled"):
        warnings.append("Closed in GitHub, but its workflow label reports unfinished work.")
    if raw.get("state") == "open" and status == "done":
        warnings.append("Reported as done, but the GitHub issue is still open.")
    priority = next((p for p in ("P0", "P1", "P2", "P3") if any(x.lower() in (p.lower(), "priority:" + p.lower(), "priority: " + p.lower()) for x in labels)), None)
    return {**ref, "id": str(raw.get("node_id") or "github:%s:%s" % (repo, ref["number"])),
            "body": raw.get("body") or "", "labels": labels, "status": status, "priority": priority,
            "assignees": [a["login"] for a in raw.get("assignees", []) if isinstance(a, dict) and isinstance(a.get("login"), str)],
            "updated_at": raw.get("updated_at"), "parent": None, "blockers": [],
            "relations": "not_loaded", "warnings": warnings,
            "verification": "not_checked", "reported_status": status}


def fetch_snapshot(client, repo, closed_days=30, labels=()):
    repo = repository_name(repo)
    metadata = client.get("repos/" + repo)
    if not isinstance(metadata, dict) or not isinstance(metadata.get("full_name"), str):
        raise GitHubError("GitHub returned an invalid repository response.")
    canonical = repository_name(metadata["full_name"])
    if canonical.lower() != repo.lower():
        raise GitHubError("GitHub redirected to a different repository. Bind its current name explicitly.")
    repo = canonical
    from urllib.parse import urlencode
    params = {"state": "open", "per_page": 100}
    if labels:
        params["labels"] = ",".join(labels)
    records = client.get("repos/%s/issues?%s" % (repo, urlencode(params)), paginate=True)
    if closed_days:
        params["state"] = "closed"
        params["since"] = (datetime.now(timezone.utc) - timedelta(days=closed_days)).isoformat()
        records += client.get("repos/%s/issues?%s" % (repo, urlencode(params)), paginate=True)
    by_number = {}
    for raw in records:
        if not isinstance(raw, dict):
            raise GitHubError("GitHub returned an invalid issue list.")
        if "pull_request" in raw:
            continue
        task = normalize_issue(raw, repo)
        if task["number"] in by_number:
            # An issue can change state between the open and closed page reads.
            previous = by_number[task["number"]]
            if (previous.get("updated_at") or "") > (task.get("updated_at") or ""):
                continue
        by_number[task["number"]] = task

    def hydrate(task):
        if task["state"] == "closed":
            task["relations"] = "closed_history"
            return task
        path = "repos/%s/issues/%d" % (repo, task["number"])
        errors = []
        try:
            blockers = client.get(path + "/dependencies/blocked_by?per_page=100", paginate=True)
            task["blockers"] = [issue_ref(b, repo) for b in blockers]
        except GitHubError:
            errors.append("Dependencies could not be read; readiness is unknown.")
        try:
            parent = client.get(path + "/parent")
            if not isinstance(parent, dict):
                raise GitHubError("Invalid parent response.")
            task["parent"] = issue_ref(parent, repo)
        except GitHubError as exc:
            if exc.status != 404:  # No parent is normally represented by a 404.
                errors.append("Parent relationship could not be read.")
        task["relations"] = "partial" if errors else "loaded"
        task["warnings"].extend(errors)
        open_blockers = [b for b in task["blockers"] if b["state"] != "closed"]
        if task["status"] == "ready" and open_blockers:
            task["status"] = "blocked"
            task["warnings"].append("Reported ready, but prerequisite issues are still open.")
        if task["status"] == "ready" and errors:
            task["status"] = "blocked"
        return task

    # Read-only hydration: no labels, assignments, comments, or issue bodies are changed.
    with ThreadPoolExecutor(max_workers=4) as pool:
        issues = list(pool.map(hydrate, by_number.values()))
    issues.sort(key=lambda x: (x["priority"] or "P9", x["number"]))
    now = utc_now()
    return {"schema_version": 1, "source": "github", "repository": repo,
            "repository_url": "https://github.com/" + repo, "generated_at": now,
            "last_successful_sync": now, "scope": {"closed_days": closed_days, "labels": list(labels)},
            "sync": {"status": "partial" if any(x["relations"] == "partial" for x in issues) else "fresh",
                     "last_attempt_at": now, "error": None},
            "issues": issues, "execution_enabled": False}
