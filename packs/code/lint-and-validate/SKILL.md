---
name: lint-and-validate
description: "Use when checking code changes with the project’s configured linters and type checkers; report failures and unrun checks."
---

# Lint and Validate

## When to Use

Use after behavior or configuration changes when a repository has relevant lint or type checks. Read the repository's instructions and package scripts first. Run focused checks during development and the required checks before completion.

## Procedure

1. Identify the changed languages, configured commands, and installed tools. Inspect package scripts before executing them: a script named `lint` can modify files or run arbitrary project code.
2. Run the project's read-only lint/type-check commands. For Node projects, prefer declared scripts such as `npm run lint` and `npm run typecheck`. Do not use `npx` to silently fetch an absent checker.
3. For Python, use configured, already installed tools such as `ruff check .` or `mypy .`. Do not assume every `pyproject.toml` configures both. Never add `--fix` without inspecting the proposed changes and the task's authorization.
4. Fix relevant failures without deleting user work, weakening rules, or raising timeouts just to pass. If a required tool is unavailable, report the exact check that did not run.
5. Report commands, exit results, scope and remaining limitations. Passing lint does not prove the absence of runtime or security defects.

## Example

After correcting a TypeScript behavior, inspect `package.json`, run the configured focused regression test, then `npm run lint` and `npm run typecheck` if those scripts exist. If TypeScript is declared but not installed, report the missing local checker; do not substitute a downloaded package or call the result a pass.

## Limitations

Project commands may mutate files or access the network; inspect them before running. These instructions do not replace the project’s CI contract. Do not label unrun checks as successful.
