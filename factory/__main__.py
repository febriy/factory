"""Run with python3 -m factory. GitHub operations in this release are read-only."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys

from .board import write_board
from .github import GitHub, fetch_snapshot, normalize_issue, repository_name
from .state import FactoryError, Store, utc_now


ROOT = Path(__file__).resolve().parent.parent


def demo_snapshot():
    samples = [
        (1, "Turn a substantial goal into reviewed software", "planned", "P1", "Define a feature, review its slices, then implement and verify each one."),
        (2, "Read GitHub issues into a durable snapshot", "done", "P1", "Acceptance criteria\n- Keep every issue's stable ID.\n- Preserve the previous snapshot on a failed refresh."),
        (3, "See dependencies and the next action on the board", "running", "P1", "A parent is a grouping relationship. A blocker is a prerequisite. The board should show both."),
        (4, "Keep developer edits when synchronizing changes", "ready", "P1", "Compare the remote version before publishing a queued update. Preserve newer developer edits."),
        (5, "Recover an interrupted worker without losing changes", "blocked", "P1", "Choose how the runtime verifies a worker is alive before retrying its unfinished work."),
        (6, "Prepare a PR with acceptance evidence", "review", "P2", "Show the changed behavior, tested revision, check results, and remaining concerns."),
        (7, "Agree which repository to use for the pilot", "triage", "P1", "Bind an actual owner/repository before reading or writing shared work."),
        (8, "Add an editable board", "cancelled", "P3", "Deferred until the read-only workflow and synchronization are reliable."),
    ]
    tasks = []
    for number, title, status, priority, body in samples:
        task = normalize_issue({"number": number, "title": title, "body": body,
                                "state": "closed" if status in ("done", "cancelled") else "open",
                                "labels": [{"name": "factory:" + status}, {"name": priority}],
                                "updated_at": utc_now()}, "example/demo")
        task.update(id="demo:%d" % number, url=None, repository=None, relations="loaded")
        if number > 1:
            task["parent"] = {"number": 1, "title": samples[0][1], "url": None, "state": "open"}
        if number == 5:
            task["warnings"] = ["A developer decision is needed before implementation can continue."]
        tasks.append(task)
    now = utc_now()
    return {"schema_version": 1, "source": "demo", "repository": None, "repository_url": None,
            "generated_at": now, "last_successful_sync": None,
            "scope": {"closed_days": 30, "labels": []}, "sync": {"status": "demo", "error": None},
            "issues": tasks, "execution_enabled": False}


def parser():
    result = argparse.ArgumentParser(description="Local software-factory board. This release reads GitHub; it does not execute jobs or publish updates.")
    result.add_argument("--state-dir", type=Path, help="Local snapshot directory (default: .factory/runtime in this checkout)")
    sub = result.add_subparsers(dest="command", required=True)
    sync = sub.add_parser("sync", help="Read GitHub issues and regenerate board.json and board.html")
    sync.add_argument("--repo", help="GitHub owner/repository; required for the first live sync")
    sync.add_argument("--closed-days", type=int, help="Include closed issues updated in this many days (default 30; 0 for open only)")
    sync.add_argument("--label", action="append", help="Only issues with ALL supplied labels; remembered on subsequent syncs")
    sync.add_argument("--all-labels", action="store_true", help="Clear any saved label filters")
    board = sub.add_parser("board", help="Render a board from the saved snapshot without contacting GitHub")
    board.add_argument("--output", type=Path, help="Optional destination for the generated HTML")
    status = sub.add_parser("status", help="Show the saved repository, synchronization health, and issue counts")
    status.add_argument("--json", action="store_true", help="Print the complete snapshot as JSON")
    sub.add_parser("demo", help="Generate an explicitly illustrative board in .factory/demo, separate from live state")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    directory = args.state_dir or ROOT / ".factory" / ("demo" if args.command == "demo" else "runtime")
    store = Store(directory)
    try:
        with store.lock():
            previous = store.load()
            if args.command == "demo":
                if previous and previous["source"] != "demo":
                    raise FactoryError("This directory contains live data. Choose another --state-dir for the demo.")
                data = demo_snapshot()
                store.save(data)
                write_board(data, store.directory / "board.html")
                store.event("demo_generated", issues=len(data["issues"]))
            elif args.command == "sync":
                if previous and previous["source"] == "demo":
                    raise FactoryError("This is a demo directory. Use a separate state directory for GitHub data.")
                repo = args.repo or (previous or {}).get("repository")
                if not repo:
                    raise FactoryError("No repository is bound. Run python3 -m factory sync --repo OWNER/REPO.")
                repository_name(repo)
                if previous and previous["repository"].lower() != repo.lower():
                    raise FactoryError("This directory belongs to another repository. Choose a new --state-dir.")
                scope = (previous or {}).get("scope", {})
                days = args.closed_days if args.closed_days is not None else scope.get("closed_days", 30)
                if not 0 <= days <= 3650:
                    raise FactoryError("--closed-days must be between 0 and 3650.")
                if args.all_labels and args.label:
                    raise FactoryError("Use either --all-labels or --label, not both.")
                labels = [] if args.all_labels else (args.label if args.label is not None else scope.get("labels", []))
                try:
                    data = fetch_snapshot(GitHub(), repo, days, labels)
                except FactoryError:
                    if previous:
                        previous["sync"] = {"status": "error", "last_attempt_at": utc_now(),
                                            "error": "Refresh failed. Cached cards are preserved; run sync again after checking GitHub access and connectivity."}
                        store.save(previous)
                        write_board(previous, store.directory / "board.html")
                        store.event("refresh_failed", repository=repo)
                    raise
                store.save(data)
                write_board(data, store.directory / "board.html")
                store.event("snapshot_refreshed", repository=data["repository"], issues=len(data["issues"]), health=data["sync"]["status"])
            elif args.command == "board":
                if not previous:
                    raise FactoryError("No saved board. Run sync --repo OWNER/REPO, or demo for an illustrative preview.")
                write_board(previous, args.output or store.directory / "board.html")
                print((args.output or store.directory / "board.html").resolve())
                return 0
            elif args.command == "status":
                if not previous:
                    raise FactoryError("No saved board. Run sync --repo OWNER/REPO first.")
                if args.json:
                    print(json.dumps(previous, indent=2, ensure_ascii=False))
                else:
                    print("Repository:", previous.get("repository") or "Demo (illustrative data)")
                    print("Sync:", previous["sync"]["status"])
                    print("Last successful refresh:", previous.get("last_successful_sync") or "Never")
                    print("Issues:", len(previous["issues"]), dict(Counter(x["status"] for x in previous["issues"])))
                    print("Execution: disabled; board reports remote status without verifying acceptance or merge evidence.")
                return 0
            print(store.directory / "board.html")
            if args.command == "sync" and data["sync"]["status"] == "partial":
                print("Some relationships could not be read. Inspect the warnings on affected cards.", file=sys.stderr)
        return 0
    except (FactoryError, OSError) as exc:
        print("factory:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
