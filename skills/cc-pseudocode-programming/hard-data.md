# Evidence: Pseudocode Programming Process

## Key Points

- [KEY POINT p.220] "Programmers prefer pseudocode for easing construction, detecting insufficiently detailed designs, ease of documentation and modification"
- [KEY POINT p.230] "A working routine isn't enough - if you don't know why it works, study it until you do"

## Empirical Findings

- [HARD DATA: Ostrand and Weyuker 1984] "Only about 5% of all errors are hardware, compiler, or operating-system errors" (p.230)
  - Context: Programmers cause 95% of errors - don't blame tools
- [HARD DATA: Ramsey, Atwood, and Van Doren 1983] "Programmers prefer pseudocode for construction ease, detecting insufficient detail, documentation and modification ease" (p.220)
  - Context: Survey validating PPP benefits over other design approaches

## Anti-Patterns

- [CODING HORROR p.218] Low-Level Pseudocode
  - Description: "Using syntax like *hRsrcPtr, malloc(), specific return codes in pseudocode"
  - Why it's wrong: "Eliminates the main benefit of higher-level design; won't become good comments"

- [CODING HORROR p.231] "Just One More Compile" Syndrome
  - Description: "Compiling repeatedly hoping next compile will fix the problem"
  - Why it's wrong: "Leads to hasty, error-prone changes that take more time in the long run"

- [CODING HORROR p.231] Hacking/Compiling/Fixing Cycle
  - Description: "Tweaking buggy code instead of understanding and rewriting"
  - Why it's wrong: "Hacks indicate incomplete understanding and guarantee future errors"

- [CODING HORROR p.230] Superstitious Programming
  - Description: "Code works but programmer doesn't understand why"
  - Why it's wrong: "Nothing is ever right just because it seems to work"
