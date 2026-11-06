# Quality harness

Read this for harness assembly or execution in a product with the harness installed. The reusable files are in [assets/repo-harness](../assets/repo-harness/); their `VERSION` identifies the template revision. These are inactive assets, not hooks for the factory checkout.

## Onboard a product only when requested

1. Inspect the intended checkout's commands, CI, agent instructions, and critical journeys. Resolve its GitHub target independently from the factory source repository.
2. Reuse recorded risk decisions. Ask up to three questions for missing consequential risks; derive product review rules from the answers. Put each rule's risk and safe path in the product's existing agent instructions.
3. Present the product-specific configuration and scope for approval unless already authorized. Reuse the factory planning adapter; do not create a competing `spec`, `fix-issue`, or `ship` skill.
4. Merge the assets into the product without overwriting existing hooks or scripts. Configure `product_checks` in `scripts/agent-check.sh` using its verified native commands. The template deliberately fails until configured. `full` is the default; `fast` is a deliberately selected subset or the same suite. Document unavailable lint/typecheck/build coverage honestly. Keep commands authoritative in the script and link from agent instructions.
5. Review the draft `protected-paths.json`. Adapt migration paths and lockfile coverage to the stack. Its patterns are template defaults, not user-derived product risk rules. Confirm protection of the harness controls themselves. Record the source template version and factory Git revision in the product's agent documentation.
6. Start with a provisional acceptance journey for human review; after acceptance, treat it as human-owned. Visible protected scenarios are not hidden holdouts. A genuinely hidden suite requires a separate trusted execution boundary.
7. Commit the reviewed baseline before arming. Merge hook definitions into the existing configuration and review/trust them through `/hooks`. The current wire format is documented in [official OpenAI hook documentation](https://learn.chatgpt.com/docs/hooks).

## Run an approved task

Use the active Codex session id supplied in hook input; do not invent one or parse an undocumented transcript format. If the orchestrator cannot obtain it, run checks manually and state that automatic Stop verification is unavailable.

From the product checkout, arm once after scope approval and before implementation:

```bash
python3 .codex/hooks/factory_harness.py arm --session SESSION_ID --base BASE_COMMIT
```

Repeated arming with identical arguments preserves the repair budget; a conflicting scope is rejected. The task baseline is a commit, not a moving branch name. To authorize a protected-path exception, record the user's actual authorization and pass the exact relative path with `--allow-path` and an authorization reference with `--reason` when first arming. Wildcards and symlink aliases are not exception paths. Flags record authorization; they cannot grant it.

Stop does nothing without an armed session or changes relative to its base. Otherwise it checks protected paths and runs `bash scripts/agent-check.sh fast`. A failing result requests at most three continuations across the entire armed task, even if turn IDs change. A successful intermediate check does not reset the budget or cache later results. After the limit, the hook reports failure and allows stopping. It never marks a task done. Failed or corrupt hook state reports unavailable verification without creating an unbounded continuation loop.

The check process has a 120-second timeout; a timeout kills its process group. Adjust the agreed fast subset if necessary. The manifest's 150-second outer timeout leaves room for reporting. Keep raw logs and secrets out of hook reasons: only the last 500 bytes of command output are included, and that output may reach the model/UI.

Before PR handoff, run full checks and verify protected paths:

```bash
bash scripts/agent-check.sh full
python3 .codex/hooks/factory_harness.py guard --base BASE_COMMIT
```

The guard includes committed, staged, unstaged, and nonignored untracked changes. Rename source and destination are both checked. Existing migrations are defined at the task base, so adding and refining a new migration remains possible. Environment files and scenarios are always protected, including newly added ones. Git-ignored untracked files are outside diff verification; the patch hook can still protect direct edits to them.

After final verification or an explicit unfinished-work handoff:

```bash
python3 .codex/hooks/factory_harness.py disarm --session SESSION_ID
```

Disarming removes only hook-local state under the worktree's Git directory. Preserve the task checkpoint, failure evidence, and files. Re-arming to evade the repair limit is outside the contract. State is isolated by checkout/worktree and session and locked during Stop verification; it is neither a job claim nor a scheduler checkpoint.

## CI and limits

Use the same check script for full CI. Execute the protected-path guard implementation and policy from a trusted base, against the candidate checkout. Fetch that base explicitly; a shallow checkout without it is insufficient. For a PR, select the base/merge-base deliberately rather than assuming `HEAD~1`.

For example, in a trusted CI step with `BASE_COMMIT` and `RUNNER_TEMP` already set:

```bash
git show "$BASE_COMMIT:.codex/hooks/factory_harness.py" > "$RUNNER_TEMP/factory-harness.py"
python3 "$RUNNER_TEMP/factory-harness.py" guard --base "$BASE_COMMIT"
bash scripts/agent-check.sh full
```

Protected-path exceptions must be supplied by trusted maintainer policy, not generated from PR text or candidate-controlled configuration. Changes to the check script or harness require explicit review; a PR must not make itself green by disabling its checks. Product integration must configure required CI checks and the applicable branch protection; this asset does not configure GitHub settings.

The patch hook supports canonical `apply_patch` input (`tool_input.command`), including aliases and moves. An uninspectable matching call is denied with a repair reason. Shell/MCP writes and opted-out tool paths can bypass patch inspection; the diff guard detects covered changes afterward. Hooks, local state, and repository files are agent-writable guardrails, not a security sandbox. Runtime payloads, automatic continuation identity, hook trust, and actual end-to-end operation still require a live pilot before claiming unattended reliability.
