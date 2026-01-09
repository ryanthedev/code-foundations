# Evidence: cc-control-flow-quality

## Key Points

- [KEY POINT p.355] "Write the nominal path through the code first; then write the unusual cases"
- [KEY POINT p.373] "Minimize factors affecting loop. Simplify! Treat inside as routine - keep control outside."
- [KEY POINT p.389] "In modern languages, you can easily replace nine out of ten gotos"
- [KEY POINT p.411] "Table-driven code is simpler than complicated logic, easier to modify, and more efficient"
- [KEY POINT p.423] "The fact that a design uses inheritance and polymorphism doesn't make it a good design"
- [KEY POINT p.431] "Making boolean expressions simple and readable contributes substantially to the quality of your code"
- [KEY POINT p.440] "Organize numeric tests so that they follow the points on a number line" (number-line ordering)
- [KEY POINT p.433] "Putting a test into a well-named function improves readability, and that's a sufficient reason to do it"
- [KEY POINT p.447] "It's not hard to avoid deep nesting. If you have deep nesting, you can redesign the tests or refactor code into simpler routines."
- [KEY POINT p.460] "Minimizing complexity is a key to writing high-quality code"

## Empirical Findings

- [HARD DATA: Elshoff 1976] "50 to 80 percent of if statements should have had an else clause"
  - Context: General Motors analysis of production code
- [HARD DATA: Yourdon 1986a] "Few people can understand more than three levels of nested ifs"
  - Context: Studies by Noam Chomsky and Gerald Weinberg
- [HARD DATA: SEN 1990] "NYC phone system 9-hour outage due to an extra break statement"
  - Context: Break intended for if but broke out of switch instead (January 15, 1990)
- [HARD DATA: Soloway, Bonar, and Ehrlich 1983] "Students scored 25 percent higher on comprehension tests when loop-with-exit loops were used"
  - Context: Comparison vs loops that exit at top or bottom
- [HARD DATA: McCabe 1976, Shen et al. 1985] "Control-flow complexity correlates with low reliability and frequent errors"
  - Context: Cyclomatic complexity metric
- [HARD DATA: Ward 1989b] "HP study using McCabe complexity to identify problem areas"
  - 77,000-line program: 0.31 defects/KLOC (post-release)
  - 125,000-line program: 0.02 defects/KLOC (post-release)
  - Both substantially fewer defects than other HP programs due to lower complexity
- [HARD DATA: Miller 1956] "People have trouble juggling more than 5-9 mental entities"
  - Context: Cognitive limits affecting code comprehension; potential for mental improvement is small

## Anti-Patterns

- [CODING HORROR p.385] Phony case variables
  - Description: Manufacturing derived variables to fit case statements (e.g., first character of string)
  - Why: Creates false matches; "copy", "cement", "clambake" all match 'c'
- [CODING HORROR p.373] Index cross-talk in nested loops
  - Description: Using i, j, k for multi-dimensional arrays
  - Why: Impossible to verify correct array index order; causes silent logic errors
- [CODING HORROR p.431] Deep nesting (4+ levels)
  - Description: Excessive indentation from cascading conditionals
  - Why: Comprehension deteriorates beyond 3 levels; works against managing complexity

## Evidence Strength Assessment

| Guidance | Evidence | Strength |
|----------|----------|----------|
| 3-level nesting limit | Chomsky, Weinberg via Yourdon 1986a | **Strong** - Multiple studies, cognitive basis |
| McCabe threshold of 10 | McCabe 1976, Shen 1985, Ward 1989b | **Strong** - Multiple studies with defect correlation |
| Loop-with-exit pattern | Soloway 1983 | **Moderate** - Single study, 25% improvement |
| 50-80% ifs need else | Elshoff 1976 | **Moderate** - Single corporate study |
| Recursion vs iteration | McConnell opinion, p.393 | **Weak** - No empirical study cited; use judgment |
| Table vs inheritance | McConnell opinion, p.423 | **Weak** - No comparative study; context-dependent |

**Note on weak evidence:** Items with weak evidence are still useful heuristics but should not be treated as absolute rules. When someone challenges these with a reasonable counter-argument, engage on the merits rather than citing authority.
