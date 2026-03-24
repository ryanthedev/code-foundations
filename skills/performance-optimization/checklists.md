# Checklists: performance-optimization

Sources: A Philosophy of Software Design (Ch. 20), Code Complete 2nd Ed. (Ch. 25-26)

---

## Gate: Measurement First (MANDATORY)

- [ ] M-1: "Is the program correct and complete before optimizing?"
- [ ] M-2: "Did I MEASURE existing system behavior (not just 'user said it's slow')?"
- [ ] M-3: "Did I IDENTIFY where the system spends most time (specific locations)?"
- [ ] M-4: "Did I ESTABLISH a baseline for comparison?"
- [ ] M-5: "Do I have actual profiling data (timing, call counts, memory usage)?"
- [ ] M-6: "Did I run multiple times to account for variance?"
- [ ] M-7: "Did I identify WHICH dimension is the problem (throughput, latency, memory, CPU)?"

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

- [ ] CR-1: "What is the smallest amount of code for the common case?"
- [ ] CR-2: "Did I disregard existing code structure entirely?"
- [ ] CR-3: "Did I ignore special cases in current code?"
- [ ] CR-4: "Did I consider only data needed for critical path?"
- [ ] CR-5: "Did I choose the most convenient data structure?"
- [ ] CR-6: "Did I define 'the ideal' (simplest and fastest with complete redesign freedom)?"
- [ ] CR-7: "Did I design the rest of the class around these critical paths?"

---

## Consolidation Techniques

- [ ] CT-1: "Can I encode multiple conditions in single value?"
- [ ] CT-2: "Can I use single test for multiple cases?"
- [ ] CT-3: "Can I combine layers into single method?"
- [ ] CT-4: "Can I merge variables into single structure?"

---

## Code Tuning Procedure

- [ ] TP-1: "Did I save a working version before tuning?"
- [ ] TP-2: "Am I making only ONE change at a time?"
- [ ] TP-3: "Did I measure the effect of this specific change?"
- [ ] TP-4: "Did I back out changes that didn't produce measurable improvement?"
- [ ] TP-5: "Did I try more than one approach for each bottleneck (iterated)?"

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

- [ ] AM-1: "Did I RE-MEASURE to verify measurable performance difference?"
- [ ] AM-2: "Did changes provide significant speedup (with data)?" -> Keep
- [ ] AM-3: "Did changes make system simpler AND at least as fast?" -> Keep
- [ ] AM-4: "Neither speedup nor simpler?" -> BACK THEM OUT

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

Total items: 67
