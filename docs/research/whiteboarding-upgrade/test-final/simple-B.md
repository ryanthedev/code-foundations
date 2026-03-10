# Plan: Rename whiteboarding command to plan

**Created:** 2026-03-10
**Status:** ready
**Complexity:** simple

---

## Context

Rename the user-facing command from `/code-foundations:whiteboarding` to `/code-foundations:plan` by renaming the command file. The underlying `skills/whiteboarding/` skill remains unchanged -- only the command entry point changes so users type a shorter, more intuitive name.

## Constraints

- Only the command file changes; do not rename the skill directory or skill name
- Do not update references in other files (CLAUDE.md, building/SKILL.md, etc.) -- that is a separate pass
- The renamed command must still invoke the same `code-foundations:whiteboarding` skill

---

## Implementation Phases

### Phase 1: Rename command file and update internal references
**Model:** haiku

**Goal:** Rename `commands/whiteboarding.md` to `commands/plan.md` and update the heading and any self-referencing text inside the file so it reads as `/plan` rather than `/whiteboarding`.

**Scope:**
- IN: Rename file `commands/whiteboarding.md` -> `commands/plan.md`; update the `# /whiteboarding` heading and any self-referencing text within the file
- OUT: Skill directory, CLAUDE.md, README.md, building/SKILL.md, prototype/SKILL.md, or any other files that reference the old command name

**Constraints:** The `Skill(code-foundations:whiteboarding)` invocation inside the command file must stay as-is -- that references the skill, not the command.

**Done when:**
- [ ] `commands/plan.md` exists with correct heading (`# /plan`)
- [ ] `commands/whiteboarding.md` no longer exists
- [ ] `Skill(code-foundations:whiteboarding)` call inside the file is unchanged

---

## Test Coverage

**Level:** None -- file rename with no executable code.

## Test Plan

- [ ] Verify `commands/plan.md` exists and parses valid YAML frontmatter
- [ ] Verify `commands/whiteboarding.md` is removed
- [ ] Verify the skill invocation line is unchanged

---

## Notes

- Nine files across the codebase reference `code-foundations:whiteboarding`. These should be updated in a follow-up pass to point to `code-foundations:plan`. Files: CLAUDE.md, README.md, skills/building/SKILL.md, skills/prototype/SKILL.md, skills/aposd-reviewing-module-design/SKILL.md, references/assessment-framework.md, docs/whiteboarding-example-zindex-preservation.md, commands/prototype.md.
- The `description` field in the command's YAML frontmatter should also be reviewed to ensure it no longer says "whiteboarding" where "plan" is more appropriate, but the `Skill()` call must remain `code-foundations:whiteboarding`.

---

## Execution Log

_To be filled during /code-foundations:building_

---
---

## Meta-Commentary

### Did the skill correctly route to the Simple track?

Yes. The signal table makes this unambiguous: 1 file touched, 1 known pattern (file rename), zero cross-cutting concerns, low uncertainty, 1 phase. Every signal points to Simple. The classification required no judgment call.

### Was the ceremony appropriate for this task's complexity?

Yes. The Simple track kept ceremony minimal: 2 questions, no approach comparison (the approach is obvious -- rename the file), no self-check, flat checklist format. The entire whiteboarding session would take under 5 minutes in practice. The skill's anti-rationalization table explicitly addresses "This is too simple for planning" by noting that simple tasks get the Simple track, not a pass. That is the right call here -- even a trivial rename benefits from noting the 9 files that reference the old name (captured in Notes), which a "just do it" approach might miss.

### Is the plan sufficient for a pre-gate agent?

Yes. The pre-gate agent needs: Goal (rename file + update heading), Scope (what is IN and OUT), Constraints (preserve the skill invocation), and Done-when criteria (3 verifiable items). All are present. The explicit OUT scope is especially important here -- without it, a pre-gate agent might eagerly update all 9 referencing files, which the user explicitly deferred. The constraint about preserving the `Skill(code-foundations:whiteboarding)` call prevents a common mistake where the agent renames everything containing "whiteboarding."

### Any friction or confusion from the skill instructions?

Minor points:

1. **AskUserQuestion enforcement**: The skill says "Each question below MUST use `AskUserQuestion` tool. Do NOT output questions as text." In this simulation, questions were presented inline. In a real session, this enforcement is valuable -- it forces a stop-and-wait that prevents the skill from racing ahead. No friction, just a simulation artifact.

2. **Test Coverage question feels forced for trivial tasks**: The mandatory test coverage question ("How much test coverage do you want?") is slightly awkward for a file rename. The user's answer of "None" is the only sensible choice. A possible improvement: for Simple track tasks with no executable code, default to "None" and note why, rather than presenting the full 5-option menu. This is a minor friction point, not a blocker.

3. **Model recommendation was straightforward**: The haiku keyword list includes "rename" explicitly, and Done-when has 3 items with 1 file area. Haiku is the clear choice. No ambiguity.

4. **The skill's "File hints" field is listed in the Medium/Complex template but absent from the Simple template**: This is correct -- Simple phases do not need file hints since the scope description is sufficient for 1-3 files. No confusion here.

5. **Notes section was useful**: The skill template includes a Notes section for "anything pre-gate agents should know that does not fit in phase constraints." This was the right place to capture the 9-file reference list -- it is not actionable in this plan but is critical context for the follow-up pass. Good design.

Overall, the skill handled this Simple task with appropriate lightweight ceremony. The routing was correct, the template was right-sized, and the plan provides everything a pre-gate agent needs without over-specifying.
