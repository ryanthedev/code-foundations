# Checklists: cc-performance-tuning

Source: Code Complete 2nd Edition, Chapters 25-26

---

## Overall Program Performance (p.607)

- [ ] OP-1: "Have you considered improving performance by changing the program requirements?" → Red flag: Optimizing features that don't need to exist
- [ ] OP-2: "Have you considered improving performance by modifying the program's design?"
- [ ] OP-3: "Have you considered improving performance by modifying the class design?"
- [ ] OP-4: "Have you considered improving performance by avoiding operating system interactions?" (Good: Batch calls, Bad: Call per operation)
- [ ] OP-5: "Have you considered improving performance by avoiding I/O?" → Red flag: I/O in tight loops
- [ ] OP-6: "Have you considered improving performance by using a compiled language instead of an interpreted language?"
- [ ] OP-7: "Have you considered improving performance by using compiler optimizations?"
- [ ] OP-8: "Have you considered improving performance by switching to different hardware?"
- [ ] OP-9: "Have you considered code tuning only as a last resort?" → Red flag: Micro-optimizing before measuring

---

## Code-Tuning Approach (p.608)

- [ ] CT-1: "Is your program fully correct before you begin code tuning?" → Red flag: Optimizing broken code
- [ ] CT-2: "Have you measured performance bottlenecks before beginning code tuning?" → Red flag: Guessing at bottlenecks
- [ ] CT-3: "Have you measured the effect of each code-tuning change?" (Good: Profile before/after, Bad: Assume improvement)
- [ ] CT-4: "Have you backed out the code-tuning changes that didn't produce the intended improvement?"
- [ ] CT-5: "Have you tried more than one change to improve performance of each bottleneck--that is, iterated?"

---

## Improve Both Speed and Size (p.642-643)

- [ ] SS-1: "Substitute table lookups for complicated logic" (Good: Array lookup, Bad: Nested if-else)
- [ ] SS-2: "Jam loops" (combine loop bodies with same iteration count)
- [ ] SS-3: "Use integer instead of floating-point variables" (where precision allows)
- [ ] SS-4: "Initialize data at compile time" (Good: const arrays, Bad: runtime initialization)
- [ ] SS-5: "Use constants of the correct type" (avoid implicit conversions)
- [ ] SS-6: "Precompute results" → Red flag: Recalculating same values repeatedly
- [ ] SS-7: "Eliminate common subexpressions"
- [ ] SS-8: "Translate key routines to a low-level language" (only for verified bottlenecks)

---

## Improve Speed Only (p.643-644)

- [ ] SO-1: "Stop testing when you know the answer" (short-circuit evaluation)
- [ ] SO-2: "Order tests in case statements and if-then-else chains by frequency" (Good: Most common first, Bad: Alphabetical)
- [ ] SO-3: "Compare performance of similar logic structures"
- [ ] SO-4: "Use lazy evaluation" (defer computation until needed)
- [ ] SO-5: "Unswitch loops that contain if tests" (move invariant conditionals outside)
- [ ] SO-6: "Unroll loops" (reduce overhead for small fixed iterations)
- [ ] SO-7: "Minimize work performed inside loops" → Red flag: Invariant calculations in loop body
- [ ] SO-8: "Use sentinels in search loops" (eliminate boundary checks)
- [ ] SO-9: "Put the busiest loop on the inside of nested loops"
- [ ] SO-10: "Reduce the strength of operations performed inside loops" (Good: addition, Bad: multiplication)
- [ ] SO-11: "Change multiple-dimension arrays to a single dimension" (for performance-critical access)
- [ ] SO-12: "Minimize array references" (cache in local variables)
- [ ] SO-13: "Augment data types with indexes" (Good: Index structures, Bad: Linear search)
- [ ] SO-14: "Cache frequently used values" → Red flag: Recomputing expensive operations
- [ ] SO-15: "Exploit algebraic identities" (e.g., x * 2 → x << 1)
- [ ] SO-16: "Reduce strength in logical and mathematical expressions"
- [ ] SO-17: "Be wary of system routines" (some are slow; measure if critical)
- [ ] SO-18: "Rewrite routines inline" (only for small, frequently called functions)

---

## Red Flags

- [ ] RF-1: "Premature optimization?" - Tuning before profiling → Measure first, optimize second
- [ ] RF-2: "Optimizing non-bottlenecks?" - 80% time spent in 20% of code → Profile to find the 20%
- [ ] RF-3: "Sacrificing clarity for unmeasured gains?" - Obscure code without data → Keep readable unless proven bottleneck
- [ ] RF-4: "I/O in tight loops?" - File/network operations repeated → Batch or cache
- [ ] RF-5: "Recalculating invariants?" - Same computation every iteration → Move outside loop or cache
- [ ] RF-6: "No before/after measurements?" - Can't verify improvement → Profile both states
- [ ] RF-7: "Optimizing algorithm instead of data structure?" - O(n²) in fast language vs O(n log n) → Fix algorithm first
- [ ] RF-8: "Trading maintainability for < 10% gain?" - Complex optimization for minor speedup → Not worth it
- [ ] RF-9: "Guessing at performance?" - Assumptions about what's slow → Profiler reveals truth
- [ ] RF-10: "Compiler can do it better?" - Manual optimizations compiler handles → Trust modern compilers for simple transforms

---

Total items: 50
