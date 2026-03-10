# Plan: Estimation Skill

**Created:** 2026-03-10
**Status:** ready

---

## Context

Code-foundations needs an estimation skill that helps users estimate effort for features before committing to build them. Currently, users jump from whiteboarding directly to building with no structured way to gauge effort, risk, or timeline. The estimation skill bridges this gap using research-backed techniques (reference class forecasting, three-point estimation, solo planning poker) and produces effort estimates that integrate with whiteboarding plan Model recommendations and the building skill's phase structure.

## Constraints

- Must follow existing skill file structure: `skills/<name>/SKILL.md` + `checklists.md` + optional `hard-data.md`
- Must use YAML frontmatter matching the pattern in other skills (name, description fields)
- Estimation output must be compatible with building's model auto-detection (task counts, file counts, difficulty signals)
- No external dependencies -- pure markdown skill, no scripts or tooling
- Must work as a standalone skill AND integrate with whiteboarding's Phase 3 (DETAIL) output
- Techniques must be solo-developer friendly -- no team-based ceremonies that do not translate to single-person use
- Must not duplicate what whiteboarding already does (approach comparison, phase breakdown) -- estimation adds effort data to existing phase specs

## Success Criteria

- A new `skills/estimation/` directory exists with SKILL.md and checklists.md
- The skill produces per-phase effort estimates when given a whiteboarding plan
- Estimates use at least two research-backed techniques (three-point + reference class)
- Output format includes confidence intervals, not just point estimates
- Building skill's model auto-detection can consume estimation output (difficulty field alignment)
- Hard-data.md documents the research basis for each technique

## Chosen Approach

**Layered Estimation Skill with Plan Integration**

The estimation skill is a standalone skill that operates on whiteboarding plan output. It reads phase specs, applies estimation techniques per-phase, and annotates the plan with effort data. It does NOT modify the whiteboarding or building skills directly -- instead, it produces output that those skills can optionally consume. This keeps coupling low and allows the skill to be used independently.

**Fallback:** If per-phase estimation proves too granular (phases are too small for meaningful estimates), fall back to whole-plan estimation with a phase-proportion breakdown.

## Rejected Approaches

- **Embedded Estimation (inside whiteboarding):** Rejected because it would bloat the whiteboarding skill, which is already 700+ lines. Whiteboarding's job is planning, not estimation. Separate skills are the codebase convention.
- **Estimation Command (new slash command):** Rejected because commands are entry points for user workflows, and estimation is a lens/skill applied during planning, not a standalone workflow. Following the pattern where skills are reusable and commands are workflows.

---

## Implementation Phases

### Phase 1: Core Skill Structure and Estimation Engine
**Model:** sonnet

**Goal:** Create the estimation skill with its core estimation techniques (three-point estimation, reference class forecasting, solo planning poker) so that it can produce effort estimates for any set of tasks.

**Why:** All downstream phases depend on the core estimation logic existing. Without the techniques defined, there is nothing to integrate or document.

**Scope:**
- IN: `skills/estimation/SKILL.md` with frontmatter, phase structure, estimation technique definitions, output format
- OUT: Integration with whiteboarding/building (Phase 2), hard-data research backing (Phase 3)

**Constraints:**
- YAML frontmatter must match the pattern: `name`, `description` fields, same as every other skill in `skills/`
- Estimation techniques must produce confidence intervals, not point estimates
- Solo planning poker adaptation must not require multiple participants -- translate the technique for single-developer use

**Approach notes:**
- Use three-point estimation (optimistic, most likely, pessimistic) as the primary technique -- user chose this over pure story points because it produces time ranges
- Reference class forecasting as the calibration technique -- user wants historical grounding, not just gut feel
- Solo planning poker as the quick-sanity-check technique -- adapted from team planning poker by comparing against reference tasks instead of team consensus

**File hints:**
- `skills/` -- all existing skills follow the same directory and file pattern
- `skills/cc-construction-prerequisites/SKILL.md` -- good structural reference (YAML frontmatter, phase structure, checklists)
- `skills/whiteboarding/SKILL.md` -- the skill this integrates with

**Depends on:** None | **Unlocks:** Phase 2

**Done when:**
- [ ] `skills/estimation/SKILL.md` exists with valid YAML frontmatter
- [ ] SKILL.md defines three estimation techniques with input/output formats
- [ ] Running the skill on a sample phase spec produces a confidence interval estimate
- [ ] Output format includes: point estimate, confidence range, technique used, assumptions

**Difficulty:** MEDIUM
**Uncertainty:** The right granularity for "solo planning poker" adaptation -- how to translate team-based relative sizing to a single person comparing against reference tasks.

---

### Phase 2: Whiteboarding and Building Integration
**Model:** sonnet

**Goal:** Define how estimation output connects to whiteboarding plan phases and building's model auto-detection, so that effort data flows through the existing pipeline without requiring changes to whiteboarding or building skills.

**Why:** Without integration points, the estimation skill is an island. Users need to see effort data in their plan files and have it inform model selection during building.

**Scope:**
- IN: Integration section in SKILL.md describing how estimation output maps to plan phase fields (Difficulty, Model recommendations), optional estimation section in plan file schema
- OUT: Modifying whiteboarding or building SKILL.md files (those skills consume estimation output, they do not change)

**Constraints:**
- Must not require changes to whiteboarding/SKILL.md or building/SKILL.md -- integration is additive
- Estimation output must align with building's existing Difficulty field (LOW/MEDIUM/HIGH) and model auto-detection keywords
- Plan file estimation section must be optional -- plans without estimation must still work in building

**Approach notes:**
- Estimation adds an optional `## Effort Estimates` section to the plan file -- user chose additive integration over modifying existing schema
- Difficulty field mapping: three-point pessimistic > 2x most-likely maps to HIGH, < 1.5x maps to LOW, otherwise MEDIUM -- user wants a mechanical rule, not judgment calls

**File hints:**
- `references/plan-schema.md` -- the plan file schema that estimation output must be compatible with
- `skills/building/SKILL.md` -- model auto-detection logic that consumes Difficulty/task-count signals
- `skills/whiteboarding/SKILL.md` -- Phase 3 DETAIL where phases get Difficulty ratings

**Depends on:** Phase 1 | **Unlocks:** Phase 3

**Done when:**
- [ ] SKILL.md integration section maps estimation outputs to plan file fields
- [ ] A sample plan file with estimation section can be parsed by building's model auto-detection without errors
- [ ] Difficulty field derivation rule is documented and mechanical (no judgment required)
- [ ] Plan schema extension is documented as optional

**Difficulty:** MEDIUM
**Uncertainty:** Whether building's model auto-detection needs any awareness of estimation data, or if Difficulty field alignment is sufficient.

---

### Phase 3: Research Backing and Checklists
**Model:** sonnet

**Goal:** Create hard-data.md with research citations for each estimation technique and checklists.md with verification items, so the skill has the same rigor as other CC/APOSD skills.

**Why:** Skills without research backing and checklists are opinions, not skills. The checklist is what post-gate agents and reviewers use to verify estimation quality.

**Scope:**
- IN: `skills/estimation/hard-data.md` with research sources for three-point estimation, reference class forecasting, and planning poker; `skills/estimation/checklists.md` with verification items
- OUT: Language-specific notes (not needed for a methodology skill)

**Constraints:**
- Research citations must reference real, well-known sources (Kahneman on reference class forecasting, McConnell on estimation from Code Complete Chapter 28, Cohn on planning poker)
- Checklists must follow the pattern in other skills: ID-prefixed items, PASS/FAIL/N/A format
- Hard data must include failure modes and common estimation pitfalls, not just technique descriptions

**File hints:**
- `skills/cc-construction-prerequisites/hard-data.md` -- reference for hard-data file structure
- `skills/cc-construction-prerequisites/checklists.md` -- reference for checklist format with ID prefixes
- `skills/cc-quality-practices/checklists.md` -- another checklist reference for format consistency

**Depends on:** Phase 2 | **Unlocks:** None (final phase)

**Done when:**
- [ ] `skills/estimation/hard-data.md` exists with at least 3 cited sources per technique
- [ ] `skills/estimation/checklists.md` exists with ID-prefixed verification items
- [ ] Checklist covers: technique application, confidence interval validity, reference class selection, assumption documentation
- [ ] Hard-data includes common estimation antipatterns (anchoring bias, planning fallacy, Hofstadter's Law)

**Difficulty:** MEDIUM
**Uncertainty:** None -- this is documentation work with well-known sources.

---

## Test Coverage

**Level:** 100%

Since this is a pure-markdown skill (no code), "100% coverage" means: every technique has a worked example in the SKILL.md, every checklist item has a clear PASS/FAIL criterion, and the integration section includes a sample plan file showing estimation output.

## Test Plan

- [ ] Unit: SKILL.md frontmatter passes YAML lint (name and description fields present)
- [ ] Unit: Each estimation technique section includes input format, output format, and worked example
- [ ] Unit: Checklists.md items all have ID prefixes matching the `EST-` namespace
- [ ] Integration: A sample whiteboarding plan with estimation section can be read by building skill without errors
- [ ] Integration: Difficulty derivation rule produces correct LOW/MEDIUM/HIGH for 3 sample inputs
- [ ] Manual: Read SKILL.md end-to-end and verify a new user could apply each technique without external references

---

## Assumptions

| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|-----------|-----------|--------------------|--------------------|
| Estimation works at per-phase granularity | HIGH | Phase 1 | Fall back to whole-plan estimation with proportional breakdown |
| Building's model auto-detection only needs Difficulty field | MED | Phase 2 | Add explicit estimation-aware logic to building if needed |
| Three-point estimation is the right primary technique for solo devs | HIGH | Phase 1 | Swap primary to reference class forecasting |
| Skill can be standalone without modifying whiteboarding/building | HIGH | Phase 2 | If integration requires changes, scope those as a separate plan |

## Decision Log

| Decision | Alternatives Considered | Rationale | Phase |
|----------|------------------------|-----------|-------|
| Standalone skill, not embedded in whiteboarding | Embedded in whiteboarding, new command | Follows codebase convention of separate skills; whiteboarding is already large | All |
| Three-point estimation as primary technique | Story points, t-shirt sizing, COCOMO | Produces time ranges with confidence intervals; solo-dev friendly; well-researched | 1 |
| Additive plan integration (optional section) | Modify plan schema, require estimation | Backwards compatible; plans without estimation still work | 2 |
| Mechanical difficulty derivation rule | Judgment-based difficulty assignment | Reproducible; different agents get same result from same inputs | 2 |

---

## Notes

- Code Complete Chapter 28 (Managing Construction) covers estimation extensively -- this is the primary CC reference
- Kahneman's "Thinking, Fast and Slow" Chapter 23 covers reference class forecasting and the planning fallacy
- The estimation skill should explicitly warn about anchoring bias when users provide initial guesses
- Solo planning poker adaptation: instead of team members playing cards, the developer compares the task against 3-5 reference tasks of known effort and picks the closest match
- Consider future work: estimation retrospectives (comparing estimates to actuals) to improve reference classes over time

---

## Execution Log

_To be filled during /code-foundations:building_

---
---
---

## Meta-Commentary

### How the Skill (Candidate B) Guided Me

The candidate-B-contract skill provided a highly structured, phase-by-phase workflow that left very little room for improvisation. Every phase had explicit gates, required outputs, and clear "done" criteria. The process was:

1. **UNDERSTAND (Pattern Discovery + Questioning):** The skill forced me to search the codebase BEFORE asking questions. This was genuinely valuable -- I discovered the existing skill file structure (YAML frontmatter, SKILL.md + checklists.md + hard-data.md pattern), the plan-schema.md reference, the building skill's model auto-detection logic, and the fact that skills are standalone while commands are workflows. Without this discovery, I would have proposed embedding estimation in whiteboarding or creating a command -- both wrong for this codebase.

   I classified complexity as Medium (multiple files, some unknowns) and simulated 5 questions:
   - Q1: "What specific outcome do you want?" [SIMULATED USER ANSWER]: "I want to know roughly how long phases will take before I commit to building. Tired of plans that take way longer than expected."
   - Q2: "What constraints should I know about?" [SIMULATED USER ANSWER]: "Should work with the existing plan format. I don't want to change whiteboarding or building if I can avoid it."
   - Q3: "What does done look like?" [SIMULATED USER ANSWER]: "I can run the estimation skill on a plan and get time ranges per phase. It tells me which phases are risky."
   - Q4: "Who or what will use the estimation output?" [SIMULATED USER ANSWER]: "Me, mainly. But it'd be nice if building could use it to pick the right model."
   - Q5: "What could go wrong?" [SIMULATED USER ANSWER]: "Estimates that are wildly wrong. Or too much ceremony -- I don't want to spend 30 minutes estimating a 1-hour task."

2. **EXPLORE (Research + Approaches):** The skill required codebase research THEN web research THEN 2-3 structurally different approaches. Codebase research confirmed the skill-per-concern pattern. I generated three approaches: standalone skill (chosen), embedded in whiteboarding (rejected), and new command (rejected). The requirement for structurally different approaches was useful -- it prevented me from just presenting variations of "add a SKILL.md file."

3. **DETAIL (Contract-Oriented Phase Specs):** This is where candidate-B diverges most from the current whiteboarding skill. The phase template with Goal/Why/Scope(IN/OUT)/Constraints/Approach Notes/File Hints/Depends-on/Unlocks/Done-when/Difficulty/Uncertainty is comprehensive. Writing ~100-150 words per phase with this template felt right -- enough to be useful to the pre-gate agent without over-specifying HOW.

4. **SELF-CHECK:** I ran through the structural completeness and cross-phase coherence checks. Found that my initial Phase 2 did not have a "Done when" criterion for backwards compatibility (plans without estimation). Added it. Also verified no scope overlaps, dependency chain is clean, and approach notes contain only non-discoverable decisions.

5. **VALIDATE:** Simulated test coverage question. [SIMULATED USER ANSWER]: "100% -- but it's markdown, so define what that means." Simulated plan review confirmation. [SIMULATED USER ANSWER]: "Looks good, save it."

6. **SAVE:** Wrote the plan file following the schema exactly.

### Where the Skill Helped vs. Where I Felt Under-Constrained

**Helped most:**
- **Pattern discovery before questions** was the single most valuable constraint. It changed the shape of the plan (standalone skill, not embedded).
- **Phase template with explicit fields** prevented vague handwaving. The IN/OUT scope and Approach Notes fields were particularly useful for preventing scope creep.
- **Self-check checklist** caught a missing "Done when" criterion I would have shipped without.
- **YAGNI gate** made me cut a Phase 4 I was drafting about "estimation retrospectives" -- genuinely not needed for v1.
- **Anti-rationalization table** prevented me from skipping the approach comparison ("obviously it should be a standalone skill").

**Under-constrained:**
- **How much codebase search is enough** -- the skill says to search but does not give a stopping criterion. I could have searched for 5 minutes or 50 minutes. In practice I searched until I had the skill file pattern and the integration points, but a less experienced user might over-search or under-search.
- **Web research depth** -- the skill says to use WebSearch when technology choices are involved, but this feature is about methodology, not technology. I skipped web research (no libraries to compare). The skill could be more explicit about when web research is N/A.
- **Approach notes: what counts as "non-discoverable"** -- the examples are clear (JWT not sessions), but for a methodology skill like estimation, almost everything is a user decision. I found myself unsure whether "three-point estimation as primary technique" counts as non-discoverable or whether a pre-gate agent could figure that out. I included it because the pre-gate agent cannot infer why the user chose three-point over story points.
- **Phase count for pure-markdown skills** -- the 3-5 phase guidance assumes code phases with tests and builds. For a documentation/skill-creation task, the phases feel slightly artificial. But the structure still helped organize the work.

### How Long the Plan Took (Effort/Ceremony)

In terms of actual work: reading and searching the codebase took the most time (exploring ~15 files across skills, agents, commands, references). The questioning phase was fast (simulated). The approach comparison was moderate. The phase detailing with the template was moderate -- the template is long but each field has a clear purpose, so filling it out was mechanical rather than creative. The self-check was fast (5 minutes of verification). Total ceremony: roughly 60-70% of the effort went into understanding/research, 30% into writing the plan. This ratio feels right.

### Whether the Plan Feels "Enough" for a Pre-Gate Agent

Yes. Each phase gives the pre-gate agent:
- **Goal + Why:** What to accomplish and why it matters
- **Scope IN/OUT:** Clear boundaries to prevent scope creep
- **File hints:** Where to start discovery (not mandates, just starting points)
- **Constraints:** Non-obvious requirements it must respect
- **Approach notes:** User decisions it cannot rediscover
- **Done when:** Verifiable exit criteria

The pre-gate agent would search `skills/cc-construction-prerequisites/` to understand the existing pattern, then design the estimation skill files following that pattern. It has enough strategic direction without being told function signatures or file contents. The Uncertainty fields flag what needs extra investigation (solo planning poker adaptation).

One gap: the plan does not include example output of what an estimation section in a plan file looks like. The pre-gate agent would need to design this during Phase 2. That feels appropriate -- it is a HOW question, not a WHAT question -- but a more anxious planner might want to include a sample.
