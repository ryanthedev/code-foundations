# Cognitive Scientist Analysis: Whiteboarding Skill Improvements

## Persona Lens

The cognitive science principles most relevant to task decomposition in software planning are:

1. **Hierarchical Task Analysis (HTA):** Expert problem-solvers decompose goals into sub-goals recursively, with each level having its own entry/exit criteria. The whiteboarding skill currently does linear decomposition (sections) but lacks recursive depth or explicit dependency modeling.

2. **Cognitive Load Theory (Sweller):** Working memory can hold ~4 chunks simultaneously. Planning that requires tracking too many constraints simultaneously degrades quality. The current skill asks for constraints but does not help manage or pre-allocate them across plan sections.

3. **Means-Ends Analysis:** Expert planners identify the gap between current state and goal state, then select operators to reduce the largest gap first. The current skill jumps from problem statement to approaches without explicit gap analysis.

4. **Chunking and Expert-Novice Differences:** Experts chunk related items into meaningful units, reducing cognitive load. Novice planners treat each task as independent. The current skill's flat section template does not encourage chunking related tasks.

5. **Cognitive Writing Theory (Flower & Hayes):** Successful complex output requires iterative cycling through planning, translating (generating), and reviewing -- not a single linear pass. The current skill is purely linear: understand, explore, detail, validate, save.

6. **Observation-Expectation Monitoring:** Effective plans include expected outcomes at each step, enabling divergence detection during execution. The current plan schema lacks expected outcomes per phase.

---

## Key Research Findings

### Paper 2502.12568 - CogWriter (Cognitive Writing for Constrained Long-Form Generation)
- **Finding 1:** LLMs struggle to maintain multiple simultaneous constraints over long outputs. CogWriter's planning agent pre-allocates constraints to specific sections before generation begins, improving constraint satisfaction by +0.16 average accuracy over GPT-4o-mini baseline.
- **Finding 2:** The plan-generate-review cycle (from Flower & Hayes cognitive writing theory) outperforms single-pass generation, CoT, and self-refine. The three cognitive processes -- hierarchical planning, continuous monitoring, and dynamic reviewing -- must all be present (Table 3 in paper).
- **Finding 3:** Parallel section generation is possible once a plan with clear boundaries exists. Each section only needs local context plus global constraints.
- **Finding 4:** Removing the PlanRevise step (reviewing the plan before generation) dropped range instruction accuracy from 0.61 to 0.45 -- plan review is critical.

### Paper 2502.01390 - Plan-Then-Execute (User Trust Study, N=248)
- **Finding 1:** Plan quality is the single strongest predictor of both user trust and task performance. Poor plans cannot be saved by good execution.
- **Finding 2:** Separating planning and execution into two stages reduces cognitive load and improves task clarity compared to dynamic planning-execution.
- **Finding 3:** User involvement in planning is beneficial for high-risk tasks but can actually hurt for low-risk tasks (involvement fatigue). The current skill applies uniform ceremony regardless of risk/complexity.
- **Finding 4:** Users develop false confidence from plausible-sounding plans that are actually flawed. Plans need explicit verification mechanisms, not just user approval.
- **Finding 5:** Hierarchical plan structure (multi-level steps like 1.x, 1.x.y) improves user comprehension and error detection compared to flat lists.

### Paper 2502.11221 - PlanGenLLMs (Survey of LLM Planning)
- **Finding 1:** Six evaluation criteria for plans: completeness, executability, optimality, representation, generalization, and efficiency. The current whiteboarding skill evaluates none of these explicitly.
- **Finding 2:** Task decomposition can be sequential, parallel, or asynchronous. The current skill only does sequential decomposition (phases depend linearly).
- **Finding 3:** LLMs tend toward unnecessarily long plans (length bias). Plans need conciseness pressure.
- **Finding 4:** Closed-loop systems (plans that adapt based on feedback) outperform open-loop systems. The current skill produces static plans with no adaptation mechanism.
- **Finding 5:** Object/action grounding -- ensuring plan steps reference only available capabilities -- is critical for executability. The current skill does codebase search but does not ground plan steps against actual capabilities.

### Paper 2502.04392 - Division-of-Thoughts (Hybrid Model Planning)
- **Finding 1:** Plan granularity should adapt to executor capability. Fine-grained plans for weaker executors, coarse plans for stronger ones. The current skill has fixed granularity (200-300 word sections).
- **Finding 2:** Plans should include expected observations at each step. When actual observations diverge from expected, re-planning is triggered. The current plan schema has no expected outcomes.
- **Finding 3:** Observation-expectation monitoring catches 20-30% of steps that would otherwise fail silently.

### Paper 2502.04180 - MaAS (Multi-Agent Architecture Search)
- **Finding 1:** Query-dependent compute allocation -- easy tasks need simple processing, hard tasks need more. Using the same pipeline for all queries wastes 55-94% of compute budget.
- **Finding 2:** Early-exit mechanisms allow confident intermediate results to skip remaining stages.

### Paper 2501.13411 - VulnBot (Multi-Agent Pentesting)
- **Finding 1:** Context loss is the #1 failure mode (42.36%) in multi-step agent tasks. Phase specialization with inter-phase summarization reduces this.
- **Finding 2:** Penetration Task Graphs (DAGs) for dependency management outperform flat task lists.

### Paper 2502.05453 - DAMCS (Decentralized Multi-Agent Cooperation)
- **Finding 1:** Hierarchical knowledge graphs (experience -> goal -> long-term goal) enable effective retrospection and planning without overwhelming context.
- **Finding 2:** Goal-oriented memory linking experiences to goals helps detect when a goal is stagnating and suggests alternatives.

---

## Current Skill Gaps

### Gap 1: No Plan Quality Verification
The current skill validates plans only through user confirmation ("Does this plan look complete?"). Research (2502.01390) shows users develop false confidence from plausible-sounding plans. Research (2502.12568) shows that explicit plan review against constraints improves accuracy by 10-16 percentage points.

### Gap 2: No Constraint Pre-Allocation
The skill collects constraints in Phase 1 but never explicitly maps them to plan sections. CogWriter (2502.12568) demonstrates that pre-allocating constraints to sections before detailed planning prevents constraint violations from accumulating.

### Gap 3: Missing Expected Outcomes Per Phase
The plan schema has no field for "what success looks like" at each phase. DoT (2502.04392) shows that observation-expectation monitoring catches 20-30% of failures. Without expected outcomes, there is no basis for detecting plan divergence during building.

### Gap 4: No Dependency Modeling
Plan phases are assumed to be linear (Phase 1, Phase 2, Phase 3...). VulnBot (2501.13411) and PlanGenLLMs (2502.11221) show that DAG-based dependency modeling (some phases can run in parallel, some have prerequisites) is more accurate and efficient.

### Gap 5: Fixed Ceremony Regardless of Risk
The skill applies the same 6-phase process to everything. Research (2502.01390) shows that over-involvement on low-risk tasks is counterproductive, while high-risk tasks need more ceremony. MaAS (2502.04180) shows query-dependent processing saves 55-94% of overhead.

### Gap 6: No Plan Review Loop
The skill is linear: understand -> explore -> detail -> validate -> save. CogWriter (2502.12568) shows the plan-generate-review cycle is essential. The current skill never loops back to revise the plan structure based on what was learned during detailing.

### Gap 7: No Executability Grounding
The plan template says "Files to create/modify" but never verifies that the referenced files, functions, APIs, or patterns actually exist or are feasible. PlanGenLLMs (2502.11221) identifies executability (action/object grounding) as a critical evaluation criterion.

### Gap 8: No Plan Conciseness Pressure
PlanGenLLMs (2502.11221) documents LLM length bias -- plans tend to be unnecessarily long. The current YAGNI gate is a good start but is applied only at the section level, not at the task level within sections.

---

## Specific Proposals

### Proposal 1: Add Constraint Pre-Allocation Step to Phase 3 (DETAIL)

- **Research basis:** CogWriter (2502.12568) -- pre-allocating constraints to sections before generation improved constraint satisfaction by +0.16 accuracy. Removing PlanAdjust (local constraint allocation) dropped accuracy from 0.55 to 0.45.
- **Current gap:** Constraints are collected in Phase 1 but never explicitly mapped to plan phases. They float as a disconnected list.
- **Proposed change:** Add a new step between Phase 2 (EXPLORE) and Phase 3 (DETAIL) current content:

```markdown
### Step 3a: Constraint Allocation (Before Detailing)

Before writing detailed sections, map every constraint and success criterion to specific plan phases:

| Constraint | Allocated To Phase | Verification Method |
|------------|-------------------|---------------------|
| [constraint 1] | Phase N | [how to verify] |
| [constraint 2] | Phase M | [how to verify] |

**Rules:**
- Every constraint from Phase 1 MUST appear in at least one phase
- If a constraint cannot be allocated, it is either too vague (refine it) or infeasible (flag it)
- Constraints that span multiple phases need a verification point in the LAST phase they touch

Present allocation to user: "Here's how constraints map to phases. Any missing?"
```

- **Expected impact:** Prevents constraint violations from accumulating during building. Makes constraints actionable rather than decorative. Based on CogWriter data, expect ~15% improvement in constraint satisfaction during execution.

### Proposal 2: Add Expected Outcomes to Plan Phase Schema

- **Research basis:** DoT (2502.04392) -- observation-expectation monitoring catches 20-30% of step failures. Plans with expected observations enable divergence detection during execution. PlanGenLLMs (2502.11221) -- executability requires verifiable postconditions.
- **Current gap:** The plan phase template has Goal, Files, Implementation details, and Dependencies -- but no expected outcome or verification criteria.
- **Proposed change:** Modify the Section Template in Phase 3 and the Plan File Schema in Phase 5:

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Goal:** [what this phase accomplishes]

- [ ] [Specific task with file path]
- [ ] [Specific task with file path]

**Files:**
- `path/to/file.ts`

**Details:**
[Implementation specifics]

**Expected Outcome:**
- [Observable result when this phase succeeds, e.g., "tests pass", "API returns 200", "component renders"]
- [State change: what is different after this phase vs before]

**Divergence Signal:**
- [What would indicate this phase is going wrong, e.g., "type errors in more than 2 files", "test suite takes >30s"]
```

- **Expected impact:** Enables the building command to detect plan divergence during execution rather than discovering failures only at the end. Based on DoT data, expect to catch 20-30% of issues earlier.

### Proposal 3: Add Plan Review Gate Before SAVE

- **Research basis:** CogWriter (2502.12568) -- removing PlanRevise dropped range accuracy from 0.61 to 0.45. The plan-generate-review cycle is essential per cognitive writing theory (Flower & Hayes). Plan-Then-Execute (2502.01390) -- plan quality is the single strongest predictor of trust and performance; verification mechanisms are needed beyond user approval.
- **Current gap:** The skill goes DETAIL -> VALIDATE (user confirms) -> SAVE. There is no structured review of the plan against the original problem statement and constraints. User confirmation alone produces false confidence (2502.01390).
- **Proposed change:** Add a Plan Review step between VALIDATE and SAVE:

```markdown
## Phase 4b: PLAN REVIEW (Structured Verification)

Before saving, verify the plan against six criteria:

| Criterion | Check | Status |
|-----------|-------|--------|
| **Completeness** | Does every success criterion from Phase 1 have a corresponding task? | |
| **Executability** | Do all referenced files/functions/APIs exist? (Search to verify) | |
| **Constraint Coverage** | Does the constraint allocation from 3a cover all constraints? | |
| **Dependency Order** | Can phases execute in the specified order? Any circular dependencies? | |
| **Conciseness** | Can any phase be removed without affecting success criteria? Remove it. | |
| **Risk** | What is the single most likely failure point? Add a mitigation note. | |

**If any criterion fails:** Loop back to DETAIL to fix, then re-review.

**Anti-rationalization:** "The user already approved it" -- user approval checks intent alignment, not structural soundness. Both are required.
```

- **Expected impact:** Catches structural plan defects before execution begins. Based on CogWriter data, plan review improved accuracy by ~10 percentage points. Based on 2502.01390, plan quality is the strongest predictor of execution success.

### Proposal 4: Add Risk-Adaptive Ceremony Levels

- **Research basis:** Plan-Then-Execute (2502.01390) -- user involvement helps for high-risk tasks but hurts for low-risk tasks. MaAS (2502.04180) -- query-dependent compute allocation saves 55-94% of overhead while maintaining quality.
- **Current gap:** The skill classifies complexity (simple/medium/complex) and adjusts question count, but the rest of the workflow (approaches, sections, validation) is identical regardless. A config file rename gets the same ceremony as an architecture migration.
- **Proposed change:** Extend the complexity classification to affect the entire workflow:

```markdown
### Ceremony Adaptation by Complexity

| Phase | Simple | Medium | Complex |
|-------|--------|--------|---------|
| UNDERSTAND | 2-3 questions | 4-5 questions | 6-8 questions |
| EXPLORE | 1 approach (if obvious) + brief rationale | 2 approaches | 3 approaches + research |
| DETAIL | Inline tasks (no section breaks) | 2-3 sections | Full sectioned plan |
| VALIDATE | Quick confirmation | Section-by-section | Section-by-section + Plan Review gate |
| SAVE | Minimal plan file | Standard plan file | Full plan file with expected outcomes |

**Simple exit ramp:** If complexity is Simple AND the user confirms the approach, skip DETAIL sectioning and write a flat checklist plan directly.
```

- **Expected impact:** Reduces planning overhead for simple tasks by ~60% (estimated from MaAS cost reduction data applied to planning time). Prevents the involvement fatigue documented in 2502.01390 for low-risk work.

### Proposal 5: Add Dependency Graph to Plan Schema

- **Research basis:** VulnBot (2501.13411) -- Penetration Task Graphs (DAGs) with dependency edges outperform flat task lists. PlanGenLLMs (2502.11221) -- task decomposition can be sequential, parallel, or asynchronous; parallel decomposition improves efficiency. DAMCS (2502.05453) -- hierarchical goal structures (LTG -> G -> E) enable effective progress tracking.
- **Current gap:** Plan phases are implicitly linear (Phase 1, Phase 2, Phase 3...) with a simple "Dependencies" field. No explicit modeling of which phases can run in parallel or which have hard prerequisites.
- **Proposed change:** Add a dependency section to the Plan File Schema:

```markdown
## Phase Dependencies

```
Phase 1: Core data model
  └─> Phase 2: API endpoints (needs Phase 1)
  └─> Phase 3: UI components (needs Phase 1)
Phase 4: Integration tests (needs Phase 2 AND Phase 3)
```

**Rules:**
- Phases with no dependency between them CAN be built in parallel
- Mark phases that modify the same files as dependent (even if logically independent)
- The building command uses this graph to determine execution order
```

- **Expected impact:** Enables parallel phase execution during building, reducing total implementation time. Prevents hidden dependencies from causing rework. VulnBot showed 3.3x improvement from structured dependency management.

### Proposal 6: Add Executability Grounding Check

- **Research basis:** PlanGenLLMs (2502.11221) -- executability (action/object grounding) is one of six critical evaluation criteria. Plans must reference only available actions and recognizable objects. Multi-robot survey (2502.03814) -- always provide an explicit capability matrix rather than relying on assumptions.
- **Current gap:** The plan says "modify `path/to/file.ts`" but never verifies the file exists. It says "use library X" but never checks if the dependency is available. The codebase search in Phase 1 finds patterns but does not ground the plan against them.
- **Proposed change:** Add to Phase 3 (DETAIL), after writing each section:

```markdown
### Executability Check (Per Section)

After writing each plan section, verify:

| Check | Action |
|-------|--------|
| Files exist | Search for each referenced file path |
| Functions exist | Search for each referenced function/class |
| Dependencies available | Check package.json/requirements.txt for referenced libraries |
| Patterns consistent | Compare proposed patterns against Phase 1 pattern discovery |

**If a reference doesn't exist:**
- File: Mark as "CREATE" explicitly
- Function: Mark as "NEW" explicitly
- Library: Add "INSTALL [library]" as a prerequisite task
- Pattern deviation: Note WHY deviating from existing patterns

This prevents hallucinated plan steps that reference non-existent code.
```

- **Expected impact:** Eliminates a class of plan failures where the building phase discovers referenced code does not exist. PlanGenLLMs documents 15-30% hallucination rates in LLM-generated plans.

### Proposal 7: Add Inter-Phase Context Summaries

- **Research basis:** VulnBot (2501.13411) -- context loss is the #1 failure mode (42.36%) in multi-step agent tasks. Phase specialization with inter-phase summarization reduces this. DAMCS (2502.05453) -- structured communication schemas reduce information loss between agents.
- **Current gap:** When the building command executes a plan, each phase may run in a fresh context (after /clear). The plan file carries forward, but there is no structured mechanism for capturing what was learned during one phase and feeding it to the next.
- **Proposed change:** Add to the Plan File Schema:

```markdown
### Phase N: [Name]
...

**Context Forward:** [To be filled during building]
- Key decisions made:
- Files created/modified:
- Unexpected findings:
- State for next phase:
```

- **Expected impact:** Reduces context loss between building phases, especially after /clear operations. Based on VulnBot data, context loss causes 42% of multi-step failures; structured summaries directly address this.

---

## Priority Ranking

| Rank | Proposal | Impact | Effort | Rationale |
|------|----------|--------|--------|-----------|
| 1 | **Proposal 2: Expected Outcomes** | High | Low | Minimal schema change, catches 20-30% of failures earlier. Directly improves building execution quality. |
| 2 | **Proposal 3: Plan Review Gate** | High | Medium | Plan quality is the #1 predictor of execution success (2502.01390). Structured review catches what user approval misses. |
| 3 | **Proposal 1: Constraint Pre-Allocation** | High | Low | Small addition to Phase 3, but prevents the most common class of plan failures: forgotten constraints. |
| 4 | **Proposal 6: Executability Grounding** | High | Medium | Eliminates hallucinated plan references. Critical given 15-30% hallucination rates in LLM plans. |
| 5 | **Proposal 4: Risk-Adaptive Ceremony** | Medium | Medium | Reduces friction for simple tasks. Important for adoption but does not affect plan quality for complex tasks. |
| 6 | **Proposal 7: Inter-Phase Context Summaries** | Medium | Low | Simple schema addition. Impact depends on how often building uses /clear between phases. |
| 7 | **Proposal 5: Dependency Graph** | Medium | High | Conceptually valuable but requires building command changes to leverage. Lower ROI until building supports parallel phases. |

---

## Summary of Research-Backed Principles

The research converges on five principles for improving the whiteboarding skill:

1. **Plan quality dominates execution quality.** Invest more in plan verification than in execution flexibility (2502.01390).
2. **Pre-allocate constraints before detailing.** Map every constraint to a specific plan section before writing details (2502.12568).
3. **Plans need expected outcomes, not just tasks.** Without postconditions, divergence during execution is undetectable (2502.04392, 2502.11221).
4. **Review plans structurally, not just for user approval.** User approval catches intent misalignment; structural review catches completeness, executability, and dependency errors (2502.12568, 2502.01390).
5. **Adapt ceremony to risk/complexity.** Over-involvement on simple tasks causes fatigue without quality benefit (2502.01390, 2502.04180).
