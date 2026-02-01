# Phase 3: Smart Batching Implementation Discovery

**Date:** 2026-02-01
**Branch:** feat/agent-scripts-batch-mode
**Status:** Discovery Complete

## Overview

Update `orchestrate-checking-agent.md` to implement intelligent batching from units.jsonl using test pairs, call graph clustering, directory grouping, and layer affinity.

---

## Question 1: Fields Enabling Smart Batching

### Primary Batching Fields

| Field | Type | Batching Purpose |
|-------|------|------------------|
| `file` | string | Directory grouping (extract dirname) |
| `layer` | enum | Layer-based grouping (api/service/domain/data/infra) |
| `calls` | string[] | Call graph clustering |
| `isTest` | boolean | Test pair detection |
| `testsUnit` | string | Test pairing (which unit this test covers) |
| `diff` | string | Token estimation for size limits |
| `lines` | [int, int] | Size calculation |

### Secondary Fields (Check Skipping)

- `hasLoops`, `hasTryCatch`, `hasAsync`, `hasThrow`, `hasRecursion`
- Used for check skipping, not batching

---

## Question 2: Token Estimation from Diff

### Formula
```
diff_lines = count newlines in diff field
diff_tokens = diff_lines * 12  (diff lines are ~12 tokens due to +/- markers)
```

### Budget Allocation per Batch
| Content | Allocation |
|---------|-----------|
| Checklist | ~500 tokens |
| Skill context | ~1000 tokens |
| Unit diffs | ~2000-2500 tokens |
| Source context | ~500 tokens |
| **Total** | **~4000 tokens** |

### Practical Threshold
Reserve 1500 for checklist+skills → 2500 for diffs → ~208 diff lines max

---

## Question 3: Batching Algorithm Priority

### 6-Phase Algorithm (strict order)

```
Phase 1: Skip Excluded Files
├─ *.lock, *-lock.json (lockfiles)
├─ *.generated.*, *.pb.*, *_generated.* (generated)
├─ *.min.js, *.bundle.js (bundled)
├─ __snapshots__/* (snapshots)
└─ vendor/*, node_modules/* (dependencies)

Phase 2: Test Pairs
├─ For each unit where isTest: true
├─ Find matching unit via testsUnit field
└─ Pair into single batch

Phase 3: Call Graph Clusters
├─ Build connected components via calls[]
├─ Units that call each other → same batch
└─ Only if cluster fits in token budget

Phase 4: Directory Groups
├─ Group by dirname(file)
└─ Chunk by token limit

Phase 5: Layer Grouping
├─ Group by layer field
└─ Chunk by token limit

Phase 6: Finalize
└─ Split any oversized batches
```

---

## Question 4: Output Format

### checking-batches.json Schema

```json
{
  "total_units": 25,
  "total_batches": 6,
  "skipped_count": 3,
  "skipped": [
    {"file": "package-lock.json", "reason": "lockfile"}
  ],
  "batches": [
    {
      "id": 1,
      "shared_context": "Test pair: UserService",
      "batch_strategy": "test_pair",
      "units": [...],
      "total_diff_tokens": 485
    }
  ]
}
```

### Batch Strategy Values
- `test_pair` - Test paired with subject
- `call_graph` - Connected by calls
- `directory` - Same directory
- `layer` - Same architectural layer

---

## Implementation Approach

The orchestrator agent needs to be an **LLM agent** (not bash script) because:
1. Needs to understand unit relationships semantically
2. Call graph clustering requires graph traversal logic
3. Test-to-subject matching may need fuzzy matching
4. Context description generation benefits from LLM

### Agent Workflow

1. Read `$BASE_DIR/units.jsonl`
2. Parse each line as JSON
3. Apply skip filters (lockfiles, generated, etc.)
4. Phase 2-5: Build batches with priority
5. Write `$BASE_DIR/checking-batches.json`
6. Return summary: "X units → Y batches (Z skipped)"

---

## Key Design Decisions

1. **All fields preserved**: Output includes all unit fields for checker agents
2. **Conservative token budget**: Use 2500 for diffs, leave 1500 for checklist
3. **Test pairs first**: Always pair tests with subjects before other grouping
4. **Directory grouping fallback**: Most effective for typical PRs
