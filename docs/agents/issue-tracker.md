# Issue tracker binding

The selected shared tracker is GitHub Issues in the target product repository. Factory source is distributed through `febriy/factory`; that does not bind a product tracker. No product target is selected by installation.

Before a remote operation, identify the target from an explicit user-supplied owner/repository or the intended checkout's verified Git remote. Record which repository is the target. Do not infer it from an example, a source skill repository, or the current directory name.

Until binding is available, prepare requested local spec and ticket drafts under `.factory/plans/`. Local drafts are not published GitHub issues and do not authorize execution. Record their publication state honestly.

For a configured target, read issues with their bodies, comments, labels, sub-issues, dependencies, and linked PRs. Use the connected GitHub tools or `gh` as supported; persist stable IDs for later reconciliation. For multiline issue bodies and comments, use structured tool arguments or UTF-8 temporary files passed with `--body-file`.

Use parent/sub-issue links for containment and native issue dependency links for blockers. When an API operation requires an issue database ID, do not substitute its display number or GraphQL node ID. Check local CLI help before assuming a flag is supported.

External PRs are not an automatic request/triage surface in this setup. Explicitly requested PR work remains in scope.

Publication of approved work, review comments, merge, and deployment follow the user's authorization for the task. Installing skills alone authorizes none of these external actions.
