# Plan: Estimation Skill

**Created:** 2026-03-10
**Status:** ready

---

## Context

Add a new `estimation` skill to code-foundations that produces research-backed effort estimates for features before committing to build them. The skill should use reference class forecasting, three-point estimation, and solo planning poker to generate estimates that integrate with whiteboarding Model recommendations and the building skill's phase structure.

## Constraints

- Must follow existing skill file structure: `skills/<name>/SKILL.md` + `checklists.md` + optional `hard-data.md`
- YAML frontmatter must include `name` and `description` fields matching the convention of other skills
- Estimation techniques must be backed by research citations (McConnell's "Software Estimation" is the primary source; Code Complete Chapter 28 covers estimation)
- Output must produce per-phase effort bands (not single-point estimates) compatible with the building skill's phase loop
- Must not duplicate what whiteboarding already does -- whiteboarding defines WHAT to build, estimation quantifies HOW LONG
- Estimates must use relative units (T-shirt sizes or story points mapped to hour ranges) rather than absolute hours, to avoid false precision
- Must integrate with the existing Model recommendation logic (haiku/sonnet/opus thresholds) so that effort estimates inform model selection

## Chosen Approach

**Standalone skill with whiteboarding integration hook**

The estimation skill is a self-contained skill under `skills/estimation/` that can be invoked independently or chained from whiteboarding. This is structurally the same as how `cc-construction-prerequisites` exists as its own skill but is loaded by the pre-gate agent. The alternative of embedding estimation into whiteboarding would bloat that skill and violate single-responsibility. The alternative of making it an agent would be over-engineering -- estimation is a checklist-driven analysis, not a multi-step workflow requiring file I/O.

---

## Phases

### Phase 1: Skill Foundation
**Model:** sonnet

**Goal:** Create the estimation skill directory and core SKILL.md with the three estimation techniques (reference class forecasting, three-point estimation, solo planning poker) structured as a checklist-driven workflow.

**Scope:**
- IN: `skills/estimation/SKILL.md` with YAML frontmatter, technique descriptions, workflow phases, output format
- OUT: checklists.md, hard-data.md, command file, integration with other skills

**Constraints:** Techniques must reference McConnell's research. Output format must produce per-phase effort bands (e.g., "Phase 1: S [2-4h]") not single-point estimates. The skill must work standalone when invoked directly.

**Done-when:** SKILL.md exists, passes YAML frontmatter validation, contains all three techniques with clear workflow steps, and produces a defined output format.

---

### Phase 2: Research Backing and Checklists
**Model:** sonnet

**Goal:** Create hard-data.md with research citations backing the three estimation techniques and checklists.md with the itemized checklist for systematic estimation.

**Scope:**
- IN: `skills/estimation/hard-data.md` with research data, `skills/estimation/checklists.md` with numbered checklist items
- OUT: Language-specific notes, integration hooks, command file

**Constraints:** Hard data must cite specific studies (Jorgensen 2004 on expert estimation bias, Kahneman/Tversky on planning fallacy, McConnell cone of uncertainty). Checklist IDs must follow the pattern used by other skills (e.g., `EST-01`, `EST-02`).

**Done-when:** hard-data.md contains at least 5 research citations with specific findings. checklists.md contains numbered items covering all three techniques. Both files follow the structure of existing skill reference files.

---

### Phase 3: Whiteboarding Integration
**Model:** sonnet

**Goal:** Add an estimation hook to the whiteboarding skill so that after phases are defined (SHAPE) and before SAVE, the user can optionally run estimation to get per-phase effort bands written into the plan file.

**Scope:**
- IN: Modifications to whiteboarding SKILL.md to add optional estimation step, updates to plan file schema to include effort estimates per phase
- OUT: Changes to building skill, changes to commands, changes to agents

**Constraints:** Integration must be optional -- whiteboarding must still work without estimation. Effort bands in the plan file must be parseable by the building skill's model auto-detection (effort size can inform model choice). Do not break the existing 4-field phase template; effort goes in plan metadata, not in phase fields.

**Done-when:** Whiteboarding SKILL.md references estimation as an optional step. Plan file schema supports effort bands per phase. Existing whiteboarding flow is unbroken (estimation step is skippable).

---

### Phase 4: Model Recommendation Enhancement
**Model:** sonnet

**Goal:** Update the building skill's model auto-detection to factor in effort estimates when present in the plan file, so that high-effort phases default to opus and low-effort phases default to haiku.

**Scope:**
- IN: Modifications to building SKILL.md model auto-detection logic, modifications to whiteboarding SKILL.md model recommendation logic
- OUT: Agent template changes, command changes, new agent types

**Constraints:** Effort-based model selection must be a fallback -- explicit `**Model:**` overrides in the plan still take highest priority. Existing plans without effort estimates must continue to work with current auto-detection. The mapping must be: S/XS effort -> haiku bias, L/XL effort -> opus bias, M effort -> sonnet (no change).

**Done-when:** Building skill's model auto-detection documentation includes effort-based rules. Plans with effort bands get adjusted model recommendations. Plans without effort bands behave identically to current behavior.

---

## Test Coverage

**Level:** 100%

---

## Notes

- The estimation skill is a "leaf" skill -- it does not load other skills. It is loaded by the user or by whiteboarding.
- Reference class forecasting requires the user to identify analogous past work. For solo devs using code-foundations, this means comparing against previous plan execution logs in `docs/plans/`. The skill should suggest checking completed plans.
- Solo planning poker is an adaptation: the user estimates from three "hats" (optimist, pessimist, realist) rather than using multiple people. This is documented in McConnell as a debiasing technique.
- Three-point estimation (optimistic, most likely, pessimistic) produces a weighted average: (O + 4M + P) / 6. The skill should compute this and present a range.
- The skill should warn against common estimation antipatterns: anchoring on first estimate, not accounting for integration time, forgetting testing effort, optimism bias.
- Pre-gate agents do not need to know about estimation -- it is a planning-time activity, not a construction-time activity.

---

## Execution Log

_To be filled during /code-foundations:building_

---
---
---

# Meta-Commentary

## How the Candidate-A Skill Guided Me

The candidate-A-minimal skill (`candidate-A-minimal.md`) is the same content as the current `skills/whiteboarding/SKILL.md` -- it IS the current whiteboarding skill. So this test is evaluating how well the current whiteboarding skill guides planning.

### What I Followed (Phase by Phase)

**DISCOVER Phase:**
- **Step 1a (Codebase Search):** The skill mandates searching before asking. I searched for estimation-related content, explored the skill directory structure, read existing skill files for patterns, checked references, and examined how skills integrate with agents and commands. This was genuinely useful -- I discovered that `cc-construction-prerequisites` already references estimation ("Estimated effort exceeds 1 week" as a threshold), that the plan-schema.md defines the file format I need to target, and that skills follow a consistent 3-4 file pattern.
- **Step 1b (Adaptive Questioning):** I classified this as "medium" complexity (multiple files, some unknowns -- new skill directory + modifications to 2 existing skills). The skill says to ask 3-5 questions. I simulated 5 questions below.
- **Step 1c (Problem Statement):** Produced and "confirmed."

**Simulated Questions and Answers:**

1. "What specific outcome do you want from the estimation skill?"
   [SIMULATED USER ANSWER]: "I want to know how long something will take before I commit to building it. Right now I whiteboard a plan and have no idea if it's a 2-hour thing or a 2-day thing until I'm halfway through."

2. "What constraints should I know about? (a) Must work without any external tools/APIs, (b) Must integrate with existing whiteboarding flow, (c) Must use specific estimation methodology, (d) Other"
   [SIMULATED USER ANSWER]: "B and C -- it should plug into whiteboarding and use real estimation techniques, not just vibes."

3. "What does 'done' look like? (a) Standalone skill I invoke manually, (b) Automatic step in whiteboarding, (c) Both -- works standalone but also hooks into whiteboarding, (d) Other"
   [SIMULATED USER ANSWER]: "C. I want to be able to just run it on its own too."

4. "Who/what will use the estimates? (a) Just me for personal planning, (b) The building skill to choose models, (c) Both, (d) Other"
   [SIMULATED USER ANSWER]: "Both I guess? If I know a phase is big, the model should probably be opus."

5. "What could go wrong with estimation in this context? (a) False precision -- single-point estimates that feel exact but aren't, (b) Overhead -- estimation takes too long for small features, (c) Staleness -- estimates become wrong as implementation reveals surprises, (d) All of the above"
   [SIMULATED USER ANSWER]: "A mostly. I don't want it to pretend it knows exactly how long something takes."

**SHAPE Phase:**
- I presented approaches (in my working process, not shown in the plan). The three I considered:
  - **A: Standalone skill + whiteboarding hook** -- new skill directory, optional integration
  - **B: Embed in whiteboarding** -- add estimation as a mandatory sub-phase of whiteboarding
  - **C: Estimation agent** -- new agent type that runs estimation as a subagent dispatch
- The user (simulated) picked A because B would bloat whiteboarding and C is over-engineering.
- Then I defined 4 phases using the exact 4-field template (Goal, Scope IN/OUT, Constraints, Done-when).

**CONFIRM Phase:**
- Test coverage question: simulated answer "100%"
- Phase-by-phase approval: simulated user confirming each phase.
- Final plan summary: simulated "looks good."

**SAVE Phase:**
- Applied model recommendations: all phases are sonnet (3-4 tasks each, no OPUS_KEYWORDS, scope is moderate).
- Wrote using the exact plan file schema from the skill.

**HANDOFF Phase:**
- Would ask "Plan saved. How would you like to proceed?" -- simulated as complete.

---

## Where the Skill Helped

1. **Codebase search before questions was genuinely valuable.** I found patterns (skill directory structure, YAML frontmatter format, existing estimation references in cc-construction-prerequisites, plan-schema.md) that directly informed the plan. Without this step I would have guessed at conventions.

2. **The 4-field phase template with strict exclusions is excellent.** It prevented me from specifying file paths, function signatures, or implementation details. Every time I started writing "create a file called estimation.md with sections for..." I caught myself against the exclusion table. The constraint that phases should be 50-75 words forced compression.

3. **YAGNI gate caught one phase.** I initially had a Phase 5 for "command file creation" (`commands/estimation.md`). The YAGNI gate made me ask "could we ship without it?" -- yes, the skill works without a dedicated command since users can invoke it via `Skill(code-foundations:estimation)`. Removed.

4. **Approach comparison forced a real decision.** Even though "standalone skill" felt obvious, comparing against "embed in whiteboarding" and "estimation agent" surfaced real trade-offs (bloat vs. coupling vs. overhead).

5. **Anti-rationalization table caught me twice.** Once when I wanted to add file paths ("Pre-gate searches the codebase with fresh state"), once when I wanted to add checklist item IDs ("Pre-gate designs these via cc-routine-and-class-design skill").

## Where I Felt Under-Constrained

1. **No guidance on HOW to do codebase search.** The skill says "search for similar features, same directory patterns, related components, naming conventions" but doesn't say how deep to go. I searched broadly because the feature request was architectural, but for a simpler request I might under-search. A heuristic like "spend 2-5 minutes, read 3-5 files minimum" would help.

2. **Approach selection criteria are vague for medium tasks.** The skill says "present 2-3 structurally different approaches" but gives no framework for GENERATING approaches. For this feature, the three approaches (standalone skill, embed in existing skill, new agent) came from my knowledge of the codebase architecture. A less familiar planner might struggle. The old whiteboarding skill at least had a research step.

3. **No guidance on phase ORDERING.** The skill says 2-7 phases, each independently testable, but doesn't say how to decide order. I ordered by dependency (foundation first, integration last), but the skill doesn't enforce or suggest this. A "phases should be ordered by dependency -- each phase should only depend on completed predecessors" statement would help.

4. **Constraint field definition is slippery.** "Non-discoverable requirements only -- things pre-gate cannot find by searching" is a good principle but hard to apply in practice. Is "must reference McConnell's research" discoverable? Technically yes (search for McConnell references in other skills), but the specific requirement that THIS skill should cite specific studies is user intent. I erred on the side of including more constraints.

5. **No word on how to handle the Notes section.** The plan schema includes a Notes section, but the skill workflow doesn't have a step for populating it. I added notes because they felt important (explaining solo planning poker, the PERT formula, etc.), but the skill didn't tell me to. This is where implementation details creep in through the back door.

## Effort / Ceremony Assessment

- **Time equivalent:** This would take roughly 15-20 minutes in a real session (5 min codebase search, 5 min questions, 5 min shaping phases, 2 min confirmation, 2 min saving).
- **Ceremony level:** Appropriate for a medium-complexity feature. The strict 4-field template kept each phase tight. I did not feel over-ceremonied.
- **Compared to old whiteboarding skill:** Significantly less ceremony. The old skill had a DETAIL phase requiring 200-300 words per section with file paths and implementation details. That phase is entirely gone. The plan is ~60% shorter.

## Is This Plan "Enough" for a Pre-Gate Agent?

**Yes, with caveats.**

**What works well for pre-gate:**
- Goal + Scope IN/OUT gives pre-gate clear search boundaries
- Constraints carry the non-obvious requirements (research citations, output format, integration rules)
- Done-when gives post-gate clear verification criteria
- The Notes section fills gaps that don't fit in the 4 fields

**What might cause pre-gate friction:**
- Phase 3 (Whiteboarding Integration) modifies an existing skill file. Pre-gate will need to read the current whiteboarding SKILL.md and figure out where to insert the estimation hook. The plan says "add optional estimation step" but not where in the flow. Pre-gate's `cc-construction-prerequisites` skill should handle this via codebase discovery, but it's the most ambiguous phase.
- Phase 4 (Model Recommendation Enhancement) touches two skills' auto-detection logic. Pre-gate will need to understand how model auto-detection currently works across both whiteboarding and building. The constraint about "fallback, not override" should guide it, but the cross-file scope is tricky.

**Overall verdict:** The plan provides sufficient intent and constraints for a pre-gate agent with fresh codebase context and loaded design skills to produce good pseudocode. It is a better input than an over-specified plan would be, because it leaves room for pre-gate to discover the current state of the code and design accordingly.
