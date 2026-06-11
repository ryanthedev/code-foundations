# Checklists: performance-optimization

Sources: A Philosophy of Software Design (Ch. 20), Code Complete 2nd Ed. (Ch. 25-26)

---

## Expensive Operations Reference

| Operation | Cost | Context |
|-----------|------|---------|
| Network (datacenter) | 10-50 us | Tens of thousands of instructions |
| Network (wide-area) | 10-100 ms | Millions of instructions |
| Disk I/O | 5-10 ms | Millions of instructions |
| Flash storage | 10-100 us | Thousands of instructions |
| Dynamic memory allocation | Significant | malloc/new, freeing, GC overhead |
| Cache miss | Few hundred cycles | Often determines overall performance |
| I/O vs memory | ~1000x difference | Batch I/O, avoid I/O in tight loops |
| Interpreted vs compiled | >100x slower | PHP/Python vs C++ |

---

## Code Tuning Patterns (empirical data — only after profiling confirms <4% hot path)

### Sentinel Value in Search Loop (23-65% faster)
```java
// BEFORE: Compound test every iteration
found = false; i = 0;
while (!found && i < count) {
    if (item[i] == target) found = true;
    i++;
}

// AFTER: Single test per iteration
item[count] = target;  // sentinel
i = 0;
while (item[i] != target) { i++; }
if (i < count) { /* found at position i */ }
```

### Loop Unswitching (19-28% faster)
```java
// BEFORE: Testing invariant condition every iteration
for (i = 0; i < count; i++) {
    if (type == TYPE_A) { processTypeA(item[i]); }
    else { processTypeB(item[i]); }
}

// AFTER: Test once outside loop
if (type == TYPE_A) {
    for (i = 0; i < count; i++) { processTypeA(item[i]); }
} else {
    for (i = 0; i < count; i++) { processTypeB(item[i]); }
}
```

### Strength Reduction (90-99.9% faster)
```java
// BEFORE: Expensive operation
if (Math.sqrt(x) < Math.sqrt(y)) { ... }

// AFTER: Algebraically equivalent (when x,y >= 0)
if (x < y) { ... }
```

### Page Fault Loop Ordering (up to 1000x faster)
```java
// BEFORE: Column-major access causes page faults
for (column = 0; column < MAX_COLUMNS; column++)
    for (row = 0; row < MAX_ROWS; row++)
        table[row][column] = BlankTableElement();

// AFTER: Row-major access, sequential memory
for (row = 0; row < MAX_ROWS; row++)
    for (column = 0; column < MAX_COLUMNS; column++)
        table[row][column] = BlankTableElement();
```

---

## Gate: Measurement First (MANDATORY)

- [ ] M-1: Program is correct and complete before optimizing
- [ ] M-2: Profiling data (timing, call counts, memory usage) captured and on-hand — not just "user said it's slow"
- [ ] M-3: Specific hotspot location identified (not just "it's slow")
- [ ] M-4: Baseline established for before/after comparison
- [ ] M-5: Multiple runs taken to account for variance
- [ ] M-6: Problem dimension identified: throughput, latency, memory, or CPU

---

## Decision Tree Gates (Steps 3-6)

- [ ] DT-1: "Have I considered relaxing requirements?" (Features that don't need to exist)
- [ ] DT-2: "Have I considered modifying program/class design?"
- [ ] DT-3: "Have I considered avoiding OS interactions?" (Batch calls vs call-per-op)
- [ ] DT-4: "Have I considered avoiding I/O in tight loops?"
- [ ] DT-5: "Have I considered a better algorithm/data structure?"
- [ ] DT-6: "Have I considered compiler optimizations?"
- [ ] DT-7: "Have I considered switching hardware?"
- [ ] DT-8: "Am I considering code tuning only as a last resort?"

---

## Fundamental Fixes (APOSD Stage 2)

- [ ] FF-1: "Can I add a cache?"
- [ ] FF-2: "Can I use a different algorithm? (e.g., balanced tree vs list)"
- [ ] FF-3: "Can I bypass layers? (e.g., kernel bypass for networking)"
- [ ] FF-4: "If fundamental fix exists: am I implementing with standard design techniques?"
- [ ] FF-5: "If no fundamental fix: am I proceeding to critical path redesign?"

---

## Critical Path Redesign (APOSD Stage 3)

- [ ] CR-1: Smallest amount of code for the common case identified
- [ ] CR-2: Existing code structure set aside (redesign from scratch, not patch)
- [ ] CR-3: Special cases from current code excluded from the critical path analysis
- [ ] CR-4: Only data needed for critical path included
- [ ] CR-5: Most convenient data structure chosen for the critical path
- [ ] CR-6: "The ideal" defined (simplest and fastest with complete redesign freedom)
- [ ] CR-7: Rest of class designed around these critical paths

---

## Consolidation Techniques

- [ ] CT-1: "Can I encode multiple conditions in single value?"
- [ ] CT-2: "Can I use single test for multiple cases?"
- [ ] CT-3: "Can I combine layers into single method?"
- [ ] CT-4: "Can I merge variables into single structure?"

---

## Code Tuning Procedure

- [ ] TP-1: Working version saved before tuning
- [ ] TP-2: Exactly one change made (multiple changes = unmeasurable cause)
- [ ] TP-3: Effect of this specific change measured
- [ ] TP-4: Changes that didn't produce measurable improvement backed out
- [ ] TP-5: More than one approach tried for each bottleneck (iterated)

---

## Speed and Size Improvements

- [ ] SS-1: "Substitute table lookups for complicated logic?"
- [ ] SS-2: "Jam/fuse loops with same iteration count?"
- [ ] SS-3: "Use integer instead of floating-point where precision allows?"
- [ ] SS-4: "Initialize data at compile time?"
- [ ] SS-5: "Use constants of the correct type (avoid implicit conversions)?"
- [ ] SS-6: "Precompute results instead of recalculating?"
- [ ] SS-7: "Eliminate common subexpressions?"

---

## Speed-Only Improvements

- [ ] SO-1: "Stop testing when answer known (short-circuit, break)?"
- [ ] SO-2: "Order tests by frequency (most common first)?"
- [ ] SO-3: "Use lazy evaluation (defer until needed)?"
- [ ] SO-4: "Unswitch loops with invariant conditionals?"
- [ ] SO-5: "Minimize work inside loops?"
- [ ] SO-6: "Use sentinels in search loops?"
- [ ] SO-7: "Put busiest loop on inside of nested loops?"
- [ ] SO-8: "Reduce strength of operations inside loops?"
- [ ] SO-9: "Minimize array dimensions for critical access?"
- [ ] SO-10: "Cache frequently used values in local variables?"
- [ ] SO-11: "Exploit algebraic identities?"
- [ ] SO-12: "Unroll loops ONLY if measured?"

---

## After Making Changes

- [ ] AM-1: Re-measured — measurable performance difference confirmed
- [ ] AM-2: Changes provide significant speedup (with data) → Keep
- [ ] AM-3: Changes make system simpler AND at least as fast → Keep
- [ ] AM-4: Neither speedup nor simpler → Back out

---

## Red Flags

- [ ] RF-1: "Premature optimization?" Tuning before profiling
- [ ] RF-2: "Optimizing non-bottlenecks?" 80% time in 20% of code
- [ ] RF-3: "Sacrificing clarity for unmeasured gains?" Keep readable unless proven bottleneck
- [ ] RF-4: "I/O in tight loops?" Batch or cache instead
- [ ] RF-5: "Recalculating invariants?" Move outside loop or cache
- [ ] RF-6: "No before/after measurements?" Profile both states
- [ ] RF-7: "Death by thousand cuts?" Many small inefficiencies, no single fix
- [ ] RF-8: "Pass-through methods?" Unnecessary layer crossing overhead
- [ ] RF-9: "Shallow layers?" Multiple layers same abstraction
- [ ] RF-10: "Trading maintainability for <10% gain?" Not worth it
- [ ] RF-11: "Compiler can do it better?" Trust modern compilers for simple transforms

---
