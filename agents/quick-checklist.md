# Quick Review Checklist (99 Critical Checks)

Curated from code-foundations skills. Critical issues only.

---

## Security (5)

- [ ] SEC-1: Is user input validated before use?
- [ ] SEC-2: Are SQL/shell/HTML properly parameterized or escaped?
- [ ] SEC-3: Are secrets NOT hardcoded in source?
- [ ] SEC-4: Are secrets NOT logged or exposed in error messages?
- [ ] SEC-5: Is auth/authz checked BEFORE the action?

---

## Error Handling (15)

- [ ] ERR-1: Is the code free of empty catch blocks?
- [ ] ERR-2: No bare `except:` or `catch(Exception)` that swallow all errors?
- [ ] ERR-3: Are all error-return codes checked?
- [ ] ERR-4: Does each exception include relevant context information?
- [ ] ERR-5: Are exceptions at appropriate abstraction levels?
- [ ] ERR-6: Does code avoid throwing exceptions in constructors/destructors?
- [ ] ERR-7: Does each failure point have explicit handling OR propagate?
- [ ] ERR-8: Are error messages actionable (what failed, why, how to fix)?
- [ ] ERR-9: Are partial failures handled (rollback, cleanup, consistent state)?
- [ ] ERR-10: Are Promise rejections handled (not left unhandled)?
- [ ] ERR-11: Do async/await blocks have proper try-catch coverage?
- [ ] ERR-12: Are callback errors propagated correctly (error-first pattern)?
- [ ] ERR-13: Are error boundaries in place for UI components?
- [ ] ERR-14: Does the system fail securely (fail closed, not fail open)?
- [ ] ERR-15: Is the error handled locally rather than throwing nonlocal exception?

---

## Null Safety (8)

- [ ] NULL-1: Does the routine protect itself from bad input data?
- [ ] NULL-2: Does the code check pointers/references for null before use?
- [ ] NULL-3: Are pointers set to null after they're freed?
- [ ] NULL-4: Does code handle all cases when unwrapping Option/Maybe/nullable?
- [ ] NULL-5: Are all array indexes within bounds?
- [ ] NULL-6: Are array references free of off-by-one errors?
- [ ] NULL-7: What happens with empty input (`[]`, `''`, `None`, `0`)?
- [ ] NULL-8: What happens at type boundaries (int overflow, float precision)?

---

## Logic & Control Flow (18)

### Loops
- [ ] LOGIC-1: Does the loop end under all possible conditions?
- [ ] LOGIC-2: Is the termination condition obvious?
- [ ] LOGIC-3: Does code inside for loops avoid modifying the loop index?
- [ ] LOGIC-4: Is the loop index saved before use outside the loop?
- [ ] LOGIC-5: Is nesting limited to three levels or less?
- [ ] LOGIC-6: Is the loop index an ordinal type (not floating-point)?

### Recursion
- [ ] LOGIC-7: Does recursive code include a path to stop recursion?
- [ ] LOGIC-8: Is recursion depth within stack limits?
- [ ] LOGIC-9: Does the routine use a safety counter to guarantee stopping?

### Conditionals
- [ ] LOGIC-10: Does the normal case follow the if rather than the else?
- [ ] LOGIC-11: Are if and else clauses used correctly (not reversed)?
- [ ] LOGIC-12: Is the else clause present and documented?
- [ ] LOGIC-13: Are all cases covered in switch/if-else chains?
- [ ] LOGIC-14: Is the default clause used to detect unexpected cases?
- [ ] LOGIC-15: Does each case end with a break (in C, C++, Java)?
- [ ] LOGIC-16: Does pattern matching handle all cases (exhaustiveness)?
- [ ] LOGIC-17: Are boolean expressions simplified (no double negatives)?
- [ ] LOGIC-18: Are compound conditions readable (extracted to named variables)?

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
- [ ] DESIGN-15: Is this following a pattern blindly without evaluating merit?

---

## Testing (12)

### Coverage
- [ ] TEST-1: Are there tests for this change?
- [ ] TEST-2: Do tests cover the happy path?
- [ ] TEST-3: Do tests cover error conditions?
- [ ] TEST-4: Do tests cover boundary conditions (empty, one, max)?
- [ ] TEST-5: Do tests cover invalid inputs?

### Quality
- [ ] TEST-6: Are test names descriptive of what they test?
- [ ] TEST-7: Are assertions specific and meaningful (not just `assertTrue`)?
- [ ] TEST-8: Is test setup clear and minimal?
- [ ] TEST-9: Are tests independent (no shared mutable state)?
- [ ] TEST-10: Do tests avoid testing implementation details?

### Regression
- [ ] TEST-11: Is there a test that would have caught this bug (if fixing one)?
- [ ] TEST-12: Do existing tests still pass?

---

## Concurrency (8)

- [ ] CONC-1: Is all shared mutable state identified and documented?
- [ ] CONC-2: Is each shared access point protected (lock, atomic, queue)?
- [ ] CONC-3: Are there no TOCTOU race conditions?
- [ ] CONC-4: Is lock ordering consistent (if multiple locks)?
- [ ] CONC-5: Are there no data races (read/write without sync)?
- [ ] CONC-6: Are atomic operations used for simple shared counters?
- [ ] CONC-7: Is immutability considered as alternative to locks?
- [ ] CONC-8: Is Promise.all used for parallel operations (not sequential awaits)?

---

## Resources (8)

- [ ] RES-1: Does every acquire have corresponding release?
- [ ] RES-2: Does release happen in finally/using/defer/destructor?
- [ ] RES-3: Does release happen on error paths too?
- [ ] RES-4: Are file handles, sockets, connections closed properly?
- [ ] RES-5: Are database connections released back to pool?
- [ ] RES-6: Are background threads/tasks cancelled on shutdown?
- [ ] RES-7: Is there bounded growth (caches/queues have limits)?
- [ ] RES-8: Are there no resource leaks on repeated calls?

---

## API Quality (10)

### Routine Quality
- [ ] API-1: Does each routine perform one well-defined task?
- [ ] API-2: Does the routine's name describe exactly what it does?
- [ ] API-3: Does the routine have seven or fewer parameters?
- [ ] API-4: Are parameters in a consistent order (in, in-out, out)?
- [ ] API-5: If the routine is a function, does it return a valid value under all circumstances?

### Class Quality
- [ ] API-6: Does the class present a consistent abstraction level?
- [ ] API-7: Does the class hide its implementation details?
- [ ] API-8: Is inheritance depth less than 3 levels?
- [ ] API-9: Does "is-a" relationship literally hold for inheritance (LSP)?
- [ ] API-10: Is containment used instead of inheritance when appropriate?

---

## Summary

| Category | Count |
|----------|-------|
| Security | 5 |
| Error Handling | 15 |
| Null Safety | 8 |
| Logic & Control Flow | 18 |
| Design Red Flags | 15 |
| Testing | 12 |
| Concurrency | 8 |
| Resources | 8 |
| API Quality | 10 |
| **Total** | **99** |
