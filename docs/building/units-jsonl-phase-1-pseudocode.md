# Phase 1: units.jsonl Extraction - Pseudocode

**Date:** 2026-02-01
**Branch:** feat/agent-scripts-batch-mode
**Target:** `/Users/r/repos/code-foundations/agents/extract-units.sh`

---

## Overview

Add 6 Tier 1 fields to extract-units.sh output:
- `is_test` (boolean) - filename/path pattern detection
- `layer` (string) - architectural layer inference
- `param_count` (integer) - parameter count
- `line_count` (integer) - function body line count
- `has_throw` (boolean) - throw statement presence
- `has_recursion` (boolean) - self-call detection

---

## 1. Helper Function: is_test_file(filepath)

**Purpose:** Determine if a file is a test file based on naming conventions.

**Input:** File path string
**Output:** Boolean (true if test file)

```
FUNCTION is_test_file(filepath)
    Extract basename from filepath (everything after last /)

    Check basename patterns (case-sensitive for performance):
        If basename contains ".test." or ".spec."
            Return true
        If basename starts with "test_" or ends with "_test." before extension
            Return true
        If basename ends with "Test." or "Spec." before extension (PascalCase)
            Return true

    Check path patterns:
        If filepath contains "/__tests__/"
            Return true
        If filepath contains "/tests/" or "/test/"
            Return true
        If filepath contains "/spec/" or "/specs/"
            Return true

    Return false
END FUNCTION
```

**Edge Cases:**
- `test.ts` (bare "test" as name) - NOT a test file (too ambiguous)
- `utils.test.ts` - IS a test file
- `src/__tests__/helper.ts` - IS a test file (directory pattern)
- `testing-utils.ts` - NOT a test file (substring match avoided)

---

## 2. Helper Function: infer_layer(filepath)

**Purpose:** Infer architectural layer from directory path patterns.

**Input:** File path string
**Output:** Layer string (api|service|domain|data|infra|test|config|unknown)

```
FUNCTION infer_layer(filepath)
    Check patterns in priority order (first match wins):

    API layer indicators:
        If filepath contains "/api/" or "/routes/" or "/handlers/" or "/controllers/"
            Return "api"

    Service layer indicators:
        If filepath contains "/services/" or "/usecases/" or "/use-cases/"
            Return "service"

    Domain layer indicators:
        If filepath contains "/domain/" or "/models/" or "/entities/"
            Return "domain"

    Data layer indicators:
        If filepath contains "/data/" or "/repositories/" or "/dal/" or "/persistence/"
            Return "data"

    Infrastructure layer indicators:
        If filepath contains "/infra/" or "/infrastructure/" or "/providers/"
            Return "infra"

    Test layer (checked after specific layers):
        If is_test_file(filepath) returns true
            Return "test"

    Config layer indicators:
        If filepath contains "/config/" or "/configs/"
            Return "config"
        If basename contains ".config." (e.g., webpack.config.js)
            Return "config"

    Default:
        Return "unknown"
END FUNCTION
```

**Priority Rationale:**
- Specific layers checked before test (a test in /services/ is still a test)
- Config checked last (rarely overrides other layers)
- Test checked second-to-last to catch test files not in specific layers

---

## 3. Field Calculation: param_count

**Purpose:** Count parameters from the params signature string.

**Input:** params string (e.g., "a: string, b: number")
**Output:** Integer count

```
FUNCTION calculate_param_count(params_string)
    Trim whitespace from params_string

    If params_string is empty
        Return 0

    Count number of commas in params_string
    Return comma_count + 1
END FUNCTION
```

**Known Limitation (Tier 1 acceptable):**
- Generic types like `Map<string, number>` will be counted as 2 parameters
- Example: `foo(map: Map<K, V>)` returns 2 instead of 1
- Tier 2 will use tree-sitter parameter node counting for accuracy

**Edge Cases:**
- Empty params `""` returns 0
- Single param `"x"` returns 1
- Multiple params `"a, b, c"` returns 3
- Trailing comma `"a, b,"` returns 3 (acceptable Tier 1 behavior)

---

## 4. Field Calculation: line_count

**Purpose:** Calculate the number of lines in a function/method body.

**Input:** start_line (integer), end_line (integer)
**Output:** Integer count

```
FUNCTION calculate_line_count(start_line, end_line)
    Return end_line - start_line + 1
END FUNCTION
```

**Note:** This is inclusive count. A one-liner function (start=5, end=5) returns 1.

---

## 5. Field Calculation: has_throw

**Purpose:** Determine if function contains throw/raise statements.

**Input:** throw_count (integer, already tracked by pattern matching)
**Output:** Boolean

```
FUNCTION calculate_has_throw(throw_count)
    If throw_count > 0
        Return true
    Else
        Return false
END FUNCTION
```

**Note:** throw_count is already captured by existing pattern matching on lines 329-341. This just needs to be exposed in JSON output.

---

## 6. Field Calculation: has_recursion

**Purpose:** Detect if a function calls itself (direct recursion).

**Input:** function_name (string), calls_within_function (array of call names)
**Output:** Boolean

```
FUNCTION calculate_has_recursion(function_name, calls_list)
    For each call_name in calls_list
        If call_name equals function_name exactly
            Return true

    Return false
END FUNCTION
```

**Note:** This detects direct recursion only. Mutual recursion (A calls B, B calls A) is not detected in Tier 1.

**Integration Point:** Check during the existing calls loop (lines 351-366) where call names are already being collected.

---

## 7. Integration Points in extract_file()

### 7.1 Add Helper Functions (after line ~98)

Insert `is_test_file()` and `infer_layer()` functions after `json_escape()`.

### 7.2 File-Level Calculations (after line ~322, before definition loop)

```
Before iterating over definitions:
    Calculate is_test = is_test_file(file)
    Calculate layer = infer_layer(file)
```

These are file-level, computed once per file.

### 7.3 Definition-Level Calculations (inside definition loop, line ~326)

```
After IFS read of definition fields:
    Calculate param_count from params string
    Calculate line_count from start and end
```

### 7.4 Recursion Detection (inside calls loop, line ~351-366)

```
Modify existing calls collection loop:
    Initialize has_recursion = false before loop
    Inside loop, after extracting cname:
        If cname equals name (exact match)
            Set has_recursion = true
```

### 7.5 Boolean Calculations (line ~388)

```
After existing boolean calculations:
    Calculate has_throw from throw_count
```

### 7.6 JSON Output Modifications (lines 406-416)

Current output format ends with:
```
,"loop_count":%d,"call_count":%d}
```

New output format:
```
,"loop_count":%d,"call_count":%d,"is_test":%s,"layer":"%s","param_count":%d,"line_count":%d,"has_throw":%s,"has_recursion":%s}
```

**Field ordering:** Keep existing fields stable, append new fields at end.

---

## 8. Complete JSON Output Schema

After Phase 1 implementation, each unit will have:

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

**Total fields:** 16 (was 10)

---

## 9. Testing Checklist

After implementation, verify with:

| Test Case | Expected |
|-----------|----------|
| `foo.test.ts` | is_test=true |
| `src/__tests__/bar.ts` | is_test=true, layer="test" |
| `src/services/auth.ts` | is_test=false, layer="service" |
| `api/routes/users.ts` | layer="api" |
| Function with 0 params | param_count=0 |
| Function with 3 params | param_count=3 |
| 10-line function (lines 5-14) | line_count=10 |
| Function with throw | has_throw=true |
| Recursive function | has_recursion=true |
| Function calling other functions | has_recursion=false |

---

## 10. Alternatives Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Tree-sitter param nodes | Accurate generic handling | Query changes needed | Defer to Tier 2 |
| Config file for layers | User customizable | File I/O overhead | Defer |
| Parse package.json for tests | Project-accurate | Multiple formats, complexity | Defer |

**Tier 1 philosophy:** Ship fast with 90% accuracy. Iterate based on real-world usage.
