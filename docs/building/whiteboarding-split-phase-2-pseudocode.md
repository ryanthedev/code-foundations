# Pseudocode: Phase 2 - Rewrite whiteboarding.md as thin router

## DW Verification

| DW-ID | Done-When Item | Status | Pseudocode Section |
|-------|---------------|--------|-------------------|
| DW-2.1 | `commands/whiteboarding.md` is under 100 lines | COVERED | Overall structure |
| DW-2.2 | Classification table (Quick/Standard/Full) is present | COVERED | Section 1: Classification |
| DW-2.3 | Quick track includes all 5 steps with tool calls (clarify skill dispatch, AskUserQuestion gate, conditional save to `docs/plans/` only when building, building handoff) | COVERED | Section 2: Quick Track |
| DW-2.4 | Standard/Full dispatches via `Skill(code-foundations:whiteboarding-planning)` | COVERED | Section 3: Standard/Full Dispatch |
| DW-2.5 | No Standard/Full pipeline content remains in the router | COVERED | Overall structure |

**All items COVERED:** YES

## Files to Create/Modify
- `commands/whiteboarding.md` -- complete rewrite (957 lines -> ~85 lines)

## Pseudocode

### commands/whiteboarding.md [DW-2.1, DW-2.2, DW-2.3, DW-2.4, DW-2.5]

The entire file is one artifact. Structure:

```
FRONTMATTER
  description: "Brainstorm and plan features" (unchanged)

TITLE: whiteboarding

CONTRACT STATEMENT: one line about plan being contract between whiteboarding and building

SECTION 1: CLASSIFICATION [DW-2.2]
  Classification table with three rows:
    Quick -- small focused ask, user knows what they want
    Standard (Medium) -- feature request, multiple concerns, approach comparison
    Full (Complex) -- redesign, migrate, cross-cutting, high uncertainty
  Default to Quick. Only upgrade if signals clearly demand it.

SECTION 2: QUICK TRACK [DW-2.3]
  Header: "One pass. No task pipeline. No subagent check."

  Step 1: Scan codebase
    Check for docs/code-standards.md
    If exists: read it, check staleness (git rev-list count)
      0 commits: trust it
      1-20: spot-check
      20+: regenerate
    If missing: full codebase search, generate docs/code-standards.md
      Section list only (not full template): Architecture, Naming, Imports,
        Error Handling, File Organization, Testing, Technology Decisions,
        Forbidden Patterns, Similar Implementations
      Include base-commit and generated-date markers
    Grep for similar patterns. 30 seconds, not 5 minutes.

  Step 2: Ask 1-2 questions max via AskUserQuestion
    Only if genuinely ambiguous
    Load Skill(code-foundations:clarify) to classify fault type + ambiguity direction
    If already clear, skip to step 3

  Step 3: Write plan inline
    Simple Track template (1-2 phases, 50-75 words each)
    Inline template:
      Phase N: Name
      Skills: [matched or none -- reason]
      Goal: one sentence
      Scope: IN / OUT
      Done when: DW-N.1 verifiable criterion

  Step 4: Present and ask via AskUserQuestion
    "Here's the plan. Build it, adjust it, or tell me what to do?"

  Step 5: If building
    Save to docs/plans/YYYY-MM-DD-<topic>.md with plan header
      (wrap inline plan in: title, created date, status: ready, complexity: simple,
       context section, constraints section, Implementation Phases,
       Test Coverage, Execution Log)
    git add + git commit
    Suggest default thinking effort
    Run /code-foundations:building docs/plans/<plan>.md

  Closing: under 2 minutes from invocation to handoff

SECTION 3: STANDARD / FULL TRACK [DW-2.4, DW-2.5]
  One line: dispatch to Skill(code-foundations:whiteboarding-planning)
  That's it -- no pipeline content in router

SECTION 4: CHAIN
  Receives from: user request
  Chains to: building (via saved plan file)
```

Line budget estimate:
- Frontmatter + title + contract: 8 lines
- Classification: 12 lines (header, table, default note)
- Quick track: 55 lines (header + 5 steps with inline template)
- Standard/Full dispatch: 8 lines
- Chain: 5 lines
- Separators and blanks: ~7 lines
Total: ~95 lines (under 100)

## Design Notes

1. **Code-standards generation stays inline in quick track** rather than referencing the planning skill. Quick track must be self-contained -- loading the planning skill defeats the purpose of the split. The section list (9 items) replaces the full 50-line template.

2. **Simple Track template inlined** in step 3 as a minimal 6-line template. This replaces the reference to "Simple Track template" which was in the S/F pipeline's Step 4 DETAIL section.

3. **Save contradiction resolved** per plan: step 3 writes the plan inline (in the conversation), step 5 saves to file ONLY when user chooses to build. The plan file wraps the inline plan with the standard header (title, date, status, complexity, context, etc.).

4. **Skills field requirement preserved** in the inline template via the `Skills:` line. This matches the enforcement from Phase 1's planning skill.

5. **AskUserQuestion tool calls** at steps 2 and 4. Step 2 is conditional (only if ambiguous). Step 4 is the gate that determines whether to save+build.
