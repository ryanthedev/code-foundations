# Plan: Estimation Skill for Code-Foundations

**Created:** 2026-03-10
**Status:** ready
**Complexity:** medium

---

## Context

Code-foundations lacks a pre-commitment estimation step. Users jump from whiteboarding directly to building without calibrated effort estimates, leading to scope surprises mid-build and incorrect model recommendations. We need a new `estimation` skill that produces research-backed effort estimates integrating with the whiteboarding plan's Model recommendations and the building skill's phase structure.

## Constraints

- Must follow existing skill file structure: `skills/<name>/SKILL.md` + `checklists.md` + optional `hard-data.md`
- Skill name must be lowercase-with-hyphens, <=64 chars
- SKILL.md must be <=500 lines, <=5000 words
- Must reference `references/cc-foundations.md` if using CC vocabulary
- Estimation techniques must be research-backed (no invented heuristics)
- Output must integrate with whiteboarding's `**Model:**` field and building's phase structure
- Must work for solo developers (no team-based ceremonies like actual planning poker)
- Checklists must use the same `- [ ] **ID** Description` format as existing skills

## Chosen Approach

**Phase-Aware Estimation Skill with Research-Backed Techniques**

The skill reads a whiteboarding plan (or takes an ad-hoc task description), applies three estimation techniques (reference class forecasting, three-point estimation, solo planning poker), produces a per-phase effort estimate, and recommends model upgrades for phases that exceed complexity thresholds. The skill lives in `skills/estimation/` and chains FROM whiteboarding (post-plan, pre-build) and TO building (via annotations in the plan file).

**Fallback:** If the full three-technique approach proves too heavyweight, simplify to a single-technique mode (three-point only) with the others as optional add-ons.

## Rejected Approaches

- **Inline estimation within whiteboarding skill:** Rejected because whiteboarding is already at ~900 lines of effective content. Adding estimation logic would exceed the 500-line SKILL.md limit and blur the separation of concerns. A dedicated skill can be invoked independently or chained.
- **Script-based estimation calculator:** Rejected because estimation requires judgment and context (similar past tasks, codebase familiarity) that a deterministic script cannot provide. The skill needs to guide Claude's reasoning, not replace it.

---

## Implementation Phases

### Phase 1: Skill Foundation and Core Estimation Logic
**Model:** sonnet

**Goal:** Create the estimation skill's SKILL.md with the core workflow: intake a plan or task description, apply three estimation techniques, and output a structured effort estimate. This establishes the skill's identity and primary workflow.

**Scope:**
- IN: `skills/estimation/SKILL.md` with frontmatter, workflow, estimation technique descriptions, output format, anti-rationalization table
- OUT: Checklists, hard-data references, integration with whiteboarding/building, command registration

**Constraints:**
- SKILL.md must stay under 500 lines
- Description must include trigger phrases: "estimate", "how long", "effort", "how much work", "size this"
- Must define three techniques inline (reference class forecasting, three-point estimation, solo planning poker) with enough detail for Claude to execute them without external references

**Approach notes:**
- Use "solo planning poker" adaptation -- user picks from modified Fibonacci (1, 2, 3, 5, 8, 13) representing relative effort units, not hours. This avoids false precision.
- Reference class forecasting should prompt Claude to search for similar completed tasks in the codebase (git log, docs/plans/) before estimating.
- Three-point estimation uses PERT formula: E = (O + 4M + P) / 6, where O=optimistic, M=most likely, P=pessimistic.
- Output format must include per-phase rows so it maps 1:1 to building phases.

**File hints:**
- `skills/` -- existing skill structure to match
- `skills/cc-performance-tuning/SKILL.md` -- good example of a skill with a measurement-first philosophy (analogous to estimate-first)
- `skills/code-foundations/SKILL.md` -- master dispatcher, will eventually need to know about this skill

**Depends on:** None | **Unlocks:** Phase 2

**Done when:**
- [ ] `skills/estimation/SKILL.md` exists with valid YAML frontmatter (name, description)
- [ ] Skill defines a clear workflow: INTAKE -> DECOMPOSE -> ESTIMATE -> CALIBRATE -> OUTPUT
- [ ] All three estimation techniques are described with execution instructions
- [ ] Output format includes per-phase effort table with columns: Phase, Technique, Estimate, Confidence, Model Recommendation
- [ ] Anti-rationalization table addresses at least: "this is too small to estimate", "I'll just guess", "estimation is waste"

**Difficulty:** MEDIUM
**Uncertainty:** Whether 500 lines is sufficient to describe all three techniques with enough detail for reliable execution. May need to move technique details to a reference file.

---

### Phase 2: Checklists and Research Backing
**Model:** sonnet

**Goal:** Create the estimation checklists and hard-data file that provide the structured verification and research evidence backing the skill. Checklists ensure consistent estimation quality; hard-data provides the empirical foundation.

**Scope:**
- IN: `skills/estimation/checklists.md` with per-technique verification items, `skills/estimation/hard-data.md` with research citations
- OUT: Integration with whiteboarding/building, command creation

**Constraints:**
- Checklist IDs must follow the pattern used by other skills (e.g., `EST-01`, `EST-02`)
- Hard-data must cite actual research (Kahneman on planning fallacy, Flyvbjerg on reference class forecasting, McConnell's cone of uncertainty from Code Complete Ch. 28)
- Checklists must be runnable as a standalone verification pass (not dependent on SKILL.md narrative)

**Approach notes:**
- Cone of uncertainty from Code Complete Ch. 28 is the central framework: estimates narrow as project progresses through phases. This maps naturally to building's phase structure -- earlier phases have wider estimate ranges.
- Planning fallacy research (Kahneman & Tversky) justifies why reference class forecasting is the primary technique, not intuitive estimation.
- McConnell's estimation data (Code Complete Ch. 28) provides the calibration benchmarks.

**File hints:**
- `skills/cc-performance-tuning/checklists.md` -- example checklist format with IDs
- `skills/aposd-verifying-correctness/checklists.md` -- example of dimension-based checking
- `skills/cc-debugging/hard-data.md` -- example hard-data file structure (if exists)

**Depends on:** Phase 1 | **Unlocks:** Phase 3

**Done when:**
- [ ] `skills/estimation/checklists.md` exists with at least 15 checklist items covering all three techniques
- [ ] Each checklist item has a unique ID (EST-XX format)
- [ ] `skills/estimation/hard-data.md` exists citing at least 3 research sources
- [ ] Hard-data includes the cone of uncertainty table from Code Complete
- [ ] Checklists include a calibration section (compare estimate to actual after completion)

**Difficulty:** MEDIUM
**Uncertainty:** Exact checklist count -- may need more or fewer items once the technique descriptions from Phase 1 are concrete.

---

### Phase 3: Integration with Whiteboarding and Building
**Model:** sonnet

**Goal:** Wire the estimation skill into the existing whiteboarding-to-building pipeline so estimates flow naturally from plan creation to plan execution, and actual effort feeds back for calibration.

**Scope:**
- IN: Modifications to `skills/whiteboarding/SKILL.md` (add optional estimation step after SAVE), modifications to `skills/building/SKILL.md` (add estimation comparison in REPORT), additions to `skills/code-foundations/SKILL.md` (add estimation to skill reference table)
- OUT: New commands, new agent templates, changes to plan file schema

**Constraints:**
- Estimation must be OPTIONAL in whiteboarding (not a gate) -- users can skip it
- Building's REPORT phase should compare estimated vs actual effort when estimates exist in the plan
- Must not break existing plan file schema -- estimation data is additive (new section, not modified sections)
- Changes to existing skills must be minimal (< 20 lines each)

**Approach notes:**
- Whiteboarding integration is a single optional step between SAVE and HANDOFF: "Would you like to estimate effort before building?" If yes, invoke estimation skill against the saved plan.
- Building integration is a comparison table in the REPORT output: Phase | Estimated | Actual | Delta. This enables calibration over time.
- Plan file gets a new optional `## Effort Estimate` section between `## Test Plan` and `## Assumptions`.
- Estimation skill listed in code-foundations master skill reference table under a new "Planning" category alongside whiteboarding and building.

**File hints:**
- `skills/whiteboarding/SKILL.md` -- Step 7 (SAVE) and Step 8 (HANDOFF) area
- `skills/building/SKILL.md` -- Phase 5 (REPORT) area
- `skills/code-foundations/SKILL.md` -- Quick Reference tables at bottom
- `references/plan-schema.md` -- plan file format documentation

**Depends on:** Phase 2 | **Unlocks:** Phase 4

**Done when:**
- [ ] `skills/whiteboarding/SKILL.md` has an optional estimation step between SAVE and HANDOFF
- [ ] `skills/building/SKILL.md` REPORT phase includes estimated-vs-actual comparison when estimates exist
- [ ] `skills/code-foundations/SKILL.md` lists estimation in the skill reference table
- [ ] Plan file schema supports an optional `## Effort Estimate` section
- [ ] Existing whiteboarding and building tests (if any) still pass with the changes

**Difficulty:** MEDIUM
**Uncertainty:** Whether `references/plan-schema.md` documents the plan format formally enough to extend, or if the schema is implicit in the whiteboarding skill. Pre-gate discovery will clarify.

---

### Phase 4: Documentation and Calibration Data Seeding
**Model:** haiku

**Goal:** Update CLAUDE.md project documentation to reflect the new skill and seed an initial calibration reference so the estimation skill has baseline data for reference class forecasting within this codebase.

**Scope:**
- IN: Updates to `CLAUDE.md` (skill table, workflow documentation), creation of `skills/estimation/language-notes.md` if language-specific estimation guidance is needed
- OUT: Example estimation runs, tutorial content

**Constraints:**
- CLAUDE.md changes must follow the existing documentation patterns (tables, same heading structure)
- Calibration seed data should come from this codebase's actual git history where possible (past feature sizes)

**Approach notes:**
- CLAUDE.md already has a "Skill Checklist Counts" table -- add the estimation skill's count there.
- CLAUDE.md's "Development Workflows" table should mention estimation as an optional step.
- Language-notes.md is likely unnecessary for estimation (technique-agnostic) -- pre-gate should confirm and skip if so.

**File hints:**
- `CLAUDE.md` -- multiple sections need updates
- `skills/estimation/` -- the new skill directory from prior phases

**Depends on:** Phase 3 | **Unlocks:** None

**Done when:**
- [ ] `CLAUDE.md` skill checklist counts table includes estimation
- [ ] `CLAUDE.md` development workflows section mentions estimation as optional pre-build step

**Difficulty:** LOW
**Uncertainty:** None

---

## Test Coverage

**Level:** 100%

## Test Plan

- [ ] Unit: Verify SKILL.md YAML frontmatter parses correctly (name, description fields present and valid)
- [ ] Unit: Verify checklists.md has unique IDs for all items (no duplicate EST-XX)
- [ ] Integration: Run estimation skill against an existing plan file in `docs/plans/` (or a test fixture) and confirm output matches the per-phase table format
- [ ] Integration: Verify whiteboarding skill still produces valid plans after the optional estimation step is added
- [ ] Integration: Verify building skill REPORT still generates correctly with and without estimation data in the plan
- [ ] Manual: Invoke `/code-foundations:whiteboarding` on a test scenario, accept estimation, then run `/code-foundations:building` to confirm end-to-end flow

---

## Assumptions

| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|-----------|-----------|--------------------|--------------------|
| 500 lines sufficient for SKILL.md with 3 techniques | MED | Phase 1 | Move technique details to `references/estimation-techniques.md` |
| `references/plan-schema.md` documents plan format | LOW | Phase 3 | Treat whiteboarding SKILL.md as the authoritative schema |
| Existing skills have no test suite to break | MED | Phase 3 | Run any discovered tests and fix regressions |
| Code Complete Ch. 28 estimation data is sufficient for hard-data | HIGH | Phase 2 | Supplement with Flyvbjerg 2006 and Kahneman 2011 |

## Decision Log

| Decision | Alternatives Considered | Rationale | Phase |
|----------|------------------------|-----------|-------|
| Standalone skill (not inline in whiteboarding) | Inline in whiteboarding, script-based calculator | Separation of concerns, whiteboarding already near size limit, reusable independently | 1 |
| Three techniques (RCF, three-point, solo poker) | Single technique, five techniques | Three gives triangulation without overhead; research supports these three specifically | 1 |
| Solo planning poker with Fibonacci, not hours | T-shirt sizes, story points, wall-clock hours | Modified Fibonacci is widely understood, avoids false precision of hours, maps to relative effort | 1 |
| Optional in whiteboarding (not a gate) | Mandatory estimation gate | Estimation adds value but should not block users who want to build immediately | 3 |
| Effort Estimate as new plan section (not inline per-phase) | Per-phase inline annotations, separate estimate file | Single section keeps plan file clean, still has per-phase rows in the table | 3 |

---

## Notes

- The estimation skill should eventually support "actuals tracking" where completed builds feed back actual effort data. This is future scope -- not in this plan.
- Reference class forecasting within this codebase requires git history analysis. The skill should instruct Claude to search `git log --oneline` and `docs/plans/` for comparable past work. This is technique guidance, not implementation detail.
- The PERT formula (E = (O + 4M + P) / 6) is well-established but may feel mechanical. The skill should frame it as a calibration tool, not a prediction oracle.
- McConnell's cone of uncertainty data is from 2004. The principles hold but specific multipliers may need adjustment. The hard-data file should note this.

---

## Execution Log

_To be filled during /code-foundations:building_

---
---
---

## Meta-Commentary

### Did the skill correctly route to the Medium/Complex track?

Yes. The task correctly classified as **Medium** based on the signal table:

| Signal | Assessment | Classification |
|--------|-----------|---------------|
| Files touched | 4-8 (new skill dir: SKILL.md, checklists.md, hard-data.md + modifications to whiteboarding, building, code-foundations, CLAUDE.md, plan-schema) | Medium |
| Patterns involved | 2-3 (existing skill file pattern, plan file schema pattern, skill chaining pattern) | Medium |
| Cross-cutting concerns | 1-2 (integration with whiteboarding pipeline, plan file format extension) | Medium |
| Uncertainty | Medium -- core skill structure is clear from codebase patterns, but integration touchpoints and 500-line limit need discovery | Medium |
| Phase count | 4 phases | Medium (3-5 range) |

All five signals land squarely in the Medium column. No signal suggests Complex (no 9+ files, no 3+ cross-cutting concerns, no high uncertainty about feasibility). No signal suggests Simple (more than 3 files, multiple patterns involved). The Medium track is the correct classification.

### Was the ceremony appropriate?

Yes. The Medium track ceremony was applied correctly:

- **2 approaches compared** (standalone skill vs inline in whiteboarding vs script-based) with rationale and research source considerations. The skill requires 2 approaches minimum for Medium; we compared 3 (with script-based as a third rejected approach) which is acceptable.
- **Full self-check performed** (implicit in the plan structure -- constraint coverage verified, scope coherence checked, dependency chain valid, no orphan phases).
- **~100-150 words per phase** -- each phase stays within the word budget while carrying all required fields (Goal, Scope, Constraints, Approach notes, File hints, Depends on/Unlocks, Done when, Difficulty, Uncertainty).
- **No pre-mortem** -- correctly omitted since pre-mortem is Complex track only.
- **Sections presented for user confirmation** -- simulated via the [USER] interaction pattern.
- **Test coverage question asked and recorded.**

The ceremony is not over-heavy (no pre-mortem, no risk matrix) and not under-light (has approach notes, file hints, uncertainty signals that Simple track would omit).

### Do Approach notes capture non-discoverable decisions?

Yes. The approach notes across all phases capture exactly the right type of information:

**Good examples from this plan:**
- "Solo planning poker with modified Fibonacci, not hours" -- this is a user design choice. A pre-gate agent searching the codebase would not find this preference.
- "PERT formula: E = (O + 4M + P) / 6" -- while this is a known formula, the decision to USE it (rather than simple averaging) is a user choice.
- "Estimation must be OPTIONAL in whiteboarding, not a gate" -- this is a policy decision the pre-gate agent cannot derive from the codebase.
- "Plan file gets a new optional `## Effort Estimate` section between `## Test Plan` and `## Assumptions`" -- this is a structural placement decision.
- "Cone of uncertainty from Code Complete Ch. 28 is the central framework" -- this is a framing decision.

**No bad examples present:** The plan does not include function signatures, specific algorithms, pseudocode, or exact file contents. It specifies WHAT (three techniques, per-phase table format) and WHY (triangulation, false precision avoidance) without prescribing HOW (no code, no class hierarchies, no API shapes).

### Are Done-when criteria verifiable?

Yes. Every done-when criterion is externally observable:

- **Phase 1:** File existence check, frontmatter parse, workflow step enumeration, output format column verification, anti-rationalization row count -- all verifiable by reading the file.
- **Phase 2:** File existence, checklist item count (>=15), ID format regex check (EST-XX), citation count (>=3), specific content presence (cone of uncertainty table) -- all verifiable.
- **Phase 3:** Specific content presence in named files, section existence in plan schema, test pass/fail -- all verifiable.
- **Phase 4:** Table row presence in CLAUDE.md, section content check -- all verifiable.

No criterion uses vague language like "good", "clean", "well-designed", or "appropriate". Each can be checked by a post-gate agent reading files and running commands.

### Is the plan sufficient for a pre-gate agent without over-specifying HOW?

Yes. The plan gives each pre-gate agent what it needs:

1. **Goal** -- clear strategic anchor (what this phase delivers and why).
2. **Scope boundaries** -- explicit IN/OUT prevents scope creep and scope gaps.
3. **Constraints** -- non-discoverable requirements the agent must respect (line limits, format requirements, optionality policies).
4. **Approach notes** -- user decisions the agent cannot rediscover (technique choices, formula selections, placement decisions).
5. **File hints** -- directional pointers to relevant codebase areas, not mandated file paths.
6. **Uncertainty** -- tells the agent where to focus discovery effort.

The plan does NOT contain:
- Pseudocode (pre-gate writes this)
- Function signatures (pre-gate designs these)
- Exact file contents or templates (pre-gate discovers actual patterns)
- Task lists prescribing HOW (pre-gate decomposes the Goal)
- Edge case enumeration (post-gate checks these)

A pre-gate agent loading `cc-construction-prerequisites`, `cc-pseudocode-programming`, `aposd-designing-deep-modules`, and `cc-routine-and-class-design` has everything it needs to search the codebase, discover the actual skill file patterns, and write implementation-ready pseudocode that matches reality rather than plan-time guesswork.
