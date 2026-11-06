"""Template v1: local verification guardrails, not a worker or acceptance engine."""

import argparse
from contextlib import contextmanager
import fcntl
from fnmatch import fnmatchcase
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile


POLICY = ".codex/hooks/protected-paths.json"
LIMIT = 3


class HarnessError(Exception):
    pass


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise HarnessError("Git operation failed; verify checkout and base revision.")
    return result.stdout.decode("utf-8", errors="surrogateescape").strip("\n")


def repository(cwd):
    return Path(git(cwd, "rev-parse", "--show-toplevel")).resolve()


def revision(root, ref):
    return git(root, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}")


def emit(data):
    print(json.dumps(data, ensure_ascii=True))


def load_policy(root, base):
    # Read the accepted base, so a candidate cannot silently weaken its own guard.
    data = json.loads(git(root, "show", base + ":" + POLICY))
    if not isinstance(data, dict) or set(data) != {"always", "existing"}:
        raise HarnessError("Protected-path policy needs always and existing lists.")
    for patterns in data.values():
        if not isinstance(patterns, list) or not all(isinstance(p, str) and p for p in patterns):
            raise HarnessError("Protected-path patterns must be nonempty strings.")
    return data


def matches(path, patterns):
    return any(fnmatchcase(path, p) or (p.startswith("**/") and fnmatchcase(path, p[3:]))
               for p in patterns)


def exists_at(root, base, path):
    return subprocess.run(["git", "-C", str(root), "cat-file", "-e", base + ":" + path],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def protected(root, base, paths, allowed):
    policy = load_policy(root, base)
    return sorted({p for p in paths if p not in allowed and
                   (matches(p, policy["always"]) or
                    (matches(p, policy["existing"]) and exists_at(root, base, p)))})


def changed_paths(root, base):
    # No rename detection: both source and destination must be checked.
    diff = git(root, "diff", "--name-only", "-z", "--no-renames", base, "--")
    untracked = git(root, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted(set(p for p in (diff + "\0" + untracked).split("\0") if p))


def relative_path(root, cwd, value):
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = Path(cwd) / candidate
    lexical = Path(os.path.abspath(candidate))
    try:
        paths = {lexical.relative_to(root).as_posix(), candidate.resolve().relative_to(root).as_posix()}
    except ValueError:
        raise HarnessError("Patch path leaves the checkout; use an explicitly authorized workflow.")
    return paths


def patch_paths(root, cwd, payload):
    command = payload.get("command")
    if not isinstance(command, str) or not command.startswith("*** Begin Patch\n"):
        raise HarnessError("Cannot inspect this patch format; use canonical apply_patch input.")
    paths = set()
    for line in command.splitlines():
        for prefix in ("*** Add File: ", "*** Update File: ", "*** Delete File: ", "*** Move to: "):
            if line.startswith(prefix):
                paths.update(relative_path(root, cwd, line[len(prefix):]))
    if not paths or not command.rstrip().endswith("*** End Patch"):
        raise HarnessError("Cannot identify patch paths; repair the patch before retrying.")
    return paths


@contextmanager
def session_state(root, session, load=True):
    if not session:
        raise HarnessError("A session id is required.")
    # git-path is worktree-aware; no board state or tracked product files are used.
    directory = Path(git(root, "rev-parse", "--path-format=absolute", "--git-path", "factory-harness"))
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    key = hashlib.sha256(session.encode()).hexdigest()
    path = directory / (key + ".json")
    with (directory / (key + ".lock")).open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state = json.loads(path.read_text()) if load and path.exists() else None
        yield path, state


def save(path, state):
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(state, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def validate_state(state):
    if (not isinstance(state, dict) or state.get("version") != 1 or
            type(state.get("blocks")) is not int or not 0 <= state["blocks"] <= LIMIT or
            not isinstance(state.get("base"), str) or
            not isinstance(state.get("allowed"), list) or
            not all(isinstance(p, str) for p in state["allowed"])):
        raise HarnessError("Invalid verification state; inspect and explicitly re-arm the task.")


def pre_tool(root, event):
    if event.get("tool_name") not in ("apply_patch", "Edit", "Write"):
        return {}
    with session_state(root, event.get("session_id")) as (_, state):
        if state is not None:
            validate_state(state)
        base = state["base"] if state else revision(root, "HEAD")
        allowed = state["allowed"] if state else []
        paths = patch_paths(root, event.get("cwd", str(root)), event.get("tool_input", {}))
        denied = protected(root, base, paths, allowed)
    if denied:
        raise HarnessError("Protected paths: " + ", ".join(denied[:3]) +
                           ". Obtain explicit authorization for these exact paths before editing.")
    return {}


def stop(root, event):
    with session_state(root, event.get("session_id")) as (path, state):
        if state is None:
            return {}  # Planning and standalone work are not implicitly armed.
        validate_state(state)
        if not changed_paths(root, state["base"]):
            return {}
        denied = protected(root, state["base"], changed_paths(root, state["base"]), state["allowed"])
        if denied:
            summary = "Protected paths changed: " + ", ".join(denied[:3]) + ". Restore or obtain explicit authorization."
        else:
            try:
                # Stream into a temporary file to bound memory even for noisy checks.
                with tempfile.TemporaryFile() as output:
                    process = subprocess.Popen(["bash", "scripts/agent-check.sh", "fast"], cwd=root,
                                               stdout=output, stderr=subprocess.STDOUT,
                                               start_new_session=True)
                    try:
                        result_code = process.wait(timeout=120)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                        raise
                    output.seek(0, os.SEEK_END)
                    size = output.tell()
                    output.seek(max(0, size - 500))
                    tail = " ".join(output.read().decode("utf-8", errors="replace").split())
                if result_code == 0:
                    return {"systemMessage": "Local fast checks passed; full CI and review still govern acceptance."}
                summary = "Fast checks failed (exit %d): %s. Fix the failing check." % (result_code, tail)
            except subprocess.TimeoutExpired:
                summary = "Fast checks exceeded 120 seconds. Fix the check runtime or use a smaller agreed fast subset."
        state["last_turn_id"] = event.get("turn_id")
        if state["blocks"] >= LIMIT:
            save(path, state)
            return {"systemMessage": "Verification FAILED; repair limit reached. " + summary +
                    " Report unfinished work and hand off; this is not acceptance."}
        state["blocks"] += 1
        save(path, state)
        return {"decision": "block", "reason": summary + " Repair continuation %d/%d." % (state["blocks"], LIMIT)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("pre-tool")
    commands.add_parser("stop")
    arm = commands.add_parser("arm", help="Arm an approved task; repeated calls preserve its repair budget.")
    arm.add_argument("--session", required=True)
    arm.add_argument("--base", required=True)
    arm.add_argument("--allow-path", action="append", default=[])
    arm.add_argument("--reason", default="")
    disarm = commands.add_parser("disarm", help="End local verification; does not accept or complete the task.")
    disarm.add_argument("--session", required=True)
    guard = commands.add_parser("guard", help="Check the diff against policy from a trusted base.")
    guard.add_argument("--base", required=True)
    guard.add_argument("--allow-path", action="append", default=[])
    guard.add_argument("--reason", default="")
    args = parser.parse_args()
    try:
        event = json.load(sys.stdin) if args.action in ("pre-tool", "stop") else {}
        if not isinstance(event, dict):
            raise HarnessError("Hook input must be a JSON object.")
        root = repository(event.get("cwd", os.getcwd()))
        if args.action == "pre-tool":
            emit(pre_tool(root, event))
        elif args.action == "stop":
            emit(stop(root, event))
        elif args.action == "disarm":
            with session_state(root, args.session, load=False) as (path, _):
                path.unlink(missing_ok=True)
            print("Verification disarmed; task acceptance unchanged.")
        else:
            base = revision(root, args.base)
            load_policy(root, base)
            allowed = []
            for value in args.allow_path:
                if not args.reason.strip():
                    raise HarnessError("Exact-path exceptions require --reason with the authorization reference.")
                paths = relative_path(root, root, value)
                if len(paths) != 1 or value not in paths:
                    raise HarnessError("Exceptions must be exact repository-relative paths without symlinks or traversal.")
                allowed.append(value)
            if args.action == "arm":
                with session_state(root, args.session) as (path, state):
                    new = {"version": 1, "base": base, "allowed": allowed,
                           "reason": args.reason, "blocks": 0}
                    if state is not None:
                        validate_state(state)
                        if any(state.get(k) != new[k] for k in ("base", "allowed", "reason")):
                            raise HarnessError("Task already armed with different scope; inspect before disarming.")
                    else:
                        save(path, new)
                print("Verification armed; repair budget preserved on repeated calls.")
            else:
                denied = protected(root, base, changed_paths(root, base), allowed)
                if denied:
                    raise HarnessError("Protected paths changed: " + ", ".join(denied[:5]))
                print("PASS: protected paths unchanged or explicitly authorized.")
    except (HarnessError, OSError, ValueError, TypeError, AttributeError) as exc:
        message = str(exc) if isinstance(exc, HarnessError) else "Harness input or state unreadable; inspect configuration."
        if args.action == "pre-tool":
            emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                         "permissionDecisionReason": message}})
        elif args.action == "stop":
            emit({"systemMessage": "Verification unavailable: " + message + " Report unfinished verification; do not claim acceptance."})
        else:
            print("FAIL: " + message, file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
