# Codex software factory

A lightweight factory for taking approved work toward reviewed PRs, with reusable engineering skills, explicit verification evidence, and a read-only GitHub issue board. The factory coordinates existing disciplines rather than replacing them with another set of spec, implementation, and shipping skills.

## Install

Use the Codex CLI.

```bash
codex plugin marketplace add febriy/factory
codex plugin add software-factory@febriy-factory
```

Start a new Codex chat and select Software Factory from the skill picker. The install guide covers the desktop picker, upstream skills, and the standalone install for older clients. [Installation and updates](docs/install.md)

## What works

- A factory skill with planning, bounded execution, review, evidence, and handoff contracts.
- Reusable, **inactive** quality-harness assets: a configurable check script, patch guard, bounded Stop hook, and protected-path diff guard. Tests exercise them in temporary repositories. They are not integrated into a product or trusted by installing the skill.
- A Python CLI that reads GitHub issues into versioned local JSON and renders a self-contained HTML board, preserving cached data after failed reads.

Run the demo from a factory source checkout.

```bash
python3 -m factory demo
```

Open `.factory/demo/board.html`. Actual GitHub reads require `gh` installed and authenticated. Choose a product explicitly with `python3 -m factory sync --repo OWNER/REPO`; the factory source repository is not an implicit product target.

## Design and operation

- [Harness design considerations](docs/harness-design.md): ownership, guardrails, retry limits, evidence, distribution, trade-offs, and deferred work.
- [Quality-harness reference](skills/software-factory/references/quality-harness.md): later product onboarding, task arming, exceptions, CI integration, and limitations.
- [Skill assembly](docs/skill-assembly.md): upstream disciplines, invocation policies, and factory adaptations.
- [Operating contract](skills/software-factory/references/operating-contract.md): readiness, evidence, acceptance, and recovery.
- [Board runbook](docs/run-the-board.md): GitHub reads, filtering, status, and recovery.
- [Installation provenance](factory/skills.lock.json): pinned upstream revision, file checksums, and preserved personal skill variants from the original assembly.

The engineering methods primarily come from [Matt Pocock's skills](https://github.com/mattpocock/skills/tree/main/skills/engineering). Their installation is separate; this repository contains the custom composition layer and records upstream provenance and license notices.

## Limits

The board reports tracker state; it does not verify completion or run workers. Write-through synchronization, execution claims/checkpoints, PR/check-based completion verification, and scheduling remain unbuilt. Harness assets still need a product-specific configuration and live pilot. No product integration, hook trust, branch protection, or automatic review setting is enabled by installation.

## Next step

When product integration is requested, configure the harness for one selected product and demonstrate a manual issue-to-reviewed-PR flow. Use that pilot to guide write-through synchronization, durable worker recovery, and completion verification. Scheduling follows reliable manual operation and requires an explicit request.

## Development

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions runs the same command. Python code uses the standard library. Personal apps, generated output, credentials, and local issue snapshots are not part of this distribution.
