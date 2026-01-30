# Triage: Semantic Unit Extraction

## Overview

Extract semantic units (functions, classes, tests) from code using AST parsing, then route to review categories based on characteristics.

**Strategy:**
1. Run `extract-units.sh` - uses tree-sitter CLI when available
2. For files in `fallback_files`, dispatch LLM extraction agents in parallel
3. Route units to categories based on characteristics

---

## Step 1: Run Extraction Script

```bash
cd agents/lens
./extract-units.sh {DIFF_ARGS} > {BASE_DIR}/extraction.json
```

Output:
```json
{
  "units": [
    {"type": "function", "name": "validateInput", "file": "src/auth.ts", "lines": [10, 25],
     "characteristics": {"has_loops": false, "has_try_catch": true, "has_async": false, "has_io_calls": false, "nesting_depth": 2}}
  ],
  "fallback_files": ["file1.swift", "file2.kt"],
  "tree_sitter_available": true
}
```

---

## Step 2: LLM Fallback (if needed)

For each file in `fallback_files`, dispatch a haiku agent **in parallel**:

```
Task(
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Extract: {FILENAME}",
  prompt: """
Extract semantic units from this code file.

Read: {FILE_PATH}

Return JSON:
{
  "file": "{FILE_PATH}",
  "units": [
    {"type": "function|class|method|test", "name": "...", "lines": [start, end],
     "characteristics": {"has_loops": bool, "has_try_catch": bool, "has_async": bool, "has_io_calls": bool}}
  ]
}

Characteristics to detect:
- has_loops: for, while, forEach, map, reduce, filter
- has_try_catch: try, catch, except, rescue, finally
- has_async: async, await, Promise
- has_io_calls: fetch, http, fs., query, execute, connect

Return valid JSON only.
"""
)
```

Merge fallback results into `extraction.json`.

---

## Step 3: Route to Categories

Route each unit based on characteristics (from `config.yaml`):

| Category | Routing Rules |
|----------|---------------|
| **defensive** | `has_try_catch: true` OR `has_io_calls: true` OR file in `auth/`, `security/` |
| **quality** | All units (every unit gets quality review) |
| **correctness** | `type: "test"` OR file matches `*_test.*`, `*.test.*`, `*.spec.*` |
| **performance** | `has_loops: true` OR `has_async: true` OR `nesting_depth >= 3` |
| **documentation** | File matches `*.md`, `docs/`, `README*` |

**Units can appear in multiple categories.** Quality always includes all units.

Write category files to `{BASE_DIR}/{category}.json`.

---

## Characteristics Reference

| Characteristic | Detected By | Routes To |
|----------------|-------------|-----------|
| `has_loops` | for, while, forEach, map, reduce, filter | performance |
| `has_try_catch` | try, catch, except, rescue, finally | defensive |
| `has_async` | async, await, Promise | performance |
| `has_io_calls` | fetch, http, fs., query, execute, connect | defensive |
| `nesting_depth` | Indentation analysis (≥3 = complex) | performance |
| `type: test` | Unit type from AST | correctness |

---

## Integration

This triage step is called from `commands/review.md` (Standard/Deep mode).

The extracted units with characteristics enable:
- **Precise routing**: Only review loops in performance, only review error handling in defensive
- **Reduced noise**: Skills only see relevant code
- **Evidence trail**: Characteristics explain why a unit was routed to a category
