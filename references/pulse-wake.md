---
name: pulse-wake
description: How Abigail's autonomous wake is scheduled, and what the owner has to set up for it to fire
---

# Pulse Wake

Pulse is the only part of Abigail that needs setting up outside a conversation. Nothing in the skill schedules itself — a scheduled task on the owner's machine invokes her, she does the work in `PULSE.md`, and she exits. Until that task exists she is a memory agent that never wakes on her own, however complete `PULSE.md` looks.

**Default wake frequency:** daily, early morning. **Quiet hours:** she skips any pulse that fires while a session looks active. Both are owner-adjustable and live in `PULSE.md`, which is the authority on what she *does* once woken; this file only covers how the waking is triggered.

## The invocation

```
claude -p "/agent-abigail --pulse" --permission-mode acceptEdits
```

Three parts of that are load-bearing:

- **`-p`** runs headless and exits. Without it the scheduler opens an interactive session nobody is sitting at.
- **`--pulse`** is what routes her to Pulse Mode instead of a normal waking. The bootloader passes it to `wake.py`, which appends `PULSE.md` to what she loads.
- **The working directory must be the project root**, the folder `{project-root}/_bmad/` sits in, because that is how her sanctum is located. Set it explicitly in the scheduler; a scheduled task does not inherit the shell's directory.

`--permission-mode acceptEdits` lets her write without a prompt, which she must be able to do with no one present. Her dominion is her sanctum, so that is the scope of what it permits — but it *is* unattended file writing, so it should be a deliberate choice rather than a default someone inherits.

## Setting it up

**Windows** — run once in PowerShell, adjusting the path and time:

```powershell
$action = New-ScheduledTaskAction -Execute "claude" `
  -Argument '-p "/agent-abigail --pulse" --permission-mode acceptEdits' `
  -WorkingDirectory "$env:USERPROFILE"
$trigger = New-ScheduledTaskTrigger -Daily -At 6:00am
Register-ScheduledTask -TaskName "Abigail Pulse" -Action $action -Trigger $trigger `
  -Description "Daily silent upkeep: curate memory, reconcile the ledger, leave a review set."
```

If `claude` is not on the scheduler's PATH, pass its full path to `-Execute` (`(Get-Command claude).Source` will print it).

**macOS / Linux** — `crontab -e`, then:

```
0 6 * * * cd "$HOME" && claude -p "/agent-abigail --pulse" --permission-mode acceptEdits
```

## Checking and stopping it

```powershell
Get-ScheduledTask -TaskName "Abigail Pulse"          # is it registered
Start-ScheduledTask -TaskName "Abigail Pulse"        # fire one now, to test
Unregister-ScheduledTask -TaskName "Abigail Pulse"   # stop it entirely
```

Fire one manually before trusting the schedule. A successful first pulse on an empty ledger writes nothing and says nothing — that is the silence rule working, not a failure. To see it actually do something, run it once after a session where a concept was taught.

## If the owner does not want it

Pulse is optional and declining it costs nothing structural: she works exactly as a memory agent, and `review` still computes what is due the moment they ask for it. Note the decision in `PULSE.md` so she stops offering, and skip the scheduled task. What is lost is only the preparation — they will get the same review set, just built while they wait rather than before they arrive.
