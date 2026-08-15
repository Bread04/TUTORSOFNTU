#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for bench.py.

The timing itself is not asserted on -- wall-clock numbers are not reproducible
in CI. What is tested is everything that turns numbers into a claim: the
log-log fit, the shape labels, and the parsing that gets there.

Run: uv run --managed-python test_bench.py
"""

from __future__ import annotations

import importlib.util
import math
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "bench.py"
spec = importlib.util.spec_from_file_location("bench", SCRIPT)
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)

SIZES = [100, 1_000, 10_000, 100_000]


def synthetic(exponent: float, constant: float = 1e-9) -> list[float]:
    """Perfect timings for n**exponent, as the fit should recover them."""
    return [constant * (n ** exponent) for n in SIZES]


class TestFitExponent(unittest.TestCase):
    def test_recovers_linear(self):
        self.assertAlmostEqual(bench.fit_exponent(SIZES, synthetic(1.0)), 1.0, places=6)

    def test_recovers_quadratic(self):
        self.assertAlmostEqual(bench.fit_exponent(SIZES, synthetic(2.0)), 2.0, places=6)

    def test_recovers_constant(self):
        self.assertAlmostEqual(bench.fit_exponent(SIZES, synthetic(0.0)), 0.0, places=6)

    def test_n_log_n_lands_between_linear_and_quadratic(self):
        times = [1e-9 * n * math.log2(n) for n in SIZES]
        exponent = bench.fit_exponent(SIZES, times)
        self.assertGreater(exponent, 1.0)
        self.assertLess(exponent, 1.5)

    def test_needs_two_usable_points(self):
        self.assertIsNone(bench.fit_exponent([100], [0.1]))

    def test_ignores_non_positive_values(self):
        # log() is undefined there; dropping them must not raise.
        self.assertIsNone(bench.fit_exponent([0, 10], [0.0, 0.1]))

    def test_single_repeated_size_has_no_slope(self):
        self.assertIsNone(bench.fit_exponent([100, 100], [0.1, 0.2]))


class TestLabelGrowth(unittest.TestCase):
    def test_maps_measured_exponents_to_shapes(self):
        self.assertEqual(bench.label_growth(0.02), "O(1) or O(log n)")
        self.assertEqual(bench.label_growth(1.01), "O(n)")
        self.assertEqual(bench.label_growth(1.31), "O(n log n)")
        self.assertEqual(bench.label_growth(1.98), "O(n^2)")
        self.assertEqual(bench.label_growth(3.02), "O(n^3)")

    def test_negative_slope_is_called_noise(self):
        self.assertIn("noise", bench.label_growth(-0.4))

    def test_beyond_cubic_is_flagged_rather_than_labelled(self):
        self.assertIn("steeper than cubic", bench.label_growth(4.5))

    def test_every_shape_range_is_reachable(self):
        for low, high, name in bench.SHAPES:
            self.assertEqual(bench.label_growth((low + high) / 2), name)


class TestParseApproach(unittest.TestCase):
    def test_splits_label_from_code(self):
        self.assertEqual(bench.parse_approach("linear:x in data"), ("linear", "x in data"))

    def test_keeps_colons_inside_the_code(self):
        label, stmt = bench.parse_approach("slice:data[1:5]")
        self.assertEqual(label, "slice")
        self.assertEqual(stmt, "data[1:5]")

    def test_rejects_a_missing_label_separator(self):
        with self.assertRaises(ValueError):
            bench.parse_approach("just some code")

    def test_rejects_an_empty_statement(self):
        with self.assertRaises(ValueError):
            bench.parse_approach("label:   ")


class TestTiming(unittest.TestCase):
    def test_substitutes_the_size_token_in_setup_and_statement(self):
        seconds, loops = bench.time_once("len(data)", "data = list(range({n}))", 50, repeat=1, number=10)
        self.assertGreater(seconds, 0)
        self.assertEqual(loops, 10)

    def test_a_broken_statement_raises_rather_than_reporting_a_time(self):
        with self.assertRaises(NameError):
            bench.time_once("undefined_name", "pass", 10, repeat=1, number=1)


class TestRender(unittest.TestCase):
    def build_report(self, exponent: float) -> dict:
        times = synthetic(exponent)
        measurements = []
        previous = None
        for size, seconds in zip(SIZES, times):
            measurements.append({
                "size": size,
                "seconds": seconds,
                "loops": 1,
                "ratio": (seconds / previous) if previous else None,
            })
            previous = seconds
        return {
            "sizes": SIZES,
            "repeat": 3,
            "noisy": False,
            "approaches": [{
                "label": "candidate",
                "statement": "work()",
                "measurements": measurements,
                "exponent": exponent,
                "growth": bench.label_growth(exponent),
            }],
        }

    def test_renders_a_table_with_the_shape_named(self):
        rendered = bench.render_markdown(self.build_report(2.0))
        self.assertIn("| candidate |", rendered)
        self.assertIn("O(n^2)", rendered)
        self.assertIn("slope 2.00", rendered)

    def test_output_is_ascii_only(self):
        self.assertTrue(bench.render_markdown(self.build_report(1.0)).isascii())

    def test_noise_warning_appears_only_when_flagged(self):
        clean = self.build_report(1.0)
        self.assertNotIn("microsecond floor", bench.render_markdown(clean))
        clean["noisy"] = True
        self.assertIn("microsecond floor", bench.render_markdown(clean))

    def test_two_sizes_warns_that_a_slope_means_little(self):
        report = self.build_report(1.0)
        report["sizes"] = SIZES[:2]
        report["approaches"][0]["measurements"] = report["approaches"][0]["measurements"][:2]
        self.assertIn("Three or more", bench.render_markdown(report))


if __name__ == "__main__":
    unittest.main(verbosity=2)
