# Phase 3 Review: orchestrate-checking-agent.md

**Reviewer:** claude-opus-4-5
**Date:** 2026-02-01
**Skills Applied:** aposd-verifying-correctness, cc-quality-practices

---

## Verification Summary

| Requirement | Status | Evidence |
|-------------|--------|----------|
| 7 workflow steps documented | PASS | Steps 1-7 in Workflow section |
| Token estimation formula | PASS | `diff_tokens = count_newlines * 12`, budget 2500 |
| Skip patterns complete | PASS | Table in Step 2 covers all 5 categories |
| Test pair matching uses isTest/testsUnit | PASS | Step 3 explicitly uses both fields |
| Output schema includes batch_strategy | PASS | Batch Schema table, valid values enumerated |
| Example shows multiple batch strategies | PASS | JSON example shows test_pair, call_graph, directory |

---

## Detailed Verification

### 1. Workflow Steps (7 required + output)

| Step | Name | Implementation |
|------|------|----------------|
| 1 | Read and Parse Units | Lines 37-62 |
| 2 | Apply Skip Filters | Lines 63-77 |
| 3 | Create Test Pairs | Lines 79-92 |
| 4 | Build Call Graph Clusters | Lines 94-114 |
| 5 | Group by Directory | Lines 116-146 |
| 6 | Group by Layer | Lines 148-163 |
| 7 | Handle Stragglers | Lines 165-180 |
| 8 | Write Output | Lines 182-265 |

All 7 batching steps documented with clear pseudocode. Step 8 provides detailed output specification.

### 2. Token Estimation Formula

From Token Budget section (lines 17-31):
```
TOKENS_PER_DIFF_LINE = 12
DIFF_TOKEN_BUDGET = 2500
diff_tokens = (count_newlines_in_diff) * 12
```

Formula and budget correctly specified.

### 3. Skip Patterns

Table at lines 67-73 includes:

| Pattern | Category |
|---------|----------|
| `*.lock`, `*-lock.json` | lockfile |
| `*.generated.*`, `*.pb.*`, `*_generated.*` | generated |
| `*.min.js`, `*.bundle.js` | bundled |
| `__snapshots__/*` | snapshot |
| `vendor/*`, `node_modules/*` | vendor |

All 5 skip categories present with concrete examples.

### 4. Test Pair Matching

Step 3 (lines 79-92):
> "For each remaining unit where `isTest: true` and `testsUnit` is not empty:
> 1. Find the unit with `name` matching `testsUnit`"

Both `isTest` and `testsUnit` fields used correctly.

### 5. batch_strategy Field

Batch Schema table (lines 258-264) defines:
- Field: `batch_strategy`
- Type: string
- Valid values: `test_pair`, `call_graph`, `directory`, `layer`, `fallback`

All values documented with descriptions.

### 6. Multiple Batch Strategies in Example

Example output (lines 186-251) shows:
- Batch 1: `"batch_strategy": "test_pair"`
- Batch 2: `"batch_strategy": "call_graph"`
- Batch 3: `"batch_strategy": "directory"`

Three different strategies demonstrated.

---

## Correctness Verification (aposd-verifying-correctness)

### Requirements: PASS
- All 6 requirements mapped to specific sections
- Discovery doc requirements fully translated to agent spec

### Concurrency: N/A
- Single-agent sequential workflow

### Errors: PASS
- Verification checklist before output (lines 176-180)
- Edge cases handled (test without subject, orphaned units)

### Resources: N/A
- Agent reads/writes files per workflow

### Boundaries: PASS
- Empty input: Handled (produces empty batches)
- Large input: Token chunking in each step
- Single unit: Becomes single-unit batch

### Security: N/A
- Internal system, no untrusted input

---

## Quality Practices Checklist (cc-quality-practices)

- [x] Verification checklist before output
- [x] Clear examples with JSON snippets
- [x] Rationale for each batching strategy
- [x] Edge cases addressed (test without subject, orphaned calls)
- [x] Token budget chunking algorithm documented
- [x] Consistent terminology with discovery/pseudocode docs

---

## Consistency Check

| Document | Purpose | Alignment |
|----------|---------|-----------|
| units-jsonl-phase-3-discovery.md | Requirements | Aligned |
| units-jsonl-phase-3-pseudocode.md | Algorithm spec | Aligned |
| orchestrate-checking-agent.md | Agent instructions | Complete |

Algorithm flow matches across all three documents. Implementation adds `fallback` batch_strategy not in discovery (appropriate addition for stragglers).

---

## Verdict

**PASS**

The implementation in `orchestrate-checking-agent.md` correctly implements all Phase 3 requirements:
1. Complete 7-step workflow with detailed instructions
2. Token estimation formula and budget correctly specified
3. All skip patterns documented with examples
4. Test pair matching using correct fields
5. Output schema fully specified with batch_strategy values
6. Example demonstrates multiple batch strategies

No issues found. Ready for Phase 4 integration.
