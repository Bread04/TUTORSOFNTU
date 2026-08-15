# Felicia 🧩

A coding and algorithms tutor for [Claude Code](https://claude.com/claude-code), built as an agent skill. Abigail's sister — same species, different subject.

She teaches toward **the code you write alone**, not the code you can follow while she narrates. Her mission, in her own words:

> Turn your owner from someone who can follow code into someone who can write it alone. Not the understanding that holds while you are explaining — the kind that survives the blank editor, the failing test, and the problem nobody has solved for them yet.

She draws before she explains, because code is a thing that *moves* and a paragraph about movement is a poor substitute for watching it move. She is precise without being cold, opinionated about craft and honest that they are opinions rather than laws. And she will not let "I get it" pass unexamined — she asks in a way that makes admitting confusion the easy answer rather than the embarrassing one.

## What she does

| | |
|---|---|
| **Explain** | What the code does, what problem it was invented to solve, and where it shows up unlabelled. She checks your prerequisites first, then makes you *predict the output* before she reveals it — because the gap between your prediction and reality is the most precise diagnostic there is. Asks "where did I lose you?", never "does that make sense?" |
| **Challenge** | Reads the ledger, picks the thing that will bite, then adds the constraint that closes the escape route — no recursion, O(1) space, one pass. A problem you can solve *around* teaches nothing. Worked, then faded, then cold, and she goes quiet while you work. |
| **Critique** | Reads every line and runs it before saying anything, then picks the three findings that generalise over the twenty that don't. Every finding carries its reason, because "extract this" is a rule you'll misapply and "extract this, because it now does two things and you can't name it without saying *and*" is a reason you can carry to code she'll never see. |
| **Debug** | You narrow it, the machine adjudicates. She sees the bug immediately and doesn't say it — she asks the question that would have made you see it. What gets written down afterwards is the broken model, not the fix. |
| **Review** | Spaced retrieval over what has decayed. She asks you to *write*, not to recognise, because recognition is worthless as evidence here. |

Underneath sits a **ledger**: every concept with a strength score, its prerequisites, and the specific broken belief behind any error — `believes the recursive call resumes at the top of the function, not at the call site`, never `struggles with recursion`.

Above that sits her **Tells** table, which is the part that makes her different. A single mistake is noise; the same mistake in three costumes is a Tell. Off-by-one on every half-open range, a nested loop reached for before a hash map, never writing the base case first. She records one after seeing it twice, then aims challenges at it directly — because one fixed Tell repairs code you haven't written yet.

## She runs your code

She executes things rather than asserting them, and two of her instruments exist because the alternative is being confidently wrong:

**`trace-table.py`** produces a real line-by-line variable trace, because hand-simulated traces are wrong often enough to matter and a wrong trace table teaches a false model with the teacher's authority behind it.

```
| # | Line | Depth | Code                                  | n |
| 4 | 2    | >>>   | `if n <= 1:`                          | 1 |
| 5 | 3    | >>>   | `return 1  -> return 1`               | 1 |
| 6 | 4    | >>    | `return n * fact(n - 1)  -> return 2` | 2 |
| 7 | 4    | >     | `return n * fact(n - 1)  -> return 6` | 3 |
```

**`bench.py`** times approaches across input sizes and fits the growth curve, so complexity is something you watch bend rather than something she claims.

```
| Approach  | n=1,000 | n=5,000       | n=20,000      | Growth             |
| list scan | 2.7 us  | 13.7 us (x5.0)| 55.9 us (x4.1)| O(n) (slope 1.01)  |
```

Both are Python instruments. In other languages she reasons and measures differently, and says so.

She works in scratch files and will not edit your source unless you ask.

## Requirements

- [Claude Code](https://claude.com/claude-code)
- [uv](https://docs.astral.sh/uv/) on your PATH (her scripts are stdlib-only, no dependencies to install)

## Install

Clone the collection, then copy her into your Claude Code skills directory:

```bash
git clone https://github.com/Bread04/TUTORSOFNTU.git
cp -r TUTORSOFNTU/agent-felicia ~/.claude/skills/
```

On Windows, that destination is `%USERPROFILE%\.claude\skills\agent-felicia`.

Restart Claude Code, then say **"talk to Felicia"** or run `/agent-felicia`.

## First Breath

The first time you wake her, she runs **First Breath** — a one-time conversation where she learns how *you* code. Not by asking: she'll teach you something small, then get you writing three or four lines, and watch. Did you run it or hand it over for approval? Did you read the error or scroll past it? Is everything named `x` and `temp`? Did you check the empty case unprompted?

People can't report how they code. Everyone says they learn by doing and almost nobody knows whether it's true. Five minutes of watching beats an hour of asking.

It happens exactly once and everything after is built on it, so give it a real conversation. Come with a bug or a concept you're actually stuck on — she calibrates better against something real, and it's a better first meeting than an intake form.

## Where her memory lives

Her sanctum is created at `_bmad/memory/agent-felicia/` under whatever directory you launch Claude Code from. It holds who she is, what she knows about you, your concept ledger, and your Tells.

**It is not in this repo, and it should not be** — it is personal to you, and it is the only copy. Back it up like you would any notebook you would hate to lose.

## Layout

```
SKILL.md            her bootloader: identity, laws, activation
customize.toml      name, title, icon, agent type
references/         capability prompts (explain, challenge, critique, debug, review) + guidance
assets/             sanctum templates, written out at First Breath
scripts/            wake, sanctum init, trace tables, benchmarking, spaced-retrieval scheduling
scripts/tests/      51 unit tests across the three domain scripts
```

Built with the BMad agent builder.
