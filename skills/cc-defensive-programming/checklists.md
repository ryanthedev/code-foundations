# Checklists: Defensive Programming

Source: Code Complete 2nd Edition, Chapter 8

---

## General (p.211)

### Critical (Crisis Triage)

- [ ] GC-1: "Does the routine protect itself from bad input data?" → Red flag: Trusting external input without validation
- [ ] GC-2: "Have you used assertions to document assumptions, including preconditions and postconditions?" (Good: Assert at entry/exit, Bad: Defensive code everywhere)
- [ ] GC-3: "Have assertions been used only to document conditions that should never occur?" → Red flag: Using assertions for normal error handling

---

### High Priority

- [ ] GH-1: "Does the architecture or high-level design specify a specific set of error-handling techniques?"
- [ ] GH-2: "Does the architecture or high-level design specify whether error handling should favor robustness or correctness?" (Good: Consistent strategy, Bad: Ad-hoc decisions per routine)
- [ ] GH-3: "Have barricades been created to contain the damaging effect of errors and reduce the amount of code that has to be concerned about error processing?" → Red flag: Error handling scattered throughout system

---

### Standard

- [ ] GS-1: "Have debugging aids been used in the code?"
- [ ] GS-2: "Have debugging aids been installed in such a way that they can be activated or deactivated without a great deal of fuss?"
- [ ] GS-3: "Is the amount of defensive programming code appropriate - neither too much nor too little?" (Good: Validate at boundaries, Bad: Validate everywhere)
- [ ] GS-4: "Have you used offensive-programming techniques to make errors difficult to overlook during development?"

---

## Exceptions (p.211-212)

### High Priority

- [ ] EH-1: "Has your project defined a standardized approach to exception handling?"
- [ ] EH-2: "Have you considered alternatives to using an exception?" → Red flag: Throwing exceptions for control flow
- [ ] EH-3: "Is the error handled locally rather than throwing a nonlocal exception, if possible?"
- [ ] EH-4: "Does the code avoid throwing exceptions in constructors and destructors?"

---

### Critical

- [ ] EC-1: "Are all exceptions at the appropriate levels of abstraction for the routines that throw them?" (Good: Domain exceptions, Bad: Implementation detail exceptions)
- [ ] EC-2: "Does each exception include all relevant exception background information?"
- [ ] EC-3: "Is the code free of empty catch blocks? (Or if an empty catch block truly is appropriate, is it documented?)" → Red flag: Empty catch blocks without explanation

**Exception for Result types:** Catching generic `Exception` at infrastructure boundaries is acceptable when:
- Method returns a Result/Either type (sum type, discriminated union, algebraic data type)
- Exception is logged or attached to error
- Returns typed domain error, not generic failure

Common names: `Result<T,E>` (Rust/Swift/C#), `Either<L,R>` (Haskell/Scala/vavr), discriminated union (F#/TS), `(T, error)` (Go).

---

## Security Issues (p.212 + Modern Additions)

### Critical - Original (McConnell)

- [ ] SO-1: "Does the code that checks for bad input data check for attempted buffer overflows, SQL injection, HTML injection, integer overflows, and other malicious inputs?" → Red flag: Blacklist-based validation
- [ ] SO-2: "Are all error-return codes checked?" → Red flag: Ignoring return values
- [ ] SO-3: "Are all exceptions caught?" (Good: Catch at appropriate level, Bad: Swallow all exceptions)
- [ ] SO-4: "Do error messages avoid providing information that would help an attacker break into the system?" → Red flag: Verbose error messages with stack traces in production

---

### Critical - Modern Threats (2020s additions)

- [ ] SM-1: "Does input validation check for path traversal / directory traversal attacks?" (Good: Allowlist safe paths, Bad: Filter `../`)
- [ ] SM-2: "Does input validation check for Server-Side Request Forgery (SSRF)?" → Red flag: User-controlled URLs without validation
- [ ] SM-3: "Does input validation check for command injection (especially for CLI tools and shell commands)?" → Red flag: String concatenation for shell commands
- [ ] SM-4: "Does input validation check for XML External Entity (XXE) attacks?"
- [ ] SM-5: "Does deserialization of untrusted data use safe patterns (allowlists, not denylists)?" → Red flag: Deserializing untrusted data without type restrictions
- [ ] SM-6: "Are rate limits and abuse prevention in place for public endpoints?"

---

### High Priority - Async/Modern Patterns

- [ ] SA-1: "Are Promise rejections handled (not left unhandled)?" → Red flag: Unhandled promise rejections
- [ ] SA-2: "Do async/await blocks have proper try-catch coverage?"
- [ ] SA-3: "Are callback errors propagated correctly (error-first pattern)?"
- [ ] SA-4: "Are error boundaries in place for React/frontend components?"

---

## Priority Groups

**CRITICAL (Always check - even in crisis):**
GC-1 to GC-3 (General Critical), EC-1 to EC-3 (Exceptions Critical), SO-1 to SO-4 (Security Original)

**HIGH (Check when time permits):**
GH-1 to GH-3 (General High), EH-1 to EH-4 (Exceptions High)

**STANDARD (Full review):**
GS-1 to GS-4 (General Standard), SM-1 to SM-6 (Security Modern), SA-1 to SA-4 (Security Async)

---

## Quick Reference: Priority by Situation

| Situation | Use These Items |
|-----------|-----------------|
| **Production crisis (2 min)** | GC-1 to GC-3, EC-1 to EC-3, SO-1 to SO-4 |
| **Code review (15 min)** | All Critical + High Priority items (GC, GH, EC, EH, SO) |
| **Architecture review** | GH-1 to GH-3, SM-1 to SM-6 |
| **Full audit (1 hour)** | All 31 items |

---

## Red Flags

- [ ] RF-1: "Trusting external input?" - No validation at boundaries → Add input validation at barricades
- [ ] RF-2: "Empty catch blocks?" - Swallowing exceptions without documentation → Handle or propagate with context
- [ ] RF-3: "Error handling scattered everywhere?" - Defensive checks in every routine → Consolidate at boundaries with barricades
- [ ] RF-4: "Exceptions for control flow?" - Using exceptions as goto → Use return values or Result types
- [ ] RF-5: "Verbose production errors?" - Stack traces in user-facing messages → Generic message to user, log details internally
- [ ] RF-6: "Blacklist-based validation?" - Filtering known bad patterns → Allowlist-based validation
- [ ] RF-7: "String concatenation for shell commands?" - Injection vulnerabilities → Use parameterized APIs
- [ ] RF-8: "Unhandled promise rejections?" - Silent failures in async code → Add rejection handlers
- [ ] RF-9: "Assertions for normal error handling?" - Using assert for expected errors → Use proper error handling mechanisms
- [ ] RF-10: "Ignoring return codes?" - Not checking for failure → Check all return values
- [ ] RF-11: "Catch-log-continue?" - Exception caught and logged but execution continues with no indication of failure to caller → Return error result, re-throw, or set observable error state
- [ ] RF-12: "Fallback masking failure?" - Default value substituted on error (`catch { return null }`, `|| default`, `?? fallback`) without distinguishing "no result" from "operation failed" → Use Result type or distinct error sentinel; log the original error

---
