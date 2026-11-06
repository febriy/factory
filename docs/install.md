# Install the factory

Supported environment: macOS or Linux, Python 3.9+, Git 2.31+, and Codex with skills support. The board also needs the GitHub CLI authenticated for the target repository. Python runtime code uses the standard library; there is no package installation step. Hooks additionally require a supported local Codex runtime and trust review.

## Clone and link the skill

```bash
git clone https://github.com/febriy/factory.git
cd factory
python3 scripts/install_factory.py
python3 -m unittest discover -s tests -v
```

The installer links `skills/software-factory` from this clone into `${CODEX_HOME:-~/.codex}/skills/software-factory`. Keep the clone at that location. It preserves an existing directory or different symlink rather than overwriting it; a repeated installation of the same checkout is safe. Use `--codex-home /your/codex-home` for another Codex directory. The skill is available on your next Codex turn.

This installs only the factory entry point. It does not install upstream skills, configure hooks, choose a product, publish issues, change GitHub settings, or schedule jobs. Ask Codex to use `$software-factory` to plan an outcome or inspect assembly status.

## Install engineering disciplines as needed

The [assembly document](skill-assembly.md) explains which disciplines are used. They are independent dependencies, not vendored into this repository. [factory/skills.lock.json](../factory/skills.lock.json) records their inspected upstream revision and file hashes; installation-specific preservation entries describe the original assembly, not necessarily your machine.

Use Codex's `$skill-installer` to install the required skills from `mattpocock/skills` at commit `5beb35b040e3de97e54fa9e386d7e42d15c295c2`. For example, with the bundled installer in its default location:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo mattpocock/skills \
  --ref 5beb35b040e3de97e54fa9e386d7e42d15c295c2 \
  --path skills/engineering/code-review skills/engineering/tdd skills/engineering/diagnosing-bugs
```

Choose other paths from the manifest as the task needs them. Inspect existing installations instead of replacing personal variants. The factory must report a missing required discipline rather than claim it was installed. Installation does not change upstream human-invocation policies.

## Preview or bind a board

```bash
python3 -m factory demo
```

Open `.factory/demo/board.html`. To read your actual product issues, authenticate `gh` and follow [the board runbook](run-the-board.md). `febriy/factory` is the factory source repository, not an automatically selected product. Read-only board use does not require installing all engineering skills.

## Harness assets and updates

The template is in `skills/software-factory/assets/repo-harness`. Follow the [quality-harness reference](../skills/software-factory/references/quality-harness.md) only when product integration is requested. Copying an unconfigured template will fail checks deliberately. Existing hooks require a merge, not replacement. Review product risks, commands, policy, and hook trust before enabling anything.

For reproducible use, record or check out a reviewed factory commit. Pulling this clone changes the linked factory skill; inspect changes before updating. Product harness copies stay pinned to their recorded template version and factory commit until deliberately upgraded. No auto-update runs.

To remove the skill, verify that the installed `software-factory` entry is the symlink to this clone, then remove only that link. The clone and product harness copies remain intact.
