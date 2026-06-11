# Checklists: aposd-verifying-correctness

Source: A Philosophy of Software Design (Ousterhout) + verification practices

---

## 1. Requirements Coverage

**Detect:** Were requirements stated? (explicit list, user request, spec)

- [ ] RC-1: "Did I list each requirement explicitly?"
- [ ] RC-2: "For each requirement: can I point to code that implements it?"
- [ ] RC-3: "Any requirement without code?" → **Not done**
- [ ] RC-4: "Any code without requirement?" → Scope creep or missing requirement

**Red flag:** "I think I covered everything" without explicit mapping

---

## 2. Concurrency Safety

**Detect:** Multiple threads/processes, async/await, shared mutable state, web handlers, queue workers?

- [ ] CS-1: "Did I identify all shared mutable state?"
- [ ] CS-2: "Is each access point protected (lock, atomic, queue, immutable)?"
- [ ] CS-3: "Are there no time-of-check to time-of-use (TOCTOU) gaps?"
- [ ] CS-4: "Is lock ordering consistent (if multiple locks)?"

**Red flag:** "It's probably fine" or "Python GIL handles it"

---

## 3. Error Handling

**Detect:** I/O, external calls, resource acquisition, user input, parsing?

- [ ] EH-1: "Does each failure point have explicit handling OR propagate?"
- [ ] EH-2: "No bare `except:` or `except Exception: pass`?"
- [ ] EH-3: "Are error messages actionable (what failed, why, how to fix)?"
- [ ] EH-4: "Are partial failures handled (rollback, cleanup, consistent state)?"
- [ ] EH-5: "Does any error path silently continue as if nothing happened?" → Catch-log-continue, default returns on failure, and swallowed callbacks all create silent failures — verify each error path either surfaces to the caller or is observable (logs, metrics, alerts)

**Red flag:** "Errors are rare" or "caller handles it" without checking caller

---

## 4. Resource Management

**Detect:** File handles, sockets, connections, locks, large allocations, background threads?

- [ ] RM-1: "Does every acquire have corresponding release?"
- [ ] RM-2: "Does release happen in finally/context manager/destructor?"
- [ ] RM-3: "Does release happen on error paths too?"
- [ ] RM-4: "Are there no resource leaks on repeated calls?"
- [ ] RM-5: "Is there bounded growth (caches have limits, queues have limits)?"

**Red flag:** "It cleans up eventually" or daemon threads without shutdown

---

## 5. Boundary Conditions

**Detect:** Collections, strings, byte arrays, numeric ranges, optional/nullable values?

- [ ] BC-1: "What happens with empty input (`[]`, `''`, `None`, `0`)?"
- [ ] BC-2: "What happens with single item (edge case often different from N)?"
- [ ] BC-3: "What happens with maximum size (memory? time?)?"
- [ ] BC-4: "What happens with invalid values (negative, NaN, special characters)?"
- [ ] BC-5: "What happens at type boundaries (int overflow, float precision)?"

**Red flag:** "Nobody would pass that" or "that's an edge case"

---

## 6. Security (if applicable)

**Detect:** User-provided data, file contents from external sources, URLs/paths/identifiers from users?

- [ ] SE-1: "Is input validated before use?"
- [ ] SE-2: "No string concatenation for SQL/shell/HTML (use parameterized)?"
- [ ] SE-3: "Is path traversal prevented (no `../` exploitation)?"
- [ ] SE-4: "Are secrets not logged or exposed in errors?"
- [ ] SE-5: "Is auth/authz checked BEFORE action, not after?"

**Red flag:** "It's internal only" (internals get exposed)

---

## Quick Verification Summary

- [ ] QV-1: "Requirements were stated?" → Each mapped to code
- [ ] QV-2: "Shared state exists?" → All access protected
- [ ] QV-3: "Operations can fail?" → All failures handled
- [ ] QV-4: "Resources acquired?" → All released (including on errors)
- [ ] QV-5: "Variable-size input?" → Edge cases handled
- [ ] QV-6: "Untrusted input?" → Input validated

---
