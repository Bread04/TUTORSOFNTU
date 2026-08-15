#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Waking — load the agent's sanctum in one pass, or route to First Breath.

Run on activation. Determines the mode from the filesystem and, when the
sanctum exists, prints the full identity in a single read (INDEX, PERSONA,
CREED, BOND, MEMORY, CAPABILITIES, LEDGER) so the agent becomes itself in one
shot instead of seven. When no sanctum exists, it prints a directive to run
First Breath.

LEDGER.md is part of the waking set rather than an on-demand read: this agent
aims its teaching at the owner's weak points, and it cannot do that from the
first turn without knowing what they hold. If the ledger ever grows past the
point where loading it is cheap, that is a signal to consolidate concepts, not
to drop it from the load.

This loads runtime memory only. It never reads or writes config or customize.toml.

Usage:
    uv run --managed-python wake.py <project-root>

    project-root: The root of the project (where _bmad/ lives)
"""

import sys
from pathlib import Path

SKILL_NAME = "agent-felicia"

# The sanctum is prose written by the agent, so it will contain em-dashes,
# quotes, and whatever else it felt like. Windows consoles default to a
# codepage that cannot encode those, and an encoding error here means the agent
# fails to wake at all. Replace rather than crash.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# Load order — the "become yourself" set.
IDENTITY_FILES = [
    "INDEX.md",
    "PERSONA.md",
    "CREED.md",
    "BOND.md",
    "MEMORY.md",
    "CAPABILITIES.md",
    "LEDGER.md",
]


def emit(path: Path) -> None:
    print(f"\n===== {path.name} =====")
    try:
        print(path.read_text(encoding="utf-8").rstrip())
    except FileNotFoundError:
        print(f"(missing: {path.name})")


def main() -> int:
    args = sys.argv[1:]
    positional = [a for a in args if not a.startswith("--")]
    if not positional:
        print("Usage: wake.py <project-root>", file=sys.stderr)
        return 2

    project_root = Path(positional[0]).resolve()
    sanctum = project_root / "_bmad" / "memory" / SKILL_NAME

    core_ok = (
        sanctum.is_dir()
        and (sanctum / "CREED.md").is_file()
        and (sanctum / "MEMORY.md").is_file()
    )
    if not core_ok:
        print("MODE: FIRST_BREATH")
        print(f"NO SANCTUM at {sanctum}")
        print("This is your one birth. Load references/first-breath.md and follow it.")
        return 0

    print("MODE: WAKING")
    print(f"Sanctum: {sanctum}")
    for name in IDENTITY_FILES:
        emit(sanctum / name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
