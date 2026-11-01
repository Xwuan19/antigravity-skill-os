---
name: integration-reality-checker
description: "Check whether external integrations are truly verified or only covered by mocks, and report untested boundaries."
---

**Skill OS:** A local fake or captured fixture is not proof that a real external service works. Report the evidence level and any untested live boundary.


# Purpose

Separate unit-level confidence from evidence that system boundaries actually interoperate.

# When to activate

A feature crosses a process/service/database/provider boundary and tests mock that boundary.

# When not to activate

A pure function/module has no external contract.

# Preconditions

- Read applicable repository instructions before edits.
- Preserve unrelated working-tree changes and establish a baseline when the workflow can modify code.
- Identify which tools and environments are actually available; do not claim unavailable checks ran.

# Required inputs

- Integration boundaries
- Current mocks/fakes
- Available local/sandbox services
- Credentials policy

# Workflow

1. List each external boundary and the assumptions encoded by the application: protocol, schema, auth, errors, retries, timeouts, transactions.
2. Mark which assumptions are covered only by mocks or hand-written fakes.
3. Choose the lowest-cost realistic check: contract test, local fake server with captured schema, ephemeral container/database, or provider sandbox.
4. Keep unit tests fast, adding realistic checks only for assumptions that mocks cannot establish.
5. Exercise at least success, invalid input/auth where relevant, and one realistic failure/timeout path.
6. Compare real responses/schema to mock fixtures and update mocks only after the contract is confirmed.
7. Record integrations that remain credential- or network-blocked.

# Relevant tools

Containers, local services, contract tests, provider sandbox/docs.

# Safety restrictions

Never use production credentials or mutate production data for a verification run without explicit authorization.

# Validation

- At least one realistic boundary check covers each high-impact integration where the environment permits.
- Mocks match observed/authoritative contract data.
- Unexecuted integrations are clearly labeled.

# Expected output

- Integration evidence matrix
- Mock/real discrepancies
- Executed contract tests
- Blocked integrations

# Failure handling

If real credentials/services are unavailable, stop at local contract fixtures and mark external verification pending.

# Completion criteria

The skill is complete only when every applicable validation item above has observed evidence or is explicitly marked not executed with the concrete blocker. Do not replace missing evidence with confidence language.
