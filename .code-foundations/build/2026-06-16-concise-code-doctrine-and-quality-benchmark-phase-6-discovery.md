# Discovery + Design: Phase 6 - Conditional integration into build-agent.md

## Files Found
- `agents/build-agent.md` — production agent, target for landing
- `benchmarks/concise-doctrine/arms/build-agent.concise.md` — validated concise variant (source of truth)
- `benchmarks/concise-doctrine/arms/build-agent.baseline.md` — byte-check reference
- `benchmarks/concise-doctrine/results/full-run/REPORT.md` — GO verdict confirmed

## Current State

VERDICT: GO confirmed. Last line of REPORT.md:

> VERDICT: GO — quality improved (reduced LOC/complexity: sonnet/loc: -8.0000, sonnet/fn_len_max: -6.0000, opus/loc: -10.0000 and 3 more) with no correctness or mutation regression and equal-or-better readability.

`diff agents/build-agent.md benchmarks/concise-doctrine/arms/build-agent.baseline.md` → empty (files are identical). The production agent has NOT diverged from the validated baseline, so the cleanest landing is a direct copy of the concise arm.

## Gaps

None. Precondition is met, files are where the plan expects them, and the clean-copy path is available.

## Code Standards

No `docs/code-standards.md` found in the worktree. Not applicable — this phase edits a Markdown agent definition, not source code.

## Test Infrastructure

No pytest suite for this phase's verification. Verification is command-based:
- `grep -c "### Concise Implementation" agents/build-agent.md` == 1
- `diff agents/build-agent.md benchmarks/concise-doctrine/arms/build-agent.concise.md` empty (byte-alignment)
- grep checks that existing Baseline Discipline subsections are still present verbatim
- `cd benchmarks/concise-doctrine && .venv/bin/python -m pytest -q` to confirm benchmark suite unaffected

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-6.1 | `agents/build-agent.md` contains the validated subsection + Phase-1 check, and a diff against the prior state shows ONLY those additions (no other deltas). | COVERED | `grep -c "### Concise Implementation" agents/build-agent.md` == 1; `diff agents/build-agent.md benchmarks/concise-doctrine/arms/build-agent.concise.md` empty; git diff shows only additions |
| DW-6.3 | The landed wording is byte-aligned with the `concise` arm's additions (`diff agents/build-agent.md benchmarks/concise-doctrine/arms/build-agent.concise.md` is empty). | COVERED | `diff agents/build-agent.md benchmarks/concise-doctrine/arms/build-agent.concise.md` must produce no output |

**All items COVERED:** YES

## Design Decisions

The cleanest approach: `cp benchmarks/concise-doctrine/arms/build-agent.concise.md agents/build-agent.md`. This is valid because the production agent is byte-identical to the validated baseline right now. Copying the concise arm lands exactly the two validated additions and nothing else:
1. The `### Concise Implementation` subsection (lines 58–61 of the concise arm) under `Baseline Discipline (always on)`.
2. The one-line Phase-1 design check (line 100 of the concise arm) appended to the `### Design Decisions` section.

No built-in/existing solution applies here — this is a file copy, not a code problem. The copy is the most reliable way to achieve byte-alignment with the validated source; manual editing could introduce whitespace drift.

## Prerequisites
- [x] `agents/build-agent.md` exists and is byte-identical to baseline
- [x] `benchmarks/concise-doctrine/arms/build-agent.concise.md` exists (validated source)
- [x] VERDICT: GO confirmed in REPORT.md
- [x] Python benchmark suite exists at `benchmarks/concise-doctrine/`

## Recommendation
BUILD — copy validated concise arm over production agent; run all four verification commands.
