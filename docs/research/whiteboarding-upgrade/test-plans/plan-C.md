# Plan: Estimation Skill

**Created:** 2026-03-10
**Status:** ready
**Complexity:** medium

---

## Context

We need a new `estimation` skill for code-foundations that helps users produce effort estimates before committing to build features. The skill should apply research-backed techniques (reference class forecasting, three-point estimation, planning poker for solo devs) and produce output that integrates with the whiteboarding plan's Model recommendations and the building skill's phase structure.

## Constraints

- Must follow existing skill file structure (`skills/<name>/SKILL.md` + `checklists.md`)
- Must integrate with the whiteboarding-to-building pipeline, not replace it
- No external dependencies or runtime code -- this is a pure skill definition (markdown files)
- Estimation output should be usable by the building skill's model auto-detection logic
- Must work for solo developers (no team ceremonies like real planning poker)

## Success Criteria

- A user can invoke the estimation skill and get a structured effort estimate for a feature
- The estimate maps to the building skill's phase structure (per-phase effort)
- The estimate informs model recommendations (complex phases get opus, simple get haiku)
- The skill includes research-backed hard data justifying the techniques used

## Chosen Approach

**Standalone skill with whiteboarding integration hooks**

The estimation skill exists as its own skill (`skills/estimation/`) with a defined output format. The whiteboarding skill gains a small integration point: after DETAIL (phase breakdown), the user can optionally invoke the estimation skill to annotate phases with effort estimates. The estimation output writes into the plan file's phase sections, which the building skill already reads.

This approach keeps the estimation skill decoupled -- usable independently or as part of the whiteboarding flow. It avoids modifying the building skill at all (building already reads `**Model:**` from plan phases; estimation just helps set those values more accurately).

**Rejected:** Embedded estimation within whiteboarding -- would bloat the whiteboarding skill, violate single-responsibility, and make estimation unavailable outside the planning flow.

---

## Implementation Checklist

### Phase 1: Core Estimation Skill Definition
**Model:** sonnet

**Goal:** Create the estimation skill's SKILL.md with the three estimation techniques, a phased workflow, and defined output format that matches the plan file schema.

**Scope:**
- IN: SKILL.md with YAML frontmatter, technique descriptions, workflow phases, output template, anti-rationalization table, chaining metadata
- OUT: Checklists, hard-data, language-notes (Phase 2 and 3)

**Tasks:**
- [ ] Create `skills/estimation/SKILL.md` with YAML frontmatter following naming conventions (`name: estimation`, triggers, description)
- [ ] Define the estimation workflow phases: SCOPE (what to estimate), CLASSIFY (estimation technique selection), ESTIMATE (apply technique), CALIBRATE (sanity-check and adjust), OUTPUT (structured result)
- [ ] Specify the three estimation techniques with when-to-use guidance: reference class forecasting (for features with historical analogs), three-point estimation (for uncertain scope), planning poker for solo devs (for phase-level granularity)
- [ ] Define the output format that writes per-phase effort annotations compatible with the plan file schema
- [ ] Add crisis invariants, anti-rationalization table, and pressure-testing scenarios following existing skill patterns

**Constraints:**
- YAML frontmatter must match the pattern in other skills (name, description fields)
- Workflow must be checklist-based like other skills (numbered phases with checkboxes)
- Output format must not conflict with existing plan file fields

**Depends-on:** None | **Unlocks:** Phase 2, Phase 3

**Done when:**
- [ ] `skills/estimation/SKILL.md` exists with valid YAML frontmatter
- [ ] All five workflow phases defined with checkboxes
- [ ] Output template shows per-phase effort annotation format
- [ ] Chaining section references whiteboarding and building

---

### Phase 2: Checklists and Hard Data
**Model:** sonnet

**Goal:** Create the supporting checklist file with concrete estimation checks, and the hard-data file with research citations backing each technique.

**Scope:**
- IN: `checklists.md` with estimation quality checks; `hard-data.md` with research summaries for reference class forecasting, three-point estimation, and planning poker
- OUT: Language-specific notes (not applicable for a methodology skill)

**Tasks:**
- [ ] Create `skills/estimation/checklists.md` with checks organized by estimation phase (scope validation, technique selection, estimate quality, calibration checks)
- [ ] Create `skills/estimation/hard-data.md` with research backing: Kahneman & Tversky on planning fallacy, Flyvbjerg on reference class forecasting, PERT three-point formula origins, solo estimation calibration studies
- [ ] Ensure checklist IDs follow the pattern used by other skills (prefixed, unique)

**Constraints:**
- Hard data must cite actual research, not invented statistics
- Checklist count should be reasonable (20-40 checks, consistent with other skills)

**Depends-on:** Phase 1 (need SKILL.md to know which phases checklists map to) | **Unlocks:** Phase 4

**Done when:**
- [ ] `skills/estimation/checklists.md` exists with organized, ID-prefixed checks
- [ ] `skills/estimation/hard-data.md` exists with cited research for each technique
- [ ] Checklist phases align with the workflow phases defined in SKILL.md

---

### Phase 3: Whiteboarding Integration
**Model:** haiku

**Goal:** Add an optional estimation hook to the whiteboarding skill so users can invoke estimation after phase breakdown, without making estimation mandatory.

**Scope:**
- IN: Small addition to whiteboarding SKILL.md referencing the estimation skill at the DETAIL-to-VALIDATE transition
- OUT: Changes to building skill (not needed -- building already reads Model field from plan files)

**Tasks:**
- [ ] Add an optional step in the whiteboarding skill's VALIDATE phase (or between DETAIL and VALIDATE) that suggests invoking the estimation skill
- [ ] Update the whiteboarding skill's chaining section to reference the estimation skill

**Constraints:**
- Must be optional -- whiteboarding must work identically without estimation
- Addition should be 10-15 lines maximum to avoid bloating the whiteboarding skill

**Depends-on:** Phase 1 (estimation skill must exist to reference) | **Unlocks:** Phase 4

**Done when:**
- [ ] Whiteboarding SKILL.md mentions estimation as an optional step
- [ ] The integration point is clearly marked as optional
- [ ] Existing whiteboarding flow is not disrupted (no mandatory new gates)

---

### Phase 4: Documentation and Registration
**Model:** haiku

**Goal:** Register the new skill in project documentation so it is discoverable and the skill count stays accurate.

**Scope:**
- IN: Updates to CLAUDE.md skill tables, plugin description if skill count changes
- OUT: Version bump, marketplace publishing (separate concern)

**Tasks:**
- [ ] Update CLAUDE.md to reference the estimation skill in appropriate sections (Architecture, Development Workflows)
- [ ] Add estimation to the whiteboarding-to-building workflow documentation where relevant

**Constraints:**
- Do not change version number (that is a separate publishing step)
- Keep documentation updates minimal and accurate

**Depends-on:** Phase 1, Phase 2, Phase 3 | **Unlocks:** None

**Done when:**
- [ ] CLAUDE.md references the estimation skill
- [ ] A user reading CLAUDE.md can discover the estimation skill and understand when to use it

---

## Test Coverage

**Level:** None

This is a documentation/skill-definition feature -- there is no runtime code to test. Verification is structural: files exist, YAML parses, checklists are well-formed, cross-references resolve.

## Test Plan

- [ ] Manual: Verify `skills/estimation/SKILL.md` has valid YAML frontmatter (name, description fields present)
- [ ] Manual: Verify `skills/estimation/checklists.md` has at least 20 checks with unique ID prefixes
- [ ] Manual: Verify `skills/estimation/hard-data.md` cites real research (not fabricated)
- [ ] Manual: Verify whiteboarding SKILL.md still works without invoking estimation (optional integration)
- [ ] Manual: Verify estimation output format is compatible with plan file schema (Model field, phase structure)
- [ ] Manual: Walk through a sample estimation using the skill's workflow to verify coherence

---

## Notes

- The estimation skill is purely a methodology skill (like cc-debugging or prototype) -- it defines a process, not runtime code. This means no unit tests apply; verification is structural and walkthrough-based.
- Reference class forecasting requires the user to identify analogous past work. For a solo dev using code-foundations for the first time, this technique may not be useful until they have a few completed plans to reference. The skill should acknowledge this cold-start limitation.
- Three-point estimation (optimistic, most likely, pessimistic) maps naturally to the building skill's phase structure -- each phase gets three estimates, and the weighted average informs Model selection.
- Planning poker for solo devs is an adaptation: instead of team consensus, the solo dev estimates from three perspectives (optimist, pessimist, realist) to counteract anchoring bias.
- The output format must avoid conflicting with existing plan fields. Using a `**Effort:**` annotation per phase (alongside existing `**Model:**`) is the safest integration path.
- Estimation should NOT delay the whiteboarding flow. It is invoked after phases are defined, not before. This prevents estimation paralysis from blocking planning.

---

## Execution Log

_To be filled during /code-foundations:building_

---
---
---

# Meta-Commentary

## How the Skill Guided Me

Candidate C (adaptive whiteboarding) imposed a clear sequence: DISCOVER, CLASSIFY, UNDERSTAND, EXPLORE, DETAIL, VALIDATE, SAVE, HANDOFF. Each step had explicit gates and outputs. Here is how each step played out:

### DISCOVER (Pattern Discovery)
The skill required searching the codebase before asking any questions. This was genuinely useful -- I found the exact skill file structure (SKILL.md + checklists.md + hard-data.md + optional language-notes.md), the YAML frontmatter pattern, the plan file schema, and the whiteboarding/building integration points. Without this step, I would have had to guess at conventions or ask the user about them.

### CLASSIFY (Complexity Assessment)
I classified this as **Medium** based on:
- Files touched: 5-7 (3 new files in skills/estimation/, 1 edit to whiteboarding, 1 edit to CLAUDE.md)
- Patterns involved: 2 known patterns (skill file structure, plan file schema), 1 new (estimation techniques)
- Cross-cutting concerns: 1 (whiteboarding integration)
- Uncertainty: Medium -- clear what to build, approach needs some thought
- Phase count: 4

This felt right. Simple would have under-planned the integration points. Complex would have been overkill for what is essentially creating markdown files following established patterns.

### UNDERSTAND (Adaptive Questioning)
The skill required 4-5 questions for Medium track, asked one at a time via AskUserQuestion. Since I am simulating, I asked and answered:

**Q1: What specific outcome do you want?**
[SIMULATED USER ANSWER]: "I want to be able to estimate how long a feature will take before I commit to building it. Right now I just guess."

**Q2: What constraints should I know about?**
[SIMULATED USER ANSWER]: "It should fit into the existing plugin structure. I don't want to install anything new. And it should be optional -- I don't want to be forced to estimate every time."

**Q3: What does 'done' look like?**
[SIMULATED USER ANSWER]: "I can run the skill, it walks me through estimating, and the result shows up in my plan file so building knows about it."

**Q4: Who/what will use this?**
[SIMULATED USER ANSWER]: "Just me. Solo dev. I want something lighter than full planning poker but more rigorous than guessing."

**Q5: What could go wrong?**
[SIMULATED USER ANSWER]: "It could be so much ceremony that I skip it every time. Or the estimates could be meaningless because I have no historical data yet."

These answers were realistic but not overly helpful -- the user gave direction without spelling out the solution.

### EXPLORE (Research + Approaches)
The skill required comparing 2 structurally different approaches for Medium track. I considered:

**Approach A: Standalone skill with integration hooks** -- estimation lives in its own skill directory, whiteboarding gets a small optional reference.

**Approach B: Estimation embedded in whiteboarding** -- add estimation phases directly into the whiteboarding SKILL.md as a new track/branch.

I chose A because it keeps skills decoupled (matching the codebase convention where each skill is independent) and avoids bloating the already-long whiteboarding skill.

[SIMULATED USER ANSWER to "Which approach?"]: "A, definitely. I don't want whiteboarding to get any bigger."

### DETAIL (Track-Specific Plan)
The Medium track template required: Goal, Scope (IN/OUT), Tasks, Constraints, Depends-on/Unlocks, Done-when per phase. The YAGNI gate was useful -- I initially had a Phase 5 for "command file creation" (`commands/estimation.md`) but cut it because the skill can be invoked directly via `Skill(code-foundations:estimation)` without a dedicated command, and adding the command later is trivial.

### VALIDATE
The skill required asking about test coverage. Since this is a documentation-only feature, "None" was the honest answer but the skill still made me think about it and justify the choice.

[SIMULATED USER ANSWER to test coverage]: "None -- it's just markdown files."

Plan summary was presented and confirmed.

[SIMULATED USER ANSWER to "Does this plan look complete?"]: "Looks good. Let's go."

### SAVE and HANDOFF
Writing the plan file and offering build/manual options.

[SIMULATED USER ANSWER to handoff]: "Clear conversation and build."

## Where the Skill Helped vs. Where I Felt Under-Constrained

### Helped significantly:
- **DISCOVER step** forced me to search the codebase first. This is the single biggest improvement over the current whiteboarding skill. I found patterns I would have otherwise asked the user about or guessed at.
- **Complexity classification** with explicit signals table made the track choice defensible rather than arbitrary.
- **Track-specific templates** (Medium template with Scope IN/OUT, Depends-on/Unlocks) produced more structured phases than the current skill's freeform sections.
- **YAGNI gate per phase** caught an unnecessary Phase 5 before it entered the plan.
- **"Plan specifies WHAT and WHY, never HOW"** invariant kept me from writing pseudocode or function signatures into the plan. This is a good discipline.
- **Model recommendation per phase** with the keyword-based auto-detection logic was easy to apply and produced sensible results (sonnet for substantive phases, haiku for small edits).

### Under-constrained:
- **Question quality**: The skill says "ask ONE at a time" and gives a sequence (outcome, constraints, done, users, failure modes), but the questions are generic. For a domain like estimation, domain-specific questions (e.g., "do you have historical data to reference?") would have been more useful. The skill doesn't help me formulate domain-aware questions.
- **Approach comparison depth**: The skill says "structurally different approaches" but doesn't guide how deep the comparison should go for Medium track (no pre-mortem, no formal trade-off table). I had to decide how much detail to include in the rejection rationale on my own.
- **Phase granularity**: The skill caps at 7 phases but gives no guidance on how fine-grained to go. Is "create SKILL.md" and "create checklists.md" one phase or two? I had to use judgment. The signals table (files, tasks, etc.) helps with classification but not with phase decomposition.
- **Section confirmation simulation**: The skill says "present each section and get user confirmation before proceeding to the next" for Medium track. In practice this means 4 separate confirmation rounds. The value is real (catching misalignment early) but the ceremony is noticeable.

## How Long the Plan Took (Effort/Ceremony)

Following the skill step by step for a Medium-complexity task:
- DISCOVER: ~3 minutes (codebase search, pattern summary)
- CLASSIFY: ~1 minute (quick, table-driven)
- UNDERSTAND: ~5 minutes (5 questions, one at a time, with simulated answers)
- EXPLORE: ~4 minutes (2 approaches, comparison, decision)
- DETAIL: ~10 minutes (4 phases, Medium template per phase, YAGNI gate)
- VALIDATE: ~2 minutes (test coverage question, plan summary)
- SAVE: ~3 minutes (writing the file)

**Total: ~28 minutes of simulated effort.** For a real session with a real user, each question round-trip adds latency, so probably 35-40 minutes wall clock. The skill's own estimate of "~15 minutes" for Medium feels optimistic; this is closer to 30. But the plan quality is notably higher than what the current whiteboarding skill produces -- especially the Scope IN/OUT boundaries, the explicit Depends-on/Unlocks chains, and the YAGNI-gated phase list.

## Whether the Plan Feels "Enough" for a Pre-Gate Agent

**Yes, with some caveats.**

The pre-gate agent needs: (1) what to build per phase, (2) what files are involved, (3) constraints to respect, (4) success criteria to verify against. This plan provides all four.

What the pre-gate agent will discover on its own (and should NOT be in the plan):
- Exact YAML frontmatter syntax (it will read other skills)
- Checklist ID prefix conventions (it will grep for patterns)
- How to structure the checklists.md sections (it will read examples)
- The whiteboarding SKILL.md's exact insertion point (it will read the file)

The one area where the plan is thinner than ideal is Phase 2 (checklists and hard-data). The plan says "cite real research" but doesn't name specific papers or page numbers. The pre-gate agent will need to either use web search or rely on the implementation agent's training knowledge for accurate citations. This is a genuine gap -- but it is a WHAT gap (what research to cite), not a HOW gap, so it belongs in the plan. If I were a real user, I might ask the whiteboarding agent to be more specific here. The adaptive skill did not prompt me to go deeper because its DETAIL template focuses on tasks and constraints, not content guidance.

Overall: the plan is solid for pre-gate. The Medium template hits the right level of detail -- enough to guide without over-specifying.
