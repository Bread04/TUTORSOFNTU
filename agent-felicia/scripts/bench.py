#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# ///
"""
Bench - time approaches across input sizes so complexity is watched, not asserted.

Runs each approach at each size, reports best-of-repeat timings, the ratio
between consecutive sizes, and the growth exponent fitted on a log-log line.
Claiming an algorithm is quadratic settles nothing; watching the time go up a
hundredfold when the input goes up tenfold settles it in one command.

The `{n}` token in setup and statement code is replaced with the current size,
so one setup string covers every size.

It EXECUTES the code it is given. Read the code first.

Usage:
    uv run --managed-python bench.py \\
        --setup "data = list(range({n})); target = -1" \\
        --approach "linear:target in data" \\
        --approach "set:target in set(data)" \\
        --sizes 1000,10000,100000

Exit codes: 0 = report produced, 2 = bad input, 3 = an approach raised.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import timeit
from pathlib import Path

# Fitted log-log slope -> the shape it most likely is. Ranges are deliberately
# loose: real measurements are noisy and constants dominate at small sizes.
SHAPES = [
    (0.00, 0.30, "O(1) or O(log n)"),
    (0.30, 0.80, "sublinear - likely O(log n) with real work per step"),
    (0.80, 1.15, "O(n)"),
    (1.15, 1.55, "O(n log n)"),
    (1.55, 2.40, "O(n^2)"),
    (2.40, 3.40, "O(n^3)"),
]
NOISE_FLOOR_SECONDS = 5e-6

# Windows consoles default to a codepage that cannot encode arbitrary text.
# Replace rather than crash.
for stream in (sys.stdout, sys.stderr):
    try:
        stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def label_growth(exponent: float) -> str:
    for low, high, name in SHAPES:
        if low <= exponent < high:
            return name
    if exponent < 0:
        return "no growth measured (times fell as n rose - almost certainly noise)"
    return f"steeper than cubic (exponent {exponent:.2f}) - check for exponential work"


def fit_exponent(sizes: list[int], times: list[float]) -> float | None:
    """Least-squares slope of log(time) against log(n). That slope is the exponent."""
    points = [(math.log(n), math.log(t)) for n, t in zip(sizes, times) if n > 0 and t > 0]
    if len(points) < 2:
        return None
    n_points = len(points)
    mean_x = sum(x for x, _ in points) / n_points
    mean_y = sum(y for _, y in points) / n_points
    denominator = sum((x - mean_x) ** 2 for x, _ in points)
    if denominator == 0:
        return None
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in points)
    return numerator / denominator


def time_once(stmt: str, setup: str, size: int, repeat: int, number: int | None) -> tuple[float, int]:
    """Best-of-repeat seconds per execution, plus the loop count actually used."""
    concrete_stmt = stmt.replace("{n}", str(size))
    concrete_setup = setup.replace("{n}", str(size))
    timer = timeit.Timer(stmt=concrete_stmt, setup=concrete_setup)
    if number is None:
        number, _ = timer.autorange()
    results = timer.repeat(repeat=repeat, number=number)
    return min(results) / number, number


def parse_approach(raw: str) -> tuple[str, str]:
    label, separator, stmt = raw.partition(":")
    if not separator or not stmt.strip():
        raise ValueError(f"--approach must be LABEL:CODE, got {raw!r}")
    return label.strip(), stmt.strip()


def render_markdown(report: dict) -> str:
    sizes = report["sizes"]
    lines = ["| Approach | " + " | ".join(f"n={n:,}" for n in sizes) + " | Growth |",
             "|" + "|".join("---" for _ in range(len(sizes) + 2)) + "|"]

    for result in report["approaches"]:
        cells = []
        for entry in result["measurements"]:
            seconds = entry["seconds"]
            cell = f"{seconds * 1e6:,.1f} us" if seconds < 1e-3 else f"{seconds * 1e3:,.2f} ms"
            if entry.get("ratio") is not None:
                cell += f" (x{entry['ratio']:.1f})"
            cells.append(cell)
        growth = result["growth"] or "-"
        exponent = result["exponent"]
        if exponent is not None:
            growth += f" (slope {exponent:.2f})"
        lines.append(f"| {result['label']} | " + " | ".join(cells) + f" | {growth} |")

    notes = ["xN is the multiplier over the previous size. Compare it to how much n grew."]
    if report["noisy"]:
        notes.append(
            "Some timings are near the microsecond floor, where constants and noise dominate. "
            "Raise the smallest size before drawing conclusions from the slope."
        )
    if len(sizes) < 3:
        notes.append("Two sizes fit a line through two points. Three or more makes the slope mean something.")

    lines.append("")
    lines.extend(f"> {note}" for note in notes)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Time approaches across input sizes and report the measured growth.",
        epilog="Use {n} in --setup/--approach for the current size. "
               "Exit codes: 0 = report produced, 2 = bad input, 3 = an approach raised.",
    )
    parser.add_argument("--setup", default="pass", help="Setup code, run once per timing (not timed)")
    parser.add_argument("--approach", action="append", required=True, metavar="LABEL:CODE",
                        help="An approach to time; repeat for a head-to-head")
    parser.add_argument("--sizes", default="1000,10000,100000",
                        help="Comma-separated input sizes (default 1000,10000,100000)")
    parser.add_argument("--repeat", type=int, default=5, help="Timing runs per size, best wins (default 5)")
    parser.add_argument("--number", type=int, help="Loops per run; omit to calibrate automatically")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write here instead of stdout")
    args = parser.parse_args()

    try:
        sizes = [int(s.strip()) for s in args.sizes.split(",") if s.strip()]
        approaches = [parse_approach(raw) for raw in args.approach]
    except ValueError as exc:
        print(f"Bad input: {exc}", file=sys.stderr)
        return 2
    if not sizes:
        print("No sizes given.", file=sys.stderr)
        return 2

    results = []
    noisy = False
    for label, stmt in approaches:
        measurements = []
        previous: float | None = None
        for size in sizes:
            try:
                seconds, number = time_once(stmt, args.setup, size, args.repeat, args.number)
            except Exception as exc:
                print(f"Approach {label!r} raised at n={size}: {type(exc).__name__}: {exc}", file=sys.stderr)
                return 3
            if seconds < NOISE_FLOOR_SECONDS:
                noisy = True
            measurements.append({
                "size": size,
                "seconds": seconds,
                "loops": number,
                "ratio": (seconds / previous) if previous else None,
            })
            previous = seconds

        exponent = fit_exponent(sizes, [m["seconds"] for m in measurements])
        results.append({
            "label": label,
            "statement": stmt,
            "measurements": measurements,
            "exponent": exponent,
            "growth": label_growth(exponent) if exponent is not None else None,
        })

    report = {"sizes": sizes, "repeat": args.repeat, "approaches": results, "noisy": noisy}
    payload = json.dumps(report, indent=2) if args.format == "json" else render_markdown(report)

    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
