# Evidence: cc-data-organization

## Evidence Quality Guide

Evidence varies in strength. Use this guide to calibrate confidence in recommendations.

| Indicator | Meaning | Example Claims |
|-----------|---------|----------------|
| **STRONG** | Replicated studies, industry consensus, demonstrable failure modes | Float equality fails; currency rounding errors; buffer overflows from pointers |
| **MODERATE** | Single study, expert consensus, logical derivation from strong evidence | Name length 10-16 chars [Gorla 1990]; span/live time metrics |
| **WEAK** | Author opinion, single anecdote, convention without empirical backing | Reserve 0 for invalid enum; memory parachute; boolean parameter documentation |

### Applying Evidence Quality

- **STRONG evidence items:** Treat as non-negotiable. Violations are latent defects.
- **MODERATE evidence items:** Follow as defaults. Exceptions should be documented and justified.
- **WEAK evidence items:** Use professional judgment. Consider language/context. These are reasonable heuristics, not proven rules.

## Quantitative Measures

### Span and Live Time (p.245-246)

| Metric | Definition | Goal |
|--------|------------|------|
| **Span** | Lines between consecutive references to same variable | Minimize |
| **Live Time** | Total statements from first to last reference | Minimize |

**Why it matters:** Code between variable references is a "window of vulnerability" where modifications can introduce bugs.

**Example comparison:**
- Bad: Average live time ~54 (declarations at top, use scattered)
- Good: Average live time ~7 (declare/initialize at point of use)

**Actions:**
- Declare variables close to first use
- Group related statements together
- If variable groupings suggest natural boundaries, consider splitting routine

## Key Points

- [KEY POINT p.293] "Top programmers fix their code to eliminate all compiler warnings."
- [KEY POINT p.295] "Many fractional decimal numbers can't be represented accurately using binary."
- [KEY POINT p.310] "All problems with arrays are caused by the fact that array elements can be accessed randomly."
- [KEY POINT p.311] "Programmer-defined data types are one of the most powerful capabilities a language can give you to clarify your understanding of a program."
- [KEY POINT p.263] "The most important naming consideration: name fully and accurately describes the entity."
- [KEY POINT p.323] "Pointer usage is one of the most error-prone areas of modern programming."
- [KEY POINT p.335] "Most experienced programmers have concluded that using global data is riskier than using local data."
- [KEY POINT p.339] "Anything you can do with global data, you can do better with access routines."

## Empirical Findings

- [HARD DATA: Glass 1991] **MODERATE** "The use of named constants has been shown to greatly aid program maintenance."
  - Context: Centralizing control over things that might change reduces maintenance efforts
  - Evidence quality: Expert consensus, logical derivation

- [HARD DATA: Mills and Linger 1986] **MODERATE** "Designs using sequential structures resulted in fewer variables, fewer variable references, relatively efficient and highly reliable software."
  - Context: Small experiment comparing random vs sequential data access patterns
  - Evidence quality: Single study, limited sample

- [HARD DATA: Gorla, Benander, and Benander 1990] **MODERATE** "Debugging effort minimized when variable names averaged 10-16 characters."
  - Context: Programs with names averaging 8-20 characters were almost as easy to debug
  - Evidence quality: Single study, use as heuristic not rule

- [HARD DATA: Card, Church, and Agresti 1986] **MODERATE** "Unreferenced variables correlated with higher fault rates."
  - Evidence quality: Single study, correlation not causation

- [HARD DATA: Howard and LeBlanc 2003] **STRONG** "Many common security problems, especially buffer overruns, can be traced back to erroneous use of pointers."
  - Evidence quality: Replicated industry-wide, demonstrable exploits

- [HARD DATA: Weinberg 1983] **STRONG** "Mariner 1 space probe lost due to transcription error (overbar vs hyphen)."
  - Context: Hard-to-distinguish characters in variable names/code
  - Evidence quality: Documented incident with verified cause

### Claims Without Empirical Backing (WEAK)

The following recommendations from Code Complete lack cited empirical support. They represent reasonable author opinion but should not be treated as proven:

| Claim | Why Still Useful | When to Override |
|-------|-----------------|------------------|
| "Reserve enum 0 for invalid" | Catches uninitialized C-style enums | TypeScript string enums, Rust/Kotlin with exhaustive matching |
| "Allocate memory parachute" | Graceful degradation pattern | Languages with managed memory/GC |
| "Document boolean parameters" | Improves call-site readability | When using named arguments or builder pattern |
| "Names 10-16 chars optimal" | Gorla study is limited; use as guideline | Context-dependent; short names fine for obvious locals |

## Anti-Patterns

*All anti-patterns are **STRONG** evidence - they represent demonstrable failure modes.*

- [CODING HORROR p.302] **STRONG** Complicated Boolean Test
  - Description: Multi-line conditional without named boolean variables
  - Why it's wrong: Readers skip over it; error-prone; hard to modify

- [CODING HORROR p.304] **MODERATE** Boolean Literals as Parameters
  - Description: `RetrievePayrollData(data, true, false, false, true)`
  - Why it's wrong: Incomprehensible even to author after one week
  - Note: Named arguments or builder patterns in modern languages may mitigate

- [CODING HORROR p.295] **STRONG** Float Equality Comparison
  - Description: `if (nominal == sum)` where sum = 0.1 added 10 times
  - Why it's wrong: Sum equals 0.9999999999999999, not 1.0
  - Evidence: IEEE 754 specification guarantees this behavior

- [CODING HORROR p.321] **MODERATE** Swapping Unstructured Data
  - Description: 18+ lines to swap two groups of related variables
  - Why it's wrong: With structures, same operation is 3 lines

- [CODING HORROR p.293] **STRONG** Integer Overflow in Intermediate Results
  - Description: `1000000 * 1000000 / 1000000` expects 1000000, gets -727
  - Why it's wrong: Intermediate result (1,000,000,000,000) overflows 32-bit int before division
  - Fix: Use 64-bit types or reorder operations
  - Evidence: Deterministic, reproducible on all platforms

- [CODING HORROR p.336] **STRONG** Aliasing Problem with Global Data
  - Description: Global variable passed as parameter to routine that also accesses it as global
  - Example: `WriteGlobal(globalVar)` where routine uses both `inputVar` and `globalVar`
  - Why it's wrong: Same variable accessed by two names; `inputVar = 0` then `globalVar = inputVar + 5` makes inputVar equal 5, not 0
  - Fix: Never pass global as parameter to routine that also uses it as global
  - Evidence: Compiler cannot detect; guaranteed silent failure
