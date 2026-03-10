# Whiteboarding Session: Estimation Skill

## Step 1: DISCOVER

### Step 1a: Codebase Search (Pattern Discovery)

## Existing Patterns Found
- **Skill structure pattern**: Every skill in `skills/` follows `SKILL.md` + `checklists.md` + optional `hard-data.md` and `language-notes.md`. YAML frontmatter with `name` and `description`. SKILL.md contains workflow; checklists.md contains enumerated checks.
- **Skill family naming**: Two prefixes -- `cc-*` (Code Complete / process rigor) and `aposd-*` (APOSD / design philosophy). A new `cc-estimation` skill follows this convention since estimation is a CC topic (Chapter 28).
- **Shared references**: CC skills reference `references/cc-foundations.md` for shared vocabulary. The estimation skill should do the same.
- **Building pipeline integration**: The `building` skill reads `**Model:**` per phase from plan files. The `whiteboarding` skill produces plan files with phase specs. Estimation output would feed into whiteboarding's DETAIL step.
- **Master dispatcher routing**: `skills/code-foundations/SKILL.md` classifies tasks into WRITE, DEBUG, REVIEW, OPTIMIZE, REFACTOR, SIMPLIFY, SECURE. Estimation is a new task type that would need routing or be invoked directly.
- **No existing estimation patterns**: No skill, reference, or command addresses effort estimation. This establishes a new pattern.

## Conventions to Follow
- Naming: lowercase-with-hyphens, `cc-` prefix
- Structure: `skills/cc-estimation/SKILL.md` + `checklists.md` + `hard-data.md`
- YAML frontmatter: `name` + `description` (description <=1024 chars, 3rd person, action verb, trigger phrases)
- Skill body: imperative form, decision tables, checklists, anti-rationalization table

## Similar Implementations
- `skills/whiteboarding/SKILL.md`: Produces plan files with phases -- estimation output should integrate with this
- `skills/cc-construction-prerequisites/SKILL.md`: Pre-coding checks -- estimation is a pre-planning check
- `references/cc-foundations.md`: Shared CC vocabulary that estimation should reference

---

### Step 1b: Adaptive Questioning

Based on pattern discovery, this touches 4-8 files (SKILL.md, checklists.md, hard-data.md, whiteboarding SKILL.md integration, possibly cc-foundations reference, possibly code-foundations router), involves 2-3 patterns (skill creation, plan file integration, shared reference), and has medium uncertainty around the estimation-to-planning interface. Classifying as **Medium**.

**Question 1:** What specific outcome do you want from the estimation skill -- a standalone effort estimate, or something that feeds directly into whiteboarding plan phases?

[USER]: Both. I want to be able to run it standalone to get a quick estimate, but when used before whiteboarding, it should produce output that informs Model recommendations and phase difficulty ratings in the plan.

**Question 2:** What estimation techniques should be included? You mentioned reference class forecasting, three-point estimation, and planning poker for solo devs. Are these the complete set, or should there be others like story points or function point analysis?

[USER]: Stick with those three. Reference class forecasting as the primary technique, three-point estimation for individual phases, and a solo planning poker variant for sanity-checking. Story points and function points are team-oriented and don't fit our solo-dev context.

**Question 3:** Who or what will consume the estimation output? Just the human user, or should the building pipeline also read it?

[USER]: The user primarily. But whiteboarding should be able to read a saved estimate file and use it when assigning Model recommendations and Difficulty ratings per phase. The building pipeline doesn't need to read estimates directly.

**Question 4:** What could go wrong -- what's the main risk you see with this skill?

[USER]: Overconfidence. The biggest risk is that having a skill produces a false sense of precision. Estimates should always surface uncertainty ranges, not point estimates. And the skill should make it clear that estimates are probabilistic, not commitments.

---

## Problem Statement

We are building a `cc-estimation` skill for code-foundations that helps solo developers estimate effort for features before committing to build them. It uses three research-backed techniques (reference class forecasting, three-point estimation, and solo planning poker) to produce probabilistic effort estimates with explicit uncertainty ranges. The skill works standalone and integrates with whiteboarding by producing estimate files that inform Model recommendations and phase Difficulty ratings.

## Constraints
- Output estimates as ranges, never point estimates
- Three techniques only: reference class forecasting, three-point, solo planning poker
- Solo-dev context -- no team-oriented techniques
- Must follow existing skill structure conventions (SKILL.md + checklists.md + hard-data.md)
- Integration with whiteboarding must not require whiteboarding skill changes beyond reading an estimate file
- Estimation is probabilistic guidance, not a commitment -- skill must reinforce this

## Success Criteria
- Skill produces effort estimates with confidence intervals
- Standalone mode: user gets an estimate without needing to run whiteboarding
- Integrated mode: whiteboarding can read estimate output to inform phase specs
- Hard-data.md documents research backing for each technique
- Anti-rationalization table addresses overconfidence and anchoring bias

---

## Step 2: CLASSIFY

Based on pattern discovery, this is a **Medium** task. It touches 4-6 files (new skill directory with 3 files + whiteboarding integration touchpoint + possible reference update), involves 2 patterns (skill creation + plan file integration), has 1 cross-cutting concern (whiteboarding integration), and medium uncertainty around the estimate-to-plan interface. Following the Medium track.

---

## Step 3: EXPLORE (Research + Approaches)

### Codebase Research
- Already using: Markdown-based skill files with YAML frontmatter, checklists with enumerated IDs, hard-data.md for research backing
- Similar solutions: `cc-construction-prerequisites` gates coding on readiness checks; estimation gates planning on effort understanding
- Not using: No numeric output formats, no structured data files beyond markdown -- estimates should stay markdown-native

### Web Research
- **Reference class forecasting** (Kahneman/Tversky, Flyvbjerg): Estimate by analogy to completed similar projects. Corrects "inside view" optimism bias. Flyvbjerg 2006 found that without RCF, IT projects overrun by 27% on average.
- **Three-point estimation** (PERT): Optimistic (O), Most Likely (M), Pessimistic (P). Expected = (O + 4M + P) / 6. Standard deviation = (P - O) / 6. Well-established in project management since 1950s.
- **Planning poker** (Grenning 2002): Convergence technique. Solo variant: estimate, then argue against yourself from pessimist/optimist perspectives, re-estimate. Reduces anchoring.

### Approach A: Standalone Skill with File Output

Estimation skill produces a markdown estimate file (`docs/estimates/YYYY-MM-DD-<topic>.md`) following a fixed schema. Whiteboarding reads this file when present and uses it to inform Difficulty and Model fields. No changes to whiteboarding SKILL.md beyond a "check for estimate file" step.

| Aspect | Detail |
|--------|--------|
| **Pros** | Clean separation; skill works independently; estimate file is a persistent artifact |
| **Cons** | Requires convention for file naming/location; whiteboarding needs to know where to look |
| **Best when** | Estimation and whiteboarding are separate sessions |
| **Research source** | Codebase pattern: whiteboarding already saves to `docs/plans/` |

### Approach B: Inline Estimation Within Whiteboarding

Add estimation as a sub-step of whiteboarding's DISCOVER phase. No separate skill -- estimation logic lives inside the whiteboarding skill as an optional step triggered by user request.

| Aspect | Detail |
|--------|--------|
| **Pros** | No new skill to maintain; estimation is always contextual |
| **Cons** | Violates single-responsibility; bloats whiteboarding; cannot run standalone; loses estimation as a reusable pattern |
| **Best when** | Estimation is only ever used during planning |
| **Research source** | Codebase pattern: whiteboarding is already 800+ lines |

### Decision

[USER]: Approach A. I want estimation to be standalone and reusable. Keeping it separate is cleaner.

## Chosen Approach: Standalone Skill with File Output
**Rationale:** Clean separation of concerns. Estimation produces a persistent artifact that any downstream consumer (whiteboarding, user) can read. Follows existing codebase patterns where skills produce files in `docs/` directories.
**Fallback:** If the file-based integration proves too loose, add a direct skill invocation step in whiteboarding that calls estimation inline.

## Rejected Approaches
- **Inline Estimation Within Whiteboarding:** Violates single-responsibility, bloats an already large skill, and prevents standalone use.

---

## Step 4: DETAIL (Medium Track)

---

## Step 5: SELF-CHECK

### Structural Completeness Check
- **Constraint coverage:** "Ranges not points" -> Phase 1 (SKILL.md workflow). "Three techniques only" -> Phase 1. "Solo-dev context" -> Phase 1. "Skill structure conventions" -> Phase 1 + Phase 2. "Whiteboarding integration" -> Phase 3. "Probabilistic not commitment" -> Phase 1 (anti-rationalization table) + Phase 2 (hard-data.md).
- **Success criteria chain:** Standalone estimates -> Phase 1. Integrated mode -> Phase 3. Hard-data.md -> Phase 2. Anti-rationalization -> Phase 1.
- **Scope coherence:** Phase 1 (core skill), Phase 2 (research backing), Phase 3 (integration). No overlap.
- **Scope completeness:** All features covered across 3 phases.
- **Dependency chain:** Phase 1 -> Phase 2 -> Phase 3. Linear, no orphans.
- **Approach notes audit:** Only non-discoverable decisions (file output format, technique selection).
- **File hints present:** All phases have file hints.
- **Done-when verifiable:** All criteria are externally observable.
- **YAGNI pass:** All 3 phases needed for stated success criteria.

### Cross-Phase Coherence Check
- **No contradictions:** Confirmed.
- **Interface alignment:** Phase 1 produces SKILL.md that Phase 2's hard-data.md supports; Phase 3 assumes both exist.
- **Progressive delivery:** Phase 1 produces a usable skill.
- **Risk front-loading:** Highest uncertainty (estimation workflow design) is in Phase 1.

---

## Step 6: VALIDATE

**Test coverage question:**

[USER]: 100% coverage. Unit tests for the estimation calculations (three-point formula, etc.) if we end up with any scripts, plus manual verification that the skill workflow produces correct output.

**Full plan review presented to user:**

[USER]: Looks good. Ship it.

---

Now writing the plan file:

---

# Plan: CC Estimation Skill

**Created:** 2026-03-10
**Status:** ready
**Complexity:** medium

---

## Context

We are building a `cc-estimation` skill for code-foundations that helps solo developers estimate effort for features using three research-backed techniques: reference class forecasting, three-point estimation, and a solo planning poker variant. The skill produces probabilistic effort estimates as ranges (never point estimates) and saves them as markdown files in `docs/estimates/`. Output integrates with the whiteboarding skill by informing Model recommendations and phase Difficulty ratings.

## Constraints

- Output estimates as ranges with confidence intervals, never point estimates
- Three techniques only: reference class forecasting, three-point estimation, solo planning poker
- Solo-dev context -- no team-oriented estimation techniques
- Follow existing skill structure: SKILL.md + checklists.md + hard-data.md
- Integration with whiteboarding via file convention, not skill modification
- Estimates are probabilistic guidance, not commitments -- skill must reinforce this
- CC prefix (`cc-estimation`) since estimation is a Code Complete topic (Chapter 28)

## Chosen Approach

**Standalone Skill with File Output**

Estimation skill lives at `skills/cc-estimation/` and produces estimate files at `docs/estimates/YYYY-MM-DD-<topic>.md`. Whiteboarding reads estimate files when present to inform Difficulty and Model fields per phase. Clean separation: estimation is reusable standalone, and whiteboarding integration is additive, not invasive.

**Fallback:** If file-based integration proves too loose (whiteboarding ignores estimates), add a direct `INVOKE cc-estimation` step to whiteboarding's DISCOVER phase.

## Rejected Approaches

- **Inline Estimation Within Whiteboarding:** Violates single-responsibility, bloats an 800+ line skill, prevents standalone use, and loses estimation as a reusable pattern.

---

## Implementation Phases

### Phase 1: Core Estimation Skill
**Model:** sonnet

**Goal:** Create the `cc-estimation` skill with its workflow, checklists, and anti-rationalization table so that a user can invoke it standalone to produce an effort estimate file.

**Scope:**
- IN: `skills/cc-estimation/SKILL.md`, `skills/cc-estimation/checklists.md`, estimate output file schema, all three estimation techniques, anti-rationalization table
- OUT: hard-data.md (Phase 2), whiteboarding integration (Phase 3), modifications to any existing skills

**Constraints:**
- YAML frontmatter must have `name` and `description` fields only
- Description must be <=1024 chars, 3rd person, action verb, with trigger phrases
- SKILL.md must be <=500 lines
- Checklists must use enumerated IDs (e.g., EST-01, EST-02)

**Approach notes:**
- Use reference class forecasting as the PRIMARY technique (user does this first), three-point estimation for per-phase granularity, solo planning poker as a sanity check -- this ordering was a user decision, not discoverable from the codebase
- Estimate output schema saves to `docs/estimates/YYYY-MM-DD-<topic>.md` -- this convention mirrors `docs/plans/` but is a new directory, chosen by user
- Anti-rationalization table must address: overconfidence, anchoring bias, planning fallacy, false precision, and "this time is different" thinking

**File hints:**
- `skills/cc-estimation/` -- new directory, create both files here
- `skills/cc-construction-prerequisites/SKILL.md` -- reference for skill structure conventions
- `skills/code-foundations/SKILL.md` -- reference for how skills are listed and routed

**Depends on:** None | **Unlocks:** Phase 2

**Done when:**
- [ ] `skills/cc-estimation/SKILL.md` exists with valid YAML frontmatter, workflow covering all three techniques, and anti-rationalization table
- [ ] `skills/cc-estimation/checklists.md` exists with enumerated checks for each technique
- [ ] Estimate output schema documented in SKILL.md produces range-based estimates with confidence intervals
- [ ] Standalone invocation produces a markdown file at `docs/estimates/YYYY-MM-DD-<topic>.md`

**Difficulty:** MEDIUM
**Uncertainty:** Workflow ordering of the three techniques -- reference class forecasting first may feel unintuitive to users unfamiliar with it. Pre-gate should investigate whether the SKILL.md needs an explicit "why this order" note.

---

### Phase 2: Research Backing (hard-data.md)
**Model:** haiku

**Goal:** Document the empirical research backing each estimation technique so the skill's recommendations are grounded in evidence, not opinion.

**Scope:**
- IN: `skills/cc-estimation/hard-data.md` covering research for reference class forecasting, three-point estimation, and solo planning poker
- OUT: Modifications to SKILL.md or checklists.md, any other skill files

**Constraints:**
- Must cite specific studies with authors and years (Kahneman/Tversky, Flyvbjerg, Grenning, PERT origins)
- Must include quantitative findings where available (e.g., Flyvbjerg's 27% IT overrun statistic)

**Approach notes:**
- Reference class forecasting research: Kahneman/Tversky (inside vs outside view), Flyvbjerg 2006 (large-N study of IT project overruns) -- user specifically wants these sources cited
- Three-point / PERT: US Navy 1958 Polaris program origin, standard deviation formula derivation
- Solo planning poker: Grenning 2002 adaptation -- user chose solo variant, document why team version doesn't apply

**File hints:**
- `skills/cc-estimation/` -- hard-data.md goes here
- `skills/cc-performance-tuning/hard-data.md` -- reference for hard-data.md format conventions (if it exists)
- `references/cc-foundations.md` -- shared CC vocabulary to align with

**Depends on:** Phase 1 | **Unlocks:** Phase 3

**Done when:**
- [ ] `skills/cc-estimation/hard-data.md` exists with cited research for all three techniques
- [ ] Each technique section includes at least one quantitative finding

**Difficulty:** LOW
**Uncertainty:** None

---

### Phase 3: Whiteboarding Integration
**Model:** sonnet

**Goal:** Enable the whiteboarding skill to read estimation output files and use them to inform per-phase Difficulty ratings and Model recommendations, completing the estimation-to-planning pipeline.

**Scope:**
- IN: Whiteboarding skill's DETAIL step reads estimate file when present, mapping estimate ranges to Difficulty and Model fields
- OUT: Changes to building skill, changes to estimation skill core workflow, changes to any agent templates

**Constraints:**
- Whiteboarding must work identically when no estimate file exists (integration is additive, not breaking)
- Mapping from estimate ranges to Difficulty/Model must be deterministic and documented

**Approach notes:**
- Integration point is whiteboarding's Step 4 (DETAIL), not Step 1 (DISCOVER) -- user wants estimation to happen before whiteboarding, not during it
- Mapping heuristic: estimate range width informs Difficulty (narrow range = LOW, wide range = HIGH), estimate magnitude informs Model (small = haiku, large = opus) -- this mapping is a user design decision

**File hints:**
- `skills/whiteboarding/SKILL.md` -- integration point in Step 4 (DETAIL)
- `skills/cc-estimation/SKILL.md` -- output schema that whiteboarding reads

**Depends on:** Phase 2 | **Unlocks:** None

**Done when:**
- [ ] Whiteboarding SKILL.md includes a step in DETAIL that checks for `docs/estimates/` files matching the current topic
- [ ] When estimate file exists, Difficulty and Model fields are informed by estimate data
- [ ] When no estimate file exists, whiteboarding behavior is unchanged
- [ ] Mapping from estimate ranges to Difficulty/Model is documented in the whiteboarding skill

**Difficulty:** MEDIUM
**Uncertainty:** The mapping heuristic (range width -> Difficulty, magnitude -> Model) may need tuning after real-world use. Pre-gate should check whether the mapping can be a simple table or needs conditional logic.

---

## Test Coverage

**Level:** 100%

## Test Plan

- [ ] Unit: Verify three-point estimation formula produces correct expected value and standard deviation for known inputs
- [ ] Unit: Verify estimate output file schema matches documented format
- [ ] Integration: Run estimation skill standalone and verify it produces a valid estimate file in `docs/estimates/`
- [ ] Integration: Run whiteboarding with a pre-existing estimate file and verify Difficulty/Model fields reflect estimate data
- [ ] Integration: Run whiteboarding without an estimate file and verify behavior is unchanged
- [ ] Manual: Invoke estimation on a real feature idea and verify the workflow feels natural and produces useful output

---

## Assumptions

| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|-----------|-----------|--------------------|--------------------|
| `docs/estimates/` directory convention is acceptable | HIGH | 1 | Use `docs/plans/` with estimate prefix |
| Whiteboarding DETAIL step can read external files without major restructuring | MED | 3 | Add a separate pre-whiteboarding step instead |
| Three techniques are sufficient for solo-dev estimation | HIGH | 1 | Add techniques in future iteration |

## Decision Log

| Decision | Alternatives Considered | Rationale | Phase |
|----------|------------------------|-----------|-------|
| Standalone skill with file output | Inline in whiteboarding | Clean separation, reusable, follows codebase conventions | All |
| CC prefix (cc-estimation) | aposd-estimation, no prefix | Estimation is a Code Complete topic (Ch 28), aligns with existing naming | 1 |
| Reference class forecasting as primary technique | Three-point first, equal weight | RCF corrects optimism bias which is the #1 estimation failure mode | 1 |
| File-based whiteboarding integration | Direct skill invocation | Looser coupling, works across sessions, no whiteboarding dependency on estimation | 3 |
| Estimate ranges to Difficulty/Model mapping | Manual user override only | Deterministic mapping provides useful defaults; user can still override in plan | 3 |

---

## Notes

- Code Complete Chapter 28 covers estimation extensively -- the pre-gate agent should read this section of `references/cc-foundations.md` for vocabulary alignment
- The `code-foundations/SKILL.md` master router does not need an ESTIMATE task type for v1 -- the skill is invoked directly. A future iteration could add routing.
- Solo planning poker is an adaptation -- there is less published research on the solo variant than the team version. The hard-data.md should be transparent about this.

---

## Execution Log

_To be filled during /code-foundations:building_

---
---
---

## Meta-Commentary

### Did the skill correctly route to the Medium/Complex track?

Yes. The signal table from the FINAL-SKILL.md was applied correctly:

- **Files touched:** 4-6 (three new files in `skills/cc-estimation/`, one modification to `skills/whiteboarding/SKILL.md`, possible reference update) -- Medium range (4-8)
- **Patterns involved:** 2 (skill creation pattern + plan file integration pattern) -- Medium range (2-3)
- **Cross-cutting concerns:** 1 (whiteboarding integration) -- Medium range (1-2)
- **Uncertainty:** Medium -- the core skill structure is clear, but the estimation-to-whiteboarding interface needs design
- **Phase count:** 3 -- Medium range (3-5)

All five signals land squarely in Medium. No signal suggests Simple or Complex. The classification is clean.

### Was the ceremony appropriate?

Yes. The Medium track provides:

- **2 approach comparison:** Standalone vs Inline -- structurally different approaches as required. Not variations of the same idea.
- **Full self-check:** Constraint coverage, scope coherence, dependency chain, YAGNI pass all executed. The self-check caught no issues because the plan was well-structured from discovery.
- **~100-150 words per phase:** Phase 1 is the meatiest (~150 words in the core fields), Phase 2 is lean (~100 words, appropriate for a LOW difficulty phase), Phase 3 is mid-range (~130 words).
- **Questions asked:** 4 (the Medium minimum), each one at a time, each with a distinct purpose.

The ceremony was neither too heavy (would be if we added pre-mortem, which is Complex-only) nor too light (would be if we skipped approach comparison or self-check).

### Do Approach notes capture non-discoverable decisions?

Yes. Each Approach note passes the "could the pre-gate agent discover this by searching the codebase?" test:

- **Phase 1:** "Use reference class forecasting as PRIMARY technique" -- user preference, not discoverable. "Estimate output saves to `docs/estimates/`" -- new convention, not discoverable. Anti-rationalization focus areas -- user priority, not discoverable.
- **Phase 2:** Specific research citations to include -- user requirement, not discoverable. Why solo variant over team version -- user context, not discoverable.
- **Phase 3:** "Integration point is Step 4 (DETAIL), not Step 1 (DISCOVER)" -- architectural decision, not discoverable. Mapping heuristic (range width -> Difficulty) -- design decision, not discoverable.

No Approach note contains implementation details like function signatures, pseudocode, or specific algorithms. The notes say WHAT decision was made and WHY, leaving HOW to the pre-gate agent.

### Are Done-when criteria verifiable?

Yes. Every criterion is externally observable:

- File existence checks (`skills/cc-estimation/SKILL.md exists`) -- verifiable with `ls`
- Content checks (`valid YAML frontmatter`, `enumerated checks`) -- verifiable by reading the file
- Behavioral checks (`produces a markdown file at docs/estimates/`) -- verifiable by running the skill
- Negative checks (`whiteboarding behavior is unchanged`) -- verifiable by running whiteboarding without an estimate file

No criterion uses vague language like "well-designed" or "properly structured." Each can be mechanically verified by the post-gate agent.

### Is the plan sufficient for a pre-gate agent without over-specifying HOW?

Yes. The plan tells each pre-gate agent:

- **WHAT** to build (Goal + Scope IN/OUT)
- **WHY** certain decisions were made (Approach notes)
- **WHERE** to look (File hints at directory level, not exact paths)
- **WHAT DONE LOOKS LIKE** (Done-when criteria)
- **WHAT TO WORRY ABOUT** (Uncertainty field)

The plan does NOT tell the pre-gate agent:

- What functions to create
- What the SKILL.md content should look like (beyond structural conventions)
- How to implement the three-point formula
- What the checklists.md entries should say
- How to structure the whiteboarding integration code

The pre-gate agent has 4 design skills loaded (`cc-construction-prerequisites`, `cc-pseudocode-programming`, `aposd-designing-deep-modules`, `cc-routine-and-class-design`) and fresh codebase access. It will discover existing skill conventions, design the module structure, and write pseudocode with better information than the plan could provide. The plan gives it the right problem without constraining the solution.
