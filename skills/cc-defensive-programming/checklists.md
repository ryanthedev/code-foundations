# Checklists: Defensive Programming

Source: Code Complete 2nd Edition, Chapter 8

---

## Priority Groups

**CRITICAL (Always check - even in crisis):**
Items 1-3 from General, Items 5-7 from Exceptions, Items 1-4 from Security

**HIGH (Check when time permits):**
Items 4-6 from General, Items 1-4 from Exceptions

**STANDARD (Full review):**
Items 7-10 from General

---

## General (p.211)

### Critical (Crisis Triage)
- [ ] 1. "Does the routine protect itself from bad input data?"
- [ ] 2. "Have you used assertions to document assumptions, including preconditions and postconditions?"
- [ ] 3. "Have assertions been used only to document conditions that should never occur?"

### High Priority
- [ ] 4. "Does the architecture or high-level design specify a specific set of error-handling techniques?"
- [ ] 5. "Does the architecture or high-level design specify whether error handling should favor robustness or correctness?"
- [ ] 6. "Have barricades been created to contain the damaging effect of errors and reduce the amount of code that has to be concerned about error processing?"

### Standard
- [ ] 7. "Have debugging aids been used in the code?"
- [ ] 8. "Have debugging aids been installed in such a way that they can be activated or deactivated without a great deal of fuss?"
- [ ] 9. "Is the amount of defensive programming code appropriate - neither too much nor too little?"
- [ ] 10. "Have you used offensive-programming techniques to make errors difficult to overlook during development?"

## Exceptions (p.211-212)

### High Priority
- [ ] 1. "Has your project defined a standardized approach to exception handling?"
- [ ] 2. "Have you considered alternatives to using an exception?"
- [ ] 3. "Is the error handled locally rather than throwing a nonlocal exception, if possible?"
- [ ] 4. "Does the code avoid throwing exceptions in constructors and destructors?"

### Critical
- [ ] 5. "Are all exceptions at the appropriate levels of abstraction for the routines that throw them?"
- [ ] 6. "Does each exception include all relevant exception background information?"
- [ ] 7. "Is the code free of empty catch blocks? (Or if an empty catch block truly is appropriate, is it documented?)"

**Exception for Result types:** Catching generic `Exception` at infrastructure boundaries is acceptable when:
- Method returns a Result/Either type (sum type, discriminated union, algebraic data type)
- Exception is logged or attached to error
- Returns typed domain error, not generic failure

Common names: `Result<T,E>` (Rust/Swift/C#), `Either<L,R>` (Haskell/Scala/vavr), discriminated union (F#/TS), `(T, error)` (Go).

## Security Issues (p.212 + Modern Additions)

### Critical - Original (McConnell)
- [ ] 1. "Does the code that checks for bad input data check for attempted buffer overflows, SQL injection, HTML injection, integer overflows, and other malicious inputs?"
- [ ] 2. "Are all error-return codes checked?"
- [ ] 3. "Are all exceptions caught?"
- [ ] 4. "Do error messages avoid providing information that would help an attacker break into the system?"

### Critical - Modern Threats (2020s additions)
- [ ] 5. Does input validation check for path traversal / directory traversal attacks?
- [ ] 6. Does input validation check for Server-Side Request Forgery (SSRF)?
- [ ] 7. Does input validation check for command injection (especially for CLI tools and shell commands)?
- [ ] 8. Does input validation check for XML External Entity (XXE) attacks?
- [ ] 9. Does deserialization of untrusted data use safe patterns (allowlists, not denylists)?
- [ ] 10. Are rate limits and abuse prevention in place for public endpoints?

### High Priority - Async/Modern Patterns
- [ ] 11. Are Promise rejections handled (not left unhandled)?
- [ ] 12. Do async/await blocks have proper try-catch coverage?
- [ ] 13. Are callback errors propagated correctly (error-first pattern)?
- [ ] 14. Are error boundaries in place for React/frontend components?

---

## Quick Reference: Priority by Situation

| Situation | Use These Items |
|-----------|-----------------|
| **Production crisis (2 min)** | General 1-3, Exceptions 5-7, Security 1-4 |
| **Code review (15 min)** | All Critical + High Priority items |
| **Architecture review** | General 4-6, Security 5-10 |
| **Full audit (1 hour)** | All 24 items |

---

Total items: 24 (21 original + 3 modern security)
