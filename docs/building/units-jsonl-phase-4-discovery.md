# Phase 4: Wire into /code-foundations:review Discovery

**Date:** 2026-02-01
**Branch:** feat/agent-scripts-batch-mode
**Status:** Discovery Complete

## Overview

Update `/code-foundations:review` to use the new extraction pipeline:
1. Call `extract-with-diff.sh` to produce `units.jsonl`
2. Pass to `orchestrate-checking-agent` for batching
3. Dispatch checker agents per batch

---

## Current State Analysis

### review.md Structure

The review command is a large agent template (~1400 lines) with:
- YAML frontmatter with allowed-tools
- Two flows: SANITY_FLOW and PR_FLOW
- Multiple phases: Extraction, Orchestrate, Checking, Investigation, Summary

### Current Extraction (STEP 5 / SANITY STEP 1)

Currently dispatches `code-foundations:extraction-agent` subagents that:
1. Receive a batch of file paths
2. Extract units from those files
3. Write to `$BASE_DIR/extraction/` directory

### Target Extraction

Replace with single call to `extract-with-diff.sh`:
1. Run script with DIFF_CMD args
2. Script outputs `units.jsonl` directly
3. No need for multiple extraction agents

---

## Required Changes

### Change 1: Replace Extraction Agents with Shell Script

**Location:** SANITY STEP 1: EXTRACTION (lines ~334-376) and STEP 5: PHASE 1 (lines ~696-745)

**Current (multi-agent):**
```python
for batch in batches:
    Task(subagent_type="code-foundations:extraction-agent", ...)
```

**New (single script call):**
```bash
$PLUGIN_ROOT/agents/extract-with-diff.sh $DIFF_ARGS > $BASE_DIR/units.jsonl
```

**Benefits:**
- Much faster (no LLM calls for extraction)
- Consistent output format
- Less token usage

### Change 2: Update Orchestrate Input

**Location:** SANITY STEP 2: ORCHESTRATE (lines ~380-413) and STEP 6: PHASE 2a (lines ~753-862)

**Current:** Orchestrator reads from `$BASE_DIR/extraction/` directory (multiple files)

**New:** Orchestrator reads from `$BASE_DIR/units.jsonl` (single JSONL file)

The orchestrate-checking-agent.md is already updated in Phase 3 to expect `units.jsonl`.

### Change 3: Update Checker Agent Input

**Location:** SANITY STEP 3: CHECKING (lines ~417-489) and STEP 6b: PHASE 2b (lines ~864-922)

**Current:** Checker receives units from orchestrator's `checking-batches.json`

**No change needed:** The orchestrator output format (`checking-batches.json`) remains compatible.

---

## Integration Points

### 1. DIFF_ARGS Variable

Already computed in STEP 3 (GET DIFF TARGET):
- Staged → `--staged`
- Unstaged → (empty)
- All uncommitted → `HEAD`
- Branch diff → `$MERGE_BASE HEAD`

Script accepts these directly.

### 2. Script Location

Script is at `$PLUGIN_ROOT/agents/extract-with-diff.sh` (created in Phase 2).

### 3. Output Location

Script outputs to stdout, redirect to `$BASE_DIR/units.jsonl`:
```bash
$PLUGIN_ROOT/agents/extract-with-diff.sh $DIFF_ARGS > $BASE_DIR/units.jsonl
```

---

## Affected Sections

### SANITY FLOW

1. **SANITY STEP 1: EXTRACTION** - Replace with script call
2. **SANITY STEP 2: ORCHESTRATE** - Already expects units.jsonl (Phase 3)
3. **SANITY STEP 3-6** - No changes needed

### PR FLOW

1. **STEP 5: PHASE 1 - EXTRACTION** - Replace with script call
2. **STEP 6: PHASE 2a - CHECK ORCHESTRATION** - No changes needed
3. **STEP 6b onwards** - No changes needed

---

## Implementation Checklist

1. [ ] In SANITY STEP 1, replace extraction agent dispatch with:
   ```bash
   $PLUGIN_ROOT/agents/extract-with-diff.sh $DIFF_ARGS > $BASE_DIR/units.jsonl
   ```

2. [ ] In STEP 5, replace extraction agent dispatch with same script call

3. [ ] Update phase task subjects (remove "batch X" since single call)

4. [ ] Verify orchestrator input path matches (`$BASE_DIR/units.jsonl`)

5. [ ] Test both flows (--sanity and --pr)

---

## Backward Compatibility

- extraction-agent.md can remain for fallback cases
- New script handles missing tree-sitter gracefully (fallback_files output)
- If script fails, could fall back to extraction agents

---

## Performance Impact

| Phase | Before | After |
|-------|--------|-------|
| Extraction | N haiku agents (~5-10s per batch) | 1 shell script (<2s total) |
| Token usage | ~500 tokens per agent call | ~0 tokens |
| Latency | Parallel but LLM overhead | Sequential but fast |

**Net improvement:** Extraction phase from ~30s to <2s for typical PR.
