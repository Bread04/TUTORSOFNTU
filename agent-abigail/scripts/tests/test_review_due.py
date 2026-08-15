#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Tests for review-due.py. Run: uv run scripts/tests/test_review_due.py"""

import importlib.util
import sys
from datetime import date
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parent.parent / "review-due.py"
spec = importlib.util.spec_from_file_location("review_due", MODULE_PATH)
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)

FAILURES = []


def check(name, condition, detail=""):
    if condition:
        print(f"  PASS  {name}")
    else:
        print(f"  FAIL  {name} {detail}")
        FAILURES.append(name)


LEDGER = """# Ledger

## Strength Scale

| Value | Means |
|-------|-------|
| 0 | Taught. |
| 5 | Teaches it back. |

## The Table

| Concept | Domain | First | Last | Strength | Prerequisites | Misconception |
|---------|--------|-------|------|----------|---------------|---------------|
| Integration by parts | math | 2026-07-01 | 2026-08-01 | 2 | product rule; antiderivatives | treats dx as decoration |
| Conservation of energy | physics | 2026-06-01 | 2026-08-13 | 4 | work-energy theorem |  |
| Eigenvectors | math | 2026-05-01 | 2026-08-14 | 5 | matrix multiplication |  |
| Broken row | math | 2026-01-01 | not-a-date | 3 |  |  |
| Bad strength | math | 2026-01-01 | 2026-08-01 | nine |  |  |
"""

ASOF = date(2026, 8, 14)

print("parse_ledger")
rows = rd.parse_ledger(LEDGER)
check("reads only the concept table", len(rows) == 5, f"got {len(rows)}")
check("first concept correct", rows[0]["concept"] == "Integration by parts")
check("ignores the strength-scale table", all(r["concept"] not in ("0", "5") for r in rows))

print("evaluate — due states")
ev = [rd.evaluate(r, ASOF) for r in rows]
by_name = {e["concept"]: e for e in ev}

ibp = by_name["Integration by parts"]
check("strength 2 gives a 4-day interval", ibp["interval_days"] == 4)
check("13 days past a 4-day interval is due", ibp["due"] is True)
check("overdue count correct", ibp["days_overdue"] == 9, f"got {ibp['days_overdue']}")
check("prerequisites split on semicolon", ibp["prerequisites"] == ["product rule", "antiderivatives"])
check("misconception preserved", ibp["misconception"] == "treats dx as decoration")

coe = by_name["Conservation of energy"]
check("strength 4 gives a 21-day interval", coe["interval_days"] == 21)
check("seen yesterday at strength 4 is not due", coe["due"] is False)

eig = by_name["Eigenvectors"]
check("strength 5 gives a 60-day interval", eig["interval_days"] == 60)
check("seen today is not due", eig["due"] is False)

print("evaluate — unreadable rows surface rather than vanish")
check("bad date flagged", "problem" in by_name["Broken row"])
check("bad strength flagged", "problem" in by_name["Bad strength"])
check("no bad row silently marked due", "due" not in by_name["Bad strength"])

print("boundary — due exactly on the interval day")
row = {
    "concept": "Boundary",
    "domain": "math",
    "first": "2026-08-01",
    "last": "2026-08-10",
    "strength": "1",
    "prerequisites": "",
    "misconception": "",
}
check("due on the exact due date", rd.evaluate(row, date(2026, 8, 12))["due"] is True)
check("not due the day before", rd.evaluate(row, date(2026, 8, 11))["due"] is False)

print("empty ledger")
empty = rd.parse_ledger("# Ledger\n\n| Concept | Domain | First | Last | Strength | Prerequisites | Misconception |\n|--|--|--|--|--|--|--|\n")
check("header with no rows yields nothing", empty == [], f"got {empty}")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILED: {', '.join(FAILURES)}")
    sys.exit(1)
print("All tests passed.")
