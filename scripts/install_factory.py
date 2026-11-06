#!/usr/bin/env python3
"""Link this checkout's factory skill into Codex without replacing existing skills."""

import argparse
import os
from pathlib import Path
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", type=Path,
                        default=Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")))
    args = parser.parse_args(argv)
    source = Path(__file__).resolve().parent.parent / "skills/software-factory"
    destination = args.codex_home.expanduser().resolve() / "skills/software-factory"
    if not (source / "SKILL.md").is_file():
        print("Factory source is missing; run from a complete clone.", file=sys.stderr)
        return 2
    if destination.is_symlink() and destination.resolve() == source:
        print("Already installed: " + str(destination))
        return 0
    if destination.exists() or destination.is_symlink():
        print("Existing skill preserved: " + str(destination) +
              ". Inspect it and choose the intended installation before retrying.", file=sys.stderr)
        return 2
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.symlink_to(source, target_is_directory=True)
    print("Installed: " + str(destination) + " -> " + str(source))
    print("Available on your next Codex turn. Hooks and upstream skills were not installed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
