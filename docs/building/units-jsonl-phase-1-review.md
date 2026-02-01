# Phase 1 Review: units.jsonl Extraction

**Date:** 2026-02-01
**Reviewer:** Claude Code (aposd-verifying-correctness + cc-quality-practices)
**File:** `/Users/r/repos/code-foundations/agents/extract-units.sh`

---

## Verdict: PASS

The implementation faithfully follows the pseudocode specification, handles all documented edge cases, and introduces no regressions to existing functionality.

---

## Requirements Coverage (6/6 fields)

| Field | Location | Status |
|-------|----------|--------|
| `is_test` | `is_test_file()` lines 100-132, used lines 419-420 | IMPLEMENTED |
| `layer` | `infer_layer()` lines 134-193, used lines 421-422 | IMPLEMENTED |
| `param_count` | lines 431-436 | IMPLEMENTED |
| `line_count` | line 438 | IMPLEMENTED |
| `has_throw` | lines 441, 453, 506, 510 | IMPLEMENTED |
| `has_recursion` | lines 463, 469-472 | IMPLEMENTED |

---

## Helper Function Verification

### is_test_file() - MATCHES PSEUDOCODE

**Basename patterns implemented:**
- `.test.` and `.spec.` (line 106)
- `test_` prefix and `_test.` suffix (line 110)
- `Test.` and `Spec.` PascalCase (line 114)

**Path patterns implemented:**
- `__tests__` directory (line 119)
- `/tests/` and `/test/` directories (line 123)
- `/spec/` and `/specs/` directories (line 127)

**Edge case handling:**
- `test.ts` (bare "test" as name) - correctly NOT matched (requires pattern like `.test.` or `test_`)
- `utils.test.ts` - correctly matched via `.test.` pattern
- `src/__tests__/helper.ts` - correctly matched via `__tests__` pattern
- `testing-utils.ts` - correctly NOT matched (avoids substring false positives)

### infer_layer() - MATCHES PSEUDOCODE

**Priority order verified (first match wins):**
1. API: `/api/`, `/routes/`, `/handlers/`, `/controllers/` (lines 140-144)
2. Service: `/services/`, `/usecases/`, `/use-cases/` (lines 147-151)
3. Domain: `/domain/`, `/models/`, `/entities/` (lines 154-158)
4. Data: `/data/`, `/repositories/`, `/dal/`, `/persistence/` (lines 161-165)
5. Infra: `/infra/`, `/infrastructure/`, `/providers/` (lines 168-172)
6. Test: calls `is_test_file()` (lines 175-178)
7. Config: `/config/`, `/configs/`, `.config.` in basename (lines 181-189)
8. Default: `"unknown"` (line 192)

---

## Field Calculation Verification

### param_count (lines 431-436)

```bash
local params_trimmed="${params//[()[:space:]]/}"
if [[ -n "$params_trimmed" ]]; then
  param_count=$(($(printf '%s' "$params" | tr -cd ',' | wc -c) + 1))
fi
```

**Pseudocode match:** EXACT
- Empty params `""` returns 0 (params_trimmed would be empty)
- Single param `"x"` returns 1 (0 commas + 1)
- Multiple params `"a, b, c"` returns 3 (2 commas + 1)

### line_count (line 438)

```bash
local line_count=$((end - start + 1))
```

**Pseudocode match:** EXACT
- One-liner (start=5, end=5) returns 1

### has_throw (lines 506, 510)

```bash
local has_loops=false has_try_catch=false has_async=false has_throw=false
...
(( throw_count > 0 )) && has_throw=true
```

**Pseudocode match:** EXACT
- throw_count already tracked during pattern matching (line 453)
- Boolean conversion follows spec

### has_recursion (lines 463, 469-472)

```bash
local has_recursion=false
...
if [[ "$cname" == "$name" ]]; then
  has_recursion=true
fi
```

**Pseudocode match:** EXACT
- Direct recursion detected via exact name match
- Mutual recursion not detected (documented Tier 1 limitation)

---

## JSON Output Verification

**Line 536-537:**
```bash
printf ',"is_test":%s,"layer":"%s","param_count":%d,"line_count":%d,"has_throw":%s,"has_recursion":%s}' \
  "$is_test" "$layer" "$param_count" "$line_count" "$has_throw" "$has_recursion"
```

- All 6 new fields present
- Appended to existing fields (no schema break)
- Field types correct: booleans as `true`/`false`, integers as numbers, layer as quoted string

---

## Regression Check

**Existing fields preserved (no changes to output format):**
- `type`, `name`, `file`, `lines` (line 525-526)
- `visibility` (line 529)
- `modifiers` (line 530)
- `params` (line 531)
- `return_type` (line 532)
- `calls` (line 533)
- `has_loops`, `has_try_catch`, `has_async` (line 534)
- `loop_count`, `call_count` (line 535)

**Result:** NO REGRESSIONS

---

## Correctness Verification (aposd-verifying-correctness)

| Dimension | Status | Notes |
|-----------|--------|-------|
| Requirements | PASS | All 6 fields mapped to code |
| Concurrency | N/A | Sequential bash script, no shared state |
| Errors | PASS | tree-sitter failures handled, empty arrays guarded |
| Resources | PASS | No file handles, bounded arrays |
| Boundaries | PASS | Empty params, zero-length functions, empty arrays all handled |
| Security | N/A | Trusted input from git diff |

---

## Known Limitations (Tier 1 Acceptable)

1. **param_count with generics:** `Map<K, V>` counted as 2 parameters instead of 1. Documented in pseudocode; planned fix in Tier 2 using tree-sitter parameter node counting.

2. **Direct recursion only:** `has_recursion` detects self-calls but not mutual recursion (A calls B, B calls A). Documented in pseudocode.

---

## Additional Enhancements Noted

The diff includes a regex fix for handling numbered capture format:
```bash
# Before: capture: definition.function...
# After:  capture: 4 - definition.function...
```

This is a correctness improvement to tree-sitter output parsing, not part of Phase 1 spec but beneficial.

---

## Summary

| Criterion | Result |
|-----------|--------|
| All 6 fields implemented | PASS |
| Helper functions match pseudocode | PASS |
| JSON output includes all new fields | PASS |
| No regressions to existing fields | PASS |
| Edge cases handled | PASS |

**Final Verdict: PASS**
