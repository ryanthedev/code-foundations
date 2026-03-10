# Whiteboarding Skill Upgrade: Synthesis of 70 Proposals from 10 Expert Personas

**Date:** 2026-03-09
**Input:** 10 expert analyses (01-10), 88 research papers, 70 proposals
**Output:** Implementation-ready spec for rewriting `skills/whiteboarding/SKILL.md`

---

## Methodology

Each proposal was tagged with its source persona(s), research citations, and reported effect sizes. Proposals were grouped by semantic overlap, then ranked by: (a) cross-persona consensus count, (b) strength of research evidence, (c) magnitude of reported improvements.

**Persona key:**
- CS = Cognitive Scientist (01)
- PM = Project Manager (02)
- AI = AI/LLM Researcher (03)
- SA = Systems Architect (04)
- AC = Agile Coach (05)
- MS = Military Strategist (06)
- UX = UX Designer (07)
- CD = Compiler Designer (08)
- GD = Game Designer (09)
- FA = Failure Analyst (10)

---

## TIER 1: Must-Have (5+ persona consensus)

### 1.1 Dependency Graph Between Plan Phases

**Consensus:** 9/10 personas (CS, PM, AI, SA, AC, MS, UX, CD, GD)
**Only missing:** FA (who addresses it indirectly via inter-phase dependency fields)

**Research evidence:**
- VulnBot (2501.13411): DAG-based dependency management showed 3.3x improvement over flat task lists
- PaperCoder (2504.17192): Without dependency-aware ordering, code generation produces import errors and cross-file inconsistencies
- HiMAP-Travel (2603.04750): Explicit dependency info enables 2.5x latency reduction via parallelization
- Manager Agent (2510.02557): "No dependency tracking between sub-tasks" is a red flag
- HTAM (2511.17198): Aligning structure with intrinsic task-dependency graph is the superior strategy

**Current gap:** Plan phases are implicitly sequential. The `Dependencies` field is freeform text with no enforcement, no graph, no topological validation.

**Implementation spec:**

Add to Phase 3 (DETAIL), after all sections are drafted, as a mandatory step:

```markdown
### Dependency Graph (MANDATORY after all sections drafted)

After drafting all sections, construct the dependency graph:

1. Assign each section an ID (P1, P2, ...)
2. For each section, list which other sections it depends on
3. Verify NO circular dependencies exist
4. Identify which sections can execute in parallel (no shared dependencies)
5. Identify the critical path (longest sequential chain)

**If circular dependency found:** Refactor sections to break the cycle.
```

Replace the `Dependencies` field in the Section Template with structured fields:

```markdown
**Depends on:** [Phase IDs] | **Unlocks:** [Phase IDs]
```

Add to the Plan File Schema (Phase 5), after `## Implementation Checklist`:

```markdown
## Dependency Graph

```
Phase 1: [Name]
  └─> Phase 2: [Name] (needs Phase 1)
  └─> Phase 3: [Name] (needs Phase 1)
Phase 4: [Name] (needs Phase 2 AND Phase 3)
```

**Critical path:** Phase 1 → Phase 2 → Phase 4
**Parallelizable:** Phase 2 and Phase 3
```

---

### 1.2 Per-Phase Success Criteria / Expected Outcomes

**Consensus:** 9/10 personas (CS, PM, AI, SA, AC, MS, UX, CD, FA)
**Only missing:** GD (who addresses it via risk-rated phases with reflection checkpoints)

**Research evidence:**
- PaperBench (2504.01848): Agents claim completion prematurely; forced piecemeal execution tripled scores (2.6% to 8.5%)
- Division-of-Thoughts (2502.04392): Observation-expectation monitoring catches 20-30% of step failures
- SWEET-RL (2503.15478): Per-turn credit assignment requires independently verifiable success signals
- Step-wise PDDL (2603.06064): Self-assessed progress is unreliable 67% of the time
- Talk Freely Execute Strictly (2603.06394): Machine-checkable specs prevent drift between intent and action

**Current gap:** Phase template has Goal, Files, Implementation details, Dependencies -- but no expected outcome, no verification criteria, no "done when" definition.

**Implementation spec:**

Replace the Section Template in Phase 3 with:

```markdown
### Section N: [Name]

**Goal:** [what this section accomplishes]

**Files to create/modify:**
- `path/to/file.ts` - [what changes]

**Implementation details:**
- [specific function/class/pattern]

**Depends on:** [Phase IDs] | **Unlocks:** [Phase IDs]

**Done when (binary criteria):**
- [ ] [Specific, testable condition, e.g., "`POST /api/users` returns 201 with valid payload"]
- [ ] [Specific, testable condition, e.g., "Unit tests pass"]

**If this fails:** [Fallback strategy or escalation path]
```

Also update the Plan File Schema in Phase 5 to include `**Done when:**` in each phase.

Add this rule to Phase 3:
> **Every phase must have at least one externally verifiable success criterion.** If you cannot define a testable pass/fail condition, the phase is underspecified -- break it down further. "Looks correct" is NOT a valid criterion.

---

### 1.3 Risk Identification and Assumption Tracking

**Consensus:** 8/10 personas (PM, SA, AC, MS, GD, FA, CS, CD)
**Combines:** Risk Register (PM, SA, GD, FA) + Assumption Tracking (PM, MS, FA) + Pre-Mortem (FA)

**Research evidence:**
- CLEA (2503.00729): 44.4% of plan failures from outdated assumptions
- HiMAP-Travel (2603.04750): Constraint/assumption drift is the primary failure in long-horizon plans
- ExRAP (2509.08222): Environmental observations become less reliable over time; assumptions decay
- Plan and Budget (2505.16122): Front-loading effort on high-uncertainty sub-tasks yields 193.8% efficiency gain

**Current gap:** Zero structured risk identification. "What could go wrong?" is asked only for Medium+ complexity and the answer is not captured in the plan output. No assumption tracking whatsoever.

**Implementation spec:**

Add to Phase 2 (EXPLORE), after approach selection, as a mandatory step:

```markdown
### Risk & Assumption Identification (MANDATORY)

After choosing an approach, identify:

**Assumptions** (things believed true but not verified):

| # | Assumption | Confidence | Verify Before Phase | If Wrong |
|---|-----------|------------|--------------------|---------|
| A1 | [e.g., "API supports batch operations"] | High/Med/Low | Phase N | [fallback] |

**Risks** (things that could go wrong):

| # | Risk | Likelihood | Impact | Mitigation | Phase Affected |
|---|------|-----------|--------|-----------|---------------|
| R1 | [e.g., "Rate limits hit during batch processing"] | Med | High | [e.g., "Add retry with backoff"] | Phase 2 |

**Rules:**
- Unverified assumptions affecting 3+ phases: verify NOW before proceeding
- Every HIGH impact risk must have an explicit mitigation
- Reducible risks (can investigate further) should become Phase 1 tasks
```

Add `## Assumptions` and `## Risks` sections to the Plan File Schema.

Add Pre-Mortem question to Phase 2 (MANDATORY):
```markdown
### Pre-Mortem (after approach selection)

Ask via AskUserQuestion:
"Imagine this approach has failed. What is the most likely reason?"

Record answer. If the failure mode is not already covered by the plan, add a constraint or section to address it.
```

---

### 1.4 Plan Review / Verification Gate

**Consensus:** 7/10 personas (CS, PM, AI, SA, UX, CD, FA)

**Research evidence:**
- CogWriter (2502.12568): Removing PlanRevise dropped accuracy from 0.61 to 0.45
- Plan-Then-Execute (2502.01390): Plan quality is the single strongest predictor of trust and performance; user approval alone produces false confidence
- ALAS (2505.12501): LLMs failed 7/10 trials without external verification; succeeded 10/10 with it
- SagaLLM (2503.11951): LLMs cannot reliably self-validate

**Current gap:** Skill goes DETAIL -> VALIDATE (user confirms) -> SAVE. No structured self-review. User confirmation catches intent misalignment but not structural flaws.

**Implementation spec:**

Add a Plan Integrity Check between Phase 3 (DETAIL) and Phase 4 (VALIDATE):

```markdown
### Plan Integrity Check (MANDATORY before presenting to user)

Before presenting the plan for user review, verify:

| Check | Method |
|-------|--------|
| **Completeness** | Every success criterion from Phase 1 has a corresponding task |
| **Constraint coverage** | Every constraint is allocated to at least one phase |
| **Dependency ordering** | All listed dependencies are satisfied by earlier phases; no cycles |
| **Testability** | Every phase has at least one externally verifiable "Done when" criterion |
| **Executability** | All referenced files/functions/APIs exist (search to verify) or are explicitly marked CREATE/NEW |
| **Conciseness** | Can any phase be removed without affecting success criteria? Remove it. |
| **File conflict** | No two phases modify the same file in incompatible ways without explicit sequencing |
| **Phase count** | Plan has 2-7 phases (not 1, not 8+) |

**If any check fails:** Fix before presenting to user. Do NOT ask the user to verify plan integrity -- that is YOUR job. The user's review time should be spent on strategic decisions.

**Anti-rationalization:** "The user already approved it" -- user approval checks intent alignment, not structural soundness. Both are required.
```

---

### 1.5 Adaptive Ceremony / Complexity-Driven Plan Structure

**Consensus:** 7/10 personas (CS, SA, AC, UX, CD, AI, FA)

**Research evidence:**
- Plan-Then-Execute (2502.01390): User involvement helps for high-risk tasks but hurts for low-risk tasks (involvement fatigue)
- MaAS (2502.04180): Query-dependent compute allocation saves 55-94% of overhead
- Plan and Budget (2505.16122): Difficulty-weighted budgeting improves efficiency by up to 193.8%
- Thinkless (2505.13379): Adaptive compute allocation achieves 50-90% token reduction on easy tasks
- STEP (2506.21030): Minimal advantage on short-simple tasks but massive advantage on long-complex ones

**Current gap:** Complexity classification (simple/medium/complex) only adjusts question count. The rest of the workflow (approaches, sections, validation, plan file schema) is identical regardless.

**Implementation spec:**

Replace the current complexity classification table with a comprehensive one that controls the entire workflow:

```markdown
### Complexity-Driven Plan Structure

| Dimension | Simple | Medium | Complex |
|-----------|--------|--------|---------|
| Questions | 2-3 | 4-5 | 6-8 |
| Approaches | 2 (brief rationale) | 2-3 | 3 + web research |
| Max phases | 3 | 5 | 7 |
| Section detail | File + function names | File + function + key logic | Full details + edge cases |
| Decomposition depth | 2 levels (Goal → Tasks) | 3 levels (Goal → Subgoals → Tasks) | 3 levels + sub-tasks if needed |
| Risk/assumptions | Optional | Required | Required + pre-mortem |
| Plan review gate | Quick self-check | Full integrity check | Full integrity check + execution trace |
| Feasibility gate | Skip | Optional | Required |

**Simple exit ramp:** If complexity is Simple AND the user confirms the approach, skip sectioned DETAIL and write a flat checklist plan directly.

**Over-decomposition guard:** If your plan exceeds 7 phases, you are planning too granularly. Combine related sections or split into multiple plans.
```

---

### 1.6 Constraint Pre-Allocation / Cross-Cutting Constraint Tracking

**Consensus:** 5/10 personas (CS, GD, FA, PM, SA)

**Research evidence:**
- CogWriter (2502.12568): Pre-allocating constraints to sections improved constraint satisfaction by +0.16 accuracy
- HiMAP-Travel (2603.04750): Budget satisfaction drops from 98% (Day 1) to 42% (Day 5) without structural constraint separation; stays above 90% with it
- CLEA (2503.00729): 44.4% of plan failures from constraint violations

**Current gap:** Constraints are collected in Phase 1 as a flat list, never mapped to specific plan phases, and forgotten during execution.

**Implementation spec:**

Add to Phase 3 (DETAIL), before writing detailed sections:

```markdown
### Constraint Allocation (Before Detailing)

Classify and allocate every constraint:

**Global constraints** (must hold across ALL phases):
- [ ] [constraint] -- Enforced by: [how the builder checks this]

**Per-phase constraints:**
| Constraint | Allocated To Phase | Verification Method |
|------------|-------------------|---------------------|
| [constraint 1] | Phase N | [how to verify] |

**Rules:**
- Every constraint from Phase 1 MUST appear in at least one phase or as a global constraint
- If a constraint cannot be allocated, it is either too vague (refine it) or infeasible (flag it)
- Global constraints must be restated in the plan file header (not buried in phase details)
- Global constraints are checked after EVERY phase during building
```

Update the Plan File Schema to replace the flat `## Constraints` with:

```markdown
## Global Constraints (Checked After EVERY Phase)
- [ ] [constraint] -- Enforcement: [mechanism]

## Per-Phase Constraints
[listed within each phase]
```

---

### 1.7 Inter-Phase Context / Handoff Contracts

**Consensus:** 6/10 personas (CS, SA, MS, UX, GD, FA)
**Combines:** Context Flow (SA, MS, UX), Interface Contracts (SA, GD), Context Summaries (CS), Carry-Forward (FA)

**Research evidence:**
- VulnBot (2501.13411): Context loss is the #1 failure mode (42.36% of failures) in multi-step agent tasks
- COMPASS (2510.08790): Separating strategic oversight from tactical execution improves accuracy by up to 20%
- ReCAP (2510.23822): 32% improvement from structured context management alone
- MAS survey (2505.18286): Edge-level defects occur when downstream is overwhelmed by upstream context

**Current gap:** Phases are listed as independent checklists with no specification of what each phase produces or consumes. When building resumes after /clear, the connection between phases is lost.

**Implementation spec:**

Add to the Section Template:

```markdown
**Requires from prior phases:** [specific artifacts, files, interfaces needed]
**Produces for later phases:** [specific artifacts, files, interfaces created]
**Context forward:** [To be filled during building -- key decisions, unexpected findings, state for next phase]
```

Add validation step to Phase 3: "For each dependency edge in the dependency graph, verify that the upstream phase's `Produces` includes everything the downstream phase's `Requires` lists. If there is a mismatch, the plan has an interface gap -- resolve it."

---

## TIER 2: Strong (3-4 persona consensus)

### 2.1 Replanning Triggers / Failure Recovery Protocol

**Consensus:** 4/10 personas (PM, GD, MS, FA)

**Research evidence:**
- Plan-and-Act (2503.09572): Replanning triggered by unexpected results is essential; closed-loop planning improves success by 67.3%
- ALAS LRCP (2505.12501): Local-first recovery hierarchy prevents cascading failures
- StructuredAgent (2603.05294): OR-node fallback recovers from 50%+ of failures

**Implementation spec:**

Add `## Replanning Triggers` section to Plan File Schema:

```markdown
## Replanning Triggers

| Trigger | Detection | Response |
|---------|-----------|----------|
| Global constraint becomes infeasible | [signal] | Re-whiteboard constraints |
| Phase dependency produces different interface than expected | Interface mismatch | Re-whiteboard affected phases |
| Effort exceeds 2x estimate for any phase | Phase taking much longer | Re-whiteboard scope |
| Assumption invalidated | Check Assumptions table | Replan affected phases |

**Recovery hierarchy (try in order):**
1. Local fix within the phase (retry, alternative implementation)
2. Try fallback approach listed in the phase's "If this fails" field
3. Reorder independent phases
4. Bounded replan of affected phases only
5. Full replan (last resort)

**NEVER scrap the entire plan without first trying steps 1-4.**
```

Add to Anti-Rationalization Table:
```markdown
| "The plan says X but reality is Y, I'll just adjust" | Plan drift is constraint drift. If reality diverges from plan, STOP and update the plan file. Silent adjustments compound. |
```

---

### 2.2 Difficulty / Uncertainty Rating Per Phase

**Consensus:** 4/10 personas (SA, FA, AI, AC)

**Research evidence:**
- Plan and Budget (2505.16122): Difficulty-weighted budgeting yields up to 193.8% efficiency improvement
- Thinkless (2505.13379): Self-aware difficulty assessment achieves 50-90% token reduction on easy tasks

**Implementation spec:**

Add to the Section Template:

```markdown
**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [what we don't know that could change this plan]
```

Add instruction after all sections are defined:
```markdown
### Effort Front-Loading Rule

Review difficulty ratings across all phases:
- If the first phase is NOT the highest-difficulty phase, consider reordering to front-load uncertainty
- HIGH difficulty phases should get more detailed implementation notes, fallback strategies, and more success criteria
- LOW difficulty phases can have briefer detail

Update Model recommendations to incorporate difficulty:
- HIGH difficulty or significant uncertainty → opus (regardless of task/file count)
- LOW difficulty and tasks <= 2 and files <= 2 → haiku
- Otherwise → sonnet
```

---

### 2.3 Feasibility Gate / Goal Relaxation

**Consensus:** 3/10 personas (AC, CD, GD)

**Research evidence:**
- ContextMatters (2506.15828): Bidimensional goal relaxation achieved +52.45% success rate
- PlanGenLLMs (2502.11221): 15-30% hallucination rates in LLM-generated plans; executability is a critical evaluation criterion

**Implementation spec:**

Add to Phase 2, after approach selection (for Medium/Complex only):

```markdown
### Feasibility Gate (Medium/Complex Only)

For the chosen approach, verify feasibility against the codebase:

| Requirement | Codebase Support | Status |
|------------|-----------------|--------|
| [requirement] | [what exists] | FEASIBLE / PARTIAL / INFEASIBLE |

**If INFEASIBLE, apply goal relaxation:**
1. **Functionality relaxation** (adjust WHAT): Can a simpler version achieve the core intent?
2. **Feasibility relaxation** (adjust HOW): Can existing infrastructure achieve a partial version?

**Relaxation rule:** Find the MINIMAL modification that preserves user intent. Present trade-off to user:
"[Original goal] requires [missing infrastructure]. Alternatives:
- A: [relaxed goal] using [existing infrastructure] -- delivers [X% of value]
- B: [full goal] requiring [additional work] -- adds [N] phases"

**Do NOT silently scope-cut. Present the trade-off explicitly.**
```

---

### 2.4 Commander's Intent / Goal Anchoring

**Consensus:** 3/10 personas (MS, UX, AC)
**Combines:** Commander's Intent (MS) + Goal Anchor Checkpoints (UX) + Vertical Slice Validation (AC)

**Research evidence:**
- COMPASS (2510.08790): Strategy drift (losing sight of original goal) is the primary failure mode; up to 20% accuracy improvement from strategic oversight
- ReCAP (2510.23822): 32% improvement from goal anchoring alone

**Implementation spec:**

Add `## Commander's Intent` to Plan File Schema, between `## Context` and `## Constraints`:

```markdown
## Commander's Intent

**End-state:** [1 sentence: what does the system look like when this is done?]
**Priority of constraints:**
1. [Most important -- never sacrifice this]
2. [Important -- sacrifice only if #1 requires it]
3. [Desirable -- sacrifice if needed]
**Key judgment:** [The single most important trade-off the implementer will face, and how to decide]
```

Add Goal Anchor Checks at phase transitions:

```markdown
### Goal Anchor Check (at each major phase transition)

Before proceeding, re-read the Problem Statement and Commander's Intent.
1. Does the current work DIRECTLY address the stated problem?
2. Have any sections crept in that serve a DIFFERENT problem?
3. Are the success criteria from Phase 1 still achievable?

**Format:** "Goal anchor verified: [current phase] directly addresses [problem summary]."
```

---

### 2.5 Explicit Reasoning / Decision Log Per Section

**Consensus:** 3/10 personas (PM, UX, SA)

**Research evidence:**
- Plan-and-Act (2503.09572): Each plan step must have explicit Reasoning; vague steps are the primary failure mode
- QuaSAR (2502.12616): Separating content from logical structure improves reasoning accuracy by up to 8%
- Lingxi (2510.11838): Procedural knowledge (how and why) is 6.3% more effective than raw outcome data

**Implementation spec:**

Add `**Reasoning:**` field to Section Template:
```markdown
**Reasoning:** [WHY this section is needed -- what problem it solves, not just what it does]
```

Replace the Notes section in Plan File Schema with a structured Decision Log:
```markdown
## Decision Log

### Decision 1: [What was decided]
- **Alternatives considered:** [what else was on the table]
- **Rationale:** [WHY this choice]
- **Reversal cost:** [low/medium/high]
```

Add to Anti-Rationalization Table:
```markdown
| "The reason is obvious" | If it's obvious, writing it takes 10 seconds. If it's wrong, the explicit reasoning lets someone catch it. |
```

---

### 2.6 Fallback / Alternative Approach Preservation

**Consensus:** 4/10 personas (CD, GD, FA, AC)

**Research evidence:**
- StructuredAgent (2603.05294): AND/OR trees with fallback OR nodes recovered from 50%+ of failures
- SWE-Adept (2603.01327): Hypothesis branching with max 3 alternatives was optimal

**Implementation spec:**

Add to Plan File Schema, after `## Chosen Approach`:

```markdown
## Fallback Approaches

### Fallback 1: [Name]
**Trigger:** [Under what conditions to switch]
**Key difference from primary:** [What changes]
**Reusable phases:** [Which phases carry over]
**Phases that change:** [Which need new implementation]
```

Add `**If this fails:**` field to each phase in the Section Template (already included in 1.2 above).

Add to Anti-Rationalization Table:
```markdown
| "We committed to an approach, changing now wastes work" | Sunk cost fallacy. Fallback approaches preserve partial progress. Switching early is cheaper than discovering infeasibility at Phase 5. |
```

---

### 2.7 Phase Count Constraint

**Consensus:** 4/10 personas (PM, UX, CD, AC)

**Research evidence:**
- MultiAgentBench (2503.01935): Performance peaks at 7 iterations then drops sharply
- Plan-and-Act (2503.09572): Plan step count should stay under 7

**Implementation spec:** Already incorporated into 1.5 (Adaptive Ceremony) above. The max phases column (Simple: 3, Medium: 5, Complex: 7) enforces this. The Plan Integrity Check (1.4) also validates phase count.

---

## TIER 3: Interesting Single-Persona Ideas Worth Considering

### 3.1 Per-File Implementation Specs (Analysis Stage)
**Source:** AI (03)
**Research:** PaperCoder (2504.17192) -- per-file specs reduced post-generation fixes to 0.81% of code lines.
**Recommendation:** Add as optional for Complex plans. Include file spec template (Purpose, Exports, Imports from, Key logic, Estimated size) when plan touches 9+ files.

### 3.2 Execution Trace Step
**Source:** UX (07)
**Research:** CWM (2510.02387) -- trace-augmented reasoning grounds decisions in concrete behavior.
**Recommendation:** Add as optional for Complex plans. Trace happy path and most likely error path through planned implementation before VALIDATE. Already included in 1.5 as "execution trace" for Complex plans.

### 3.3 Code-Form Plans (Pseudocode Structure)
**Source:** PM (02)
**Research:** Code to Think (2502.19411) -- code-form plans improve instruction following by +5.7%.
**Recommendation:** Add as optional guidance for plans with conditional paths or iteration over similar items.

### 3.4 Control Flow Type Annotations
**Source:** CD (08)
**Research:** ReAcTree (2511.02424) -- sequence/fallback/parallel annotations double success rates.
**Recommendation:** Partially addressed by Dependency Graph (1.1) which identifies parallel phases. Full control flow types (fallback, conditional) are addressed by the fallback field (2.6). Not worth adding as a separate annotation given the overlap.

### 3.5 Configuration-as-First-Class-Output
**Source:** AI (03)
**Research:** PaperCoder (2504.17192) -- config generation separates parameters from implementation.
**Recommendation:** Add brief guidance to Phase 3: "If the feature involves configurable parameters, create a Configuration section listing parameters, defaults, and sources."

### 3.6 Static/Dynamic Section Markers in Plan Schema
**Source:** UX (07)
**Research:** COMPASS (2510.08790) -- separating static from dynamic context enables better context management.
**Recommendation:** Add HTML comments (`<!-- STATIC CONTEXT -->` / `<!-- DYNAMIC CONTEXT -->`) to Plan File Schema template. Low cost, compound benefit for building skill context management.

### 3.7 Prior Plan Reference / Pattern Memory
**Source:** MS (06), UX (07)
**Research:** HiPlan (2508.19076) -- milestone library from prior demonstrations enables structured experience reuse.
**Recommendation:** Add to Phase 1 (UNDERSTAND), after Pattern Discovery: "Search docs/plans/ for related prior plans. Reference successful patterns and avoid previously identified risks." Low effort, value scales with repository maturity.

### 3.8 Structured Question Types for Plan Space Exploration
**Source:** CD (08)
**Research:** Plan Space Conversation (2603.02070) -- users asked fewer but richer questions (11.4 vs 22.8) with suggested question types.
**Recommendation:** Add to Phase 2 for Medium/Complex: "Use targeted questions: Why-not [existing pattern]? What-if [relax constraint]? Which matters more: [A] or [B]?"

### 3.9 Effort Distribution Estimation
**Source:** AI (03), SA (04)
**Research:** PaperBench (2504.01848) -- agents spend all effort on first component, ignore others.
**Recommendation:** Add after all sections defined: estimate relative effort per phase (must sum to 100%). Flag phases over 40%. Partially addressed by difficulty rating (2.2).

### 3.10 Conflict Analysis Between Constraints
**Source:** CD (08)
**Research:** Plan Space Conversation (2603.02070) -- MUS/MCS analysis explains why goals conflict.
**Recommendation:** Add to Phase 2 for Medium/Complex: "Check each constraint pair for conflicts. Surface unresolvable conflicts to user before proceeding."

---

## TENSIONS AND RESOLUTIONS

### Tension 1: "Add more structure" vs. "Reduce ceremony"
- **More structure advocates:** PM, CD, FA (want risk registers, dependency graphs, contracts, verification gates)
- **Less ceremony advocates:** AC, UX, SA (want adaptive depth, simple exit ramps, progressive elaboration)
- **Resolution:** These are NOT contradictory. The Adaptive Ceremony system (1.5) resolves this by scaling structure to complexity. Simple plans get minimal ceremony (2-3 questions, flat checklist, quick self-check). Complex plans get full structure (dependency graphs, risk registers, feasibility gates, plan review). The key insight from multiple papers: applying uniform ceremony regardless of complexity is the anti-pattern.

### Tension 2: "Detail everything upfront" vs. "Progressive elaboration"
- **Full detail:** AI (per-file specs), CD (contracts with pre/post conditions), PM (complete risk register)
- **Defer detail:** SA (progressive detail resolution -- Phase 1 full, Phase 4+ sketch), UX (adaptive plan depth)
- **Resolution:** Front-load detail on HIGH uncertainty/difficulty phases, defer detail on LOW uncertainty phases. SA's progressive resolution is right: Phase 1 gets FULL detail because it has the highest epistemic uncertainty; later phases get STANDARD or SKETCH detail because earlier phases will produce information that changes them. This is supported by Plan and Budget (2505.16122) which shows cosine/polynomial decay schedules for effort allocation.

### Tension 3: "Plans should be static artifacts" vs. "Plans should be living documents"
- **Static:** CS, CD (plan is a contract, verified before execution begins)
- **Living:** MS (replanning triggers), GD (constraint reclassification during building), PM (assumption tracking)
- **Resolution:** The plan file is STATIC at save time but has designated DYNAMIC sections (Execution Log, Context Forward) that are updated during building. Replanning triggers define conditions for returning to whiteboarding rather than silently modifying the plan during building. This preserves the plan-as-contract while acknowledging reality.

### Tension 4: "LLMs should self-verify" vs. "Self-verification is impossible"
- **Self-verify:** CS (plan review gate), UX (strategic coherence self-check), PM (plan self-check)
- **Cannot self-verify:** FA (citing ALAS/Godel), PM (citing SagaLLM)
- **Resolution:** Structured checklists partially compensate for self-verification limitations. The Plan Integrity Check (1.4) is NOT asking the LLM to judge quality subjectively -- it is a mechanical checklist (does every constraint map to a phase? do files exist? are there circular dependencies?). These are verifiable properties, not subjective assessments. The user review catches what the checklist cannot. Both are required.

---

## CONSOLIDATED IMPLEMENTATION PLAN

### What to change in SKILL.md

#### Phase 1: UNDERSTAND
- Add: Prior plan search in docs/plans/ (3.7)
- No other changes needed

#### Phase 2: EXPLORE
- Add: Risk & Assumption Identification step (1.3) -- MANDATORY after approach selection
- Add: Pre-Mortem question (1.3) -- MANDATORY
- Add: Feasibility Gate (2.3) -- Medium/Complex only
- Add: Conflict Analysis (3.10) -- Medium/Complex only
- Add: Structured question types guidance (3.8) -- Medium/Complex only

#### Phase 3: DETAIL
- Replace: Section Template with enriched version (1.2 + 1.7 + 2.2 + 2.5)
- Add: Constraint Allocation step before detailing (1.6)
- Add: Dependency Graph construction after all sections (1.1) -- MANDATORY
- Update: Complexity classification to control full workflow (1.5)
- Add: Effort front-loading rule (2.2)
- Add: Configuration surface guidance (3.5) -- optional

#### New Phase 3b: PLAN REVIEW
- Add: Plan Integrity Check (1.4) -- MANDATORY before presenting to user
- Add: Execution Trace step (3.2) -- Complex only

#### Phase 4: VALIDATE
- Existing user confirmation stays
- Add: Goal Anchor Check (2.4) -- lightweight re-verification

#### Phase 5: SAVE
- Update: Plan File Schema with new sections:
  - Commander's Intent (2.4)
  - Global Constraints + Per-Phase Constraints (1.6)
  - Assumptions (1.3)
  - Risks (1.3)
  - Dependency Graph (1.1)
  - Updated phase template with: Done when, Depends on/Unlocks, Requires/Produces, Difficulty, Reasoning, If this fails, Context forward (1.2, 1.7, 2.2, 2.5, 2.6)
  - Fallback Approaches (2.6)
  - Decision Log (2.5) -- replaces Notes
  - Replanning Triggers (2.1)
  - Static/Dynamic context markers (3.6)
  - Effort Distribution (3.9) -- optional

#### Phase 6: HANDOFF
- No changes needed

#### Anti-Rationalization Table
- Add 4 new entries (from 1.4, 2.1, 2.5, 2.6)

#### Crisis Invariants
- Add: "Flag cross-file dependencies" (from AI analysis)
- Add: "Allocate constraints to phases" (from CS analysis)

### Updated Section Template (Final Consolidated Version)

This replaces the existing Section Template in Phase 3:

```markdown
### Section N: [Name]

**Goal:** [what this section accomplishes]
**Reasoning:** [WHY this section is needed]
**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [what we don't know that could change this]

**Files to create/modify:**
- `path/to/file.ts` - [what changes]

**Implementation details:**
- [specific function/class/pattern]

**Depends on:** [Phase IDs] | **Unlocks:** [Phase IDs]
**Requires from prior phases:** [specific artifacts needed]
**Produces for later phases:** [specific artifacts created]

**Done when (binary criteria):**
- [ ] [Specific, testable condition]
- [ ] [Specific, testable condition]

**If this fails:** [Fallback strategy or escalation path]
```

### Updated Plan File Schema (Final Consolidated Version)

This replaces the existing Plan File Schema in Phase 5:

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready

---
<!-- STATIC CONTEXT - Do not modify during building -->

## Commander's Intent

**End-state:** [1 sentence]
**Priority of constraints:** [numbered list]
**Key judgment:** [most important trade-off]

## Context

[Problem statement from Phase 1]

## Global Constraints (Checked After EVERY Phase)

- [ ] [constraint] -- Enforcement: [mechanism]

## Chosen Approach

**[Approach name]**
[Rationale from Phase 2]

## Fallback Approaches

### Fallback 1: [Name]
**Trigger:** [when to switch]
**Key difference:** [what changes]
**Reusable phases:** [which carry over]

## Assumptions

| # | Assumption | Confidence | Verify Before Phase | If Wrong |
|---|-----------|------------|--------------------|---------|
| A1 | [assumption] | High/Med/Low | Phase N | [fallback] |

## Risks

| # | Risk | Likelihood | Impact | Mitigation | Phase Affected |
|---|------|-----------|--------|-----------|---------------|
| R1 | [risk] | Med | High | [mitigation] | Phase N |

## Decision Log

### Decision 1: [What was decided]
- **Alternatives considered:** [options]
- **Rationale:** [why]
- **Reversal cost:** low/medium/high

<!-- END STATIC CONTEXT -->
---
<!-- DYNAMIC CONTEXT - Updated during building -->

## Dependency Graph

```
Phase 1 → Phase 2 → Phase 4
Phase 1 → Phase 3 ↗
```
**Critical path:** [longest chain]
**Parallelizable:** [independent phases]

## Implementation Checklist

### Phase 1: [Name]
**Model:** [recommended model]
**Difficulty:** [LOW/MEDIUM/HIGH]
**Depends on:** none | **Unlocks:** Phase 2, Phase 3

- [ ] [Specific task with file path]

**Per-phase constraints:**
- [local constraint]

**Done when:**
- [ ] [binary criterion]

**If this fails:** [fallback]

**Requires:** --
**Produces:** [artifacts for downstream]
**Context forward:** _[filled during building]_

---

### Phase 2: [Name]
...

## Test Coverage

**Level:** [100% / Backend only / Backend + frontend / None / Per-phase]

## Test Plan

- [ ] Unit: [specific tests]
- [ ] Integration: [specific tests]

## Replanning Triggers

| Trigger | Detection | Response |
|---------|-----------|----------|
| [condition] | [signal] | [action] |

## Execution Log

_Updated during /code-foundations:building_

<!-- END DYNAMIC CONTEXT -->
```

---

## WHAT TO REMOVE / REPLACE

| Current Content | Action | Reason |
|----------------|--------|--------|
| Flat `## Constraints` in Plan Schema | Replace with Global + Per-Phase constraint system | 1.6 |
| `## Notes` section | Replace with `## Decision Log` | 2.5 |
| Freeform `**Dependencies:**` in Section Template | Replace with `**Depends on:** / **Unlocks:**` | 1.1 |
| Fixed 200-300 word section guidance | Replace with complexity-adaptive detail levels | 1.5 |
| Complexity affecting only question count | Extend to control entire workflow | 1.5 |

---

## EVIDENCE STRENGTH SUMMARY

| Proposal | Personas | Strongest Evidence | Effect Size |
|----------|----------|-------------------|-------------|
| 1.1 Dependency Graph | 9/10 | VulnBot 3.3x, HiMAP 2.5x latency reduction | Very High |
| 1.2 Success Criteria | 9/10 | PaperBench 3x score improvement, DoT 20-30% failure catch | Very High |
| 1.3 Risk/Assumptions | 8/10 | CLEA 44.4% failure prevention, P&B 193.8% efficiency | Very High |
| 1.4 Plan Review Gate | 7/10 | CogWriter 0.45→0.61, ALAS 3/10→10/10 | Very High |
| 1.5 Adaptive Ceremony | 7/10 | MaAS 55-94% overhead savings, Thinkless 50-90% token reduction | High |
| 1.6 Constraint Tracking | 5/10 | CogWriter +0.16, HiMAP 42%→91% budget satisfaction | High |
| 1.7 Context/Handoff | 6/10 | VulnBot 42% failure prevention, COMPASS 20% accuracy | High |
| 2.1 Replanning Triggers | 4/10 | CLEA 67.3% improvement with closed-loop | Medium-High |
| 2.2 Difficulty Rating | 4/10 | Plan and Budget 193.8% efficiency | Medium-High |
| 2.3 Feasibility Gate | 3/10 | ContextMatters +52.45% | Medium |
| 2.4 Commander's Intent | 3/10 | COMPASS 20%, ReCAP 32% | Medium |
| 2.5 Decision Log | 3/10 | Plan-and-Act (qualitative), Lingxi 6.3% | Medium |
| 2.6 Fallback Approaches | 4/10 | StructuredAgent 50%+ recovery | Medium |
