<!-- Source skills (checklists are authoritative — this file provides framework only):
  - skills/cc-pseudocode-programming
  - skills/aposd-designing-deep-modules
  - skills/cc-routine-and-class-design
-->

# Pre-Gate Standards

Framework and narrative guidance for discovery and design. Checklists referenced below are the authoritative source — Read() them.

---

## Pseudocode First

Write pseudocode before code. Iterating on pseudocode is cheaper than iterating on code.

**Detail level:** Pseudocode is ready when generating code is "nearly automatic" — every design decision is already made. If you pause to think HOW, the pseudocode needs more detail.

**Language:** Pure English, no syntax. Pseudocode becomes comments. Bad: `allocate using malloc`, `*hRsrcPtr = value`. Good: `Allocate a dialog box structure`, `Store the resource number at the location provided by the caller`.

**Minimum viable (extreme time pressure, ~4 min — this is the FLOOR, not the ceiling):**
1. Name the routine clearly (15 sec) — naming difficulty = design problem
2. Write at least 3 lines of pseudocode (2 min)
3. Consider one alternative approach (1 min)
4. Convince yourself it's correct (30 sec) — mentally trace ALL paths (happy, error, edge cases) and explain why each produces correct output. "It looks right" is NOT convinced.

**Skip criteria (ALL must be true):** Simple accessor with NO logic, OR pass-through with NO transformation, OR single statement with zero decision points obvious from signature alone. If you're debating whether to skip, don't skip.

**Checklist:** `Read($CLAUDE_PLUGIN_ROOT/skills/cc-pseudocode-programming/checklists.md)` — apply Prerequisites, Pseudocode Quality, and Red Flags (including RF-11: no failure surfacing plan).

---

## Design-It-Twice

Never implement your first design. Generate 2-3 **radically different** approaches (not variations), sketch interfaces only, then compare.

**Comparison criteria (minimum required):** Interface simplicity, information hiding, caller ease of use, + domain-specific criterion.

**Three questions to ask when designing interfaces:**
1. "What is the simplest interface that covers all current needs?" — minimize method count
2. "In how many situations will this method be used?" — detect over-specialization (red flag: "just this one situation")
3. "Is this easy to use for my current needs?" — guard against over-generalization (red flag: "I need lots of wrapper code")

**If none attractive:** Use identified problems to drive a new round of alternatives.

**Checklist:** `Read($CLAUDE_PLUGIN_ROOT/skills/aposd-designing-deep-modules/checklists.md)` — apply Design-It-Twice Workflow, Process Integrity Checks, and Red Flags (including RF-8: module absorbs failures silently).

---

## Depth Evaluation

| Metric | Deep (Good) | Shallow (Bad) |
|--------|-------------|---------------|
| Interface size | Few methods | Many methods |
| Method reusability | Multiple use cases | Single use case |
| Hidden information | High | Low |
| Caller cognitive load | Low | High |
| Common case | Simple | Complex |

**Information hiding:** Data structures, algorithms, lower-level details (page sizes, buffers), and higher-level assumptions stay internal. Common case requires no knowledge of internals.

**Generality:** Functionality reflects current needs; interface supports multiple uses. Push specialization UP (callers handle specific features) or DOWN (internal variants).

---

## Routine and Class Thresholds

| Metric | Target | Warning | Violation |
|--------|--------|---------|-----------|
| Parameter count | ≤ 7 | — | ≥ 8 (redesign) |
| Inheritance depth | < 3 | 3 | 4+ (6+ = SEVERE) |
| McCabe complexity | ≤ 10 | — | > 10 (redesign) |

**Parameter count:** Includes optional params with defaults. Variadic counts as 1. ≥ 8 is automatic redesign, not "suggest."

**Containment is the default; inheritance is the exception.** "A is a B" must be literally true for domain experts AND every method of B must work correctly when A is substituted. Both conditions or neither. If "is a" feels uncertain, use containment.

**Cohesion classification (stop at first YES — this prevents under-classifying):**

| Level | Quality | Action |
|-------|---------|--------|
| Functional | GOOD | One operation at the routine's declared abstraction level. `CreateUser()` is ONE operation even though it involves validation, hashing, insertion — those are at a LOWER level. |
| Sequential | GOOD | Operations must be in order, output of one feeds next |
| Communicational | ACCEPT w/caution | Operations share data but order doesn't matter. Document WHY and review if functional is achievable. |
| Temporal | REDESIGN | Unless the routine orchestrates (coordinates, delegates, dispatches) rather than performs direct work |
| Procedural / Logical / Coincidental | REDESIGN | — |

**Checklist:** `Read($CLAUDE_PLUGIN_ROOT/skills/cc-routine-and-class-design/checklists.md)` — apply Class Quality, High-Quality Routines, and Red Flags (including RF-11: routine hides failure as default).

---

## Output Artifact

The pre-gate agent produces TWO files:

1. **Discovery findings** — what exists, gaps between plan and reality
2. **Pseudocode** — implementation-ready, with design comparison for non-trivial module decisions

---

## Emergency Bypass

Skip ONLY when ALL true: production down NOW, users actively impacted or data loss occurring, fix is minimal (rollback or single-line), you return for proper design within 24 hours.
