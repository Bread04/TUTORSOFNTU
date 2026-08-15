#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for review-due.py.

Run: uv run --managed-python test_review_due.py
"""

from __future__ import annotations

import importlib.util
import unittest
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "review-due.py"
spec = importlib.util.spec_from_file_location("review_due", SCRIPT)
rd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rd)

ASOF = date(2026, 3, 1)

LEDGER = """# Ledger

## Strength Scale

| Value | Means |
|-------|-------|
| 0 | Taught. Not yet written by them at all. |
| 5 | Reaches for it unprompted. |

## The Table

| Concept | Domain | First | Last | Strength | Prerequisites | Misconception |
|---------|--------|-------|------|----------|---------------|---------------|
| Binary search half-open | algorithms | 2026-01-05 | 2026-02-01 | 2 | loop invariants | treats hi as inclusive |
| Call stack | language | 2026-01-10 | 2026-02-28 | 4 | function calls |  |
| Hash map lookup | data-structures | 2026-02-01 | 2026-02-20 | 1 | hashing; equality |  |
| Broken strength | craft | 2026-01-01 | 2026-01-01 | eight | | |
| Broken date | craft | 2026-01-01 | not-a-date | 3 | | |

## Tells

| Tell | First seen | Times seen | Last seen | Status | What I am doing about it |
|------|-----------|-----------|-----------|--------|--------------------------|
| off-by-one on half-open ranges | 2026-01-05 | 4 | 2026-02-20 | active | every challenge states its range half-open |
"""


class TestParsing(unittest.TestCase):
    def setUp(self):
        self.rows = rd.parse_ledger(LEDGER)

    def test_reads_only_the_concept_table(self):
        # Five concept rows -- the strength scale and the Tells table are not concepts.
        self.assertEqual(len(self.rows), 5)

    def test_tells_table_is_not_mistaken_for_concepts(self):
        concepts = [row["concept"] for row in self.rows]
        self.assertNotIn("off-by-one on half-open ranges", concepts)

    def test_strength_scale_table_is_not_mistaken_for_concepts(self):
        self.assertNotIn("0", [row["concept"] for row in self.rows])

    def test_splits_semicolon_prerequisites(self):
        row = next(r for r in self.rows if r["concept"] == "Hash map lookup")
        result = rd.evaluate(row, ASOF)
        self.assertEqual(result["prerequisites"], ["hashing", "equality"])


class TestDueArithmetic(unittest.TestCase):
    def evaluate(self, concept: str) -> dict:
        row = next(r for r in rd.parse_ledger(LEDGER) if r["concept"] == concept)
        return rd.evaluate(row, ASOF)

    def test_intervals_widen_with_strength(self):
        self.assertEqual(rd.INTERVALS, {0: 1, 1: 2, 2: 4, 3: 9, 4: 21, 5: 60})

    def test_a_decayed_concept_is_due(self):
        result = self.evaluate("Binary search half-open")
        self.assertTrue(result["due"])
        self.assertEqual(result["interval_days"], 4)
        self.assertEqual(result["due_on"], "2026-02-05")
        self.assertEqual(result["days_overdue"], 24)

    def test_a_strong_recent_concept_is_not_due(self):
        result = self.evaluate("Call stack")
        self.assertFalse(result["due"])
        self.assertEqual(result["due_on"], "2026-03-21")

    def test_a_weak_concept_comes_due_fast(self):
        result = self.evaluate("Hash map lookup")
        self.assertTrue(result["due"])
        self.assertEqual(result["interval_days"], 2)

    def test_misconception_is_carried_through(self):
        self.assertEqual(
            self.evaluate("Binary search half-open")["misconception"],
            "treats hi as inclusive",
        )


class TestUnreadableRows(unittest.TestCase):
    """A row that cannot be read must be surfaced, never silently dropped --
    a skipped row is a concept that decays invisibly."""

    def evaluate(self, concept: str) -> dict:
        row = next(r for r in rd.parse_ledger(LEDGER) if r["concept"] == concept)
        return rd.evaluate(row, ASOF)

    def test_bad_strength_is_reported(self):
        self.assertIn("unreadable strength", self.evaluate("Broken strength")["problem"])

    def test_bad_date_is_reported(self):
        self.assertIn("unreadable last-seen date", self.evaluate("Broken date")["problem"])

    def test_out_of_range_strength_is_reported(self):
        row = {
            "concept": "x", "domain": "craft", "first": "2026-01-01",
            "last": "2026-01-01", "strength": "9", "prerequisites": "", "misconception": "",
        }
        self.assertIn("outside", rd.evaluate(row, ASOF)["problem"])


class TestEmptyLedger(unittest.TestCase):
    def test_a_fresh_ledger_parses_to_nothing(self):
        empty = "# Ledger\n\n| Concept | Domain | First | Last | Strength | Prerequisites | Misconception |\n|---|---|---|---|---|---|---|\n"
        self.assertEqual(rd.parse_ledger(empty), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
