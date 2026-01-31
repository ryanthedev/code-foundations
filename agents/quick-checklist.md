# Quick Review Checklist (99 Critical Checks)

Focused on design, correctness, performance, and structure. Security/input validation deferred to full PR review.

---

## LLM Verification (5)

Common mistakes when AI generates code.

- [ ] LLM-1: Are all API/function names spelled correctly (no typos like `read_exel`)?
- [ ] LLM-2: Do all called functions/methods actually exist in the libraries used?
- [ ] LLM-3: Are function parameters correct (not hallucinated or deprecated)?
- [ ] LLM-4: Are all required imports present?
- [ ] LLM-5: Do variable references match their declarations (no identifier mismatches)?

---

## Code Hygiene (7)

Cleanup that should happen before commit.

- [ ] CLEAN-1: Are debug statements removed (console.log, print, debugger)?
- [ ] CLEAN-2: Are TODO/FIXME comments addressed or intentionally deferred?
- [ ] CLEAN-3: Is commented-out code removed?
- [ ] CLEAN-4: Are unused imports removed?
- [ ] CLEAN-5: Are unused variables removed?
- [ ] CLEAN-6: Is dead code removed (unreachable paths)?
- [ ] CLEAN-7: Are imports organized per project conventions?

---

## Error Handling (12)

- [ ] ERR-1: Is the code free of empty catch blocks?
- [ ] ERR-2: No bare `except:` or `catch(Exception)` that swallow all errors?
- [ ] ERR-3: Are all error-return codes checked?
- [ ] ERR-4: Does each exception include relevant context (what failed, why)?
- [ ] ERR-5: Are exceptions at appropriate abstraction levels?
- [ ] ERR-6: Does each failure point have explicit handling OR propagate?
- [ ] ERR-7: Are error messages actionable (what failed, how to fix)?
- [ ] ERR-8: Are partial failures handled (rollback, cleanup, consistent state)?
- [ ] ERR-9: Are Promise rejections handled (not left unhandled)?
- [ ] ERR-10: Do async/await blocks have proper try-catch coverage?
- [ ] ERR-11: Is the error handled locally rather than throwing nonlocal exception?
- [ ] ERR-12: Does the system fail gracefully (degraded mode, not crash)?

---

## Null Safety & Boundaries (8)

- [ ] NULL-1: Does the routine protect itself from bad input data?
- [ ] NULL-2: Does the code check pointers/references for null before use?
- [ ] NULL-3: Does code handle all cases when unwrapping Option/Maybe/nullable?
- [ ] NULL-4: Are all array indexes within bounds?
- [ ] NULL-5: Are array references free of off-by-one errors?
- [ ] NULL-6: What happens with empty input (`[]`, `''`, `None`, `0`)?
- [ ] NULL-7: What happens at type boundaries (int overflow, float precision)?
- [ ] NULL-8: Are range calculations correct (n-m vs n-m+1)?

---

## Logic & Control Flow (15)

### Loops
- [ ] LOGIC-1: Does the loop end under all possible conditions?
- [ ] LOGIC-2: Is the termination condition obvious?
- [ ] LOGIC-3: Does code inside for loops avoid modifying the loop index?
- [ ] LOGIC-4: Is nesting limited to three levels or less?
- [ ] LOGIC-5: Does the loop index have a meaningful name?

### Recursion
- [ ] LOGIC-6: Does recursive code include a path to stop recursion?
- [ ] LOGIC-7: Is recursion depth within stack limits?

### Conditionals
- [ ] LOGIC-8: Does the normal case follow the if rather than the else?
- [ ] LOGIC-9: Are if and else clauses used correctly (not reversed)?
- [ ] LOGIC-10: Is the else clause present and documented?
- [ ] LOGIC-11: Are all cases covered in switch/if-else chains?
- [ ] LOGIC-12: Is the default clause used to detect unexpected cases?
- [ ] LOGIC-13: Does pattern matching handle all cases (exhaustiveness)?
- [ ] LOGIC-14: Are boolean expressions simplified (no double negatives)?
- [ ] LOGIC-15: No accidental assignment in conditionals (`=` vs `==`)?

---

## Design Red Flags (15)

### Complexity Symptoms
- [ ] DESIGN-1: Does a simple change require modifications in many places? (Change Amplification)
- [ ] DESIGN-2: Must developer know too much to work here? (Cognitive Load)
- [ ] DESIGN-3: Is it unclear what code/info is needed for changes? (Unknown Unknowns)

### Information Hiding
- [ ] DESIGN-4: Is the same knowledge duplicated in multiple modules? (Information Leakage)
- [ ] DESIGN-5: Is the interface much simpler than the implementation? (Shallow Module check)
- [ ] DESIGN-6: Are implementation details hidden from callers?
- [ ] DESIGN-7: Does structure mirror execution order rather than knowledge? (Temporal Decomposition)

### Structural Issues
- [ ] DESIGN-8: Does method only pass arguments to another with same API? (Pass-Through)
- [ ] DESIGN-9: Does general mechanism contain use-case specific code? (Special-General Mixture)
- [ ] DESIGN-10: Does same code appear in multiple places? (Code Repetition)
- [ ] DESIGN-11: Can't understand one method without another's implementation? (Conjoined Methods)

### Pattern Consistency
- [ ] DESIGN-12: Is a similar problem already solved elsewhere in this codebase?
- [ ] DESIGN-13: If diverging from established pattern, is the reason documented?
- [ ] DESIGN-14: Would a future maintainer be confused by two different approaches?
- [ ] DESIGN-15: Are standard library functions used instead of reimplementing?

---

## Testing (8)

### Coverage
- [ ] TEST-1: Are there tests for this change?
- [ ] TEST-2: Do tests cover the happy path?
- [ ] TEST-3: Do tests cover error conditions?
- [ ] TEST-4: Do tests cover boundary conditions (empty, one, max)?

### Quality
- [ ] TEST-5: Are test names descriptive of what they test?
- [ ] TEST-6: Are assertions specific and meaningful?
- [ ] TEST-7: Are tests independent (no shared mutable state)?
- [ ] TEST-8: Are test helpers/fixtures reused, not duplicated?

---

## Concurrency (6)

- [ ] CONC-1: Is all shared mutable state identified?
- [ ] CONC-2: Is each shared access point protected (lock, atomic, queue)?
- [ ] CONC-3: Are there no TOCTOU race conditions?
- [ ] CONC-4: Is lock ordering consistent (if multiple locks)?
- [ ] CONC-5: Is immutability considered as alternative to locks?
- [ ] CONC-6: Is Promise.all used for parallel operations (not sequential awaits)?

---

## Resources & Performance (12)

### Resource Management
- [ ] RES-1: Does every acquire have corresponding release (in finally/using/defer)?
- [ ] RES-2: Are file handles, sockets, connections closed properly?
- [ ] RES-3: Are database connections released back to pool?
- [ ] RES-4: Are background threads/tasks cancelled on shutdown?
- [ ] RES-5: Is there bounded growth (caches/queues have limits)?
- [ ] RES-6: Are there no resource leaks on repeated calls?

### Performance
- [ ] PERF-1: Are database queries not in loops (N+1 query problem)?
- [ ] PERF-2: Are appropriate data structures chosen (array vs set vs map)?
- [ ] PERF-3: Is string concatenation in loops using appropriate methods?
- [ ] PERF-4: Are expensive operations not repeated unnecessarily?
- [ ] PERF-5: Are timeouts set for external operations (network, file I/O)?
- [ ] PERF-6: Are async operations parallelized where independent?

---

## API & Structure Quality (11)

### Routine Quality
- [ ] API-1: Does each routine perform one well-defined task?
- [ ] API-2: Does the routine's name describe exactly what it does?
- [ ] API-3: Does the routine have seven or fewer parameters?
- [ ] API-4: If the routine is a function, does it return a valid value under all circumstances?

### Class Quality
- [ ] API-5: Does the class present a consistent abstraction level?
- [ ] API-6: Does the class hide its implementation details?
- [ ] API-7: Is containment used instead of inheritance when appropriate?

### Pattern Usage
- [ ] API-8: Are framework built-in patterns used where available?
- [ ] API-9: Do validation/error patterns match existing codebase conventions?
- [ ] API-10: Do logging patterns match existing codebase (levels, format)?
- [ ] API-11: Do configuration patterns follow existing conventions?

---

## Summary

| Category | Count |
|----------|-------|
| LLM Verification | 5 |
| Code Hygiene | 7 |
| Error Handling | 12 |
| Null Safety & Boundaries | 8 |
| Logic & Control Flow | 15 |
| Design Red Flags | 15 |
| Testing | 8 |
| Concurrency | 6 |
| Resources & Performance | 12 |
| API & Structure Quality | 11 |
| **Total** | **99** |

---

## What's NOT in this checklist (deferred to PR review)

- Security (input validation, injection, auth)
- Deep architectural review
- Documentation quality
- Code style/formatting (linter handles this)
