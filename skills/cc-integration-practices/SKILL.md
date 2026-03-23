---
name: cc-integration-practices
description: "Use when integrating components, planning integration order, setting up build processes, or diagnosing integration failures. Triggers on: integration hell, late-stage defects, unclear integration order, no daily build, broken builds, Big Bang integration, smoke test stale."
---

# Skill: cc-integration-practices

## STOP - Integration Rules

- **Never Big Bang integration** - Add components one at a time
- **Fix broken builds immediately** - Within 1 hour; stop all other work
- **Daily build is MINIMUM** - Not a ceiling; modern CI/CD goes faster

---

## Quick Reference

| Threshold/Rule | Value | Source |
|----------------|-------|--------|
| Interface errors | 39% of all errors | Basili and Perricone 1984 |
| Debugging time | Up to 50% of development | CC2 p.689 |
| Daily build adoption | Only 20-25% of projects | Cusumano et al. 2003 |
| Check-in frequency | No more than 2 days without | CC2 p.703 |
| Build fix priority | Immediately; stop all other work | CC2 p.704 |

**Key Principles:**
- Integrate incrementally, not all at once (Big Bang)
- Each integration step must produce a working system
- Build daily, test with smoke test
- Fix broken builds immediately

## Key Definitions
- **Smoke test**: Small (<15 tests), fast (<5 min), automated end-to-end sanity check. NOT a full test suite.
- **Working system**: Compiles without errors, existing tests pass, smoke test passes.
- **Immediately**: Within 1 hour; escalate if blocked. Revert counts as a fix.
- **Daily build**: Main branch builds successfully at least once per calendar day.

## Core Patterns

### Big Bang -> Incremental Integration
```
// BEFORE: Big Bang Integration [ANTI-PATTERN]
Phase 1: Develop all units separately
Phase 2: Combine everything at once
Phase 3: "System dis-integration" - debug the mess
Result: All problems surface at once, interact, mask each other

// AFTER: Incremental Integration
Step 1: Integrate component A, test
Step 2: Add component B, test combination
Step 3: Add component C, test combination
...continue until complete
Result: Each problem isolated to most recent addition
```

### No Build Process -> Daily Build + Smoke Test
```
// BEFORE: Ad-hoc Builds [ANTI-PATTERN]
- Build when "ready" (days or weeks apart)
- No automated verification
- "Works on my machine" syndrome
- Integration problems accumulate undetected

// AFTER: Daily Build + Smoke Test
- Automatic compile/link/combine every day
- Smoke test runs end-to-end verification
- Broken build = immediate fix priority
- Problems caught within 24 hours of introduction
```

### Architecture-Ignorant -> Strategy-Aligned Integration
```
// BEFORE: Bottom-Up Driven by Convenience [ANTI-PATTERN]
- Start with whatever is "ready"
- Let low-level code drive high-level design
- Contradicts information hiding
- High-level must adapt to low-level decisions

// AFTER: Strategy-Aligned Integration
- Choose strategy based on project needs
- High-level drives low-level (top-down), OR
- Risk-critical components first, OR
- Feature-oriented slices, OR
- T-shaped vertical slice to verify architecture
```

## Modes

### CHECKER
Purpose: Execute integration strategy and daily build checklists
Triggers:
  - "review our integration approach"
  - "check our build process"
  - "assess integration readiness"
Non-Triggers:
  - "which integration strategy should we use" -> APPLIER
  - "set up daily builds" -> APPLIER
Checklist: **See [checklists.md]($CLAUDE_PLUGIN_ROOT/skills/cc-integration-practices/checklists.md)**
Output Format:
  | Item | Status | Evidence | Location |
  |------|--------|----------|----------|
Severity:
  - VIOLATION: Big Bang integration, no daily build, stale smoke test
  - WARNING: Infrequent builds, incomplete smoke test
  - PASS: Meets integration and build requirements

### APPLIER
Purpose: Select integration strategy and establish daily build process
Triggers:
  - "plan integration strategy"
  - "how should we integrate these components"
  - "set up our build process"
  - "which integration order"
Non-Triggers:
  - "review our current integration" -> CHECKER

#### Integration Strategy Selection
**Evaluate in sequence. Stop at first YES - that determines your strategy.**
```
1. Is there high architectural risk or uncertainty?
   (>3 external integrations, unproven tech, novel patterns)
   YES -> T-Shaped Integration (vertical slice to verify architecture early)
   NO  -> Continue

2. Are there clear high-risk components?
   YES -> Risk-Oriented Integration (hardest parts first)
   NO  -> Continue

3. Is the system hierarchical with clear layers?
   YES -> Does high-level need early exercise?
         YES -> Top-Down (stubs for lower classes)
         NO  -> Does low-level need early verification?
               YES -> Bottom-Up (test drivers for higher)
               NO  -> Sandwich (high + low first, middle last)
   NO  -> Continue

4. Are there distinct feature sets?
   YES -> Feature-Oriented (one feature tree at a time)
   NO  -> Use Incremental with any sensible order
```

#### Daily Build Setup Procedure
```
1. Can you compile/link/combine into executable automatically?
   NO  -> Set up automated build script FIRST
   YES -> Continue

2. Is build run at least daily?
   NO  -> Schedule daily build (fixed time, off-peak)
   YES -> Continue

3. Is there a smoke test?
   NO  -> Create smoke test covering end-to-end execution
   YES -> Does it cover recent additions?
         NO  -> Update smoke test (stale test = self-deception)
         YES -> Continue

4. What happens when build breaks?
   "Fix tomorrow" -> WRONG: Fix immediately, stop all other work
   "Skip smoke test once" -> WRONG: Smoke test is the sentry
   Fix immediately -> Correct
```

Produces:
  - Integration strategy recommendation with rationale
  - Integration order/sequence
  - Daily build configuration
  - Smoke test requirements
Constraints:
  - Never let build stay broken overnight (p.704)
  - Smoke test must exercise end-to-end (p.705)
  - Check-in at least every 2 days (p.703)

## Already Built Everything Separately?
If you've built all components in isolation and are about to combine them: **STOP.**

Building separately is fine. Combining all at once means ALL interface bugs surface simultaneously - that's Big Bang. Your components aren't wasted, but add them one at a time to isolate issues to each addition.

## Benefits of Careful Integration
- Easier defect diagnosis (isolated to recent addition)
- Fewer defects slip through
- Less scaffolding code needed
- Shorter time to first working product
- Shorter overall development schedules
- Better customer relations (demonstrable progress)
- Improved developer morale
- Improved chance of project completion
- More reliable schedule estimates
- Accurate status reporting
- Improved code quality
- Less integration documentation needed


---

## Chain

| After | Next |
|-------|------|
| Integration failing | cc-debugging (STABILIZE phase) |
| Integration passing | cc-quality-practices (smoke test verification) |

