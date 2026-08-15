#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Review Due — compute which concepts have decayed past their review interval.

Parses the concept table in LEDGER.md and reports what is due for retrieval
practice, ordered so the most valuable items come first: longest overdue, then
weakest. Pure date arithmetic. It makes no judgement about what is worth
teaching -- that stays with the agent.

Only the concept table is read. The Tells table further down the file is
ignored, because a Tell is a standing habit with no review interval; it is the
agent's job to weight the due set toward whatever the live Tells touch.

Intervals widen with strength (days):
    0 -> 1    taught, not yet written by them
    1 -> 2    shaky, you were holding the pen
    2 -> 4    wrote it with hints
    3 -> 9    wrote it cold once
    4 -> 21   wrote it cold repeatedly
    5 -> 60   reaches for it unprompted / can teach it back

Rows that cannot be read (bad date, bad strength) are reported under
"needs_attention" rather than dropped -- a silently skipped row is a concept
that decays invisibly, which is the one failure this whole system exists to
prevent.

Usage:
    uv run review-due.py <path-to-LEDGER.md> [--all] [--asof YYYY-MM-DD]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

INTERVALS = {0: 1, 1: 2, 2: 4, 3: 9, 4: 21, 5: 60}

COLUMNS = [
    "concept",
    "domain",
    "first",
    "last",
    "strength",
    "prerequisites",
    "misconception",
]


def split_row(line: str) -> list[str]:
    """Split a markdown pipe-table row into trimmed cells."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_separator(cells: list[str]) -> bool:
    """True for the |---|---| row under a markdown table header."""
    return bool(cells) and all(
        cell and set(cell) <= set("-: ") and "-" in cell for cell in cells
    )


def parse_ledger(text: str) -> list[dict]:
    """Extract data rows from the ledger table.

    Finds the header row by its first column and takes the contiguous rows
    that follow. Other tables in the file (the strength scale, the interval
    key) are ignored because they do not carry a 'Concept' first column.
    """
    rows: list[dict] = []
    lines = text.splitlines()
    in_table = False

    for line in lines:
        if "|" not in line:
            if in_table:
                in_table = False
            continue

        cells = split_row(line)

        if not in_table:
            if cells and cells[0].strip().lower() == "concept":
                in_table = True
            continue

        if is_separator(cells):
            continue
        if not any(cells):
            in_table = False
            continue

        # Pad or trim to the expected width so a short row still parses.
        cells = (cells + [""] * len(COLUMNS))[: len(COLUMNS)]
        rows.append(dict(zip(COLUMNS, cells)))

    return rows


def evaluate(row: dict, asof: date) -> dict:
    """Attach due-state to a parsed row, or explain why it could not be read."""
    concept = row["concept"].strip().strip("*`")
    result = {
        "concept": concept,
        "domain": row["domain"],
        "strength": None,
        "last": row["last"],
        "prerequisites": [
            p.strip() for p in row["prerequisites"].split(";") if p.strip()
        ],
        "misconception": row["misconception"].strip(),
    }

    try:
        strength = int(row["strength"].strip())
    except (ValueError, AttributeError):
        result["problem"] = f"unreadable strength: {row['strength']!r}"
        return result

    if strength not in INTERVALS:
        result["problem"] = f"strength {strength} outside 0-{max(INTERVALS)}"
        return result
    result["strength"] = strength

    try:
        last = date.fromisoformat(row["last"].strip())
    except ValueError:
        result["problem"] = f"unreadable last-seen date: {row['last']!r}"
        return result

    interval = INTERVALS[strength]
    due_on = last + timedelta(days=interval)
    result["interval_days"] = interval
    result["due_on"] = due_on.isoformat()
    result["days_overdue"] = (asof - due_on).days
    result["due"] = asof >= due_on
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report which ledger concepts are due for spaced review.",
        epilog="Exit codes: 0 = report produced, 2 = ledger unreadable.",
    )
    parser.add_argument("ledger", help="Path to LEDGER.md")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include concepts that are not yet due",
    )
    parser.add_argument(
        "--asof",
        metavar="YYYY-MM-DD",
        help="Evaluate against this date instead of today",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        help="Write JSON here instead of stdout",
    )
    parser.add_argument("--verbose", action="store_true", help="Diagnostics to stderr")
    args = parser.parse_args()

    path = Path(args.ledger)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Cannot read ledger: {exc}", file=sys.stderr)
        return 2

    try:
        asof = date.fromisoformat(args.asof) if args.asof else date.today()
    except ValueError:
        print(f"Invalid --asof date: {args.asof!r}", file=sys.stderr)
        return 2

    rows = parse_ledger(text)
    if args.verbose:
        print(f"Parsed {len(rows)} ledger rows from {path}", file=sys.stderr)

    evaluated = [evaluate(row, asof) for row in rows if row["concept"].strip()]

    needs_attention = [r for r in evaluated if "problem" in r]
    readable = [r for r in evaluated if "problem" not in r]
    due = [r for r in readable if r["due"]]
    not_due = [r for r in readable if not r["due"]]

    # Longest overdue first, then weakest -- the order they are worth doing in.
    due.sort(key=lambda r: (-r["days_overdue"], r["strength"]))
    not_due.sort(key=lambda r: r["due_on"])

    report = {
        "as_of": asof.isoformat(),
        "ledger": str(path),
        "total_concepts": len(readable),
        "due_count": len(due),
        "due": due,
        "needs_attention": needs_attention,
    }
    if args.all:
        report["not_due"] = not_due
    elif not_due:
        report["next_due_on"] = not_due[0]["due_on"]

    payload = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
        if args.verbose:
            print(f"Wrote report to {args.output}", file=sys.stderr)
    else:
        print(payload)

    if args.verbose:
        print(
            f"{len(due)} due, {len(not_due)} not due, "
            f"{len(needs_attention)} need attention",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
