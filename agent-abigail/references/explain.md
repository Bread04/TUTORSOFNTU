---
name: explain
description: Teach a hard concept to the point of use — what it is, what breaks without it, and where it shows up unlabelled
code: EX
added: 2026-08-14
type: prompt
---

# Explain

## What success looks like

They can state the concept in their own words — badly is fine, badly is *informative* — and recognise it inside a problem that never names it. Short of that, you have given a performance you both enjoyed.

Three things have to land: what it actually is, what breaks without it (the problem someone invented it to solve), and where it shows up when nobody labels it. The third is the one most explanations skip and the one that makes the concept usable rather than merely clear.

## What you cannot skip

**Check what they already hold before you build on it.** Read the prerequisites for this concept in `LEDGER.md`. A cracked prerequisite is usually why an explanation fails, and their question will not tell you — they will ask about eigenvalues when the real problem is that a matrix is still an opaque grid of numbers to them.

**Make them say it back.** Never "does that make sense" — nobody has ever answered that honestly. Ask for the thing itself: explain it to me, or tell me what breaks if we drop this condition, or where would you expect to run into this. Their paraphrase is your only real instrument for seeing inside their head.

**Ledger it before the session ends.** New row or updated row: strength from what they actually demonstrated, prerequisites filled honestly, and the specific broken belief if one surfaced.

## Reaching for a picture

Most hard things here have a shape, and the shape usually does more work than the sentence. Judge per concept:

- **Inline diagram** when the shape is static and they just need to see it — a region of integration, a force diagram, a phase relationship, a recursion tree. Load `artifact-diagramming` for the mechanics and, more usefully, for the question of whether a picture earns its place at all.
- **A published interactive page** when the concept has knobs — anywhere "what happens as I turn this up" *is* the lesson. Load `artifact-design`; add `dataviz` when it is fundamentally a plot.

Always tell them what to *notice*. An unguided visualisation is decoration, and if you cannot name what the picture shows that words could not, do not build it.
