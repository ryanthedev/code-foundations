# Assessment Framework

Multi-dimensional assessment for code review findings. Replaces the arbitrary "Effort" scale with explicit, measurable dimensions grounded in research on LLM confidence calibration.

## Why Not Just "Effort"?

Research shows:
- LLMs are systematically overconfident when self-assessing (arXiv 2506.00072)
- High performance impedes accurate difficulty estimation (arXiv 2512.18880)
- Single-dimension scales conflate multiple concerns (scope, risk, confidence, verification)
- Post-hoc calibration is necessary for reliability

## Four Dimensions

### 1. Scope (What changes are needed)

| Level | Icon | Definition | Signals |
|-------|------|------------|---------|
| Localized | `[S:L]` | Single location, <10 lines | One file, one function |
| Bounded | `[S:B]` | Multiple locations, <50 lines | 2-5 files, clear boundaries |
| Systemic | `[S:S]` | Cross-cutting, architecture-level | Many files, interface changes |

### 2. Risk (What could go wrong)

| Level | Icon | Definition | Signals |
|-------|------|------------|---------|
| Low | `[R:L]` | Isolated impact, easily reversible | No state changes, no external calls |
| Medium | `[R:M]` | Affects related components | State mutations, DB changes |
| High | `[R:H]` | Security, data loss, cascading failure | Auth, encryption, money, user data |

### 3. Confidence (How certain is the diagnosis)

| Level | Icon | Definition | Anchor Examples |
|-------|------|------------|-----------------|
| High | `[C:H]` | Pattern well-known, seen many times | "This is a null pointer dereference" |
| Medium | `[C:M]` | Reasonable inference, some uncertainty | "This loop might not terminate" |
| Low | `[C:L]` | Speculative, needs human verification | "This business logic seems wrong" |

**Epistemic Humility**: Always state what you DON'T know.

### 4. Verification (What's needed to validate the fix)

| Level | Icon | Definition | Actions |
|-------|------|------------|---------|
| Compile | `[V:C]` | Type-check/build is sufficient | Syntax, type errors |
| Test | `[V:T]` | Existing tests should catch regressions | Logic changes with test coverage |
| Review | `[V:R]` | Human review mandatory | Security, new patterns, low confidence |

## Output Format

### Compact Form (for inline use)

```
[S:L R:H C:H V:T]
```

Reads as: Localized scope, High risk, High confidence, needs Testing.

### Expanded Form (for critical issues)

```markdown
| Dimension | Level | Rationale |
|-----------|-------|-----------|
| Scope | [S:L] Localized | Single function, 3 lines |
| Risk | [R:H] High | OOM possible, DoS vector |
| Confidence | [C:H] High | Standard pattern, well-documented |
| Verification | [V:T] Test | Need load test to verify limit |

**Unknown**: What's the expected max input size in production?
```

## Quick Reference Matrix

Common combinations and what they mean:

| Pattern | Meaning | Action |
|---------|---------|--------|
| `[S:L R:L C:H V:C]` | Trivial fix | Auto-merge candidate |
| `[S:L R:H C:H V:T]` | Small but critical | Fix immediately, add test |
| `[S:B R:M C:M V:T]` | Standard refactor | Normal review process |
| `[S:S R:H C:L V:R]` | Dangerous uncertainty | Block merge, get expert |
| `[S:* R:* C:L V:R]` | Low confidence anything | Human review required |

## Calibration Anchors

Use these reference cases to calibrate confidence:

### High Confidence (`[C:H]`)
- Null pointer dereference (obvious pattern)
- SQL injection via string concat (well-documented)
- Missing null check before `.` operator
- Empty catch block swallowing exceptions
- Missing trailing newline

### Medium Confidence (`[C:M]`)
- Loop termination conditions (requires reasoning)
- Race condition possibility (requires context)
- Performance issue in hot path (requires measurement)
- Duplicate key exception possibility (depends on data)

### Low Confidence (`[C:L]`)
- Business logic correctness (requires domain knowledge)
- Algorithm choice appropriateness (requires benchmarks)
- Error message quality (requires user context)
- "This design seems wrong" (subjective)

## Migration from Old Format

| Old | New |
|-----|-----|
| `Effort: 🟢 Quick` | `[S:L R:L C:H V:C]` |
| `Effort: 🟡 Medium` | `[S:B R:M C:M V:T]` |
| `Effort: 🔴 Large` | `[S:S R:* C:* V:R]` |

The new format is more precise because:
- A "Quick" fix can still be high-risk (security patch)
- A "Large" effort can be low-risk (big refactor, no behavior change)
- Confidence is independent of effort
- Verification needs vary by risk, not effort

## Agent Integration

Each reviewer agent should:

1. **Assess all four dimensions** for each finding
2. **State unknowns explicitly** - what would change the assessment?
3. **Use compact form** for suggestions, expanded for critical
4. **Default to lower confidence** when uncertain

## Aggregation

When aggregating across agents, use worst-case for Risk and Verification:

```
defensive: [S:L R:H C:H V:T]
quality:   [S:L R:L C:H V:C]
─────────────────────────────
combined:  [S:L R:H C:H V:T]
```

Risk:H wins over Risk:L. Verify:T wins over Verify:C.
