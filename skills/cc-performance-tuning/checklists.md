# Checklists: cc-performance-tuning

Source: Code Complete 2nd Edition, Chapters 25-26

## Overall Program Performance (p.607)

- [ ] "Have you considered improving performance by changing the program requirements?"
- [ ] "Have you considered improving performance by modifying the program's design?"
- [ ] "Have you considered improving performance by modifying the class design?"
- [ ] "Have you considered improving performance by avoiding operating system interactions?"
- [ ] "Have you considered improving performance by avoiding I/O?"
- [ ] "Have you considered improving performance by using a compiled language instead of an interpreted language?"
- [ ] "Have you considered improving performance by using compiler optimizations?"
- [ ] "Have you considered improving performance by switching to different hardware?"
- [ ] "Have you considered code tuning only as a last resort?"

## Code-Tuning Approach (p.608)

- [ ] "Is your program fully correct before you begin code tuning?"
- [ ] "Have you measured performance bottlenecks before beginning code tuning?"
- [ ] "Have you measured the effect of each code-tuning change?"
- [ ] "Have you backed out the code-tuning changes that didn't produce the intended improvement?"
- [ ] "Have you tried more than one change to improve performance of each bottleneck--that is, iterated?"

## Improve Both Speed and Size (p.642-643)

- [ ] "Substitute table lookups for complicated logic"
- [ ] "Jam loops"
- [ ] "Use integer instead of floating-point variables"
- [ ] "Initialize data at compile time"
- [ ] "Use constants of the correct type"
- [ ] "Precompute results"
- [ ] "Eliminate common subexpressions"
- [ ] "Translate key routines to a low-level language"

## Improve Speed Only (p.643-644)

- [ ] "Stop testing when you know the answer"
- [ ] "Order tests in case statements and if-then-else chains by frequency"
- [ ] "Compare performance of similar logic structures"
- [ ] "Use lazy evaluation"
- [ ] "Unswitch loops that contain if tests"
- [ ] "Unroll loops"
- [ ] "Minimize work performed inside loops"
- [ ] "Use sentinels in search loops"
- [ ] "Put the busiest loop on the inside of nested loops"
- [ ] "Reduce the strength of operations performed inside loops"
- [ ] "Change multiple-dimension arrays to a single dimension"
- [ ] "Minimize array references"
- [ ] "Augment data types with indexes"
- [ ] "Cache frequently used values"
- [ ] "Exploit algebraic identities"
- [ ] "Reduce strength in logical and mathematical expressions"
- [ ] "Be wary of system routines"
- [ ] "Rewrite routines inline"

---
Total items: 40
