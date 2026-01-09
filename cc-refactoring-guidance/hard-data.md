# Evidence: cc-refactoring-guidance

## Key Points

- [KEY POINT p.564] "Evolution should improve the internal quality of the program."
- [KEY POINT p.565] "A change made to the internal structure of the software to make it easier to understand and cheaper to modify without changing its observable behavior." (Fowler 1999)
- [KEY POINT p.579] "A big refactoring is a recipe for disaster." - Kent Beck

## Empirical Findings

- [HARD DATA: Weinberg 1983] "Error rate peaks for changes of 1-5 lines, then decreases for larger changes."
  - Context: Analysis of error rates by change size; counterintuitive finding that small changes have highest error rate

- [HARD DATA: Freedman and Weinberg 1982] "One organization introduced reviews for one-line changes: error rate went from 55 percent before reviews to 2 percent afterward."
  - Context: Demonstrates power of code review even for trivial changes

- [HARD DATA: Yourdon 1986b] "Programmers typically have more than a 50 percent chance of making an error on their first attempt to make a change."
  - Context: First-pass correctness data; supports need for verification regardless of change size

## Expert Quotes

- "All successful software gets changed." - Fred Brooks (p.563)
- "Copy and paste is a design error." - David Parnas (p.565)
- "Don't document bad code—rewrite it." - Kernighan and Plauger 1978 (p.568)

## Anti-Patterns

- [ANTI-PATTERN p.566] Setup/Takedown Code Smell
  - Description: Code requiring extensive setup before routine call or takedown after
  - Why it's wrong: Indicates the interface doesn't properly abstract its responsibilities

- [ANTI-PATTERN p.567] Tramp Data
  - Description: Data passed to one routine just so that routine can pass it to another routine
  - Why it's wrong: Increases coupling, makes code harder to understand and maintain
