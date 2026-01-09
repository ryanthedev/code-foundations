# Language Notes: cc-performance-tuning

## Critical Warning

**Results vary dramatically by language.** A technique that provides 40% improvement in one language may DEGRADE performance in another. The benchmarks below demonstrate why measurement is mandatory.

## Python

**High-risk techniques (often backfire):**
- Loop unrolling: -27% (worse) vs +34% in C++ [p.623]
- Array precomputation: -20% (worse) vs +92% in Java [p.639]

**Generally effective:**
- Loop unswitching: 28% faster [p.620]
- Caching: 49% faster [p.633]
- Algebraic identities (sqrt elimination): 90% faster [p.634]

**Baseline consideration:** Python runs >100x slower than compiled languages [Table 25-1]. Consider: Is the hot path in Python, or should it be in a compiled extension?

## Java

**Generally effective:**
- Loop unrolling: 43% faster [p.623]
- Sentinel values: 44% faster [p.626]
- Custom log2: 95% faster [p.638]
- Multi-D to 1D arrays: 47% faster [p.630]
- Minimizing loop work: 43% faster [p.625]

**Caution required:**
- Inline routines: -10% (worse) [p.641]

**Note:** Java byte code runs ~1.5x slower than C++ [Table 25-1].

## C++ / Compiled Languages

**Generally effective:**
- Most techniques work as expected
- Compiler optimizations: 40-59% improvement possible [p.596]
- Caching: 74% faster [p.633]
- sqrt elimination: 99.9% faster [p.634]

**Caution required:**
- Array reference minimization: -7% (worse) [p.631]
- Compiler may already optimize what you're trying to optimize (matrix pointer example, p.603)

**Recommendation:** Check compiler output before manual optimization.

## C# / .NET

**Generally effective:**
- Test ordering: 48% faster [p.615]
- Most loop techniques work

**Minimal gains:**
- Common subexpression elimination: 4% [p.640]
- Type-matched constants: <1% [p.638]

**Note:** Results opposite to Java for some techniques despite similar syntax [p.616].

## Visual Basic

**Generally effective:**
- Sentinel values: 65% faster [p.626]
- Integer vs float: 96% faster [p.629]
- Multi-D to 1D arrays: 66% faster [p.630]
- Strength reduction: 49% faster [p.628]

**Caution required:**
- Polynomial strength reduction: -94% (much worse) [p.636]

## PHP

**Generally effective:**
- Loop jamming: 32% faster [p.621]
- Multi-D to 1D arrays: 34% faster [p.630]
- Compile-time initialization: 39% faster [p.637]

**Caution required:**
- Custom system routines: -41% (worse) [p.638]

**Baseline consideration:** PHP runs >100x slower than compiled languages [Table 25-1].

## General Guidance

1. **Always measure** - Results above are from specific benchmark scenarios
2. **Compiler versions matter** - Results can change between compiler versions
3. **Context matters** - Your code patterns may differ from benchmarks
4. **Re-profile after upgrades** - Library/runtime changes invalidate previous measurements
