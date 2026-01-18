# Evidence: cc-performance-tuning

## Key Points (Author-Marked)

- [KEY POINT p.588] "Performance is only loosely related to code speed."
- [KEY POINT p.592] "20 percent of a program's routines consume 80 percent of its execution time."
- [KEY POINT p.596] "Optimizing compilers are better at optimizing straightforward code than tricky code."
- [KEY POINT p.588] "You can never be sure about the effect of an optimization until you measure the effect."
- [KEY POINT p.593] "The mere act of making goals explicit improves the likelihood that they'll be achieved."
- [KEY POINT p.593] "Efficiency is often best treated in the context of other issues--achieving high modifiability can provide a better basis for meeting efficiency goals than explicitly setting an efficiency target."
- [KEY POINT p.588] "Experience doesn't help much with optimization either--when machine, language, or compiler changes, all bets are off."
- [KEY POINT p.609] "The only reliable rule of thumb for code tuning is to measure the effect of each tuning in your environment."
- [KEY POINT p.609] "Insisting on measurable improvement is a good way to resist the temptation to optimize prematurely."
- [KEY POINT p.609] "If optimization isn't important enough to profile, it isn't important enough to degrade readability."
- [KEY POINT p.634] "The first optimization is often not the best. Even after you find a good one, keep looking for one that's better."
- [KEY POINT p.645] "Code tuning is a little like nuclear energy. It's a controversial, emotional topic."

## Empirical Evidence

### Foundational Studies

- [HARD DATA: Knuth 1971, p.592] "Less than 4% of a program usually accounts for more than 50% of its run time."
  - Context: Study of Fortran programs; established the Pareto distribution for code optimization

- [HARD DATA: Boehm 1987b, p.592] "20% of routines consume 80% of execution time."
  - Context: Industry studies confirming Pareto distribution

- [HARD DATA: Boehm 2000b, p.590] "TRW system initially required subsecond response, leading to $100 million estimate. Relaxing to 4-second responses 90% of the time reduced cost by $70 million."
  - Context: Requirements analysis can provide 10-100x cost savings vs. optimization

### Optimization Failure Rate

- [HARD DATA p.605] "More than half the attempted tunings will produce only a negligible improvement in performance or degrade performance."
  - Context: Author's DES encryption optimization: at least two-thirds of attempts failed
  - Implication: Plan for iteration; be prepared to back out changes

- [HARD DATA p.605] DES encryption optimization cumulative results:
  - Initial: 21:40 for 18K file
  - Goal: 37 seconds
  - Final: 0:22 (98% improvement from cumulative optimizations)
  - Key insight: No single optimization achieved goal; combination required

### Compiler Optimization Effectiveness

- [HARD DATA p.596] Compiler optimization benchmark: 49-59% improvement with C++ compiler optimizations on insertion sort.
  - Context: Compiler optimization often more effective than manual tuning

- [HARD DATA p.596] "With a good optimizing compiler, code speed can improve 40 percent or more across the board."
  - Context: Many code-tuning techniques produce gains of only 15-30%

### Language Performance Comparisons

- [HARD DATA Table 25-1, p.596] Language execution time comparison: PHP and Python run >100x slower than C++/C#/Visual Basic.
  - Context: Java (byte code) approximately 1.5x slower than C++

### Memory and I/O Performance

- [HARD DATA p.590] Page fault loop ordering: Up to 1000x faster with proper memory access patterns.
  - Context: Column-major vs row-major access on memory-limited systems; factor of 2 with more memory

- [HARD DATA p.590] I/O vs memory access: ~1000x difference (in-memory vs file operations)

- [HARD DATA p.590] System calls impose significant overhead due to context switches and kernel state recovery

### Code Structure Benchmarks

- [HARD DATA p.603] Array initialization: Unrolled version 63-74% faster than loop version (VB 63%, Java 74%).
  - Context: Fewer lines does NOT mean faster code; 10-line unrolled is faster than 3-line loop

### Routine Call Overhead

- [HARD DATA p.639] Modern machines impose virtually no penalty for routine calls:
  - C++: routine call 0.471s vs inline 0.431s (only 8% savings from inlining)
  - Java: routine call 13.1s vs inline 14.4s (-10% worse when inlined)
  - Context: You're as likely to degrade performance by keeping code inline as to optimize it

## Technique Benchmarks (Chapter 26)

### Summary Table

| Technique | Best Case | Worst Case | Source |
|-----------|-----------|------------|--------|
| Loop unswitching | Python 28% faster | VB <1% | p.620 |
| Loop jamming | PHP 32% faster | VB 4% | p.621 |
| Loop unrolling | Java 43% faster | Python -27% (worse) | p.623 |
| Sentinel values | VB 65% faster | C# 23% | p.626 |
| Integer vs float | VB 96% faster | PHP 7% | p.629 |
| 1D vs multi-D array | VB 66% faster | C# 9% | p.630 |
| Caching | C++ 74% faster | Java 45% | p.633 |
| sqrt elimination | C++ 99.9% faster | Python 90% | p.634 |
| Custom log2 | Java 95% faster | PHP -41% (worse) | p.638 |
| Inline routines | C++ 8% faster | Java -10% (worse) | p.641 |

### Logic Technique Benchmarks

- [HARD DATA p.614] Stop testing early with break keyword:
  - C++ 14% savings, Java 29% savings

- [HARD DATA p.615] Ordering tests by frequency (if-then-else reordering):
  - C# 48%, Java 50%, Visual Basic 26% savings

- [HARD DATA p.616] Case vs if-then-else performance varies wildly:
  - C# 1:1 (equivalent), Java 6:1 favoring if-then-else, Visual Basic 1:4 favoring case

- [HARD DATA p.617] Table lookups vs complicated logic:
  - C++ 33% savings (1.5:1), Visual Basic 50% savings (2:1)

### Loop Technique Benchmarks

- [HARD DATA p.620] Loop unswitching savings:
  - C++ 19%, Java 21%, Python 28% savings; Visual Basic <1%

- [HARD DATA p.621] Loop jamming (fusion) savings:
  - C++ 28%, PHP 32%, Visual Basic 4% savings

- [HARD DATA p.623] Loop unrolling (single unroll):
  - C++ 34%, Java 43%, PHP 16% savings; Python -27% (worse)

- [HARD DATA p.623] Loop unrolling (double unroll):
  - C++ 42%, Java 43%, PHP 31% savings; Python -12% (worse)

- [HARD DATA p.625] Minimizing work inside loops:
  - C++ 19%, C# 13%, Java 43% savings

- [HARD DATA p.626] Sentinel values in search loops (integer array):
  - C# 23%, Java 44%, Visual Basic 65% savings

- [HARD DATA p.626] Sentinel values in search loops (float array):
  - C# 24%, Java 33%, Visual Basic 42% savings

- [HARD DATA p.627] Busiest loop on inside:
  - C++ 33%, Java 34%, PHP 12%, Python 4% savings

- [HARD DATA p.628] Strength reduction in loops:
  - C++ 12%, Visual Basic 49% savings

### Data Transformation Benchmarks

- [HARD DATA p.629] Integer vs floating-point:
  - C++ 71% (3.5:1), PHP 7%, Visual Basic 96% (25:1) savings

- [HARD DATA p.630] Single-dimension vs multi-dimension arrays:
  - C++ 11%, C# 9%, Java 47%, PHP 34%, Python 32%, Visual Basic 66% savings

- [HARD DATA p.631] Minimize array references:
  - C++ -7% (worse), C# 7%, Visual Basic 20% savings

- [HARD DATA p.633] Caching frequently used values (hypotenuse):
  - C++ 74% (4:1), Java 45% (2:1), Python 49% (2:1), Visual Basic 47% (2:1) savings

### Expression Technique Benchmarks

- [HARD DATA p.634] Algebraic identity (sqrt comparison elimination):
  - C++ 99.9% (750:1), Visual Basic 95% (20:1), Python 90% (10:1) savings

- [HARD DATA p.636] Polynomial evaluation optimization:
  - Python 20%, Visual Basic 97% (40:1) savings
  - Further reduction: Python 3%, Visual Basic -94% (worse)

- [HARD DATA p.637] Compile-time initialization (log(2) precomputation):
  - C++ 38%, Java 28%, PHP 39% savings

- [HARD DATA p.638] Custom integer log2 vs system log:
  - C++ 93% (15:1), Java 95% (20:1) savings; PHP -41% (worse)

- [HARD DATA p.638] Type-matched constants:
  - C++ 100%, C# <1%, Java 33%, Visual Basic 100%, PHP 3% savings

- [HARD DATA p.640] Common subexpression elimination:
  - C# 4%, Python -1% (negligible/worse) savings

- [HARD DATA p.639] Precomputation results:
  - Loan calculation table lookup: Java 92% (10:1), Python -20% (worse)
  - Precompute outside loop: Java 97% (30:1), Python 66% (3:1)

### Low-Level Language Recoding

- [HARD DATA p.642] Recoding in assembler:
  - Delphi to assembler: 41% savings
  - C++ to assembler: 29% savings

## Anti-Patterns (CODING HORROR)

### Chapter 25 Anti-Patterns

- [ANTI-PATTERN p.590] Optimizing the Idle Loop
  - Description: Team found half of OS time in small loop, made it 10x faster. No system improvement.
  - Why: They had optimized the idle loop - the time waiting for work.
  - Lesson: Measure to find ACTUAL bottlenecks, not apparent ones.

- [ANTI-PATTERN p.591] Assuming "Fewer Lines = Faster"
  - Description: Condensing 10 lines to 3 lines of code
  - Why: No predictable relationship between line count and execution speed
  - Counter-example: 10-line unrolled array initialization is 60-74% faster than 3-line loop version.

- [ANTI-PATTERN p.592] Optimizing as You Go
  - Description: Striving to write fastest code while coding each routine
  - Why: Programmers spend 96% of time optimizing code that doesn't need it
  - Lesson: Almost impossible to identify bottlenecks before program is working completely.

- [ANTI-PATTERN p.591] Prioritizing Speed Over Correctness
  - Description: Treating a fast program as just as important as a correct one
  - Quote: "Yes, but your program doesn't work. If mine doesn't have to work, I can make it run instantly."
  - Lesson: Correct first, fast second. Always.

- [ANTI-PATTERN p.590] Matrix Sum Pointer "Optimization" That Failed
  - Description: Author attempted to optimize matrix summation by converting array indexing to pointer arithmetic, expecting to save 10,000 multiplications.
  - Result: NO improvement--compiler was already doing this optimization.
  - Lesson: Compilers often already optimize what you think you're optimizing; measure first.

- [ANTI-PATTERN p.602] Unindexed Database Table
  - Description: Operation much slower than similar operations; mythology grew to explain it.
  - Root cause: Database table wasn't indexed. Adding index improved performance 30x.
  - Lesson: Sometimes "performance problems" are just bugs/missing best practices.

- [ANTI-PATTERN p.602] AppTime/BaseTime System Call Overhead
  - Description: Program instantiated tens of thousands of AppTime objects. BaseTime constructor called system time (unnecessary for application).
  - Result: Overriding constructor to initialize to 0 instead of system time gave as much improvement as all other changes combined.
  - Lesson: Hidden system calls can dominate performance.

### Chapter 26 Anti-Patterns

- [ANTI-PATTERN p.619] Switched Loop
  - Description: Testing invariant condition inside loop every iteration
  - Why: Wastes 19-28% of loop time testing condition that never changes
  - Fix: Move conditional outside loop; use unswitching technique.

- [ANTI-PATTERN p.529] Floating-Point Loop Index
  - Description: Using floating-point variables as loop indexes when integers would work
  - Why: Can cause 71-96% performance penalty depending on language
  - Fix: Convert to integer index; use integer scaling if needed.

- [ANTI-PATTERN p.623] Unrolled Loop Complexity
  - Description: Five lines of straightforward code expanding to nine lines of tricky code
  - Why: Quality is poor except for the speed gain
  - Warning: Off-by-one errors in cleanup code after loop; error-prone and unmaintainable.
  - Note: Python showed -27% degradation with unrolling--can make things WORSE.

- [ANTI-PATTERN p.544] Complicated While Condition
  - Example: `while ( ( x = ( x >> 1 ) ) != 0 )`
  - Why: Particularly hard to read
  - Lesson: Avoid unless you have a good reason backed by measurement.

- [ANTI-PATTERN p.615] Ordering Tests by ASCII Sort
  - Description: Ordering case statements by ASCII sort order instead of frequency
  - Why: Can cost 26-50% performance
  - Fix: Arrange tests so fastest and most likely to be true is performed first.

- [ANTI-PATTERN p.610] Applying Optimization Without Profiling
  - Description: Applying optimizations based on intuition rather than measurement
  - Why: You don't know if this is actually a hot spot
  - Lesson: STOP; profile first to identify actual hot spots.

- [ANTI-PATTERN p.610] Assuming Past Results Apply
  - Description: Assuming an optimization that worked in one environment will work in another
  - Why: Results vary by language, compiler, version, and settings
  - Example: Python showed -27% for loop unrolling while C++ showed +34%.

## Qualifiers and Scope

### What These Techniques Can and Cannot Do

- Algorithm changes typically provide 10-100x improvement; micro-optimization only 1.1-2x
- Code tuning is appropriate ONLY after design/algorithm optimization exhausted
- Results vary dramatically across languages, compilers, and versions
- Interpreted languages (Python, PHP) often respond differently than compiled languages

### Conditions That Invalidate Optimizations

- Changing compiler brand or version
- Changing library version
- Changing compiler settings/flags
- Changing target hardware/processor
- Memory constraints affecting cache behavior

### When NOT to Apply Code Tuning

- Before program is correct and complete
- Before measuring to find actual bottleneck
- When requirements can be relaxed instead
- When design/architecture change can solve it
- When algorithm/data structure change can solve it
- When compiler optimization flags haven't been tried
- When code is not in the 4% that causes 50% of runtime

## Quotes

> "More computing sins are committed in the name of efficiency (without necessarily achieving it) than for any other single reason--including blind stupidity." --W. A. Wulf

> "We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil." --Donald Knuth

> "Jackson's Rules of Optimization: Rule 1. Don't do it. Rule 2 (for experts only). Don't do it yet--that is, not until you have a perfectly clear and unoptimized solution." --M. A. Jackson

> "No programmer has ever been able to predict or analyze where performance bottlenecks are without data. No matter where you think it's going, you will be surprised to discover that it is going somewhere else." --Joseph M. Newcomer

> "The best is the enemy of the good." --ALGOL designers' advice

## Cross-References

### Within Code Complete

- [XREF: Section 5.3] "Design Building Blocks: Heuristics" - Code tunings are heuristics, not guaranteed improvements
- [XREF: Section 25.2] "The Pareto Principle" - About 5% of a program accounts for 50% of running time
- [XREF: Chapter 18] "Table-Driven Methods" - Alternative to complicated logic chains
- [XREF: Chapter 24] "Refactoring" - Contrasts with code tuning (improves structure vs degrades it)
- [XREF: Chapter 25] "Code-Tuning Strategies" - Precedes techniques; covers when/whether to optimize
- [XREF: Chapter 26] "Code-Tuning Techniques" - Specific implementation techniques

### Related Skills

- `aposd-optimizing-critical-paths` - APOSD approach emphasizing measure-first philosophy
- `cc-defensive-programming` - Balance robustness with performance
- `cc-code-layout-and-style` - Readability tradeoffs in optimized code
- `cc-quality-practices` - Testing requirements for optimized code

### Additional Resources

- **Writing Efficient Programs** (Bentley, 1982) - Expert treatment of code tuning, trades time for space and vice versa
- **Programming Pearls, 2d ed.** (Bentley, 2000) - Appendix 4 summarizes code-tuning rules
- **Inner Loops** (Booth, 1997) - Fast 32-bit software development
- **Software Optimization Cookbook** (Gerber, 2002) - Intel Architecture specific
- **Java Performance Tuning** (Shirazi, 2000)
- **Java Platform Performance** (Wilson & Kesselman, 2000)
