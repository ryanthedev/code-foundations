# Case Study: Critical Path Review

**Type:** OPTIMIZE
**Skills:** cc-performance-tuning
**Focus:** Measure-first principle - knowing when NOT to optimize

## Why This Case Study Matters

This example shows cc-performance-tuning **correctly deciding NOT to optimize**. The skill identified redundant loops but concluded they weren't worth fixing because the code isn't in the critical path.

---

## The Flow

```
User: "use perf tuning to review this code"

→ cc-performance-tuning: Critical Path Review
→ Is this in the critical path (<4% causing >50% runtime)?
→ NO - I/O-bound, not CPU-bound
→ Check anti-patterns anyway
→ Found 2 warnings, but verdict: not worth fixing
```

---

## Critical Path Assessment

| Factor | Assessment |
|--------|------------|
| Trigger frequency | User-initiated, ~few times/minute |
| Operation type | Window move = RPC to server (network I/O dominates) |
| Hot path? | NO - I/O-bound, not CPU-bound |

**Conclusion:** RPC call is ~1000x more expensive than any local computation.

---

## Anti-Pattern Checklist

| Item | Status | Evidence |
|------|--------|----------|
| Measured before tuning? | N/A | Not a tuning change |
| Redundant loop | WARNING | Two separate loops over AllDisplays |
| Redundant loop | WARNING | Loop to find name when UUID already found |
| Work inside loop | PASS | Only simple arithmetic |
| Expensive operation in loop | PASS | Map lookup is O(1) |

---

## Findings

**WARNING #1:** Two methods both iterate over AllDisplays separately.
- **Impact:** Negligible (1-3 entries, user-triggered)
- **Verdict:** Not worth fixing

**WARNING #2:** Display name could be captured in first loop instead of looping again.
- **Impact:** Negligible
- **Verdict:** Not worth the refactoring complexity

---

## Performance Summary

| Metric | Value |
|--------|-------|
| Added operations per move | ~6 map lookups + 2-3 small loops |
| Typical AllDisplays size | 1-3 entries |
| Dominant cost | RPC to server (~1000x more expensive) |
| Overall impact | < 0.1% of operation time |

---

## Verdict

**PASS - No performance issues requiring action.**

Per McConnell: "If not worth profiling, not worth degrading readability for."

---

## Key Takeaway

The skill found issues but correctly concluded: **readability > micro-optimization for non-hot-path code.** This is the "measure first" principle in action.
