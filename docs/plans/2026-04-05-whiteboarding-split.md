# Plan: Whiteboarding Split

**Created:** 2026-04-05
**Status:** ready
**Complexity:** simple

---

## Context

The whiteboarding command is 957 lines. Quick track tasks (1-file renames, simple fixes) load the entire Standard/Full pipeline — approach comparison, pre-mortem formats, two plan schemas — that they'll never use. Split into a thin router command + a planning skill loaded via Skill() so Quick track only sees ~80 lines and Standard/Full gets focused content at ~300 lines.

## Constraints

- User entry point stays `/code-foundations:whiteboarding` — no interface change
- Quick track stays inline in the router (it's ~15 lines of logic)
- Skill assignment enforcement (every phase MUST have `**Skills:**` field) must be preserved in the planning skill
- The clarify skill (192 lines) already has the full questioning protocol — don't duplicate it

---

## Implementation Phases

### Phase 1: Create whiteboarding-planning skill
**Skills:** oberskills:skill-craft
**Gate:** Full (first phase)

**Goal:** Extract the Standard/Full pipeline into a standalone skill, trimmed to ~300 lines.

**Scope:**
- IN: Steps 1-8 (DISCOVER through HANDOFF), plan file schemas (Simple + merged Medium/Complex — load-bearing instruction, not docs), CHECK dispatch, skill assignment enforcement
- OUT: Quick track (stays in router), "What Plan Specifies vs Building Discovers" table (docs, not instruction)

**Constraints:**
- Merged schema must stay readable — if `[Medium/Complex only]` markers exceed ~30% of lines, keep two short schemas with cross-reference instead

**File hints:**
- `commands/whiteboarding.md` — source content to extract from
- `skills/clarify/SKILL.md` — confirms questioning protocol is already there

**Depends on:** None | **Unlocks:** Phase 2

**Trimming targets:**

| Section | Current | Target | How |
|---------|---------|--------|-----|
| Questioning protocol | ~50 lines | ~5 lines | "Load clarify skill" — it already has the full protocol |
| Code-standards template | ~50 lines | ~10 lines | Section list, not full markdown template |
| Two plan schemas | ~150 lines | ~60 lines | One schema with `[Medium/Complex only]` markers |
| Crisis invariants | ~18 lines | 0 | Fold non-obvious ones into the step they protect |
| EXPLORE | ~80 lines | ~40 lines | Compress research/approach/pre-mortem formats |
| DETAIL | ~120 lines | ~50 lines | Keep rules, cut verbose approach notes examples |
| "What Plan Specifies" table | ~26 lines | 0 | Cut |
| Quick Reference | ~15 lines | 0 | Redundant with step headers |

**Done when:**
- [ ] DW-1.1: `skills/whiteboarding-planning/SKILL.md` exists and is under 320 lines
- [ ] DW-1.2: All Standard/Full pipeline steps (DISCOVER through HANDOFF) are present
- [ ] DW-1.3: Plan schema is one merged template with `[Medium/Complex only]` markers (or two short schemas if markers exceed 30%)
- [ ] DW-1.4: Questioning protocol replaced with "load clarify skill" (no duplication)
- [ ] DW-1.5: Skill assignment requires `**Skills:**` on every phase — `none -- [reason]` valid, omission not

### Phase 2: Rewrite whiteboarding.md as thin router
**Skills:** none -- editing markdown instruction file, no specialized knowledge needed
**Gate:** Full (final phase)

**Goal:** Reduce the command to classification + quick track + Skill() dispatch for Standard/Full.

**Scope:**
- IN: Classification table, quick track (inline), Standard/Full routing
- OUT: All Standard/Full pipeline content (now in planning skill)

**Constraints:**
- Resolve quick track save contradiction: "write plan inline" (step 3) vs "save to docs/plans/" (step 5). Resolution: save only when user chooses to build.

**File hints:**
- `commands/whiteboarding.md` — the file being rewritten

**Depends on:** Phase 1 | **Unlocks:** None

**Done when:**
- [ ] DW-2.1: `commands/whiteboarding.md` is under 100 lines
- [ ] DW-2.2: Classification table (Quick/Standard/Full) is present
- [ ] DW-2.3: Quick track includes all 5 steps with tool calls (clarify skill dispatch, AskUserQuestion gate, conditional save to `docs/plans/` only when building, building handoff)
- [ ] DW-2.4: Standard/Full dispatches via `Skill(code-foundations:whiteboarding-planning)`
- [ ] DW-2.5: No Standard/Full pipeline content remains in the router

---

## Test Coverage

**Level:** None -- markdown-only restructuring, no executable code

## Test Plan

- [ ] Manual: Verify whiteboarding-planning skill has all Standard/Full steps
- [ ] Manual: Verify router classification table matches current
- [ ] Manual: Verify Quick track is functionally equivalent to current

---

## Execution Log

_To be filled during /code-foundations:building_
