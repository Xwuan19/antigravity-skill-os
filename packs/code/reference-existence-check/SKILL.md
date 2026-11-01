---
name: reference-existence-check
description: "Verify proposed functions, paths, configuration and services against actual sources before relying on them."
---

**Skill OS:** Verify existing inputs and APIs, but do not require a planned new output file to exist before creation. Respect permissions and avoid unsafe probes.


# Reference Existence Check

Language models draft plausible-looking references that do not exist: helper functions, config keys, file paths, ports, service names. A draft that reads well can still fail on the first call, or worse, do something unintended.

## Core rule

Before executing or approving a draft, extract every concrete reference it makes and verify each one against the real source of truth.

## What to extract

- function and method names it calls
- files, directories and paths it reads or writes
- config keys, environment variables, ports, hostnames
- service, container and package names
- facts about how the system behaves ("this service restarts its dependents")

## Steps

1. List the references in the draft.
2. For each one, look it up directly: grep the codebase for the function, list the directory, read the config, inspect the running service.
3. Mark each as confirmed (with where you found it) or not found.
4. For anything not found, check search scope and errors, inspect plausible parent locations, and report uncertainty before claiming absence.
5. Replace unconfirmed references with real ones, or stop and report the gap.
6. Only then execute.

## Verify before returning

Return a short table: reference, where it was confirmed, status. Do not call a draft "checked" if any row is unconfirmed.

## Notes

- A drafted facts-about-the-system claim is a reference too. Check it against the documentation or the live system.
- If the same draft pattern fabricates repeatedly, put the check in code (a gate that greps the references) rather than relying on a prompt rule.
