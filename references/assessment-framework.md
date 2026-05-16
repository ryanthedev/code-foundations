# Assessment Framework

Simple action-based grouping for code review findings.

## Why This Exists

Research shows LLMs are overconfident when self-assessing difficulty (arXiv 2506.00072, 2512.18880). Instead of asking "how hard is this?", we ask "what should happen next?"

## Action Types

Each finding gets an **action type** based on two questions:

1. **Can I provide a specific fix?** (confidence)
2. **Is this localized or systemic?** (scope)

| Action | When | Output |
|--------|------|--------|
| **Fix** | High confidence, localized | Code snippet to apply now |
| **Investigate** | Low confidence, unclear cause | What to check first |
| **Plan** | Systemic (many files, architecture) | Topic for `/code-foundations:plan` |
| **Decide** | Trade-off, business logic | Options for human to choose |

## Decision Flow

```
Is it systemic (many files, architecture change)?
  YES → PLAN (needs /code-foundations:plan)
  NO ↓

Am I confident about the diagnosis AND fix?
  YES → FIX (provide code)
  NO ↓

Is it a trade-off or business decision?
  YES → DECIDE (present options)
  NO  → INVESTIGATE (what to check)
```

## Confidence Anchors

Use these to calibrate when you're "confident":

**High Confidence** (can provide fix):
- Null pointer dereference
- SQL injection via string concat
- Empty catch block
- Missing input validation
- Style issues (trailing newline, formatting)

**Low Confidence** (needs investigation or decision):
- "This business logic seems wrong"
- Race condition possibility
- Performance concerns without profiling
- "This design feels off"
- Anything requiring domain knowledge

## Output Format

### Fix
```markdown
1. 🔴 [CRITICAL] file:line - issue (agent)
   ```lang
   [code to apply]
   ```
```

### Investigate
```markdown
1. 🟡 [IMPORTANT] file:line - issue (agent)
   Confidence: Low
   Check: [what to investigate first]
   **Unknown**: [what context is missing]
```

### Plan
```markdown
1. 🔴 [CRITICAL] Multiple files - issue (agent)
   Scope: Systemic
   → `/code-foundations:plan "[topic]"`
```

### Decide
```markdown
1. 🟡 [IMPORTANT] file:line - issue (agent)
   Options:
   - A: [approach] - [trade-off]
   - B: [approach] - [trade-off]
   **Unknown**: [what would inform this decision]
```

## Epistemic Humility

For anything not in "Fix", state what you don't know:

```markdown
**Unknown**: Is this method called concurrently?
**Unknown**: What's the acceptable latency for this endpoint?
**Unknown**: Is the current behavior intentional?
```

## Workflow

1. **Fix** → Apply now, run tests
2. **Investigate** → Spin off as task
3. **Plan** → Run `/code-foundations:plan`
4. **Decide** → Ask stakeholder
