# Factory operating contract

This is the factory's coordination layer, informed by the composition decisions in the Software Factory repository. The engineering methods remain in the installed upstream skills.

## Record ownership

- GitHub Issues own shared requirements, priority, parent links, native prerequisites, approval/evidence references, and shared workflow status.
- PRs, accepted commits, required checks, and merge state own integration evidence.
- Local runtime JSON owns the active run, worktree, checkpoint, cached remote versions, pending operations, and last successful sync. Keep credentials out of snapshots.
- HTML and Markdown board views are projections with a visible refresh timestamp. A view does not independently authorize execution.

When no reliable runtime helper exists, keep requested manual checkpoints and confirm remote writes directly. Do not describe loose files or issue labels as an atomic claim or an idempotent outbox. Building these guarantees is separate implementation work.

## Approvals and developer involvement

The initial workflow has developer checkpoints for the plan/test interfaces, material architecture or scope changes, PR review/merge, and release. Use the user's actual session authorization and current project policy. Keep routine actions moving inside already approved scope; do not re-ask about settled decisions.

A prototype is a question-answering artifact, not accepted product code. Wayfinding resolves decisions; build tasks deliver accepted behavior. Neither should be marked as the other merely to clear the board.

## Readiness and state

Use Triage -> Planned -> Ready -> Running -> Review -> Done, plus Blocked and Cancelled, mapped to the target's configured labels or fields. Keep triage maturity separate from execution status.

Ready requires explicit acceptance criteria, an approved scope and test interfaces, prerequisite integration, required access, and no active run. Parent containment is not a prerequisite on parent completion. For the initial per-issue PR workflow, accepted integration normally means the prerequisite PR is merged and its required checks/acceptance evidence are satisfied.

Blocked retains its prior phase, reason, decision owner, and next action. Cancelled records a deliberate stop; it does not satisfy blockers. Closed issues and green checks must be reconciled with actual acceptance evidence before Done.

An explicitly chosen integration-branch workflow has its own intermediate acceptance points. Record that policy in the approved plan; do not silently mix it with a one-PR-per-task workflow.

## Review and completion evidence

The product owns its native check commands, acceptance scenarios, and risk rules; the factory owns when verification and review are required. Use the configured product check entry point for local verification and CI. Record unavailable checks explicitly. An unconfigured harness is a verification failure, not a pass. Apply testing proportionally to behavior changes; documentation-only work need not invent behavior tests.

For each task, retain the requirements addressed, base and tested commit, clean/dirty worktree status, exact commands, exit results and relevant output, preview/reproduction evidence, linked PR, and unresolved concerns. Dirty-worktree results are provisional; verify the final PR revision. Later code, configuration, or dependency changes invalidate affected evidence. Review the requested behavior and engineering quality as separate questions, including the product's agreed risk rules. A test pass proves only the behavior it covers.

The existing PR evidence packet also carries a low/medium/high risk tier with a one-line justification. A passing fast subset is local feedback; the agreed full checks and acceptance scenarios govern integration. Human-owned acceptance scenarios are protected from routine implementation edits. Record explicit authorization for any exception and verify the resulting diff against the trusted base policy.

Done requires accepted behavior and the agreed integration evidence. Recheck after new commits. The parent goal also needs an integrated demonstration and any required developer acceptance. Merge and deployment remain governed by actual authorization, not by an agent-generated completion label.

## Resume and defer

Refresh remote state and inspect the recorded run handle, checkpoint, and worktree before retrying. Verify whether the worker is actually running; an old timestamp or file is insufficient. Preserve unfinished work. If remote state is unavailable, show stale data and defer new claims.

After an ambiguous remote write, search for its stable task/operation identity before retrying. Use the deterministic adapter once implemented; until then verify the result manually instead of claiming deduplication.

Use bounded repair attempts and checkpoint on usage limits or unavailable dependencies. The reusable harness requests at most three repair continuations per explicitly armed task/session, preserving the count across changing turn IDs and successful intermediate checks. At the limit, hand off the failure and remaining action. Stopping, disarming, or an unavailable hook never establishes acceptance. Hooks own only local verification state, not factory task status or worker claims.

A desktop prompt can guide a time budget; strict process termination requires a worker launcher. Scheduled wakes must reconcile before starting another task, and scheduling itself requires a user request.
