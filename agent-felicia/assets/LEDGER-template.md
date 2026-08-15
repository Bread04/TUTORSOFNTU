# Ledger

Every concept taught, what it rests on, and how well it is actually held — plus the Tells, the habits that cross every concept. This is the file that makes you different from a very good one-off explanation: it is how you know what has decayed, what is load-bearing, and what to aim the next challenge at.

`scripts/review-due.py` parses the concept table below, so keep the column order and the pipe format exactly as they are. Everything else about the row is yours to write well.

## Strength Scale

| Value | Means |
|-------|-------|
| 0 | Taught. Not yet written by them at all. |
| 1 | Shaky — got there, but you were holding the pen. |
| 2 | Wrote it with hints. |
| 3 | Wrote it cold, once, from an empty file. |
| 4 | Wrote it cold more than once, on problems that did not look alike. |
| 5 | Reaches for it unprompted in a context you did not set up, or can teach it back. |

Strength is evidence, not encouragement. Never raise a number because someone had a good session; raise it because they did something that only a stronger understanding could produce. Recognising correct code is not evidence — writing it is. Lowering a number is not a demotion, it is the system working: a 4 that stalls twice was never a 4, and finding that out is exactly what this file is for.

## Review Intervals

Derived from strength by the script, in days: **0 → 1, 1 → 2, 2 → 4, 3 → 9, 4 → 21, 5 → 60.** Widening intervals are the whole mechanism — retrieving something at the edge of forgetting is what makes it stick, and reviewing it while it is still fresh is close to wasted effort.

## The Table

| Concept | Domain | First | Last | Strength | Prerequisites | Misconception |
|---------|--------|-------|------|----------|---------------|---------------|

**Concept** — specific enough to review from. "Binary search on a half-open range" is a concept; "algorithms" is a syllabus. "Recursion" is too broad to be useful — split it into base cases, the call stack, and recursive descent, because those decay independently.

**Domain** — `algorithms`, `data-structures`, `complexity`, `language` (a feature of a specific language), `craft` (design, naming, decomposition, testing), `debugging`, or `tooling`. A finer tag is fine if it earns one.

**First** / **Last** — ISO dates. `First` never changes. `Last` is the most recent time they *engaged* with it, not the last time you mentioned it.

**Prerequisites** — semicolon-separated concept names that must hold for this one to work. These are what let you say *"this is going to bite, because references-versus-values never really landed."* Worth the effort to fill honestly: in code, a cracked prerequisite does not produce confusion, it produces a bug they cannot explain.

**Misconception** — the specific broken model, if there was one, in their terms. Not a topic label. `believes the recursive call resumes at the top of the function, not at the call site` is worth writing; `struggles with recursion` is not. Leave empty when there was no error worth recording, and clear it only when the fix has been *demonstrated* in code, never when it has merely been agreed to.

## Tells

Cross-cutting habits, not concepts. A single mistake is noise; the same mistake in three different costumes is a Tell, and Tells are where the leverage is — one fixed Tell repairs code they have not written yet.

Record one after you have seen it twice. Kill it when they have gone three separate sessions without it appearing, and note when you killed it — Tells come back, and knowing it returned is itself information.

| Tell | First seen | Times seen | Last seen | Status | What I am doing about it |
|------|-----------|-----------|-----------|--------|--------------------------|

**Tell** — the failure signature in mechanical terms. `off-by-one on any half-open range` or `reaches for a nested loop before considering a hash map` or `never writes the base case first` or `mutates the collection being iterated`. Write it so a challenge can be aimed at it.

**Status** — `active`, `improving`, or `dormant since YYYY-MM-DD`.

**What I am doing about it** — the concrete plan. A Tell with no plan is a complaint. `Every challenge this month states its range as half-open, and I make them say the bound out loud before they write the loop.`
