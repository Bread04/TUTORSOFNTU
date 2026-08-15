# Tutors of NTU

A pair of tutors for [Claude Code](https://claude.com/claude-code), built as agent skills.

They are the same species: each one is born once, remembers you between sessions, and keeps a ledger of what you actually hold rather than what you have been shown. They differ in what they teach and how they go about it.

| | | |
|---|---|---|
| 📐 | **[Abigail](agent-abigail/)** | Math and physics. Cheerful, and constitutionally unable to let a wrong idea stand. Teaches for transfer: worked example, faded practice, cold problem. |
| 🧩 | **[Felicia](agent-felicia/)** | Coding and algorithms. Draws before she explains, and will not let "I get it" pass unexamined. Teaches toward the code you write alone at 2am. |

## Requirements

- [Claude Code](https://claude.com/claude-code)
- [uv](https://docs.astral.sh/uv/) on your PATH — their scripts are stdlib-only, so there is nothing to install

## Install

Clone once, then copy in whichever tutors you want:

```bash
git clone https://github.com/Bread04/TUTORSOFNTU.git
cp -r TUTORSOFNTU/agent-abigail ~/.claude/skills/
cp -r TUTORSOFNTU/agent-felicia ~/.claude/skills/
```

On Windows, that destination is `%USERPROFILE%\.claude\skills\`.

Restart Claude Code, then say **"talk to Abigail"** or **"talk to Felicia"** — or run `/agent-abigail` / `/agent-felicia`.

Each tutor's own README covers what she does, how her first conversation goes, and where she keeps her memory.

> **Upgrading from an older clone?** This repo used to hold Abigail alone, at the root, installed with `git clone ... ~/.claude/skills/agent-abigail`. That no longer works — pulling into an existing install buries her `SKILL.md` a level deeper and Claude Code stops finding her. Delete the old folder and reinstall with the commands above. Her sanctum is not in the repo, so nothing you care about is lost.

## First Breath

Each tutor runs **First Breath** the first time you wake her: a one-time conversation where she works out how *you* learn, and becomes herself. It happens exactly once and everything after is built on it, so give it a real conversation rather than one-word answers.

They are born separately and remember separately. Meeting one tells the other nothing.

## Where their memory lives

Each sanctum is created under whatever directory you launch Claude Code from:

```
_bmad/memory/agent-abigail/
_bmad/memory/agent-felicia/
```

It holds who she is, what she knows about you, and your ledger.

**None of it is in this repo, and none of it should be** — it is personal to you, and it is the only copy. Back it up like any notebook you would hate to lose.

## Layout

```
agent-abigail/      her bootloader, capability prompts, sanctum templates, scripts
agent-felicia/      the same shape, her own subject
```

Both built with the BMad agent builder.
