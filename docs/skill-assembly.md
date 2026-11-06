# Assemble the factory from existing engineering skills

## Decision

Reuse the engineering methods in `mattpocock/skills`. Replace the proposal's four new engineering skills with one thin `software-factory` orchestration skill that supplies factory-specific planning, status, handoff, and completion rules. Keep deterministic coordination in software.

The upstream source was pinned at commit [`5beb35b040e3de97e54fa9e386d7e42d15c295c2`](https://github.com/mattpocock/skills/commit/5beb35b040e3de97e54fa9e386d7e42d15c295c2), inspected on 21 October 2026. Installed skill content is preserved, including supporting documents and `agents/openai.yaml`. Each new upstream installation includes its MIT license. Exact files and checksums are recorded in `factory/skills.lock.json`.

## Installed building blocks

| Stage | Upstream skills | Place in the factory |
| --- | --- | --- |
| Clarify a large or uncertain goal | `wayfinder`, `grilling`, `domain-modeling`, `prototype`, `research` | Resolve consequential unknowns before implementation. Wayfinder's decision tickets remain distinct from build tickets. |
| Specify and slice | `to-spec`, `to-tickets`, `codebase-design` | Describe observable success, agree the test interfaces, and split work into end-to-end increments with explicit blockers. |
| Triage and prepare | `triage`, `setup-matt-pocock-skills` | Establish tracker conventions and turn incoming reports into usable briefs. |
| Implement and test | `implement`, `tdd`, `diagnosing-bugs` | Build a bounded task; use meaningful behavior tests and a reproducible feedback loop for bugs. |
| Review and present | `code-review`, `pr` | Review requirements and engineering standards independently; present before/after evidence for human review. |
| Larger coordinated implementation | `implement-spec` | Optional whole-spec integration-branch workflow when explicitly selected. It is not the default per-issue PR workflow. |
| Improve the environment | `retro`, `improve-codebase-architecture`, `writing-for-agents` | Learn from demonstrated friction and improve checks, interfaces, and agent documentation. |

The original assembly installed 17 engineering skills plus two productivity dependencies (`grilling` and `writing-for-agents`). Cloning this repository does not install those dependencies. See [installation](install.md). The separate `$software-factory` entry point is our own composition layer.

## How a normal feature moves through the pieces

1. **Intake:** inspect the target repository and the outcome. Use research or a prototype only when a real uncertainty warrants it. Resolve material product and architecture decisions with the developer.
2. **Planning:** draft a spec, acceptance criteria, test interfaces, and small vertical slices. The factory planning adapter uses these upstream techniques without silently invoking their explicitly human-invoked entry points. Save enough information to resume from the artifacts.
3. **Plan review:** the developer approves the scope, dependencies, and test interfaces. Existing approval remains valid within that scope. A significant change returns the affected work to planning.
4. **Publication:** with a bound GitHub target and authorization to publish, create a parent goal and linked build issues. Capture native blocking edges separately from parent/sub-issue containment. Idempotency and sync confirmation belong to the adapter we still need to build.
5. **Execution:** one eligible issue at a time, in a worktree. Apply the reusable testing and debugging disciplines. A `ready-for-agent` label alone is insufficient to start a factory job.
6. **Review:** capture relevant check results against the actual commit and use `code-review` with an explicit fixed point. A separate review pass may use review subagents as that skill prescribes; this does not mean multiple implementation jobs run concurrently.
7. **Delivery:** prepare the PR with `pr`, then await the developer's review and merge decision under the current project policy. Reconcile merged work and release its dependents.
8. **Parent check:** demonstrate the integrated goal. Child issue closure by itself does not establish that the parent outcome is complete.

## Integration differences that need deliberate handling

### Human invocation versus unattended execution

Upstream distinguishes model-invocable disciplines from human-invoked orchestrators. In the installed Codex metadata, `to-spec`, `to-tickets`, `implement`, `implement-spec`, `wayfinder`, `triage`, `retro`, `improve-codebase-architecture`, and `setup-matt-pocock-skills` have `allow_implicit_invocation: false`.

Keep that metadata intact. An installation does not authorize a scheduler to call all of these. A human can invoke these skills directly. The factory skill supplies its own brief planning and execution coordination and reaches only reusable model-invocable disciplines automatically. It does not disguise a call to a human-invoked skill as a reference lookup. The upstream algorithms inform our adaptation; their original command entry points remain available separately.

Upstream instructions refer to a `Skill` tool and slash commands. In this Codex environment, resolve an eligible skill from the catalog and read its `SKILL.md` with file tools. A documented slash command is not a shell executable.

### Test approval without recurring interruptions

Upstream `tdd` requires agreed test seams. Capture the public interfaces and intended coverage in the approved plan so implementation can reuse that agreement. Ask again only if an interface or coverage decision materially changes, or if no agreement exists. Apply testing proportionally to the task; simple documentation or display changes do not automatically justify a new test suite.

### Per-issue PRs versus a single integration branch

Our initial factory proposal uses one implementation job and one reviewable PR per accepted slice. `implement-spec` instead coordinates implementation subagents and merges ticket branches into one integration branch. Both are useful, but selecting `implement-spec` is an explicit choice of the latter workflow. Do not silently substitute it for the pilot's simpler PR sequence or reset an unfinished worktree because a skill assumes a different branch base.

### Triage readiness versus execution state

Keep the upstream five triage roles for request maturity. Track factory workflow separately: Triage, Planned, Ready, Running, Review, Done, Blocked, Cancelled. The future GitHub adapter can represent this with `factory:*` labels. A ticket can be well specified while still waiting for a prerequisite, an approval, or a worker.

Done means accepted behavior plus the required integrated code and check evidence. Human merge and release policy still applies. Upstream references to AFK work or closing tickets are not blanket permission to merge or deploy.

### Existing local skills

`grill-with-docs`, `to-prd`, and `to-issues` already existed and were left unchanged. The older `grill-with-docs` uses `CONTEXT.md`; the current collection uses `GLOSSARY.md`. Honor the convention of an existing target repository rather than creating two competing glossaries. Use `domain-modeling` for new factory domain work. The old skills remain usable on explicit request, but are not additional mandatory pipeline stages.

`ask-matt` and `wizard` were not installed: the factory routing entry point covers this setup's selection need, and an interactive provisioning wizard is not needed for the current scope. The upstream `grill-with-docs` was not installed over the existing local copy.

## What custom work remains

| Piece | Why skills do not supply it | Evidence that it works |
| --- | --- | --- |
| Durable JSON state and journal | Instructions do not provide transactions, local locking, or checkpoints across process failure. | Restarting retains the current worktree and run record; two local controllers cannot claim the same job. |
| GitHub adapter and outbox | Publishing issues is different from reliable synchronization and deduplicating an ambiguous remote result. | A timeout after successful creation does not create a duplicate; developer edits survive reconciliation. |
| HTML board renderer | A list of skill outputs is not a shared board. | Cards show dependencies, evidence, next action, and the timestamp/pending-sync status of the view. |
| Worker lifecycle and completion checks | A skill cannot prove a process is alive or a PR is merged. | Actual run state, tested commit, required checks, and merge state govern transitions. |
| Scheduled controller wake | Installed skills do not wake themselves. | Each authorized wake reconciles prior work before choosing a new task and stays quiet when nothing changed. |

The skill assembly and the first read-only runtime increment are implemented: GitHub reads, schema-versioned JSON snapshots, single-writer local locking, an audit journal, and the HTML board. Reusable inactive quality-harness assets now add executable verification guardrails; see [design considerations](harness-design.md). The table describes the full runtime's intended acceptance criteria; transactional outbox writes, worker claims/checkpoints, completion verification, and scheduling are not yet implemented. Factory source is distributed through `febriy/factory`, independently from any product binding. See [the board runbook](run-the-board.md) for the implemented interface.

## Suggested next build increment

The first manual path is built and ready for binding to a chosen GitHub product target. Next integrate the quality harness into one explicitly selected product and demonstrate a manual issue-to-reviewed-PR flow, then continue validated write-through synchronization and worker recovery. Schedule the workflow only after manual recovery and sync checks work.

The user can start with `$software-factory` from the next turn. Use `$to-tickets`, `$implement`, or the other explicit entry points when that particular upstream workflow is desired.
