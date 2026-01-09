# Evidence: cc-performance-tuning

## Key Points

- [KEY POINT p.588] "Performance is only loosely related to code speed."
- [KEY POINT p.592] "20 percent of a program's routines consume 80 percent of its execution time."
- [KEY POINT p.596] "Optimizing compilers are better at optimizing straightforward code than tricky code."
- [KEY POINT p.588] "You can never be sure about the effect of an optimization until you measure the effect."
- [KEY POINT p.593] "The mere act of making goals explicit improves the likelihood that they'll be achieved."
- [KEY POINT p.609] "The only reliable rule of thumb for code tuning is to measure the effect of each tuning in your environment."
- [KEY POINT p.634] "The first optimization is often not the best. Even after you find a good one, keep looking for one that's better."
- [KEY POINT p.645] "Code tuning is a little like nuclear energy. It's a controversial, emotional topic."

## Empirical Findings

- [HARD DATA: Knuth 1971] "Less than 4% of a program usually accounts for more than 50% of its run time."
  - Context: Study of Fortran programs; established the Pareto distribution for code optimization

- [HARD DATA: Boehm 1987b] "20% of routines consume 80% of execution time."
  - Context: Industry studies confirming Pareto distribution

- [HARD DATA: Boehm 2000b] "TRW system initially required subsecond response, leading to $100 million estimate. Relaxing to 4-second responses 90% of the time reduced cost by $70 million."
  - Context: Requirements analysis can provide 10-100x cost savings vs. optimization

- [HARD DATA p.596] Compiler optimization benchmark: 49-59% improvement with C++ compiler optimizations on insertion sort.
  - Context: Compiler optimization often more effective than manual tuning

- [HARD DATA Table 25-1] Language execution time comparison: PHP and Python run >100x slower than C++/C#/Visual Basic.
  - Context: Java (byte code) approximately 1.5x slower than C++

- [HARD DATA p.603] Array initialization: Unrolled version 63-74% faster than loop version (VB 63%, Java 74%).
  - Context: Fewer lines does NOT mean faster code

- [HARD DATA p.590] Page fault loop ordering: Up to 1000x faster with proper memory access patterns.
  - Context: Column-major vs row-major access on memory-limited systems

- [HARD DATA p.605] "More than half the attempted tunings will produce only a negligible improvement in performance or degrade performance."
  - Context: Author's DES encryption optimization: at least two-thirds of attempts failed

## Technique Benchmarks (Chapter 26)

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

## Anti-Patterns

- [ANTI-PATTERN p.590] Optimizing the Idle Loop
  - Description: Team found half of OS time in small loop, made it 10x faster. No system improvement.
  - Why: They had optimized the idle loop - the time waiting for work.

- [ANTI-PATTERN p.591] Assuming "Fewer Lines = Faster"
  - Description: Condensing 10 lines to 3 lines of code
  - Why: No predictable relationship between line count and execution speed

- [ANTI-PATTERN p.592] Optimizing as You Go
  - Description: Striving to write fastest code while coding each routine
  - Why: Programmers spend 96% of time optimizing code that doesn't need it

- [ANTI-PATTERN p.619] Switched Loop
  - Description: Testing invariant condition inside loop every iteration
  - Why: Wastes 19-28% of loop time testing condition that never changes

## Quotes

> "More computing sins are committed in the name of efficiency (without necessarily achieving it) than for any other single reason--including blind stupidity." --W. A. Wulf

> "We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil." --Donald Knuth

> "Jackson's Rules of Optimization: Rule 1. Don't do it. Rule 2 (for experts only). Don't do it yet--that is, not until you have a perfectly clear and unoptimized solution." --M. A. Jackson
