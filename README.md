# Abigail 📐

A cheerful math and physics tutor for [Claude Code](https://claude.com/claude-code), built as an agent skill.

She teaches for **transfer and retention**, not for the nod of understanding you get at the end of a good explanation. Her mission, in her own words:

> Turn the concepts your owner finds hardest into tools they can actually reach for. Not the fleeting clarity of a good explanation — understanding that survives the week and shows up when a problem needs it.

She is warm and straight at the same time. She will tell you your reasoning is broken as cheerfully as she will tell you it is brilliant, because pretending otherwise wastes the one thing you cannot get back.

## What she does

| | |
|---|---|
| **Explain** | What the concept is, what breaks without it, and where it shows up when nobody labels it. She checks your prerequisites first, then makes you say it back — because "does that make sense?" has never once been answered honestly. Draws a diagram when the shape does the work; builds an interactive page when the concept has knobs to turn. |
| **Work It** | Worked example → faded practice → cold problem. She solves one out loud including the decisions that could have gone the other way, then removes the step that carries the *concept* (never the arithmetic), then hands you something that shares the idea and nothing on the surface. Then she goes quiet and lets you be stuck, because the reach is where the learning happens. |
| **Review** | Spaced retrieval over what has actually decayed. She asks for the thing, not *about* the thing, and refuses to let a review turn into a lesson. |

Underneath sits a **concept ledger** — a map with strength scores, prerequisite edges, and a misconception column that only clears when you *demonstrate* the fix, never when you merely agree to it.

She also runs on a **pulse**: she wakes on her own schedule, works out what is fading, and leaves a review set ready for you. She never notifies and never nags.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- [uv](https://docs.astral.sh/uv/) on your PATH (her scripts are stdlib-only, no dependencies to install)

## Install

Clone into your Claude Code skills directory:

```bash
git clone https://github.com/Bread04/TUTORSOFNTU.git ~/.claude/skills/agent-abigail
```

On Windows, that path is `%USERPROFILE%\.claude\skills\agent-abigail`.

Restart Claude Code, then say **"talk to Abigail"** or run `/agent-abigail`.

## First Breath

The first time you wake her, she runs **First Breath** — a one-time conversation where she learns how *you* learn: your pace, whether you want the answer or the nudge, how being wrong tends to land on you. She writes that into her memory and is continuous from then on.

It happens exactly once and everything after is built on it, so give it a real conversation rather than one-word answers. Come with a concept you actually want to work on — she calibrates better against something real.

## Where her memory lives

Her sanctum is created at `_bmad/memory/agent-abigail/` under whatever directory you launch Claude Code from. It holds who she is, what she knows about you, and your concept ledger.

**It is not in this repo, and it should not be** — it is personal to you, and it is the only copy. Back it up like you would any notebook you would hate to lose.

## Layout

```
SKILL.md            her bootloader: identity, laws, activation
customize.toml      name, title, icon, agent type
references/         capability prompts (explain, work-it, review) + guidance
assets/             sanctum templates, written out at First Breath
scripts/            wake, sanctum init, spaced-retrieval scheduling
```

Built with the BMad agent builder.
