# Session: Agent Scripts with AST Integration

**Date:** 2026-02-01
**Branch:** `feat/agent-scripts-batch-mode`
**Repo:** `/Users/r/repos/code-foundations`

## What Was Built

Three agent scripts with schema-enforced output:
- `add-unit.sh` - Records extracted units to units.jsonl
- `add-finding.sh` - Records check results to findings.jsonl
- `add-verdict.sh` - Records investigation verdicts to verdicts.jsonl

Three agent definitions:
- `extraction-agent.md` - AST extraction + LLM fallback
- `checker-agent.md` - Run checks against units
- `investigation-agent.md` - Verify findings, provide fixes

## Key Design Decisions

1. **AST-first extraction** via `extract-units.sh` (tree-sitter)
2. **LLM only enriches** (diff, summary) or handles fallback files
3. **CLI calls per item** (not batch stdin) - simpler, debuggable
4. **Count verification** at end of each phase
5. **Unit characteristics from AST** - `has_loops`, `has_async`, `has_try_catch`, `has_io_calls`, `nesting_depth`
6. **Fix structure uses `edits[]` array** for multi-file support
7. **Any unit type allowed** - function, method, class, interface, test, etc.

## Flow

### Extraction Phase

```
extract-units.sh $DIFF_ARGS
    → {units: [...], fallback_files: [...]}

For each AST unit:
    → get diff hunk (bash)
    → generate summary (LLM)
    → add-unit.sh --file --name --type ...

For each fallback file:
    → LLM reads file + diff
    → identifies units manually
    → add-unit.sh ...

Output: units.jsonl
```

### Checking Phase

```
Read units.jsonl + checklist

For each unit × check:
    → read code around unit lines
    → evaluate: PASS, FINDING, or N/A
    → use characteristics for N/A shortcuts (no loops → loop checks N/A)
    → add-finding.sh --batch --unit --check-id --verdict ...

Output: findings.jsonl
```

### Investigation Phase

```
Read findings (FINDING verdict only)

For each finding:
    → read code context
    → verify: CONFIRMED, FALSE_POSITIVE, or NEEDS_CONTEXT
    → if CONFIRMED: provide fix.edits[] array
    → add-verdict.sh (batch mode for CONFIRMED, CLI for others)

Output: verdicts.jsonl
```

## Files Changed

| File | Purpose |
|------|---------|
| `agents/add-unit.sh` | Schema validation, CLI args, appends to units.jsonl |
| `agents/add-finding.sh` | Schema validation, CLI args, appends to findings.jsonl |
| `agents/add-verdict.sh` | Schema validation, edits[] format, appends to verdicts.jsonl |
| `agents/extract-units.sh` | AST extraction with characteristics, C# support |
| `agents/extraction-agent.md` | AST + LLM fallback workflow |
| `agents/checker-agent.md` | Check evaluation workflow |
| `agents/investigation-agent.md` | Finding verification workflow |

## Commits on Branch

```
<pending> refactor: simplify investigation agent - CLI calls, remove batch mode
42c0d99 refactor: simplify checker agent - CLI calls, use unit characteristics
f2d9ece fix: allow any unit type (interface, test, etc.)
bedee91 refactor: simplify extraction flow - AST first, then enrich
5f9cbc6 fix: wire characteristics into AST output, add C# support
dd6ed33 fix: wire extraction-agent to use AST extraction (tree-sitter)
f8bb988 feat: add batch mode to agent scripts with unified fix.edits format
```

## Schema Examples

### units.jsonl
```json
{"file":"src/api.ts","name":"ValidateUser","type":"method","lines":[10,45],"diff":"@@ -10,6 +10,15 @@...","summary":"Added input validation","has_loops":false,"has_async":true,"has_try_catch":true,"has_io_calls":true,"nesting_depth":3}
```

### findings.jsonl
```json
{"batch":"1","unit":"ValidateUser","file":"src/api.ts","check_id":"NULL-2","verdict":"FINDING","line":42,"issue":"userId not checked for null","confidence":"HIGH"}
```

### verdicts.jsonl
```json
{"finding_id":"1-NULL-2","file":"src/api.ts","line":42,"check_id":"NULL-2","verdict":"CONFIRMED","reason":"Real issue","fix":{"explanation":"Add null check","edits":[{"file":"src/api.ts","old_string":"db.lookup(userId)","new_string":"userId ? db.lookup(userId) : null"}]}}
```

## What's Left

- [x] Investigation agent needs same refactor pattern (CLI calls, not batch)
- [ ] Integration with `commands/review.md`
- [ ] Register agents in plugin system (currently not discoverable)
- [ ] End-to-end test of full review flow
- [ ] Update CLAUDE.md with new flow documentation

## Test Commands

```bash
# Test extraction (AST path)
export BASE_DIR=/tmp/test && mkdir -p $BASE_DIR
/path/to/agents/extract-units.sh --staged | jq .

# Test extraction agent
# Dispatch with: FILES, DIFF_ARGS, PLUGIN_ROOT, BASE_DIR

# Test checker agent
# Dispatch with: UNITS_FILE, CHECKLIST, BATCH, PLUGIN_ROOT, BASE_DIR

# Verify outputs
cat $BASE_DIR/units.jsonl | jq -c '{name: .name, type: .type}'
cat $BASE_DIR/findings.jsonl | jq -c '{unit: .unit, verdict: .verdict}'
```

## Resume Instructions

To continue this work:

1. Checkout the branch: `git checkout feat/agent-scripts-batch-mode`
2. Read this file for context
3. Focus on "What's Left" items
4. Test with real diffs using the test commands above
