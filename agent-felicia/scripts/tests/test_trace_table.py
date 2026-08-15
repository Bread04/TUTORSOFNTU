#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""Unit tests for trace-table.py.

Run: uv run --managed-python test_trace_table.py
"""

from __future__ import annotations

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "trace-table.py"
spec = importlib.util.spec_from_file_location("trace_table", SCRIPT)
tt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tt)


def run_trace(source: str, watch=None, func=None, max_steps=200):
    """Trace a snippet the way main() does, and hand back the tracer."""
    compiled = compile(source, tt.SNIPPET_FILENAME, "exec")
    tracer = tt.Tracer(source.splitlines(), watch, func, max_steps)
    namespace = {"__name__": "__main__", "__file__": tt.SNIPPET_FILENAME}
    buffer = io.StringIO()
    error = None
    sys.settrace(tracer)
    try:
        with redirect_stdout(buffer):
            exec(compiled, namespace)
    except BaseException as exc:
        error = f"{type(exc).__name__}: {exc}"
    finally:
        sys.settrace(None)
    return tracer, buffer.getvalue(), error


class TestShorten(unittest.TestCase):
    def test_truncates_long_values(self):
        result = tt.shorten(list(range(100)))
        self.assertLessEqual(len(result), tt.VALUE_WIDTH)
        self.assertTrue(result.endswith("..."))

    def test_collapses_newlines(self):
        self.assertNotIn("\n", tt.shorten("a\nb"))

    def test_survives_a_broken_repr(self):
        class Hostile:
            def __repr__(self):
                raise RuntimeError("no")

        self.assertIn("unrepr-able", tt.shorten(Hostile()))


class TestLoopTrace(unittest.TestCase):
    SOURCE = "total = 0\nfor i in range(3):\n    total += i\n"

    def test_records_each_executed_line(self):
        tracer, _, error = run_trace(self.SOURCE)
        self.assertIsNone(error)
        self.assertEqual([row["line"] for row in tracer.rows], [1, 2, 3, 2, 3, 2, 3, 2])

    def test_state_is_the_value_after_the_line_ran(self):
        tracer, _, _ = run_trace(self.SOURCE)
        # Row 1 closes `total = 0`, so total is 0 there, not absent.
        self.assertEqual(tracer.rows[0]["vars"]["total"], "0")
        # The last row closes the final loop check: 0 + 1 + 2.
        self.assertEqual(tracer.rows[-1]["vars"]["total"], "3")

    def test_watch_filters_columns(self):
        tracer, _, _ = run_trace(self.SOURCE, watch={"total"})
        for row in tracer.rows:
            self.assertNotIn("i", row["vars"])
            self.assertIn("total", row["vars"])

    def test_max_steps_truncates_and_flags(self):
        tracer, _, _ = run_trace("for i in range(1000):\n    pass\n", max_steps=5)
        self.assertTrue(tracer.truncated)
        self.assertEqual(len(tracer.rows), 5)


class TestRecursionTrace(unittest.TestCase):
    """The regression that motivated the frame stack.

    Without per-frame pending lines, a caller's line gets closed using the
    callee's locals, so the table reports the wrong scope's values.
    """

    SOURCE = "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n\nresult = fact(3)\n"

    def test_depth_increases_with_each_call(self):
        tracer, _, _ = run_trace(self.SOURCE)
        self.assertTrue(tracer.seen_depth)
        self.assertEqual(max(row["depth"] for row in tracer.rows), 3)

    def test_module_level_lines_are_depth_zero(self):
        tracer, _, _ = run_trace(self.SOURCE)
        module_rows = [row for row in tracer.rows if row["scope"] == "<module>"]
        self.assertTrue(module_rows)
        self.assertTrue(all(row["depth"] == 0 for row in module_rows))

    def test_each_row_carries_its_own_frames_locals(self):
        tracer, _, _ = run_trace(self.SOURCE)
        for row in tracer.rows:
            if row["scope"] == "fact":
                self.assertIn("n", row["vars"])
            else:
                # The module frame never had an `n`; seeing one means a
                # callee's locals leaked into the caller's row.
                self.assertNotIn("n", row["vars"])

    def test_returns_unwind_in_order(self):
        tracer, _, _ = run_trace(self.SOURCE)
        returns = [row["note"] for row in tracer.rows if row["note"]]
        self.assertEqual(returns, ["return 1", "return 2", "return 6"])

    def test_module_end_is_not_reported_as_a_return(self):
        tracer, _, _ = run_trace(self.SOURCE)
        module_notes = [row["note"] for row in tracer.rows if row["scope"] == "<module>"]
        self.assertEqual(module_notes, [""] * len(module_notes))


class TestFailureCapture(unittest.TestCase):
    def test_exception_is_reported_with_the_last_state(self):
        tracer, _, error = run_trace("items = [1, 2]\ni = 5\nprint(items[i])\n")
        self.assertIn("IndexError", error)
        self.assertEqual(tracer.rows[-1]["vars"]["i"], "5")

    def test_stdout_is_captured_not_interleaved(self):
        tracer, output, _ = run_trace("print('hello')\n")
        self.assertEqual(output.strip(), "hello")
        rendered = tt.render_markdown(tracer, output, None)
        self.assertIn("Captured stdout", rendered)


class TestRender(unittest.TestCase):
    def test_empty_trace_explains_itself(self):
        tracer = tt.Tracer([], None, "nope", 200)
        self.assertIn("No lines were traced", tt.render_markdown(tracer, "", None))

    def test_table_is_ascii_only(self):
        tracer, output, _ = run_trace("a = 1\nb = a + 1\n")
        rendered = tt.render_markdown(tracer, output, None)
        self.assertTrue(rendered.isascii(), "output must survive a cp1252 console")

    def test_depth_column_appears_only_when_calls_nest(self):
        flat, _, _ = run_trace("a = 1\n")
        self.assertNotIn("Depth", tt.render_markdown(flat, "", None))
        nested, _, _ = run_trace("def f():\n    return 1\n\nf()\n")
        self.assertIn("Depth", tt.render_markdown(nested, "", None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
