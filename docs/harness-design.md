# Factory quality harness: design considerations

Status: reusable contract and inactive template v1. No product is integrated. The factory board remains read-only. A factory Git remote is a source distribution location, not an implicit product binding.

## Reuse the existing workflow

The existing factory already owns intake, approved scope/test interfaces, bounded implementation, two-axis review, and PR evidence. New `spec`, `fix-issue`, and `ship` skills would repeat those responsibilities. Extend the existing adapters instead, preserving upstream invocation policies and source files.

The missing piece is executable verification. Product-native tools remain authoritative; one product check script composes them and is called by the agent, local Stop hook, and CI. A fast subset accelerates repair while full checks govern integration. Missing infrastructure and an unconfigured template must remain visibly incomplete rather than pass.

## Ownership boundaries

| Owner | Authoritative information |
| --- | --- |
| Factory source | Coordination contract, reusable harness implementation, template version, tests |
| Product repository | Native commands, user-derived risk rules, reviewed protected-path policy, acceptance scenarios |
| Approved issue/plan | Scope, acceptance criteria, test interfaces, authorized exceptions |
| PR and CI | Evidence for the actual candidate revision and integration checks |
| Hook-local Git state | Armed baseline, session-specific repair budget, authorization references |
| Existing board/runtime | Cached tracker projection; no new acceptance or worker authority |

Human answers establish product review rules. Template path defaults are a separate, reviewable mechanism and do not imply decisions about auth, billing, or customer data. Product onboarding is a later authorized step.

## Explicit verification instead of guessing intent

A dirty checkout cannot distinguish implementation from discussion, inherited changes, or a paused task. The Stop hook therefore requires explicit arming for an approved task. Without an armed session it stays quiet. A changed task is checked against its recorded base, including committed changes; a clean working tree alone does not mean no work needs checking.

The counter belongs to the armed task/session, not `turn_id`. Stop continuations can create another prompt/turn, so resetting on every new id risks an endless loop. Three continuation requests are the total budget, retained across successful intermediate checks and repeated arming. Disarm ends verification without granting acceptance. Corrupt state or unavailable session identity requires an honest manual handoff, not speculative recovery.

This is intentionally narrower than a worker lifecycle. It cannot prove worker liveness, claim an issue, resume remote publication, or release a dependency. Those remain separate future runtime work.

## Guardrails and trusted checks

The patch hook checks source and destination paths, traversal, and symlink aliases. It supports the actual canonical patch payload rather than assuming a generic `file_path` field. Existing migrations are identified from the baseline, allowing a new migration to evolve within a task.

Exact-path exceptions preserve legitimate dependency updates and explicitly authorized maintenance. They require an authorization reference. An agent-supplied reason is an audit record, not proof of permission.

Shell tools and alternate write routes prevent an edit matcher from being a complete boundary. The diff guard therefore inspects committed and local changes, with the policy and CI guard implementation loaded from a trusted base. Changes to harness controls are protected too. Maintainers must control CI exceptions and required checks. Neither the local hooks nor an agent-writable workflow can establish a hostile-agent sandbox.

## Evidence and acceptance

Fast green checks are feedback, not acceptance. Record the base, tested commit, worktree state, commands, exit results, relevant output, and unresolved risks. Dirty-tree results are provisional. Changes to code, configuration, or dependencies invalidate affected evidence; verify the final PR revision and demonstrate the accepted journey. The existing PR packet gains a risk tier rather than another reporting format.

Human-owned acceptance tests are initially visible and protected. An agent-drafted example is provisional until reviewed. Hidden holdouts need a separate access/execution boundary; naming a folder `tests/scenarios` does not provide one.

## Distribution and upgrades

Keep canonical factory source, tests, and documentation in `febriy/factory`. Install the orchestration skill by linking a retained clone; that keeps its board runtime and supporting references available. Installation preserves existing skills and enables no hooks or product changes. Upstream disciplines remain separately installed at their recorded revision.

Distribute harness files as a reviewed copy inside each product, identified by `VERSION` plus the factory commit. This creates an intentional release boundary: pulling factory source does not silently change trusted product hooks. Upgrade by reviewing the diff from the recorded revision, preserving product-specific commands and policy, rerunning checks, and reviewing hook trust again. An automatic installer, updater, package registry, or generalized command schema is unnecessary before the first pilot.

The existing skills manifest is installation provenance, not a list of dependencies automatically installed by cloning. Local paths are normalized for portability in the published source. Personal apps, research, generated output, cached issues, and credentials are excluded from publication.

## Verification boundary

Automated tests use disposable Git repositories and synthetic hook inputs. They cover configured and unconfigured checks, failure aggregation, subdirectory paths with spaces, protected paths and renames, exact exceptions, base-policy preservation, turn-changing repair limits, fresh verification after edits, session isolation, timeout handling, and safe skill installation. They do not establish that a live Codex build invokes and trusts the hooks correctly. That requires the later product pilot.

Deferred: product configuration, user risk interview, real acceptance scenarios, product CI/branch protection, CI/comment-repair skill evaluation, durable write synchronization, worker lifecycle, and scheduling. Factory self-tests can run in GitHub Actions without activating any product harness.
