# Review Example: Picker History Plan

**Type:** REVIEW
**Skills:** code-foundations → cc-quality-practices → cc-routine-and-class-design
**Time:** 1m 49s

## Why This Case Study Matters

This is the most comprehensive example of code-foundations in action because it demonstrates:

1. **Multi-skill chaining** - The dispatcher invokes TWO specialized skills
2. **Deep checklist analysis** - 320 lines of checklists systematically applied
3. **Real architectural issue found** - Stable ID collision risk that would have caused bugs
4. **Quantified output** - Violations and warnings with exact locations
5. **Actionable recommendations** - Specific type changes, renamed methods, enumerated test cases

---

## The Flow

```
User: "please do a code-foundations code review on this plan"

→ code-foundations classifies as REVIEW
→ Invokes cc-quality-practices (CHECKER mode)
→ Reads 320 lines of checklists
→ Invokes cc-routine-and-class-design (CHECKER mode)
→ Produces structured analysis with violations/warnings
```

---

## What the Skills Found

### Critical: Stable ID Collision Risk

The plan's normalization algorithm:
```
lowercase, first 40 chars, alphanumeric + hyphens only
```

**Problem identified:** Two different windows could produce identical stable IDs:
- `com.apple.Safari:github-anthropics-claude-code-repo`
- `com.apple.Safari:github-anthropics-claude-code-docs`

Both normalize to same 40-char prefix → **collision**.

**Fix provided:** Include hash suffix or use full title with safe encoding.

### Missing Edge Cases (Dirty Tests)

The skill identified ZERO dirty tests in the plan:

| Missing Test | Issue |
|--------------|-------|
| Empty history file | What happens on first run? |
| Malformed JSON | Corrupt file handling? |
| Nil tmuxInfo map | Potential panic |
| Empty window title | ID collision risk |

### Naming/Cohesion Issue

```go
func (h *PickerHistory) RecordPick(stableID string)
  // increments frequency
  // AND sets Previous
```

**Problem:** Name suggests frequency recording, but it also mutates `Previous`.

**Fix:** Rename to `RecordSelection` (implies full selection tracking) or split into two methods.

---

## The Structured Output

### Quality Assurance Checklist

| Item | Status | Evidence |
|------|--------|----------|
| Test cases per requirement? | VIOLATION | "Unit test with mock PickerItems" is vague |
| Dirty tests (5:1 ratio)? | VIOLATION | Zero dirty tests specified |
| Boundary tests? | VIOLATION | Not mentioned |
| Multiple error-detection techniques? | WARNING | Only unit tests, no code review step |

### Routine & Class Design Checklist

| Item | Status | Evidence |
|------|--------|----------|
| Parameter count ≤ 7? | PASS | All functions have ≤3 params |
| Routine name describes what it does? | WARNING | RecordPick does more than name implies |
| Functional cohesion? | WARNING | RecordPick does TWO things |
| Implementation details hidden? | PASS | Internal map not exposed |

### Data-Flow Anomaly Check

| Pattern | Location | Issue |
|---------|----------|-------|
| Entered-Used | stableWindowID() | What if tmuxInfo is nil? |
| Defined-Exited | stableWindowID() | Empty title → ID collision risk |
| Entered-Used | sortByHistory() | Previous references window not in current list? |

---

## Summary Produced

| Category | Violations | Warnings |
|----------|------------|----------|
| Quality Assurance | 4 | 3 |
| Routine/Class Design | 0 | 3 |
| Data Flow | 3 anomalies | - |

**Verdict:** Plan needs revision before implementation.

---

## Actionable Recommendations

### Type Design Fix
```go
type PickerHistory struct {
    Previous   string            `json:"previous"`
    Frequency  map[string]int    `json:"frequency"`
    LastPicked map[string]int64  `json:"last_picked"` // Unix timestamp for LRU
}

const MaxHistoryEntries = 100

func (h *PickerHistory) RecordSelection(stableID string) // renamed
func (h *PickerHistory) Validate() error                 // new
func (h *PickerHistory) Prune()                          // LRU eviction
```

### Minimum Test Cases
| # | Test Case | Type |
|---|-----------|------|
| 1 | Tmux window → stable ID format correct | Clean |
| 2 | Non-tmux window → stable ID format correct | Clean |
| 3 | Empty title → graceful handling | Dirty |
| 4 | Nil tmuxInfo map → no panic | Dirty |
| 5 | Malformed JSON file → error returned | Dirty |
| 6 | History file doesn't exist → empty history | Dirty |
| 7 | Two similar titles → no ID collision | Boundary |
| 8 | 100+ entries → oldest evicted | Boundary |

---

## What Could Have Gone Wrong

| Without Review | With Review |
|----------------|-------------|
| ID collisions discovered in production | Collision risk caught in planning |
| Silent failures on corrupt files | Dirty tests specified upfront |
| Method naming causes confusion | Renamed before implementation |
| LRU mentioned but not designed | Type design includes timestamp |

---

## Key Takeaways

1. **Multi-skill chaining** - REVIEW tasks benefit from multiple specialized checklist skills
2. **320 lines of checklists** - Systematic coverage finds issues humans miss
3. **Real bugs caught** - ID collision would have caused actual user-facing issues
4. **Quantified output** - 4 violations, 3 warnings gives clear go/no-go signal
5. **Actionable fixes** - Not just "needs work" but specific code and test cases
