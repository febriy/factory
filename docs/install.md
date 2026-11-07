# Install the factory

## Install from the repository marketplace

The skill lives in `skills/software-factory/SKILL.md`. Codex uses its `name` and `description` to discover it. [OpenAI skill format](https://learn.chatgpt.com/docs/build-skills)

The repository's `plugin.json` packages that skill with its references, templates, and board runtime. The catalog entry in `.agents/plugins/marketplace.json` makes the plugin installable with the two commands in the README. [Factory README](../README.md#install) · [OpenAI plugin packaging guide](https://developers.openai.com/plugins/build/plugins)

On Codex desktop, you can also open a clean clone as a project, restart the app, and choose **Febriy Factory** in the Plugins Directory. Install **Software Factory** and start a new chat. In the CLI, use `$software-factory:software-factory` to select the bundled skill.

Use `--ref REF` on the marketplace add command to install from a branch, tag, or commit. Refresh a configured Git marketplace with `codex plugin marketplace upgrade febriy-factory`. Remove the plugin with `codex plugin remove software-factory@febriy-factory`. [Codex plugin commands](https://learn.chatgpt.com/docs/cli/reference#codex-plugin)

## Standalone skill install

For a Codex client without the marketplace commands, clone the repository and link the skill.

```bash
git clone https://github.com/febriy/factory.git
cd factory
python3 scripts/install_factory.py
```

Use `$software-factory` in a new chat. The installer preserves existing skills and links to the checkout, so keep the clone in place. For a custom Codex directory, pass `--codex-home /path/to/codex`. To uninstall, remove the symlink after verifying it points to this clone. Choose one installation method to keep a single factory entry in the skill picker.

## Install engineering disciplines as needed

The [assembly document](skill-assembly.md) explains which disciplines are used. They are independent dependencies, not vendored into this repository. [factory/skills.lock.json](../factory/skills.lock.json) records their inspected upstream revision and file hashes; installation-specific preservation entries describe the original assembly, not necessarily your machine.

Use Codex's `$skill-installer` to install the required skills from `mattpocock/skills` at commit `5beb35b040e3de97e54fa9e386d7e42d15c295c2`. For example, with the bundled installer in its default location:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo mattpocock/skills \
  --ref 5beb35b040e3de97e54fa9e386d7e42d15c295c2 \
  --path skills/engineering/code-review skills/engineering/tdd skills/engineering/diagnosing-bugs
```

For a full setup, ask Codex to use `$skill-installer` to install the missing entries in `installed_upstream` from the packaged `factory/skills.lock.json` at its pinned revision. Preserve existing personal variants and upstream invocation policies.

## Board and harness

Ask the installed factory skill to preview the board. The board runs on macOS or Linux with Python 3.9+ and uses authenticated `gh` for live issues. [Board runbook](run-the-board.md)

The packaged harness is a set of inactive templates. Integrate them into a product when requested. [Quality-harness reference](../skills/software-factory/references/quality-harness.md)
