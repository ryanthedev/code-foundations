# Core Sanity Checks (14)

Distilled from 99 checks via 7-agent blind consensus study. These are the checks that multiple independent agents identified as most critical for catching production bugs.

---

## Error Handling (2)

- [ ] ERR-3: "Are all error-return codes checked?"
- [ ] ERR-8: "Are partial failures handled (rollback, cleanup, consistent state)?"

---

## Null Safety & Boundaries (4)

- [ ] NULL-2: "Does the code check pointers/references for null before use?"
- [ ] NULL-4: "Are all array indexes within bounds?"
- [ ] NULL-5: "Are array references free of off-by-one errors?"
- [ ] NULL-6: "What happens with empty input (`[]`, `''`, `None`, `0`)?"

---

## Logic & Control Flow (4)

- [ ] LOGIC-1: "Does the loop end under all possible conditions?"
- [ ] LOGIC-6: "Does recursive code include a path to stop recursion?"
- [ ] LOGIC-11: "Are all cases covered in switch/if-else chains?"
- [ ] LOGIC-15: "No accidental assignment in conditionals (`=` vs `==`)?"

---

## Concurrency (2)

- [ ] CONC-2: "Is each shared access point protected (lock, atomic, queue)?"
- [ ] CONC-3: "Are there no TOCTOU race conditions?"

---

## Resources & Performance (2)

- [ ] RES-1: "Does every acquire have corresponding release (in finally/using/defer)?"
- [ ] PERF-1: "Are database queries not in loops (N+1 query problem)?"

---

## Summary

| Category | Count | Consensus |
|----------|-------|-----------|
| Error Handling | 2 | 7/7 |
| Null Safety & Boundaries | 4 | 7/7 |
| Logic & Control Flow | 4 | 6-7/7 |
| Concurrency | 2 | 6/7 |
| Resources & Performance | 2 | 7/7 |
| **Total** | **14** | |

---

## Methodology

7 independent agents were asked to select the 15 most critical checks from the full 99-check list. Selection criteria:
- Catches bugs that cause production incidents
- Applies universally (not language-specific)
- Can be evaluated by reading code
- High signal-to-noise ratio

Checks with 6/7 or 7/7 agreement were included.

---

## Usage

Apply checklist **per file**. Go through each check systematically.

### Per-file evaluation

For each changed file, evaluate all 14 checks:

```
src/api.ts:
  ERR-3:   FINDING @ line 42, 67 - error codes not checked
  ERR-8:   PASS
  NULL-2:  FINDING @ line 89 - userId not checked for null
  NULL-4:  N/A (no array access)
  NULL-5:  N/A (no array access)
  NULL-6:  PASS
  LOGIC-1: FINDING @ line 112 - while loop may not terminate
  LOGIC-6: N/A (no recursion)
  ...
```

### Verdicts

| Verdict | Meaning |
|---------|---------|
| PASS | Check satisfied for this file |
| FINDING | Check failed - list each location with line number |
| N/A | Check doesn't apply (no loops, no arrays, no concurrency, etc.) |

### One check → multiple findings

A single check can produce findings at multiple locations:
```
NULL-2:  FINDING @ line 42, 67, 89
```
