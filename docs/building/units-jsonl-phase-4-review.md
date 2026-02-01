# Phase 4: Wire into /code-foundations:review - Review

**Date:** 2026-02-01
**Branch:** feat/agent-scripts-batch-mode
**Reviewer:** Claude (aposd-verifying-correctness, cc-quality-practices)
**Status:** PASS

---

## Requirements Verification

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 1 | SANITY STEP 1 calls extract-with-diff.sh | PASS | Lines 334-385: "SANITY STEP 1: EXTRACTION (Single Script Call)" with SCRIPT_PATH="{PLUGIN_ROOT}/agents/extract-with-diff.sh" |
| 2 | STEP 5 (PR flow) calls extract-with-diff.sh | PASS | Lines 704-745: "STEP 5: PHASE 1 - EXTRACTION (Single Script Call)" with same script call pattern |
| 3 | Script path uses PLUGIN_ROOT correctly | PASS | Lines 350, 720: `SCRIPT_PATH="{PLUGIN_ROOT}/agents/extract-with-diff.sh"` |
| 4 | Output goes to BASE_DIR/units.jsonl | PASS | Lines 351, 721: `OUTPUT_FILE="{BASE_DIR}/units.jsonl"` |
| 5 | Error handling for non-zero exit codes | PASS | Lines 358-363, 728-732: Exit code check with actionable error messages |
| 6 | All other sections remain unchanged | PASS | STEP 0-4, SANITY STEP 2-6, STEP 6-10 all preserved |
| 7 | Phase task status updates preserved | PASS | Lines 340-343, 382-384 (SANITY); Lines 710-713, 740-742 (PR) |

---

## Correctness Verification (aposd-verifying-correctness)

### Requirements: PASS
- All 7 requirements mapped to specific code locations
- No requirement without implementation
- No implementation without requirement

### Concurrency: N/A
- Command template (markdown), not runtime code with shared state

### Errors: PASS
- Non-zero exit code handling in both flows
- Empty/missing output file handling
- Actionable error messages with installation hints

### Resources: N/A
- No persistent resources acquired

### Boundaries: PASS
- Empty output file handled (lines 366-377)
- Zero files case handled (lines 368-370)
- Files exist but no units extracted handled (lines 371-373)

### Security: N/A
- Parameterized paths, no unsafe input concatenation

---

## Quality Verification (cc-quality-practices)

### Pseudocode-to-Implementation Match

**SANITY STEP 1:**
```
Pseudocode (lines 51-80):     Implementation (lines 334-385):
- Mark in_progress            - Mark in_progress
- Execute script              - Execute script
- Check exit code             - Check exit code
- Handle empty file           - Handle empty file
- Mark complete               - Mark complete
```
MATCH: Exact correspondence.

**STEP 5 (PR flow):**
```
Pseudocode (lines 160-219):   Implementation (lines 704-745):
- Mark in_progress            - Mark in_progress
- Execute script              - Execute script
- Check exit code             - Check exit code
- Count units                 - Count units
- Mark complete               - Mark complete
```
MATCH: Exact correspondence.

### DIFF_ARGS Handling
- Pseudocode specifies: `--staged`, `""`, `HEAD`, `$MERGE_BASE HEAD`
- Implementation passes `{DIFF_ARGS}` directly to script
- CORRECT: Script receives args as designed

### Script Execution Context
- Both flows use: `cd "{REPO_ROOT}" && "{SCRIPT_PATH}" {DIFF_ARGS}`
- CORRECT: Script runs from repository root as specified

### Output Consumption
- SANITY STEP 2 orchestrator receives `BASE_DIR` (line 408)
- orchestrate-checking-agent.md expects `units.jsonl` at `BASE_DIR/units.jsonl`
- CORRECT: Downstream phases aligned

---

## Observations (Not Blockers)

### Documentation Drift
The following sections still reference the old multi-agent extraction approach:

1. **PARALLELIZATION SUMMARY (line 1353)**
   - Shows: "Extraction | 1 per 5 files | haiku | ceil(files / 5)"
   - Actual: Single script call

2. **Architecture diagrams (lines 25-34, 43-51)**
   - Show: "1 per 5 files" / "Batch by files (5)"
   - Actual: Single script call

These were NOT in Phase 4 scope (per pseudocode line 16: "All other phases remain unchanged"), but should be updated in a follow-up.

### Stderr Handling Design
Both pseudocode and implementation use `2>&1` which redirects stderr to the output file. If the script fails, error messages go to `units.jsonl`. The exit code check prevents downstream consumption, but error display says "Script output shown above" while output actually went to file.

This is a design decision from pseudocode, not a Phase 4 implementation error.

---

## Verdict

**PASS**

All 7 requirements are satisfied. Implementation matches pseudocode exactly. Correctness dimensions verified. No blocking issues found.

---

## Checklist Sign-off

- [x] SANITY STEP 1 calls extract-with-diff.sh
- [x] STEP 5 (PR flow) calls extract-with-diff.sh
- [x] Script path uses PLUGIN_ROOT correctly
- [x] Output goes to BASE_DIR/units.jsonl
- [x] Error handling for non-zero exit codes
- [x] All other sections remain unchanged
- [x] Phase task status updates preserved
