# Phase 2: extract-with-diff.sh Review

**Date:** 2026-02-01
**Reviewer:** Phase 2 Verification
**Script:** /Users/r/repos/code-foundations/agents/extract-with-diff.sh

---

## Correctness Verification (aposd-verifying-correctness)

### Requirements: PASS

| Requirement | Implementation | Location |
|-------------|----------------|----------|
| Main flow: parse args -> get files -> get hunks -> match -> output | Implemented in `main()` | Lines 260-417 |
| `parse_diff_hunks` function | Implemented | Lines 190-257 |
| `get_change_status` function | Implemented | Lines 50-72 |
| `overlaps` function | Implemented | Lines 75-86 |
| `generate_summary` function | Implemented | Lines 89-119 |
| `infer_layer` function | Implemented | Lines 122-175 |
| JSONL output with diff, changeStatus, summary | Implemented via jq | Lines 404-409 |
| Deleted file handling (extract from HEAD) | Implemented | Lines 303-315 |
| Error handling for git failures | Implemented | Lines 37-46, 277-285 |
| Script is executable | Verified | `chmod +x` confirmed |

### Concurrency: N/A

No shared mutable state. Sequential processing.

### Errors: PASS

| Failure Point | Handling | Location |
|---------------|----------|----------|
| git diff --name-status fails | Exit with error to stderr | Lines 37-46 |
| git diff (hunks) fails | Exit with error to stderr | Lines 277-285 |
| Deleted file not in HEAD | Warning to stderr, continue | Lines 306-309 |
| File not found | Warning to stderr, continue | Lines 312-315 |
| extract-units.sh fails | Warning to stderr, continue | Lines 319-323 |
| JSON parsing fails | Warning to stderr, continue | Lines 331-334 |

Partial results on non-critical failures (per pseudocode spec).

### Resources: PASS

| Resource | Acquisition | Release |
|----------|-------------|---------|
| Temp file for deleted files | `mktemp` (line 305) | `rm -f` (lines 308, 321, 326) |

Temp file cleanup happens on:
- HEAD extraction failure (line 308)
- extract-units.sh completion (line 326)
- extract-units.sh failure (line 321)

### Boundaries: PASS

| Edge Case | Handling |
|-----------|----------|
| No arguments (unstaged changes) | Default empty args (lines 264-268) |
| Empty file list | Loop simply doesn't iterate |
| No hunks for file | Skip file (lines 340-343) |
| No overlapping hunks for unit | Skip unit (lines 376-378) |
| Empty filepath | Skip (line 294) |
| Empty unit_json | Skip (line 347) |

### Security: N/A

No untrusted input. Script operates on git repository controlled by user.

---

## Pseudocode Alignment

### Main Flow

| Pseudocode Step | Implementation | Status |
|-----------------|----------------|--------|
| Parse command line arguments | Lines 263-268 | MATCH |
| Get list of changed files with status | `get_file_statuses()` call at line 272 | MATCH |
| Get all diff hunks | `git diff` at lines 276-286 | MATCH |
| Parse diff into lookup table | `parse_diff_hunks()` at line 290 | MATCH |
| For each changed file | Loop at line 293 | MATCH |
| Handle deleted files (extract from HEAD) | Lines 303-311 | MATCH |
| Extract units via extract-units.sh | Line 319 | MATCH |
| For each unit, find overlapping hunks | Loop at line 346, overlaps check at line 366 | MATCH |
| Generate summary | Line 389 | MATCH |
| Infer layer | Line 394 | MATCH |
| Build complete JSON with diff, summary, changeStatus, layer | Lines 404-409 | MATCH |
| Output JSONL line | Line 412 | MATCH |

### Function: parse_diff_hunks

| Pseudocode | Implementation | Status |
|------------|----------------|--------|
| Initialize state variables | Lines 193-197 | MATCH |
| Handle "diff --git" lines | Lines 201-216 | MATCH |
| Handle "@@" hunk headers | Lines 219-240 | MATCH |
| Parse newstart and newcount | Lines 226-232 | MATCH |
| Handle omitted count (=1) | Lines 230-232 | MATCH |
| Skip header lines (---, +++) | Line 243 | MATCH |
| Append content lines | Lines 247-248 | MATCH |
| Finalize last hunk | Lines 254-256 | MATCH |

### Function: get_change_status

| Pseudocode | Implementation | Status |
|------------|----------------|--------|
| A -> added | Line 54-55 | MATCH |
| M -> modified | Lines 57-58 | MATCH |
| D -> deleted | Lines 60-61 | MATCH |
| R -> modified | Lines 63-65 | MATCH |
| R* (with percentage) -> modified | Lines 63-65 (R* pattern) | MATCH |
| Default -> modified | Lines 67-69 | MATCH |

### Function: overlaps

| Pseudocode | Implementation | Status |
|------------|----------------|--------|
| unit_start <= hunk_end AND unit_end >= hunk_start | Line 81 | MATCH |

### Function: generate_summary

| Pseudocode | Implementation | Status |
|------------|----------------|--------|
| Count + lines (not ++) | Lines 94-99 | MATCH |
| Count - lines (not --) | Lines 102-107 | MATCH |
| removed=0 && added>0 -> "Add" | Lines 110-111 | MATCH |
| added > removed*2 -> "Extend" | Lines 112-113 | MATCH |
| removed > added*2 -> "Simplify" | Lines 114-115 | MATCH |
| Else -> "Update" | Lines 116-117 | MATCH |

### Function: infer_layer

| Pseudocode Pattern | Implementation | Status |
|--------------------|----------------|--------|
| api, routes, handlers, controllers | Lines 127-131 | MATCH |
| services, usecases | Lines 134-137 | MATCH |
| domain, models, entities | Lines 140-144 | MATCH |
| data, repositories, dal | Lines 147-151 | MATCH |
| infra, infrastructure, providers | Lines 154-158 | MATCH |
| .test., .spec., tests, __tests__ | Lines 161-165 | MATCH |
| config, .config. | Lines 168-171 | MATCH |
| Default -> unknown | Line 174 | MATCH |

---

## JSONL Output Format

| Required Field | Source | Status |
|----------------|--------|--------|
| file | From extract-units.sh (or updated for deleted files) | PRESENT |
| name | From extract-units.sh | PRESENT |
| type | From extract-units.sh | PRESENT |
| lines | From extract-units.sh | PRESENT |
| diff | Built from matching hunks | PRESENT |
| summary | Generated via generate_summary() | PRESENT |
| changeStatus | From get_change_status() | PRESENT |
| layer | From infer_layer() | PRESENT |
| All other fields | Preserved from extract-units.sh | PRESENT |

---

## Quality Practices (cc-quality-practices)

### Code Organization

- Clear function separation with single responsibilities
- Consistent naming conventions
- Proper use of `set -euo pipefail` for fail-fast behavior

### Error Messages

- Specific, actionable error messages to stderr
- Includes context (file path, git args) in error messages

### Edge Case Handling

- Empty inputs handled throughout
- Deleted files properly extracted from HEAD
- Missing files reported with warnings
- Partial failures allow continued processing

---

## Issues Found

None. Implementation matches pseudocode exactly.

---

## Summary

| Dimension | Result |
|-----------|--------|
| Requirements Coverage | PASS |
| Error Handling | PASS |
| Resource Management | PASS |
| Boundary Conditions | PASS |
| Pseudocode Alignment | PASS |
| Script Executable | PASS |

---

## Verdict: PASS

The implementation of `extract-with-diff.sh` correctly implements all requirements from the Phase 2 pseudocode:

1. Main flow matches pseudocode exactly
2. All 5 required functions implemented (`parse_diff_hunks`, `get_change_status`, `overlaps`, `generate_summary`, `infer_layer`)
3. JSONL output includes `diff`, `changeStatus`, `summary`, and `layer` fields
4. Deleted file handling extracts from HEAD with proper temp file cleanup
5. Error handling covers git failures and malformed input with appropriate warnings
6. Script is executable with proper shebang
