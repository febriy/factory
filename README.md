# Codex software factory

A lightweight factory for taking approved work toward reviewed PRs, with reusable engineering skills, explicit verification evidence, and a read-only GitHub issue board. The factory coordinates existing disciplines rather than replacing them with another set of spec, implementation, and shipping skills.

## Install

On macOS or Linux with Python 3.9+ and Git 2.31+:

```bash
git clone https://github.com/febriy/factory.git
cd factory
python3 scripts/install_factory.py
python3 -m unittest discover -s tests -v
```

The installer links this checkout's `$software-factory` skill into Codex, preserving existing installations. Keep the clone in place. The skill is available on your next turn; engineering dependencies remain separate. See [installation and updates](docs/install.md) for dependency installation, custom Codex directories, removal, and version pinning.

## What works

- A factory skill with planning, bounded execution, review, evidence, and handoff contracts.
- Reusable, **inactive** quality-harness assets: a configurable check script, patch guard, bounded Stop hook, and protected-path diff guard. Tests exercise them in temporary repositories. They are not integrated into a product or trusted by installing the skill.
- A Python CLI that reads GitHub issues into versioned local JSON and renders a self-contained HTML board, preserving cached data after failed reads.

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

## Development

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions runs the same command. Python code uses the standard library. Personal apps, generated output, credentials, and local issue snapshots are not part of this distribution.
