<!-- Source skills (checklists are authoritative — this file provides framework only):
  - skills/cc-control-flow-quality
  - skills/aposd-simplifying-complexity
  - skills/code-clarity-and-docs
-->

# Implementation Standards

Framework and narrative guidance for implementation. Checklists referenced below are the authoritative source — Read() them.

---

## Control Flow

**Nesting:** Max 3 levels (Chomsky-Weinberg). Arrow-shaped code = extract to routine or use guard clauses.

**Guard clauses:** Intentional exception to "nominal case in if." Use at function entry to exit early on precondition failures. Use "nominal in if" for conditionals within the function body.

**McCabe complexity:** Count starts at 1, add 1 for each if/while/for/and/or, add 1 per case.
- 0-5: fine
- 6-10: start thinking about simplification
- 10-20: exception allowed ONLY if ALL true: flat dispatch, ≤3 lines per case, exhaustive/unlikely to grow, low cognitive complexity
- 20+: mandatory refactor, no exceptions

**Loops:**
- `for` when count known, `while` when unknown, `foreach` for collections
- Loop-with-exit (`while(true)` + `break`) is valid — 25% better comprehension than duplicated code patterns
- Name indexes meaningfully in nested loops (not `i`, `j`, `k`)
- Verify exit conditions are reachable

**Booleans:** Use `true`/`false` not `0`/`1`. Use `!done` for bool, `balance != 0` for numeric. Fully parenthesize complex expressions. Extract complex booleans to named intermediate variables.

**Checklists:**
- `Read($CLAUDE_PLUGIN_ROOT/skills/cc-control-flow-quality/checklists/conditionals-and-structure.md)` — conditionals, sequential code, boolean expressions
- `Read($CLAUDE_PLUGIN_ROOT/skills/cc-control-flow-quality/checklists/loops-and-advanced.md)` — loops, recursion, async/await, red flags (including RF-11: silent catch-continue, RF-12: empty default/else)

---

## Error Reduction

**Hierarchy (apply in priority order — levels 1-3 only, Crash is separate):**

| Level | Technique | Validation Gate |
|-------|-----------|-----------------|
| 1 | Define out | Does anyone NEED to detect this error? If no → redefine semantics so error is impossible |
| 2 | Mask | Does the caller have ANY useful response? If no → handle at low level, hide from callers |
| 3 | Aggregate | Do callers handle these errors identically? If yes → single handler for multiple exceptions |

**Crash is NOT level 4.** It's a separate special case for truly unrecoverable errors in application code only. Libraries should NEVER crash — they expose errors for callers to decide.

**Incidental vs Essential errors:** Define Out works for *incidental* errors (safe to eliminate). *Essential* errors — where the caller genuinely needs to know something failed — must fail fast. Test: "If I define this error out of existence, could valid user data be silently lost?" If yes, it's essential.

**Pull complexity downward — first decide WHERE:**
1. Is this complexity closely related to THIS module's functionality?
   - NO → Should it go to a DIFFERENT module? Find the right home or leave with caller.
   - YES → Continue
2. Will pulling down simplify code elsewhere? (NO → don't pull)
3. Will pulling down simplify this module's interface? (NO → don't pull, risk of leakage)

All three must be YES to pull down. Pulling UNRELATED complexity into a module creates information leakage.

**Do NOT apply hierarchy when:**
- Security-critical errors (keep distinct types for audit)
- Retry-differentiated errors (callers need type info for retry strategy)
- Silent data loss risk (fail fast for essential data errors)
- Library code (callers decide crash policy)

**Configuration parameters are incomplete solutions.** Every parameter pushes complexity to users. Prefer dynamic computation over static configuration.

**Checklist:** `Read($CLAUDE_PLUGIN_ROOT/skills/aposd-simplifying-complexity/checklists.md)` — apply Error Reduction Hierarchy, Validation Gates, and Red Flags (including RF-7: error masked without observability).

---

## Comments and Naming

**Comments-first workflow for new code:**
1. Write interface comment (what, not how)
2. Write public method signatures with comments
3. Iterate on structure
4. Fill bodies

**Different Words Test:** If a comment restates what the code says, it adds zero value. Comments explain WHY or WHAT, never HOW (the code shows how).

**Variable comments — check these 5 points:**
1. Units (meters? pixels? seconds?)
2. Boundaries (inclusive? exclusive?)
3. Null meaning (absence? not-yet-loaded? error?)
4. Ownership (who creates? who disposes?)
5. Invariants (always positive? never empty?)

**Naming requires Precision AND Consistency:**
- Precision: "If someone sees this name without context, how closely can they guess its purpose?"
- Consistency: Check all usages, not just local context

**Red flags that signal design problems, not naming problems:**
- Hard to describe the routine → design is unclear
- Hard to pick a name → responsibility is unclear
- Comment needed to clarify name → name is wrong

**Checklist:** `Read($CLAUDE_PLUGIN_ROOT/skills/code-clarity-and-docs/checklists.md)` — apply Comments, Naming, and Red Flags sections.

---

## Obviousness

Code is obvious when a reader can understand it quickly without much thought. This is the shared goal across control flow, complexity reduction, and naming.

**The Obviousness Test:** If a reviewer says it's not obvious, it IS not obvious — regardless of whether you think it is. This is a non-negotiable gate.

**Three ways to make code obvious:**
1. Reduce nesting and complexity (guard clauses, extract to routine, table-driven)
2. Use precise, consistent names
3. Write comments that explain WHY, not WHAT

---

## Test Anchoring

Once tests pass, they are **anchored** — the passing set only grows, never shrinks. If a subsequent change breaks a previously passing test, fix the regression before continuing. Do not skip, disable, or delete a passing test to make progress.
