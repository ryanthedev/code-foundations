# Session: AST-Grep Extraction Script Merge

**Date:** 2026-02-04
**Branch:** `feat/agent-scripts-batch-mode`
**Status:** IN PROGRESS - Script merged but has bug

## What We Did

### 1. Verified AST-Grep Extraction Works
- `extract-units.sh` rewritten to use ast-grep (not tree-sitter)
- `orchestrate-batches.sh` simplified to file-based batching
- Tested on PricingAPI: 114 units → 9 batches

### 2. Fixed Plugin Cache Issues
- Plugin was reading from wrong path (`1.2.0` vs `3.5.0` subdirectory)
- Fixed `~/.claude/plugins/installed_plugins.json` to point to correct path
- Discovered Claude Code creates versioned subdirectories automatically
- **Correct cache path:** `~/.claude/plugins/cache/rtd/code-foundations/3.5.0/`

### 3. Added Version Output
- Scripts now print version to stderr: `[extract-units.sh v3.5.0]`
- Review command has `version: "3.5.0"` in frontmatter
- Added STEP 0 in review.md to output version via bash echo

### 4. Merged Extraction Scripts
- Combined `extract-units.sh` + `extract-with-diff.sh` into single script
- Removed `extract-with-diff.sh`
- Updated references in `review.md` and `orchestrate-batches.sh`
- **New version:** 3.5.1

## Current Bug

The merged script only extracts 14 units instead of 114. Something is wrong with the file loop or diff hunk matching.

**Symptom:**
```bash
cd ~/repos/PricingAPI
/Users/r/repos/code-foundations/agents/extract-units.sh main 2>/dev/null | wc -l
# Returns: 14 (should be ~114)
```

**Only these files produce output:**
- PricingApi.UnitTests/Adapters/QuoteRequestAdapterDpMarketTests.cs (11 units)
- PricingApi.UnitTests/Adapters/QuoteRequestAdapterTests.cs (3 units)

**All 14 files are detected but most produce no units.**

## Files Changed (Uncommitted)

```
agents/extract-units.sh  - Merged script (v3.5.1)
agents/extract-with-diff.sh - DELETED
commands/review.md - Updated references
agents/orchestrate-batches.sh - Updated references
```

## Previous Commits on Branch

```
535ea87 chore: add version output to extraction scripts
0aab430 chore(review): output version at start of review command
6c7b0a2 feat(extraction): migrate to ast-grep with file-based batching
17ec1ae docs: update session file with Phase 7 completion
```

## Next Steps

1. **Debug the merged script** - Find why most files don't produce units
   - Check if `file_hunks` is empty for those files
   - Check if `extract_file` is returning empty
   - The diff hunk matching might be failing

2. **Test fix on PricingAPI** - Should get ~114 units

3. **Sync to plugin cache** - Copy to `~/.claude/plugins/cache/rtd/code-foundations/3.5.0/`

4. **Test full review flow** - Run `/code-foundations:review --sanity main`

## Key Learnings

1. **Plugin cache structure:** Claude Code uses versioned subdirectories
2. **Plugin path:** Must update both `installed_plugins.json` AND the actual files
3. **Version verification:** Add version output to scripts for debugging
4. **LLMs ignore instructions:** Putting "output this text" in skill files doesn't work reliably

## Test Commands

```bash
# Test extraction
cd ~/repos/PricingAPI
/Users/r/repos/code-foundations/agents/extract-units.sh main 2>&1 | head -5

# Count units
/Users/r/repos/code-foundations/agents/extract-units.sh main 2>/dev/null | wc -l

# Test orchestration
/Users/r/repos/code-foundations/agents/extract-units.sh main 2>/dev/null | \
  /Users/r/repos/code-foundations/agents/orchestrate-batches.sh | \
  jq '.[] | {reason, units: (.units | length)}'

# Sync to cache
cp /Users/r/repos/code-foundations/agents/extract-units.sh \
   ~/.claude/plugins/cache/rtd/code-foundations/3.5.0/agents/
```
