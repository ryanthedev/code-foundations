# Phase 1: Tier 1 Fields Validation

**Date:** 2026-02-01
**Status:** DONE
**Implementation:** `/Users/r/repos/code-foundations/agents/extract-units.sh`

## Implementation Summary

Added 6 Tier 1 fields to extract-units.sh output:
1. **is_test** - Boolean, filename/path pattern detection
2. **layer** - String (api|service|domain|data|infra|test|config|unknown)
3. **param_count** - Integer, parameter count from signature
4. **line_count** - Integer, function body line count (end - start + 1)
5. **has_throw** - Boolean, throw statement presence
6. **has_recursion** - Boolean, self-call detection

## Code Changes

### 1. Helper Functions (lines 101-205)

Added two helper functions after `json_escape()`:
- `is_test_file(filepath)` - Detects test files by patterns
- `infer_layer(filepath)` - Infers architectural layer from path

### 2. File-Level Calculations (lines 422-425)

Before definition loop, calculate:
- `is_test` - Call `is_test_file()`
- `layer` - Call `infer_layer()`

### 3. Definition-Level Calculations (lines 430-436)

Inside definition loop, calculate:
- `param_count` - Count commas in params string + 1
- `line_count` - `end - start + 1`

### 4. Recursion Detection (lines 459-463)

Inside calls collection loop:
- Check if `cname == name` for direct recursion

### 5. has_throw Calculation (line 497)

After existing boolean calculations:
- `has_throw` - Check if `throw_count > 0`

### 6. JSON Output Update (lines 524-526)

Extended printf to include all 6 new fields at the end.

### 7. Bug Fix: Single-Line Functions (line 240)

Updated regex to handle numbered capture format:
```bash
# Before: capture:\ ([^,]+),\
# After:  capture:\ ([0-9]+\ -\ )?([^,]+),\
```

Single-line functions include text in tree-sitter output and use numbered captures, which the original regex didn't match.

## Validation Test Cases

### Test 1: Parameter Counting
```bash
echo 'export function noParams() {}' > test.ts
echo 'export function oneParam(x: string) {}' >> test.ts
echo 'export function threeParams(a: string, b: number, c: boolean) {}' >> test.ts

./agents/extract-units.sh --files test.ts | jq '.units[] | {name, param_count}'
```

**Expected:**
- noParams: 0
- oneParam: 1
- threeParams: 3

### Test 2: is_test Detection
```bash
# Test file patterns
__tests__/sample.ts -> is_test=true, layer="test"
utils.test.js -> is_test=true, layer="test"
test_helper.py -> is_test=true, layer="test"
UserTest.java -> is_test=true, layer="test"
src/api/user.ts -> is_test=false, layer="api"
```

### Test 3: Layer Inference
```bash
src/api/routes/users.ts -> layer="api"
src/services/auth.ts -> layer="service"
src/domain/User.ts -> layer="domain"
src/data/UserRepo.ts -> layer="data"
src/infra/db.ts -> layer="infra"
src/config/app.ts -> layer="config"
src/utils/helpers.ts -> layer="unknown"
```

### Test 4: has_throw Detection
```bash
echo 'export function throwsError() { throw new Error("test"); }' > test.ts
./agents/extract-units.sh --files test.ts | jq '.units[0].has_throw'
# Expected: true
```

### Test 5: has_recursion Detection
```bash
echo 'export function factorial(n: number): number {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}' > test.ts
./agents/extract-units.sh --files test.ts | jq '.units[0].has_recursion'
# Expected: true
```

### Test 6: line_count Accuracy
```bash
# Single-line function: lines=1
echo 'export const oneLiner = () => 42;' > test.ts

# Multi-line function: lines=11
echo 'export function multiLine() {
  let x = 1;
  let y = 2;
  let z = 3;

  x++;
  y++;
  z++;

  return x + y + z;
}' >> test.ts

./agents/extract-units.sh --files test.ts | jq '.units[] | {name, line_count}'
```

**Expected:**
- oneLiner: 1
- multiLine: 11

## Edge Cases Handled

1. **Empty parameter lists** - `()` returns param_count=0 (not 1)
2. **Single-line functions** - Fixed regex to handle numbered captures with text
3. **__tests__ directory** - Pattern changed from `/__tests__/` to `__tests__` to match root-level dirs
4. **Generic types in params** - Known limitation: `Map<K, V>` counts as 2 params (Tier 2 fix)
5. **Trailing commas** - Acceptable for Tier 1 (rare in practice)

## Deviations from Pseudocode

### 1. param_count Calculation (lines 430-434)

**Pseudocode:**
```
Trim whitespace from params_string
If params_string is empty
    Return 0
```

**Implementation:**
```bash
local params_trimmed="${params//[()[:space:]]/}"
if [[ -n "$params_trimmed" ]]; then
  param_count=$(($(printf '%s' "$params" | tr -cd ',' | wc -c) + 1))
fi
```

**Deviation:** Remove both whitespace AND parentheses for empty check. This handles the `()` case where params is not empty but contains only parentheses.

### 2. is_test_file Pattern (line 127)

**Pseudocode:**
```
If filepath contains "/__tests__/"
```

**Implementation:**
```bash
if [[ "$filepath" == *"__tests__"* ]]; then
```

**Deviation:** Removed leading slash requirement to match root-level `__tests__/` directories.

## Known Limitations (Tier 1 Acceptable)

1. **Generic types miscounted** - `Map<string, number>` counts as 2 params instead of 1
2. **Mutual recursion undetected** - Only direct recursion (A calls A) is detected
3. **Layer inference** - Path-based heuristic, not project-aware

These are acceptable for Tier 1 and will be addressed in Tier 2 with tree-sitter AST parameter node counting.

## Output Schema

Final JSON schema with all 16 fields:

```json
{
  "type": "function|method|class|interface|type",
  "name": "identifier",
  "file": "path",
  "lines": [start, end],
  "visibility": "exported|public|private|internal",
  "modifiers": ["async", "static", "arrow", "decorated"],
  "params": "parameter signature string",
  "return_type": "type annotation",
  "calls": ["name1", "name2"],
  "has_loops": boolean,
  "has_try_catch": boolean,
  "has_async": boolean,
  "loop_count": integer,
  "call_count": integer,
  "is_test": boolean,
  "layer": "api|service|domain|data|infra|test|config|unknown",
  "param_count": integer,
  "line_count": integer,
  "has_throw": boolean,
  "has_recursion": boolean
}
```

## Tests Pass

All validation tests pass:
- Parameter counting: 0, 1, 3 params ✓
- is_test detection: test files and non-test files ✓
- Layer inference: all 8 layers ✓
- has_throw: true/false ✓
- has_recursion: true/false ✓
- line_count: single-line and multi-line ✓

## Status: DONE

All 6 Tier 1 fields implemented and validated. Ready for Phase 2.
