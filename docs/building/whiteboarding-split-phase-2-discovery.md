# Discovery: Phase 2 - Rewrite whiteboarding.md as thin router

## Files Found
- `commands/whiteboarding.md` (957 lines) -- the file to rewrite
- `skills/whiteboarding-planning/SKILL.md` (300 lines) -- Phase 1 output, Standard/Full pipeline
- `skills/clarify/SKILL.md` (193 lines) -- questioning protocol (referenced by quick track step 2)

## Current State

The file has three zones:

| Zone | Lines | Range |
|------|-------|-------|
| Frontmatter + title + plan-contract statement | 8 | 1-8 |
| Classification table + quick track | 31 | 10-39 |
| Standard/Full pipeline (to be removed) | 918 | 41-957 |

Quick track currently has 5 steps:
1. Scan codebase -- references "see Code Standards below" (broken once S/F content is removed)
2. Ask 1-2 questions -- dispatches clarify skill
3. Write plan inline -- "don't save unless 2+ phases"
4. Present and ask -- "Build it, adjust it, or tell me what to do?"
5. If building -- save to docs/plans/, commit, run building

**Contradiction (from plan):** Step 3 says "write plan inline / don't save to file unless 2+ phases" but step 5 says "save to docs/plans/". Resolution per plan: save only when user chooses to build.

**Broken reference:** Step 1 says "see Code Standards below" which points to S/F content being removed. The planning skill (SKILL.md lines 32-47) has the full code-standards generation logic. Quick track needs a self-contained instruction for code-standards handling.

## Gaps

1. The "see Code Standards below" reference in quick track step 1 will dangle after removing S/F content. Fix: inline a minimal instruction (read if exists, generate with section list from planning skill, or skip for quick tasks) or point to a shared reference.

2. The plan says quick track needs "all 5 steps with tool calls" -- current step 1 (scan) has no tool call, it's just a Grep instruction. The DW item says "clarify skill dispatch, AskUserQuestion gate, conditional save to docs/plans/ only when building, building handoff" -- these are the specific tool calls, not 5 separate tool calls.

3. No Simple Track template is included in the current quick track -- step 3 says "Simple Track template" referencing the template in Step 4 DETAIL (now in planning skill). The router needs a minimal inline template or reference.

## Prerequisites
- [x] `skills/whiteboarding-planning/SKILL.md` exists (Phase 1 complete)
- [x] `commands/whiteboarding.md` exists and is the rewrite target
- [x] `skills/clarify/SKILL.md` exists for questioning dispatch
- [x] Phase 1 completed

## Recommendation
BUILD -- Rewrite `commands/whiteboarding.md` as thin router (<100 lines) with classification + quick track inline + Skill() dispatch for Standard/Full.
