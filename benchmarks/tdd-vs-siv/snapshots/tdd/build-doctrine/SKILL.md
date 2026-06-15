---
name: build-doctrine
description: "Implements a coding task from a written spec with Done-When acceptance items. Use when given a spec to implement: for each Done-When item, write a failing test first, then the minimum code to make it pass (red-green)."
---

# Build Doctrine

Implement the task described in the provided spec so it satisfies the spec's Done-When (DW) items. Write all code and tests to the exact output paths the spec names.

## Process

Test-driven, one DW item at a time. For each DW item:

1. **Red** — write a failing test that verifies the DW item. Name it for its DW-ID (e.g. `test_DW_1_1_parses_hours`). Run it; confirm it fails for the right reason.
2. **Green** — write the minimum code to make the test pass. Do not add behavior ahead of a test.
3. **Refactor** — clean up while the tests stay green.

Your tests come from the DW items: each DW item gets test(s), and that is the test suite.
