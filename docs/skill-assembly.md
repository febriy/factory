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

The [factory skill](../skills/software-factory/SKILL.md) owns the planning and execution procedure. The [operating contract](../skills/software-factory/references/operating-contract.md) defines approvals, readiness, evidence, and completion.

## Integration differences that need deliberate handling

### Human invocation versus unattended execution

Upstream distinguishes human-invoked orchestrators from model-invocable disciplines. Preserving that distinction lets users retain the original entry points while the factory supplies its own coordination. The factory skill owns routing; installed `agents/openai.yaml` files retain their invocation policies.

### Test approval without recurring interruptions

Capturing test interfaces in the approved plan lets implementation reuse that agreement when applying upstream `tdd`. The approval and evidence requirements belong to the operating contract.

### Per-issue PRs versus a single integration branch

The default per-issue workflow keeps each slice independently reviewable. `implement-spec` instead coordinates subagents on an integration branch. Selecting that workflow explicitly avoids mixing its intermediate acceptance points with the per-issue dependency policy.

### Triage readiness versus execution state

Request maturity and execution progress answer different questions: a well-specified ticket may still lack an integrated prerequisite or an available worker. Keep the [tracker label mapping](agents/triage-labels.md) separate from the operating contract's readiness and completion rules.

### Existing local skills

The original installation preserved personal variants of `grill-with-docs`, `to-prd`, and `to-issues`; their provenance is in the manifest. They are optional entry points, not extra pipeline stages. Follow the target's [domain-documentation convention](agents/domain.md) when older and newer skills use different glossary names.

## Why runtime code remains necessary

These are acceptance criteria for future controller work, not capabilities supplied by installing skills:

| Piece | Why instructions are insufficient | Evidence required |
| --- | --- | --- |
| Run persistence and claims | Checkpoints and exclusive job claims need durable state and locking. | Restarting retains the worktree and run; two controllers cannot claim the same job. |
| GitHub adapter and outbox | Remote writes can succeed despite a local timeout. | Retrying an ambiguous creation avoids duplicates and preserves newer developer edits. |
| Worker lifecycle and completion checks | A description cannot prove that a process is alive or a PR is accepted. | Observed run state, tested revision, required checks, and merge state govern transitions. |
| Scheduled controller wake | Skills do not wake themselves. | Each authorized wake reconciles prior work before selecting a new task. |

See [README](../README.md#what-works) for implemented capabilities and the [next step](../README.md#next-step) for build order. The [board runbook](run-the-board.md) covers the working read-only runtime; [harness design](harness-design.md) explains the verification decisions.
