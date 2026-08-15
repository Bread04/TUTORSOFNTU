#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Trace Table — run Python code and record what every variable actually did.

Produces the trace table a learner would draw by hand, except correct. Each row
is one line that executed and the state of the locals *after* it ran, which is
the orientation people naturally read a trace in. Recursion gets a depth column
so the call stack is visible rather than implied.

This exists because hand-simulated traces are wrong often enough to matter, and
a wrong trace table is worse than none: it teaches a false model with the
teacher's authority behind it. Let the machine do the simulating.

It EXECUTES the code it is given, in this process. Read the code first. Never
feed it anything destructive to find out what it does.

Usage:
    uv run --managed-python trace-table.py path/to/snippet.py
    uv run --managed-python trace-table.py -c "for i in range(3): print(i)"
    uv run --managed-python trace-table.py snippet.py --watch i,total --func fib
    uv run --managed-python trace-table.py snippet.py --format json

Exit codes: 0 = trace produced (even if the code raised), 2 = bad input.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

SNIPPET_FILENAME = "<traced>"
VALUE_WIDTH = 44
MANY_COLUMNS = 12

# The traced code's own output is arbitrary text, and Windows consoles default
# to a codepage that cannot encode most of it. Replace rather than crash: a
# mangled character costs a glyph, an encoding error costs the whole trace.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def shorten(value: object) -> str:
    """A readable one-line repr, truncated so the table stays a table."""
    try:
        text = repr(value)
    except Exception as exc:  # a broken __repr__ should not kill the trace
        return f"<unrepr-able: {type(exc).__name__}>"
    text = " ".join(text.split())
    if len(text) > VALUE_WIDTH:
        text = text[: VALUE_WIDTH - 3] + "..."
    return text


class Frame:
    """One live call: the line it is waiting to close, and how deep it sits."""

    __slots__ = ("scope", "depth", "line")

    def __init__(self, scope: str, depth: int):
        self.scope = scope
        self.depth = depth
        self.line: int | None = None


class Tracer:
    """Collect (line, locals-after) pairs for frames belonging to the snippet.

    A 'line' event fires *before* that line runs, so the locals it carries are
    the result of the previous line in that same frame. Rows are therefore
    emitted one step behind the events, pairing each line with the state that
    followed it.

    Calls nest strictly, so a stack tracks which line each live frame is
    waiting to close. This matters: without it, a line in the caller gets
    closed using the callee's locals, and the table quietly lies about which
    scope the values belong to. A line containing a call closes only when that
    call returns, which is also when its "after" state is genuinely known.
    """

    def __init__(self, source_lines: list[str], watch: set[str] | None, func: str | None, max_steps: int):
        self.source_lines = source_lines
        self.watch = watch
        self.func = func
        self.max_steps = max_steps
        self.rows: list[dict] = []
        self.stack: list[Frame] = []
        self.truncated = False
        self.seen_depth = False

    def source(self, lineno: int) -> str:
        if 1 <= lineno <= len(self.source_lines):
            return self.source_lines[lineno - 1].strip()
        return ""

    def snapshot(self, frame) -> dict[str, str]:
        return {
            name: shorten(value)
            for name, value in frame.f_locals.items()
            if not name.startswith("__")
            and (self.watch is None or name in self.watch)
        }

    def flush(self, live: Frame, frame, note: str = "") -> None:
        """Close the frame's pending line using that same frame's state."""
        if live.line is None:
            return
        self.rows.append(
            {
                "step": len(self.rows) + 1,
                "line": live.line,
                "depth": live.depth,
                "code": self.source(live.line),
                "scope": live.scope,
                "vars": self.snapshot(frame),
                "note": note,
            }
        )
        live.line = None

    def __call__(self, frame, event, arg):
        if frame.f_code.co_filename != SNIPPET_FILENAME:
            return None
        name = frame.f_code.co_name

        if event == "call":
            # The module frame is depth 0; every real call sits below it.
            depth = len(self.stack)
            if depth > 0:
                self.seen_depth = True
            self.stack.append(Frame(name, depth))
            return self

        if not self.stack:
            return self
        live = self.stack[-1]

        if event == "return":
            # A module "returning" is just the script ending; only real calls
            # carry a return value worth showing.
            self.flush(live, frame, note="" if name == "<module>" else f"return {shorten(arg)}")
            self.stack.pop()
            return self

        if event != "line":
            return self

        if self.func and name != self.func:
            return self

        # The locals on this event are the outcome of this frame's previous line.
        self.flush(live, frame)

        if len(self.rows) >= self.max_steps:
            self.truncated = True
            sys.settrace(None)
            return None

        live.line = frame.f_lineno
        return self


def render_markdown(tracer: Tracer, output: str, error: str | None) -> str:
    rows = tracer.rows
    if not rows:
        return "No lines were traced. Check --func, or whether the code ran at all."

    columns: list[str] = []
    for row in rows:
        for var in row["vars"]:
            if var not in columns:
                columns.append(var)

    show_depth = tracer.seen_depth
    header = ["#", "Line"]
    if show_depth:
        header.append("Depth")
    header += ["Code"] + columns
    lines = [
        "| " + " | ".join(header) + " |",
        "|" + "|".join("---" for _ in header) + "|",
    ]

    for row in rows:
        cells = [str(row["step"]), str(row["line"])]
        if show_depth:
            cells.append(">" * row["depth"] if row["depth"] else "")
        code = row["code"]
        if row["note"]:
            code = f"{code}  -> {row['note']}" if code else row["note"]
        cells.append(f"`{code}`" if code else "")
        cells += [row["vars"].get(var, "") for var in columns]
        lines.append("| " + " | ".join(cells) + " |")

    notes = []
    if tracer.truncated:
        notes.append(
            f"Stopped after {tracer.max_steps} steps. Raise --max-steps, or shrink the input "
            "— a trace this long is usually a sign the example is too big to teach from."
        )
    if len(columns) > MANY_COLUMNS:
        notes.append(f"{len(columns)} variables is a wide table. Narrow it with --watch.")
    if error:
        notes.append(f"The code raised: {error}. The last row is the state when it did.")
    if output.strip():
        notes.append("Captured stdout:\n```\n" + output.rstrip() + "\n```")

    if notes:
        lines.append("")
        lines.extend(f"> {note}" for note in notes)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Python code and print a trace table of what the variables did.",
        epilog="Exit codes: 0 = trace produced, 2 = bad input.",
    )
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument("path", nargs="?", help="Path to a .py file to trace")
    source_group.add_argument("-c", "--code", help="Code to trace, as a string")
    parser.add_argument("--watch", help="Comma-separated variable names; others are hidden")
    parser.add_argument("--func", help="Only trace lines inside this function")
    parser.add_argument("--max-steps", type=int, default=200, help="Stop after this many rows (default 200)")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write here instead of stdout")
    args = parser.parse_args()

    if args.code is not None:
        source = args.code
    else:
        try:
            source = Path(args.path).read_text(encoding="utf-8")
        except OSError as exc:
            print(f"Cannot read snippet: {exc}", file=sys.stderr)
            return 2

    try:
        compiled = compile(source, SNIPPET_FILENAME, "exec")
    except SyntaxError as exc:
        print(f"Snippet does not compile: {exc}", file=sys.stderr)
        return 2

    watch = {w.strip() for w in args.watch.split(",") if w.strip()} if args.watch else None
    tracer = Tracer(source.splitlines(), watch, args.func, max(1, args.max_steps))

    namespace: dict = {"__name__": "__main__", "__file__": SNIPPET_FILENAME}
    buffer = io.StringIO()
    error: str | None = None

    sys.settrace(tracer)
    try:
        with redirect_stdout(buffer):
            exec(compiled, namespace)
    except BaseException as exc:  # the failure is the interesting part, not a crash
        error = f"{type(exc).__name__}: {exc}"
    finally:
        sys.settrace(None)

    if args.format == "json":
        payload = json.dumps(
            {
                "rows": tracer.rows,
                "truncated": tracer.truncated,
                "stdout": buffer.getvalue(),
                "error": error,
            },
            indent=2,
        )
    else:
        payload = render_markdown(tracer, buffer.getvalue(), error)

    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
