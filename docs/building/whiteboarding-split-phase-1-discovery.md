# Discovery: Phase 1 - Create whiteboarding-planning skill

## Files Found
- `commands/whiteboarding.md` (957 lines) -- source content to extract from
- `skills/clarify/SKILL.md` (193 lines) -- confirms full questioning protocol already exists
- `skills/` directory -- 17 existing skills, no `whiteboarding-planning/` yet

## Current State

The whiteboarding command is a single 957-line file containing both quick track logic and the full Standard/Full pipeline. The Standard/Full content spans lines 43-925 (~883 lines) and includes:

| Section | Lines | Range |
|---------|-------|-------|
| Std/Full header + task creation | 35 | 43-76 |
| Quick Reference | 15 | 78-91 |
| Crisis Invariants | 19 | 93-110 |
| Step 1: DISCOVER | 159 | 112-269 |
| Step 2: CLASSIFY | 32 | 271-301 |
| Step 3: EXPLORE | 95 | 303-396 |
| Step 4: DETAIL | 125 | 398-521 |
| Step 5: SAVE | 252 | 523-773 |
| Step 6: CHECK | 60 | 775-833 |
| Step 7: CONFIRM | 70 | 835-903 |
| Step 8: HANDOFF | 22 | 904-925 |
| "What Plan Specifies" table | 27 | 926-952 |
| Chaining | 5 | 953-957 |

Key observations:
- Questioning protocol (lines 204-248, ~45 lines) heavily overlaps with `clarify/SKILL.md` -- replaceable with "Load clarify skill"
- Code-standards template (lines 140-188, ~49 lines) is a full markdown template -- compressible to a section list
- Two separate plan schemas: Simple (78 lines, 563-640) and Medium/Complex (112 lines, 642-753) -- target merge into one
- Crisis Invariants section (19 lines) is standalone -- fold non-obvious ones into their respective steps
- Quick Reference section (15 lines) is redundant with step headers
- "What Plan Specifies" table (27 lines) is docs, not instruction -- cut

## Gaps

- No gaps between plan assumptions and reality. The source file matches the plan's description.
- The `skills/whiteboarding-planning/` directory does not exist yet (expected -- we're creating it).
- Merged schema marker burden is borderline (~39% by line count). Block-level markers for whole sections (Chosen Approach, Rejected Approaches, Assumptions, Decision Log) plus inline markers for per-phase fields should keep it readable. If not, the plan allows two short schemas.

## Prerequisites
- [x] Source file exists (`commands/whiteboarding.md`)
- [x] Clarify skill exists (`skills/clarify/SKILL.md`)
- [x] Skills directory exists for new skill creation
- [x] No dependencies on other phases

## Recommendation
BUILD -- Extract Standard/Full pipeline into `skills/whiteboarding-planning/SKILL.md`, applying all trimming targets from the plan.
