---
name: build-doctrine
description: "Implements a coding task from a written spec with Done-When acceptance items. Use when given a spec to implement: stub the interface, implement it, then write tests that validate the Done-When items and any important behavior beyond them."
---

# Build Doctrine

Implement the task described in the provided spec so it satisfies the spec's Done-When (DW) items. Write all code and tests to the exact output paths the spec names.

## Process

1. **Stub the interface** — lay down the function/class signatures and data shapes the spec calls for, with empty bodies.
2. **Implement** — fill in the bodies until every DW item's behavior is complete.
3. **Validate** — write tests *after* the implementation:
   - Cover every DW item. Name those tests for their DW-ID (e.g. `test_DW_1_1_parses_hours`).
   - Then go past the DW list: add tests for the edge cases, error paths, and boundaries the implementation surfaced — anything you judge matters, even when no DW item names it.
   - Assert on intended behavior (input → expected output), not on whatever the code happens to return.
   - Run the suite. Every test must pass.
