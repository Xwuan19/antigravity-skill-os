---
name: handoff
description: Write a verified HANDOFF.md so a fresh session can continue the work without the current conversation. Use when the user says handoff, "continue later", "new session", "chuyển phiên", when context is nearly exhausted, or before any long break in a multi-step task.
---

# Handoff

The goal: a session that has never seen this conversation must be able to resume
without asking a single clarifying question. Write for that reader, not for yourself.

## When to run

- The user asks for a handoff, a new session, or to continue later.
- Context is filling up and the task is not done.
- Before switching machines, branches, or agents.

Do not run it for a task that is already complete — a summary of finished work is not a
handoff.

## Write one file

Write `HANDOFF.md` at the repository root (or the path the user names). If one already
exists, update it in place — do not create `HANDOFF-2.md`.

Use exactly these sections. Delete a section only if it is genuinely empty.

```markdown
# Handoff — <one-line task name>

**Written:** <ISO date>
**Repo state:** branch <branch> · <clean/dirty> · last commit <sha> <subject>

## Goal

What we are actually trying to achieve, in the user's words, not the implementation.
If the goal changed during the session, say so and give the current one.

## Current state

What works right now, and what does not. Be specific: name files, functions, endpoints.
State plainly what you verified and what you only assumed.

## Decisions taken

Each decision as: the choice, the reason, the alternative that was rejected.
This is what stops the next session from re-litigating settled questions.

## Files touched

| File | Change | Status |
|---|---|---|
| `path` | what changed | done / partial / broken |

## Next steps

Ordered. Each step must be independently startable:

1. <action> — <why> — <how you know it is done>

## Verification

The exact commands a fresh session should run to see the current state.
Include the expected output, so "passing" is checkable rather than remembered.

```bash
<command>
```

## Open questions / blockers

Things waiting on the user, on an external service, or on a decision.
If nothing is blocked, write "none".

## Do not

Things the next session might be tempted to do that are already settled as wrong.
This section saves the most time. Include the dead ends you already explored.
```

## Rules

- **Verify before writing.** Run the commands you put in the Verification section and
  paste real output. A handoff that claims tests pass without the output is worse than
  no handoff.
- **Reference, do not paste.** Link files by path and line, do not inline whole files.
  The next session can read them; the context you save is the context it needs.
- **Absolute or repo-relative paths**, never "the file we discussed".
- **No conversation history.** Who said what is noise. What was decided is signal.
- **Under 200 lines.** If it is longer, the decisions section is absorbing detail that
  belongs in the code or the plan file.

## Hand off to a plan file instead, when

If the work is large and still being planned, write the plan with the
`planning-with-files` skill (`task_plan.md`, `findings.md`, `progress.md`) and make
`HANDOFF.md` a short pointer to it. Two long overlapping documents is worse than one.
