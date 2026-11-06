# Use the implemented board

The Software Factory source checkout contains the Python `factory` package. Resolve the installed skill symlink to find that checkout: the skill lives at `skills/software-factory/SKILL.md` beneath its root. Run its commands with that checkout as the working directory.

Read `docs/run-the-board.md` there for the full interface and recovery behavior.

## Route the request

- **Preview:** `python3 -m factory demo` generates `.factory/demo/board.html` using prominently marked illustrative cards. Never report those cards as actual user tasks or completed work.
- **First live read:** `python3 -m factory sync --repo OWNER/REPO` verifies and saves a real GitHub binding. Use the user's intended target or a verified target checkout remote. The upstream skill repository is a reference, not an implicit target.
- **Refresh:** `python3 -m factory sync` reuses the default saved binding and filters.
- **Inspect:** `python3 -m factory status` summarizes health; `status --json` returns the snapshot.
- **Rebuild offline:** `python3 -m factory board` regenerates HTML from JSON without GitHub access.

For another target, use a separate `--state-dir` before the subcommand. Reuse that directory on every subsequent command for that board. The CLI refuses to mix demo with live state or switch the bound repository in an existing directory.

Open the generated HTML file in the app or browser. It contains its data and scripts and needs no server. The Refresh button explains the CLI command; it does not contact GitHub itself.

## Interpret results accurately

A successful core read saves the repository, issues, scope, and refresh time. Partial relationship reads remain visible as warnings. A failed core read returns a failure status and preserves cached issues and their last successful refresh time, marking the view stale. Report that cached view as cached, not as a successful refresh.

The CLI uses GitHub GET requests only. It does not publish tasks, change labels, assign workers, verify PR acceptance, or configure scheduling. Its file lock protects local snapshot writers, not implementation jobs. Reported Ready and Done states are not execution authorization or verified completion.

Write-through synchronization, worker lifecycle/checkpoints, and acceptance-based dependency release require further implementation. The remaining operating contract still applies when those modules are built.
