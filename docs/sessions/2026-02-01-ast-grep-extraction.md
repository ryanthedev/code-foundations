# Session: AST Extraction with ast-grep

**Date:** 2026-02-01
**Branch:** `feat/agent-scripts-batch-mode`
**Repo:** `/Users/r/repos/code-foundations`

## Context

Building semantic unit extraction for code review. Need to extract functions/methods/classes with metadata (params, return types, calls, loops, async) for the checker agents.

## What We Learned

### Research Findings

1. **No existing comprehensive extraction queries** - Official tree-sitter repos only have minimal `tags.scm` for "go to definition"
2. **ast-grep is the right tool** - Clean JSON output, metaVariables extraction, 20+ languages
3. **Everyone writes custom queries** - No community library for rich metadata extraction

### ast-grep Installation

```bash
brew install ast-grep  # Done - v0.40.5
/plugin marketplace add ast-grep/agent-skill  # Done
/plugin install ast-grep  # Done - RESTART REQUIRED
```

### Working Patterns

**TypeScript (works great):**
```bash
# Find async functions with params and return type
sg --pattern 'async function $NAME($$$PARAMS): $RET { $$$BODY }' --json file.ts

# Output includes metaVariables.single.NAME.text, .RET.text, etc.
```

**Characteristics detection:**
```bash
sg --pattern 'try { $$$BODY } catch ($ERR) { $$$HANDLER }' --json  # try/catch
sg --pattern 'for (const $VAR of $ITER) { $$$BODY }' --json        # for-of loops
sg --pattern 'await $EXPR' --json                                   # async
sg --pattern '$FN($$$ARGS)' --json                                  # calls
```

**C# (needs kind selector):**
```yaml
# Inline patterns don't work well - use YAML rules with kind selector
id: find-methods
language: csharp
rule:
  kind: method_declaration
```

## What We're Extracting

| Field | Purpose |
|-------|---------|
| `name` | Identify the unit |
| `type` | function, method, class |
| `file`, `lines` | Location |
| `params` | Signature, input validation checks |
| `return_type` | Type safety checks |
| `visibility` | exported/public/private |
| `has_loops` | Skip loop checks if false |
| `has_try_catch` | Skip error handling checks if false |
| `has_async` | Skip concurrency checks if false |
| `calls` | Dependency tracking, N+1 detection |

## Files Changed This Session

| File | Status |
|------|--------|
| `agents/orchestrate-checking-agent.md` | Created - batching logic |
| `agents/investigation-agent.md` | Refactored - CLI calls |
| `agents/add-verdict.sh` | Refactored - CLI for CONFIRMED |
| `agents/queries/*.scm` | Created - tree-sitter queries (may replace with ast-grep) |
| `commands/review.md` | Updated - uses orchestrate agent |

## Commits

```
ab1afd9 feat: add orchestrate-checking-agent for intelligent batching
b0b8138 chore: remove session context file
9d48c99 refactor: simplify investigation agent - CLI calls, remove batch mode
```

## Next Steps

1. **Restart Claude Code** to load ast-grep plugin
2. **Use `/ast-grep:ast-grep` skill** to write proper extraction rules
3. **Create `extract-units-sg.sh`** using ast-grep instead of tree-sitter CLI
4. **Test on all target languages:** TypeScript, C#, Go, Swift, Python

## Resume Command

```
Read docs/sessions/2026-02-01-ast-grep-extraction.md
```

Then use the ast-grep skill to write extraction rules for each language.
