# Quality-harness design considerations

For configuration and use, read the [quality-harness reference](../skills/software-factory/references/quality-harness.md). Record ownership and acceptance rules live in the [operating contract](../skills/software-factory/references/operating-contract.md); [README](../README.md#what-works) tracks implementation status.

## Extend the existing workflow

The factory already coordinates planning, implementation, review, and PR evidence. Separate `spec`, `fix-issue`, and `ship` skills would create competing workflows. The harness adds executable verification beneath the existing adapters while preserving upstream invocation policies.

Product-native tools remain authoritative. A shared check entry point lets the agent, Stop hook, and CI use the same commands without maintaining separate implementations. Product risk rules come from the user's decisions; template path defaults cannot substitute for that judgment.

## Arm verification explicitly

A dirty checkout cannot distinguish implementation from discussion, inherited changes, or a paused task. Explicit arming makes the verification obligation deliberate. Comparing against a recorded base also catches committed work that a working-tree-only check would miss.

The repair budget belongs to the armed task/session because Stop continuations may change turn IDs. Counting only by turn could permit an endless loop. Keeping hook state separate from factory task state prevents a local stopping decision from granting acceptance.

## Verify against a trusted base

Shell tools and alternate write routes can bypass a patch matcher. The diff guard provides a second check, using the baseline policy and a trusted guard implementation so a candidate cannot weaken its own verification. Exact-path exceptions support legitimate maintenance while keeping the scope reviewable; an authorization reference records a decision rather than granting permission.

These mechanisms are agent-writable guardrails. Required CI checks and maintainer review provide the integration boundary; the hooks do not establish a hostile-agent sandbox.

## Separate feedback from acceptance

Separating quick feedback from full acceptance keeps repair practical without letting partial coverage justify integration. Evidence must remain tied to the submitted revision so an earlier pass cannot justify later changes.

Visible, human-owned acceptance scenarios provide an independent statement of expected behavior. An agent-drafted example needs human review. Truly hidden holdouts would require a separate access and execution boundary, which a folder name cannot provide.

## Make upgrades deliberate

Linking the factory skill to a retained source clone keeps its references and board runtime available together. Product harnesses instead receive reviewed copies identified by template version and factory commit. This release boundary prevents a factory update from silently changing trusted product hooks or overwriting local commands and policy.

An automatic updater or generalized command schema would add machinery before a live pilot establishes what needs to vary. Disposable-repository tests establish script behavior; the next pilot must establish actual hook payloads, trust, and end-to-end operation. The [next step](../README.md#next-step) defines the build order.
