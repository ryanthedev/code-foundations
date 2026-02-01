# Phase 1: units.jsonl Extraction System Discovery

**Date:** 2026-02-01
**Branch:** feat/agent-scripts-batch-mode
**Status:** Discovery Complete - Ready for Implementation

## Executive Summary

Extract-units.sh currently outputs 10 fields with basic AST extraction via tree-sitter. Phase 1 requires adding 6 new Tier 1 fields to enable 80% of check skipping and basic batching. All required patterns exist in the .scm query files; implementation requires shell logic enhancements.

---

## Question 1: Current Output Fields

### Current Implementation (extract-units.sh lines 406-416)

Extract-units.sh produces JSON with these fields per unit:

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
  "call_count": integer
}
```

---

## Question 2: Tree-Sitter Query Patterns

### Query File Overview

5 comprehensive .scm files found in `agents/queries/`:

| Language | File | Lines | Patterns |
|----------|------|-------|----------|
| TypeScript | typescript.scm | 89 | 11 definition patterns + 7 control flow |
| Python | python.scm | 76 | 7 definition patterns + 8 control flow |
| Go | go.scm | 301 | 18 definition patterns + 25 control flow |
| C# | csharp.scm | 309 | 11 definition + 18 pattern types |
| Swift | swift.scm | 379 | 13 definition + 16 pattern types |

---

## Question 3: hasThrow Pattern Status

**All 5 languages already have throw patterns:**

- TypeScript: `(throw_statement) @pattern.throw` (line 85)
- Python: `(raise_statement) @pattern.throw` (line 69)
- Go: panic pattern + error_check (lines 125-141)
- C#: `(throw_statement) @pattern.throw` (line 188)
- Swift: `(throw_keyword) @pattern.throw` (line 251)

**Issue:** Pattern is detected but not output in JSON. **Fix:** Add `throw_count > 0` check and output `"has_throw": boolean`.

---

## Question 4: Implementation Plan for Tier 1 Fields

### Field 1: isTest (Filename Pattern Detection)

```bash
is_test=false
file_basename="${file##*/}"

case "$file_basename" in
  *test.*|*spec.*|*Test.*|*Spec.*) is_test=true ;;
esac

case "$file" in
  */__tests__/*|*/tests/*) is_test=true ;;
esac
```

### Field 2: layer (Path Pattern Inference)

```bash
infer_layer() {
  local file="$1"
  case "$file" in
    */api/*|*/routes/*|*/handlers/*|*/controllers/*)  echo "api" ;;
    */services/*|*/usecases/*)                        echo "service" ;;
    */domain/*|*/models/*|*/entities/*)               echo "domain" ;;
    */data/*|*/repositories/*|*/dal/*)                echo "data" ;;
    */infra/*|*/infrastructure/*|*/providers/*)       echo "infra" ;;
    *.test.*|*.spec.*|*/tests/*|*/__tests__/*)        echo "test" ;;
    */config/*|*.config.*)                            echo "config" ;;
    *)                                                 echo "unknown" ;;
  esac
}
```

### Field 3: paramCount

```bash
if [[ -z "${current_params// }" ]]; then
  param_count=0
else
  param_count=$(($(printf '%s' "$current_params" | tr -cd ',' | wc -c) + 1))
fi
```

### Field 4: hasThrow

Already detected, just add to output:
```bash
local has_throw=false
(( throw_count > 0 )) && has_throw=true
```

### Field 5: hasRecursion

```bash
# During calls array building:
if [[ "$cname" == "$name" ]]; then
  has_recursion=true
fi
```

### Field 6: lineCount

```bash
local line_count=$((end - start + 1))
```

---

## Code Locations and Modifications

### File: `/Users/r/repos/code-foundations/agents/extract-units.sh`

| Location | Line | Change |
|----------|------|--------|
| Boolean computation | ~388 | Add `has_throw` flag |
| hasRecursion detection | ~348 | Check during calls array building |
| lineCount calculation | ~406 | Add before JSON output |
| Helper functions | ~100 | Add `infer_layer()` and `is_test_file()` |
| paramCount calculation | ~326 | After params read |
| JSON output | 406-416 | Add new fields |

---

## Query File Status

**No .scm changes required** - All patterns present and correctly named.

| Pattern | TS | Py | Go | C# | Swift |
|---------|----|----|----|----|-------|
| Throw | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Implementation Order

| Priority | Field | Complexity |
|----------|-------|-----------|
| 1 | hasThrow | Trivial |
| 2 | lineCount | Trivial |
| 3 | paramCount | Low |
| 4 | isTest | Low |
| 5 | layer | Low |
| 6 | hasRecursion | Low |
