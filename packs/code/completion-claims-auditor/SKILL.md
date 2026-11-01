---
name: completion-claims-auditor
description: "Map completion claims to actual tests, runtime and remote evidence; distinguish passed, blocked and unverified."
---

# Purpose

Make completion an evidence state rather than a language-model judgment.

# When to activate

An agent is about to report a multi-step coding task, feature, fix, release, push, or deployment as complete.

# When not to activate

A purely advisory response has no implementation or execution claim.

# Preconditions

- Read applicable repository instructions before edits.
- Preserve unrelated working-tree changes and establish a baseline when the workflow can modify code.
- Identify which tools and environments are actually available; do not claim unavailable checks ran.

# Required inputs

- Original user requirements
- Current diff/repository state
- Test/tool outputs
- Remote state when relevant

# Workflow

1. Extract every externally meaningful completion claim from the requirements and current work.
2. For each claim, name the strongest evidence type that would establish it: file state, compilation, test, browser flow, API response, artifact smoke, Git remote hash, CI result, or external state.
3. Collect/execute that evidence and record the observed result; do not substitute intent or code inspection when runtime evidence is feasible.
4. Distinguish implemented, structurally validated, functionally verified, externally verified, and not executed.
5. Reopen any claim contradicted by evidence and fix or downgrade it before reporting.
6. Check that no failing/skipped required gate was hidden or weakened.
7. Write the final status using only evidence actually observed in this session/repository.

# Relevant tools

Repository state, test/build tools, browser/API checks, Git/GitHub/CI state.

# Safety restrictions

Never manufacture screenshots, command results, CI status, remote publication, or test outcomes.

# Validation

- Every completion statement points to evidence or is explicitly qualified.
- Local commit is not called pushed without remote verification.
- Code existence is not called working when required runtime checks were not executed.

# Expected output

- Claim-to-evidence ledger
- Failed/missing evidence
- Final allowed wording
- Exact blockers

# Failure handling

If a required evidence source is inaccessible, report the implementation plus the missing verification and the concrete next check; do not invent a percentage.

# Completion criteria

The skill is complete only when every applicable validation item above has observed evidence or is explicitly marked not executed with the concrete blocker. Do not replace missing evidence with confidence language.
