<!-- Source skills (checklists are authoritative — this file provides framework only):
  - skills/aposd-verifying-correctness
  - skills/cc-quality-practices
  - skills/aposd-reviewing-module-design
  - skills/cc-defensive-programming
-->

# Post-Gate Review Standards

Framework and narrative guidance for post-gate reviews. Checklists referenced below are the authoritative source — Read() them.

---

## Requirement Fulfillment (Check First)

Before checking code quality, verify the implementation satisfies requirements.

- [ ] Use DW items from the dispatch prompt (orchestrator extracted these from the plan)
- [ ] For each DW item: cite file:line that implements it
- [ ] Any DW item without code → NOT SATISFIED → FAIL
- [ ] Any code without a DW item → scope creep, flag it

**"I think I covered everything" without explicit DW-by-DW mapping = FAIL.**

---

## Correctness Dimensions

For each dimension: detect if it applies, verify if YES, mark N/A with reason if NO.

Dimensions: **Concurrency** (shared state, async, web handlers, background tasks), **Error Handling** (I/O, external calls, parsing, user input), **Resources** (file handles, connections, locks, caches, threads), **Boundaries** (collections, strings, numerics, optionals), **Security** (untrusted input).

**Checklist:** `Read(${CLAUDE_PLUGIN_ROOT}/skills/aposd-verifying-correctness/checklists.md)` — apply all sections that match detected dimensions.

---

## Defensive Programming

**Assertions vs Error Handling — different tools for different conditions:**
- **Assertion:** Condition that should NEVER be true (programmer bug). Use for internal invariants.
- **Error handling:** Condition that CAN occur at runtime (bad input, network failure). Use for external/environmental.
- Internal methods: assert preconditions. Public API methods: handle errors.
- NEVER put executable code inside assertions — it disappears in production builds.

**External input definition:** Any data not provably controlled by current code path. Includes internal APIs crossing network/process boundaries — "internal" does NOT mean "trusted."

**Barricade caveat:** Barricades reduce redundant validation but do NOT replace defense-in-depth for security-critical code. Ask: "If the barricade validation has a bug, what happens?"

**Correctness vs Robustness:** Safety-critical = shut down over wrong result. Consumer apps = keep running. B2B/data pipelines = analyze per case. This is a choice, not a law.

**Checklist:** `Read(${CLAUDE_PLUGIN_ROOT}/skills/cc-defensive-programming/checklists.md)` — apply General, Exceptions, Security, and Red Flags sections. Pay special attention to RF-11 (catch-log-continue) and RF-12 (fallback masking failure).

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

**Checklist:** `Read(${CLAUDE_PLUGIN_ROOT}/skills/aposd-reviewing-module-design/checklists.md)` — apply Complexity Symptoms, Module Depth, Information Hiding, and Quick Reference Red Flags (including SF-1: Silent Failure).

---

## Testing Quality

**5:1 ratio:** Mature organizations have 5 dirty tests (error/edge/bad-data) for every 1 clean test. Inverse = immature.

**50% of defect corrections are wrong the first time** if you skip STABILIZE → HYPOTHESIZE → EXPERIMENT. EXPERIMENT means designing a test WITHOUT changing production code: add logging, use a debugger, write a failing test — prove your hypothesis before touching the code. If the experiment doesn't disprove your hypothesis, you're still guessing.

**Preparation finds 90% of inspection defects.** The meeting finds only 10% more. Invest in preparation.

**No single technique exceeds 75% effectiveness.** Combining techniques (review + testing + static analysis) nearly doubles detection rates.

**Checklist:** `Read(${CLAUDE_PLUGIN_ROOT}/skills/cc-quality-practices/checklists/qa-and-testing.md)` — apply Test Cases section and Data-Flow Anomaly Patterns.

---

## Verdict Format

```
## Post-Gate Review

### Requirements: [X/Y satisfied]
- DW-N.1: [requirement] → [file:line] SATISFIED
- DW-N.2: [requirement] → NOT SATISFIED — [why]

### Correctness Dimensions
- Concurrency: [PASS/FAIL/N/A] — [evidence]
- Error Handling: [PASS/FAIL/N/A] — [evidence]
- Resources: [PASS/FAIL/N/A] — [evidence]
- Boundaries: [PASS/FAIL/N/A] — [evidence]
- Security: [PASS/FAIL/N/A] — [evidence]

### Defensive Programming: [PASS/FAIL]
[checklist results]

### Design Quality: [findings with severity]

### Testing: [PASS/FAIL]
[dirty:clean ratio, coverage gaps]

**Verdict: [PASS / FAIL — list blockers]**
```

**PASS requires:** All requirements satisfied, no FAIL dimensions, no HIGH severity design findings.
