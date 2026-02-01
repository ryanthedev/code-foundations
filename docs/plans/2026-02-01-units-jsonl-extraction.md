# units.jsonl Extraction System

Status: in-progress
Spec: /Users/r/repos/code-foundations/docs/specs/units-jsonl-spec.md

## Objective

Create an extraction pipeline that produces `units.jsonl` from git diffs, enabling intelligent batching and check skipping for code review.

## Phases

### Phase 1: Enhance extract-units.sh (Tier 1 fields)

Update `/Users/r/repos/code-foundations/agents/extract-units.sh` to output the Tier 1 fields:

Current output:
- file, name, type, lines, visibility, modifiers
- hasLoops, hasTryCatch, hasAsync, calls

Add:
- `isTest` - detect from filename pattern (*test*, *spec*, __tests__)
- `layer` - infer from path (api/service/domain/data/infra/test/config)
- `paramCount` - count from params string
- `hasThrow` - add pattern to .scm queries
- `hasRecursion` - check if name appears in calls array
- `lineCount` - compute from lines array

### Phase 2: Add diff integration

Create `/Users/r/repos/code-foundations/agents/extract-with-diff.sh`:

1. Take git diff args (--staged, branch, etc.)
2. Get changed files from diff
3. For each file, get diff hunks
4. Run extract-units.sh on each file
5. Match units to diff hunks by line overlap
6. Add `diff`, `changeStatus`, `summary` fields
7. Output as JSONL (one unit per line)

### Phase 3: Create orchestrate batching

Update `/Users/r/repos/code-foundations/agents/orchestrate-checking-agent.md` to:

1. Read units.jsonl
2. Apply batching rules from spec (test pairs -> call graph -> directory -> layer)
3. Respect ~4k token budget per batch
4. Output batch assignments

### Phase 4: Wire into /code-foundations:review

Update `/Users/r/repos/code-foundations/commands/review.md` to:
1. Call extract-with-diff.sh to produce units.jsonl
2. Pass to orchestrate-checking-agent for batching
3. Dispatch checker agents per batch

## Testing

Test against:
- ~/repos/booking-trip-creation (max/validate-linked-pnr vs main)
- ~/repos/PricingAPI (feature/x-feature-header-toggle vs main)

Verify:
- Units extracted with all Tier 1 fields
- Diff hunks correctly matched to units
- Batching groups related units (test+subject, caller+callee)
- Check skipping works based on characteristics

## Constraints

- Keep extraction fast (<1s for typical PR)
- Graceful fallback for unsupported languages (LLM extraction)
- JSONL format for streaming/append
- No breaking changes to existing review flow
