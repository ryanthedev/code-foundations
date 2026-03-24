# Post-Gate Review Standards

Combined constraints from aposd-verifying-correctness, cc-quality-practices, aposd-reviewing-module-design, and cc-defensive-programming. For full details, invoke individual skills.

---

## Requirement Fulfillment (Check First)

Before checking code quality, verify the implementation satisfies requirements.

- [ ] List each requirement explicitly (from plan done-when items)
- [ ] For each: cite file:line that implements it
- [ ] Any requirement without code → NOT DONE
- [ ] Any code without requirement → scope creep

**"I think I covered everything" without explicit mapping = FAIL.**

---

## Correctness Dimensions

For each dimension: detect if it applies, verify if YES, mark N/A with reason if NO.

**Concurrency** (shared state, async, web handlers, background tasks):
- All shared mutable state identified and protected
- No TOCTOU gaps
- Lock ordering consistent

**Error Handling** (I/O, external calls, parsing, user input):
- Each failure point has explicit handling or intentional propagation
- No bare catch / `except Exception: pass`
- Error messages are actionable (what, why, how to fix)
- Partial failures handled (rollback, cleanup, consistent state)

**Resources** (file handles, connections, locks, caches, threads):
- Every acquire has corresponding release in finally/using/destructor
- Release happens on error paths too
- Bounded growth (caches have limits)

**Boundaries** (collections, strings, numerics, optionals):
- Empty: `[]`, `""`, `null`, `0`
- Single item (often different from N items)
- Maximum size (memory? time?)

**Security** (untrusted input — any data not provably controlled by current code path):
- Input validated before use
- No string concatenation for SQL/shell/HTML
- Path traversal prevented
- Secrets not logged or exposed in errors

---

## Defensive Programming

**Crisis triage (EMERGENCY ONLY — 2 min, 5 checks = 80% of defensive bugs):**
1. External input validated at boundaries?
2. Return values checked for all external calls?
3. Error paths tested (not just happy path)?
4. Assertions on critical invariants (no side effects — code inside assertions disappears in production)?
5. Resources released on all paths?

For non-emergency review, use the full 21-item checklist: `Skill(code-foundations:cc-defensive-programming)`.

**Assertions vs Error Handling — different tools for different conditions:**
- **Assertion:** Condition that should NEVER be true (programmer bug). Use for internal invariants.
- **Error handling:** Condition that CAN occur at runtime (bad input, network failure). Use for external/environmental.
- Internal methods: assert preconditions. Public API methods: handle errors.
- NEVER put executable code inside assertions — it disappears in production builds.

**External input definition:** Any data not provably controlled by current code path. Includes internal APIs crossing network/process boundaries — "internal" does NOT mean "trusted."

**Barricade caveat:** Barricades reduce redundant validation but do NOT replace defense-in-depth for security-critical code. Ask: "If the barricade validation has a bug, what happens?"

**Correctness vs Robustness:** Safety-critical = shut down over wrong result. Consumer apps = keep running. B2B/data pipelines = analyze per case. This is a choice, not a law.

---

## Design Quality

**Depth > Length:** A long method with clean abstraction should stay together. A short method requiring understanding of another's implementation should be combined. This reverses the common small-methods bias — depth (interface simpler than implementation) matters more than length.

**Unknown unknowns = highest severity.** If it's unclear what code would be needed for a change, flag immediately — this blocks PASS even if all other findings are minor.

**Together/Apart decision procedure:**
1. Do pieces share information? → keep together
2. Would combining simplify the interface? → keep together
3. Is there repeated code? → extract shared method
4. Does it mix general-purpose with special-purpose? → separate them

**Steel-man check before flagging:** What's the best argument this design is intentional? Could it be an adapter, facade, decorator, or testing seam (injectable dependency)? Testing seams are acceptable information "leakage" — intentional and good. Only flag after considering these.

**Pass-through methods** that delegate with the same API signal a layer problem. Validation test: trace a single operation through layers — does the abstraction change at each call? If not, a layer isn't adding value.

---

## Testing Quality

**5:1 ratio:** Mature organizations have 5 dirty tests (error/edge/bad-data) for every 1 clean test. Inverse = immature.

**50% of defect corrections are wrong the first time** if you skip STABILIZE → HYPOTHESIZE → EXPERIMENT. EXPERIMENT means designing a test WITHOUT changing production code: add logging, use a debugger, write a failing test — prove your hypothesis before touching the code. If the experiment doesn't disprove your hypothesis, you're still guessing.

**Preparation finds 90% of inspection defects.** The meeting finds only 10% more. Invest in preparation.

**No single technique exceeds 75% effectiveness.** Combining techniques (review + testing + static analysis) nearly doubles detection rates.

---

## Verdict Format

```
## Post-Gate Review

### Requirements: [X/Y satisfied]
- R1: [requirement] → [file:line] SATISFIED
- R2: [requirement] → NOT SATISFIED — [why]

### Correctness Dimensions
- Concurrency: [PASS/FAIL/N/A] — [evidence]
- Error Handling: [PASS/FAIL/N/A] — [evidence]
- Resources: [PASS/FAIL/N/A] — [evidence]
- Boundaries: [PASS/FAIL/N/A] — [evidence]
- Security: [PASS/FAIL/N/A] — [evidence]

### Defensive Programming: [PASS/FAIL]
[crisis triage results]

### Design Quality: [findings with severity]

### Testing: [PASS/FAIL]
[dirty:clean ratio, coverage gaps]

**Verdict: [PASS / FAIL — list blockers]**
```

**PASS requires:** All requirements satisfied, no FAIL dimensions, no HIGH severity design findings.
