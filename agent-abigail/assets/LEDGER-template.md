# Ledger

Every concept taught, what it rests on, and how well it is actually held. This is the file that makes you different from a very good one-off explanation: it is how you know what has decayed, what is load-bearing, and what to bring back before it is gone.

`scripts/review-due.py` parses the table below, so keep the column order and the pipe format exactly as they are. Everything else about the row is yours to write well.

## Strength Scale

| Value | Means |
|-------|-------|
| 0 | Taught. Not yet demonstrated by them at all. |
| 1 | Shaky — got there, but only with heavy scaffolding. |
| 2 | Solved with hints. |
| 3 | Solved cold, once. |
| 4 | Solved cold, more than once, on different-looking problems. |
| 5 | Uses it unprompted in a context you did not set up, or can teach it back. |

Strength is evidence, not encouragement. Never raise a number because someone had a good session; raise it because they did something that only a stronger understanding could produce. Lowering a number is not a demotion, it is the system working — a 4 that stalls twice was never a 4, and finding that out is exactly what this file is for.

## Review Intervals

Derived from strength by the script, in days: **0 → 1, 1 → 2, 2 → 4, 3 → 9, 4 → 21, 5 → 60.** Widening intervals are the whole mechanism — reviewing something at the edge of forgetting is what makes it stick, and reviewing it while it is still fresh is close to wasted effort.

## The Table

| Concept | Domain | First | Last | Strength | Prerequisites | Misconception |
|---------|--------|-------|------|----------|---------------|---------------|

**Concept** — specific enough to review. "Integration by parts" is a concept; "calculus" is a syllabus.

**Domain** — `math` or `physics`, or a finer tag if it earns one.

**First** / **Last** — ISO dates. `First` never changes. `Last` is the most recent time they *engaged* with it, not the last time you mentioned it.

**Prerequisites** — semicolon-separated concept names that must hold for this one to work. These are what let you say *"this is going to bite, because the chain rule never really landed."* Worth the effort to fill honestly.

**Misconception** — the specific broken belief, if there was one, in their terms. Not a topic label. `treats dx as decoration rather than a factor` is worth writing; `struggles with integration` is not. Leave empty when there was no error worth recording, and clear it once it is genuinely fixed.
