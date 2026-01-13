# Refactor Example: Border Window Cleanup

**Type:** REFACTOR
**Skills:** cc-refactoring-guidance → cc-control-flow-quality (CHECKER) → cc-routine-and-class-design (CHECKER)
**Focus:** Post-refactoring quality gates

## Why This Case Study Matters

This example shows the **CHECKER gates** that run after refactoring to verify code quality wasn't degraded. Key demonstrations:

1. **Two skills as quality gates** - Control flow + routine design checks
2. **McCabe complexity analysis** - Quantified complexity with thresholds
3. **Pre-existing vs new issues** - Checkers distinguish what you changed from what was already there
4. **Cohesion classification** - Functional vs Temporal cohesion types

---

## The Flow

```
[After refactoring work complete]

→ cc-control-flow-quality (CHECKER mode)
  → Analyzes nesting depth and McCabe complexity
  → Flags pre-existing issues separately from new code

→ cc-routine-and-class-design (CHECKER mode)
  → LSP test, parameter counts, naming, cohesion
  → Minimum viable compliance check
```

---

## Control Flow Analysis

| File | Function | Max Nesting | McCabe | Status |
|------|----------|-------------|--------|--------|
| BorderWindow.swift | updateStyle | 1 (guard clauses) | 6 | ✓ Clean |
| SimpleBorderManager.swift | debugBordersImpl | 2 | 4 | ✓ Clean |
| SimpleBorderManager.swift | setCellAssignmentsImpl | 3 | ~14 | ⚠️ Pre-existing |

**Key insight:** The `setCellAssignmentsImpl` has complexity >10, but the checker notes this is **pre-existing structure** - the refactoring only added a dictionary lookup without adding control flow.

---

## Routine & Class Design Check

### Minimum Viable Compliance (7 checks)

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | LSP test for inheritance | ✓ PASS | No new inheritance introduced |
| 2 | Inheritance depth < 3 | ✓ PASS | No inheritance changes |
| 3 | No empty overrides | ✓ PASS | No overrides in changes |
| 4 | Parameter count ≤ 7 | ✓ PASS | Max 4 params (setCellAssignments) |
| 5 | Routine names describe function | ✓ PASS | debugBorders, updateStyle |
| 6 | Consistent abstraction | ✓ PASS | All routines operate at single level |
| 7 | Implementation hidden | ✓ PASS | SkyLight details in BorderWindow |

### Cohesion Classification

| Routine | Type | Status |
|---------|------|--------|
| updateStyle | Functional | ✓ ACCEPT - single operation: update border style |
| debugBorders | Functional | ✓ ACCEPT - single operation: dispatch to impl |
| debugBordersImpl | Temporal | ✓ ACCEPT - orchestrates color cycling |

---

## What the Refactoring Changed

**Preserved (working fixes):**
1. CGContextFlush fix - `drawContext.flush()` before `SLSFlushWindowContentRegion`
2. stackMode infrastructure - CLI sends cellStackModes for tabbed detection

**Cleaned up:**
1. Removed debug logging
2. Renamed command: `debug-flash` → `debug borders`
3. Renamed methods: `debugFlashBorder` → `debugBorders`

---

## CHECKER Gate Summary

| Gate | Result |
|------|--------|
| cc-control-flow-quality | PASS (max nesting 2, McCabe < 10 for new code) |
| cc-routine-and-class-design | PASS (functional cohesion, ≤7 params, good naming) |

---

## What Could Have Gone Wrong

| Without CHECKER Gates | With CHECKER Gates |
|-----------------------|-------------------|
| Refactoring increases complexity unnoticed | McCabe complexity tracked |
| New code inherits bad patterns | LSP and inheritance depth checked |
| Naming degrades during cleanup | Naming check enforced |
| Pre-existing issues blamed on refactoring | Pre-existing clearly distinguished |

---

## Key Takeaways

1. **CHECKER gates after refactoring** - Verify you didn't degrade quality
2. **McCabe complexity** - Quantified threshold (< 10 for new code)
3. **Pre-existing vs new** - Checkers don't blame you for existing issues
4. **Cohesion types** - Functional (ideal) vs Temporal (acceptable for orchestration)
5. **7-point compliance check** - Systematic coverage of design principles
