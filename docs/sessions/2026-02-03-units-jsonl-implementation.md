# Session: units.jsonl Implementation

**Date:** 2026-02-03
**Branch:** `feat/agent-scripts-batch-mode`
**Status:** Phase 1-5 complete, orchestrator decision pending

---

## What Was Built

### Phase 1: Enhanced extract-units.sh
Added 6 Tier 1 fields to AST extraction:
- `is_test` - filename/path pattern detection
- `layer` - architectural layer inference
- `param_count` - parameter count
- `line_count` - function body size
- `has_throw` - throw/raise detection
- `has_recursion` - self-call detection

### Phase 2: Created extract-with-diff.sh
New script that produces `units.jsonl` from git diffs:
- Parses git diff to get file statuses and hunks
- Runs extract-units.sh on changed files
- Matches units to overlapping diff hunks
- Adds `diff`, `changeStatus`, `summary` fields
- Outputs JSONL format

### Phase 3: Updated orchestrate-checking-agent.md
Documented 7-step batching algorithm:
1. Skip lockfiles/generated
2. Test pairs (isTest + testsUnit)
3. Call graph clusters
4. Directory groups
5. Layer groups
6. Stragglers
7. Write output

### Phase 4: Wired into /code-foundations:review
Replaced multi-agent extraction with single script call in both SANITY and PR flows.

### Phase 5: Implemented testsUnit Inference
Added `infer_tests_unit()` function to `extract-units.sh`:
- Strips test suffixes from filenames to infer tested unit name
- Supports multiple conventions:
  - JS/TS: `foo.test.ts` → `foo`, `foo.spec.ts` → `foo`
  - Python: `test_foo.py` → `foo`, `foo_test.py` → `foo`
  - Java: `FooTest.java` → `Foo`
  - C#: `FooTests.cs` → `Foo`, `FooSpecs.cs` → `Foo`
- Field flows through `extract-with-diff.sh` to final units.jsonl

**Verified on:**
- `booking-trip-creation`: `LinkedPnrsControllerTests.cs` → `tests_unit: "LinkedPnrsController"`
- `PricingAPI`: `QuoteRequestAdapterDpMarketTests.cs` → `tests_unit: "QuoteRequestAdapterDpMarket"`

---

## Layer System

### Final Layer Structure
| Layer | Description | Path Patterns |
|-------|-------------|---------------|
| api | HTTP endpoints | /api/, /routes/, /handlers/, /controllers/ |
| service | Business logic | /services/, /usecases/, /App/ |
| domain | Core entities | /domain/, /models/, /entities/, /Core/ |
| data | Database access | /data/, /repositories/, /dal/, /persistence/ |
| integration | External systems | /adapters/, /providers/, /clients/, /gateways/, /external/ |
| infra | Cross-cutting | /infra/, /infrastructure/, /middleware/, /extensions/, /hosting/ |
| test | Test files | *.test.*, *.spec.*, /tests/, /__tests__/, .Tests. |
| config | Configuration | /config/, /constants/, *.config.* |

### Layer Overrides
Projects can create `.code-foundations/layers.yaml`:
```yaml
overrides:
  "/Infrastructure/": integration    # Override for this repo
```

---

## Test Results

### booking-trip-creation (max/validate-linked-pnr vs main)
- Files: 18
- Units: 123
- Layers: domain (39), service (38), integration (31), api (15)
- Tests detected: 56

### PricingAPI (feature/x-features-header-toggle vs main)
- Files: 14
- Units: 139
- Layers: infra (59), integration (39), service (35), config (6)
- Tests detected: 78

---

## Open Issues

### ~~1. `testsUnit` Not Populated (HIGH)~~ ✅ RESOLVED
Implemented filename convention approach in Phase 5.

### 2. Orchestrator is LLM-Based (MEDIUM)
Using Sonnet to execute algorithmic batching logic is:
- Expensive (tokens)
- Non-deterministic
- Slower than a script

**Options:**
- Keep as LLM (flexible, handles edge cases)
- Convert to bash script (fast, deterministic, free)
- Hybrid (bash for deterministic parts, LLM for fuzzy matching)

### 3. Call Graph Matching is Fuzzy (MEDIUM)
Matching by function name alone can have false positives.
Common names like `validate`, `save`, `create` may match unrelated units.

---

## Commits on This Branch

```
a992a50 feat: add repo-level layer override config
c28a3cd feat: split infra into integration + infra layers
def4276 fix: add Middleware, Extensions, Constants to layer detection
b0317b7 fix: add C#/.NET patterns to test and layer detection
946a30e docs: mark units.jsonl extraction plan complete
0c816d8 feat(review): wire units.jsonl extraction into review command
b68f5b0 feat(orchestrate): implement smart batching from units.jsonl
692d13d feat(extract-with-diff): create diff integration script for units.jsonl
51e60c2 feat(extract-units): add Tier 1 fields for units.jsonl
```

---

## Next Steps

1. **Decide on orchestrator approach** - LLM vs bash vs hybrid
2. ~~**Implement testsUnit inference** - Enable test pairing~~ ✅ Done
3. **Test full review flow** - Run `/code-foundations:review --sanity` on a real PR
4. **Performance benchmark** - Measure extraction time on large repos

---

## Key Files

| File | Purpose |
|------|---------|
| `agents/extract-units.sh` | AST extraction with tree-sitter |
| `agents/extract-with-diff.sh` | Diff integration, produces units.jsonl |
| `agents/orchestrate-checking-agent.md` | LLM agent for batching |
| `commands/review.md` | Main review command |
| `docs/specs/units-jsonl-spec.md` | Schema and batching rules |

---

## Commands for Testing

```bash
# Test extraction on a repo
cd ~/repos/PricingAPI
/Users/r/repos/code-foundations/agents/extract-with-diff.sh main...feature/x-features-header-toggle | jq -s '{total: length, by_layer: (group_by(.layer) | map({layer: .[0].layer, count: length}))}'

# Test with layer override
echo 'overrides:
  "/Infrastructure/": integration' > .code-foundations/layers.yaml
```
