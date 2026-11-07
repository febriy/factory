# Locate the board runtime

Resolve this skill's `SKILL.md` path. Its parent skill directory sits under `skills/` at the factory package root. Run `python3 -m factory` from that root, whether it is a source checkout or a Codex plugin cache.

For a plugin installation, pass `--state-dir` before the subcommand and keep state outside the cache so it survives upgrades. Use separate directories for demo and live boards. For example, run `python3 -m factory --state-dir ~/.local/share/software-factory/demo demo` to preview the demo.

Read [the board runbook](../../../docs/run-the-board.md) for commands, repository binding, reported status, and recovery. It is the authoritative board reference.
