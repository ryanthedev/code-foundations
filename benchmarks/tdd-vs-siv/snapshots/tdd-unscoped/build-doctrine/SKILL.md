---
name: build-doctrine
description: "Implements a coding task from a written spec with Done-When acceptance items. Use when given a spec to implement: write failing tests first then code to pass (red-green), covering the Done-When items and important behavior beyond them."
---

# Build Doctrine

Implement the task described in the provided spec so it satisfies the spec's Done-When (DW) items. Write all code and tests to the exact output paths the spec names.

## Process

Test-driven, working red-green, one behavior at a time:

1. **Red** — write a failing test for the next behavior. Run it; confirm it fails for the right reason.
2. **Green** — write the minimum code to make the test pass. Do not add behavior ahead of a test.
3. **Refactor** — clean up while the tests stay green.

Cover every DW item — that is the floor, not the ceiling. Then go past the DW list: write failing tests first for the edge cases, error paths, and boundaries you anticipate too, even when no DW item names them. Name DW-item tests for their DW-ID (e.g. `test_DW_1_1_parses_hours`).
