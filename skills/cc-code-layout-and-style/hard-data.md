# Evidence: cc-code-layout-and-style

## Key Points

- [KEY POINT p.729] "The Fundamental Theorem of Formatting: Good visual layout shows the logical structure of a program."
- [KEY POINT p.735] "The details of a specific method of structuring a program are much less important than the fact that the program is structured consistently."
- [KEY POINT p.732] "White space (spaces, tabs, line breaks, blank lines) is the main tool for showing a program's structure."
- [KEY POINT p.797] "Good comments don't repeat the code or explain it. They clarify its intent."
- [KEY POINT p.798] "If it's hard to comment, either it's bad code or you don't understand it well enough."

## Empirical Findings

- [HARD DATA: Gorla, Benander, and Benander 1990] Optimal blank line density is 8-16% of program. Above 16%, debug time increases dramatically.

- [HARD DATA: Miaria et al. 1983] Subjects scored 20-30% higher on comprehension tests with 2-4 space indentation vs no indentation. Six-space indentation produced second lowest scores. Many subjects FELT six-space was easier despite lower scores.

- [HARD DATA: Jones 2000] IBM study found optimal comment density of roughly one comment per 10 statements. Fewer comments made code hard to understand; more comments also reduced understandability.

- [HARD DATA: Lind and Vairavan 1989] Areas with large numbers of comments tended to have the most defects and consume the most development effort. Programmers comment difficult code heavily.

- [HARD DATA: Fjelstad and Hamlen 1979] Maintenance programmers "most often said that understanding the original programmer's intent was the most difficult problem."

- [HARD DATA: Oman and Cook 1990b] Book Paradigm documentation reduced maintenance task time to 75% of traditional approach. Comprehension scores averaged 20% higher.

## Anti-Patterns

- [ANTI-PATTERN p.730] Layout Tells Different Story Than Code
  - Visual indentation suggests statements are in loop; only first statement actually is
  - Why wrong: Dangerous mismatch between visual and logical structure

- [ANTI-PATTERN p.731] Misleading Whitespace
  - Spacing around operators contradicts operator precedence
  - Why wrong: Humans read spacing, computers read precedence

- [ANTI-PATTERN p.758] Multiple Statements Per Line
  - "Clever" compact code hides complexity and bugs
  - Why wrong: 11% slower in performance tests; harder to debug

- [ANTI-PATTERN p.798] Commenting Tricky Code Instead of Rewriting
  - "Don't document bad code - rewrite it" (Kernighan and Plauger)
  - Why wrong: Comments can't rescue bad code; rewriting eliminates need

- [ANTI-PATTERN p.806] Hard-to-Maintain Comment Styles
  - Leader dots, columns of asterisks, fancy boxes
  - Why wrong: Won't be maintained; unmaintained formatting worse than none
