# Run the local factory board

This first working increment reads GitHub issues, persists a JSON snapshot, and renders a self-contained HTML board. It does not change GitHub issues or run implementation jobs.

## Requirements

- macOS or Linux with Python 3.9 or newer. No Python package installation is needed.
- The GitHub CLI (`gh`) installed and authenticated for the intended target repository.
- Run the commands from this Software Factory checkout.

## Preview the board

```bash
python3 -m factory demo
open .factory/demo/board.html
```

The demo is prominently marked as illustrative. It lives separately from live data. It does not represent completed work or actual GitHub issues.

## Connect a target repository

Use the actual target's owner and repository name:

```bash
python3 -m factory sync --repo OWNER/REPO
open .factory/runtime/board.html
```

After the first successful read, later refreshes remember the repository and filter settings:

```bash
python3 -m factory sync
python3 -m factory status
```

The adapter uses `gh api` with GET requests only. It verifies the repository before saving its binding. The factory source remote is not an implicit product target; installation does not select a board repository.

To track another repository, use a separate directory. The controller refuses to overwrite one repository's board with another's:

```bash
python3 -m factory --state-dir .factory/runtime/second-project sync --repo OWNER/SECOND-REPO
python3 -m factory --state-dir .factory/runtime/second-project status
```

The global `--state-dir` option goes before `sync`, `board`, `status`, or `demo`. The HTML refresh help explains the default-directory command; add the state-directory option when using a separate board.

## Scope and history

Every open issue is included by default. Closed history includes issues updated in the last 30 days. Pull requests returned by GitHub's Issues endpoint are excluded from cards.

```bash
python3 -m factory sync --closed-days 7
python3 -m factory sync --closed-days 0
python3 -m factory sync --label enhancement --label ready-for-agent
python3 -m factory sync --all-labels
```

Multiple labels mean an issue must have all of them. Both the closed-history window and label filters are retained on subsequent syncs and recorded in the JSON snapshot. The board reports the history window and refresh time. For a large repository, choose a label filter before the first read: parent and dependency details require additional reads for each open issue.

## What the board reports

The board displays issue titles, descriptions, labels, assignees, priorities P0-P3, parent goals, native prerequisite links, status warnings, and a suggested next action. Search, priority filters, issue details, and alternate views work locally without a server or external scripts.

- `factory:*` labels supply the reported workflow state. Without them, triage labels and GitHub open/closed state supply a fallback.
- Multiple factory status labels produce a warning and a Blocked card.
- A reported Ready issue with an open prerequisite is displayed as Blocked. Its original reported status remains in JSON.
- Unreadable dependencies produce a warning and cannot appear Ready.
- Parent/sub-issue containment does not make the parent a prerequisite.
- Relations are refreshed for open issues. Closed history is explicitly marked as not refreshed for relationships.
- Done is **reported**, not verified. This increment does not inspect linked PR merge state, required checks, or approved acceptance criteria. It cannot authorize execution or release dependencies for a worker.

Native relation endpoints can be unavailable because of access or platform support. The board exposes partial reads instead of silently treating them as complete. A missing parent normally returns HTTP 404; that is treated as no recorded parent.

## Files and recovery

The selected state directory contains:

| File | Purpose |
| --- | --- |
| `board.json` | Schema-versioned issue snapshot, repository binding, scope, and refresh health. |
| `board.html` | Rebuildable, self-contained, read-only view of that snapshot. |
| `events.jsonl` | Small audit trail of successful and failed refreshes. |
| `.lock` | Local single-writer lock held while a command runs. |

JSON and HTML are replaced atomically, one file at a time. The event log is an audit trail; the three files are not a shared transaction. The lock prevents simultaneous local snapshot writers; it does not claim jobs on GitHub or coordinate multiple laptops.

If a refresh fails, cached issues and the last successful refresh time are preserved, synchronization is marked as failed, and the HTML is regenerated with a warning. Re-run sync when access or connectivity returns. An unavailable core issue list never becomes an empty successful board.

Rebuild HTML offline from a saved snapshot:

```bash
python3 -m factory board
python3 -m factory board --output /tmp/factory-board.html
python3 -m factory status --json
```

Opening an HTML file does not contact GitHub. Reopen it after regenerating, or reload the browser tab. A saved view older than one hour is marked as potentially out of date.

Live state and demo output under `.factory/runtime/` and `.factory/demo/` are ignored by Git. State at other paths is not automatically ignored: keep private issue snapshots out of tracked directories. Credentials are delegated to `gh` and never embedded in the board. GitHub error stderr is not persisted. Issue text is encoded in the saved page and inserted as text, so it cannot execute as page markup.

## Verification

```bash
python3 -m unittest discover -s tests -v
```

The 28 tests cover native parent/dependency semantics, malformed records, status conflicts, pagination, repository binding, cache preservation on failure, remembered filters, local locking, interrupted writes, offline rendering, and hostile issue text. These are adapter/CLI checks with fixtures. Separate read-only smoke checks confirmed repository lookup, pagination, an actual issue read and normalization, native dependency reads, and the expected no-parent response against the previously supplied public skill repository. That repository was not bound as a pilot target. Browser checks covered search, empty results, priorities, attention and cancelled views, issue details, keyboard dismissal, refresh help, and narrow/desktop layouts.

## Next increment

Implement write-through synchronization with a durable outbox and conflict handling. Then add approved goal publication, worker checkpoints and lifecycle management, and PR/check-based completion verification. A scheduled wake is configured only after manual sync and recovery work reliably and the user chooses the intended schedule.
