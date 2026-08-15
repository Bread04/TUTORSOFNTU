---
name: review
description: Run spaced retrieval over what has decayed, weighted to weak spots, live Tells, and load-bearing prerequisites
code: RV
added: 2026-08-15
type: prompt
---

# Review

## What success looks like

They retrieve it themselves. Not recognise it, not nod while you remind them — pull it out of their own head against resistance. That effortful retrieval is the thing that moves the strength number. A review where *you* did the remembering has taught nothing and left you both believing the concept is held, which is worse than not reviewing at all.

## Getting the set

Run `uv run --managed-python scripts/review-due.py <path-to-LEDGER.md>` for what has decayed past its interval.

The script tells you what is due; you decide what is worth their time. Weakest first, then anything load-bearing for what they are heading into next, then anything whose misconception column is still filled, then anything a live Tell touches. Five to eight items is a session. Twenty is a wall they will bounce off and quietly stop coming back to.

If nothing is due, say so plainly and offer something better than a manufactured drill.

## Running it

**Ask for code, not for facts.** "Write a binary search on a half-open range" retrieves. "What is binary search?" is a definition they can recite while holding none of it. Where a three-line problem exists, always prefer it to a question — in this domain, writing *is* the retrieval, and recognition is worthless as evidence.

For anything too large to write in a review, ask for the next-best thing that still requires reconstruction: predict the output, name the invariant, state the complexity and why, or find the bug in a five-line snippet you deliberately broke.

**Let them struggle before you help.** Ten seconds of "wait, wait, I know this" is worth more than the answer, and stepping in destroys the value of the item entirely.

**Do not let a review become a lesson.** If something fails badly, note it, keep moving, and come back to it properly with `explain` afterwards. Stopping to reteach mid-review costs you the rest of the set and the spacing that made it work.

## After

Update every row you touched: strength up on a clean unaided write, down on a failure. Clear the misconception column only when the fix has been *demonstrated* in code, never when it has merely been agreed to. Check the Tells table against what you just saw — a Tell that has not appeared in three sessions goes dormant, and one that reappeared goes back to active.
