---
name: review
description: Run spaced retrieval over what has decayed, weighted to weak spots and load-bearing prerequisites
code: RV
added: 2026-08-14
type: prompt
---

# Review

## What success looks like

They retrieve it themselves. Not recognise it, not nod along while you remind them — pull it out of their own head against resistance. That effortful retrieval is the thing that moves the strength number. A review where *you* did the remembering has taught nothing and left you both believing the concept is held, which is worse than not reviewing at all.

## Getting the set

Run `uv run --managed-python scripts/review-due.py <path-to-LEDGER.md>` for what has decayed past its interval. Pulse may have already built a set into `review/YYYY-MM-DD.md` — use that if it is there.

The script tells you what is due; you decide what is worth their time. Weakest first, then anything load-bearing for what they are heading into next, then anything whose misconception column is still filled in. Five to eight items is a session. Twenty is a wall they will bounce off and quietly stop coming back to.

If nothing is due, say so plainly and offer something better than a manufactured drill.

## Running it

**Ask for the thing, not about the thing.** "What is the derivative of arctan x?" is retrieval. "Do you remember how arctan derivatives work?" is a yes/no they will answer wrong in a way that tells you nothing. Where a small problem exists, prefer it to a definition question — application retrieves much harder than recall.

**Let them struggle before you help.** Ten seconds of "wait, wait, I know this" is worth more than the answer, and stepping in destroys the value of the item entirely.

**Do not let a review become a lesson.** If something fails badly, note it, keep moving, and come back to it properly with `explain` afterwards. Stopping to reteach mid-review costs you the rest of the set and the spacing that made it work.

## After

Update every row you touched: strength up on a clean unaided retrieval, down on a failure. Clear the misconception column only when the fix has been *demonstrated*, never when it has merely been agreed to. Delete the review file once it has been run.
