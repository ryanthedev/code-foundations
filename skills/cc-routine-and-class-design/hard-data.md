# Evidence: cc-routine-and-class-design

## Key Points

- [KEY POINT p.480] "Information hiding is a particularly valuable concept. Asking 'What should I hide?' settles many difficult design issues."
- [KEY POINT p.472] "Software's Primary Technical Imperative is managing complexity. This is greatly aided by a design focus on simplicity."
- [KEY POINT p.164] "The single most important reason to create a routine is to reduce a program's complexity."
- [KEY POINT p.171] "One of the strongest mental blocks to creating effective routines is a reluctance to create a simple routine for a simple purpose."
- [KEY POINT p.181] "Use a function if the primary purpose of the routine is to return the value indicated by the function name. Otherwise, use a procedure."

## Empirical Findings

- [HARD DATA: Woodfield 1981] "Programs using ADTs had 30%+ better comprehension scores."
  - Context: Study on abstraction benefits for program understanding

- [HARD DATA: Basili 1996] "Deep inheritance significantly associated with fault rates; higher routines per class associated with higher faults; more routine calls correlated with fault rates."
  - Context: Study linking inheritance depth and class complexity to defects

- [HARD DATA: Korson and Vaishnavi 1986] "Large programs using information hiding were found to be easier to modify by a factor of 4."
  - Context: Maintainability study on information hiding effectiveness

- [HARD DATA: Card, Church, and Agresti 1986] "50% of highly cohesive routines fault free vs 18% low cohesion; 46% with no unused parameters fault free vs 17-29% with unused."
  - Context: Study of 450 routines correlating cohesion and parameter hygiene with reliability

- [HARD DATA: Selby and Basili 1991] "Routines with highest coupling-to-cohesion ratios had 7x errors and 20x fix cost."

- [HARD DATA: Basili and Perricone 1984] "39% of all errors were internal interface errors."

- [HARD DATA: Miller 1956] "People cannot track more than ~7 chunks of information at once."

- [HARD DATA: Routine Length] Lind/Vairavan 1989: optimal 100-150 lines; Jones 1986: >500 lines most error-prone.

## Anti-Patterns

- [CODING HORROR p.125] Mixed Abstraction Levels
  - Description: AddEmployee/RemoveEmployee mixed with NextItemInList/FirstItem
  - Why it's wrong: Exposes container implementation; inconsistent abstraction

- [CODING HORROR p.161] HandleStuff() Low-Quality Routine
  - Description: 11 parameters, bad name, unused parameters, no single purpose
  - Why it's wrong: Violates nearly every routine quality principle

- [CODING HORROR p.152] Empty Override
  - Description: ScratchlessCat overrides Scratch() to do nothing
  - Why it's wrong: Indicates error in base class design