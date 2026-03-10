# UX Designer Analysis: Whiteboarding Skill Improvements

## Persona Lens
How can the whiteboarding skill's structure and flow be redesigned for better outputs and user experience?

The whiteboarding skill's "user" is an LLM agent following instructions to produce an implementation-ready plan. The quality of the plan depends on how well the skill's structure guides the LLM through discovery, decomposition, and validation. Research on agentic planning reveals several structural patterns that directly improve plan quality -- patterns the current skill partially implements but could adopt more fully.

The core UX question: **Does the skill's information architecture help the LLM produce plans that survive contact with implementation?** The research says the current design has meaningful gaps in granularity control, context management, procedural knowledge capture, and dependency tracking.

---

## Key Research Findings

### 1. ReCode (2510.23564) -- Planning and Action Are the Same Thing at Different Granularities
- The rigid separation between "planning" and "execution" is the root cause of inflexible agent behavior. Plans should be recursively decomposable -- a plan IS a high-level action.
- Agents that can dynamically adjust granularity (zoom in for details, zoom out for strategy) outperform rigid plan-then-act agents.
- Novel tasks should start at the coarsest granularity and progressively refine. Well-understood tasks can skip straight to fine-grained steps.
- Key finding: "Over-decomposition" is a real failure mode -- agents keep planning instead of acting. A max decomposition depth is needed.

### 2. COMPASS (2510.08790) -- Context Management Is the Central Bottleneck
- Long-horizon tasks fail primarily because of context management, not reasoning ability. Separating tactical execution from strategic oversight improves accuracy by up to 20%.
- Three-component architecture: Main Agent (tactical), Meta-Thinker (strategic oversight), Context Manager (compression/organization).
- Static context (goals, constraints) must be separated from dynamic context (execution traces, discoveries).
- Key finding: "Strategy drift" -- the agent loses sight of the original goal -- is the primary failure mode in extended planning sessions.

### 3. ReCAP (2510.23822) -- Goal Anchoring and Recursive Context Preservation
- Three failure modes of sequential planning: context drift, loss of goal information, and recurrent failure cycles.
- "Plan-ahead decomposition": generate a full subtask list, execute the first item, refine the remainder. This preserves global intent while avoiding plan drift.
- "Structured re-injection": when returning from a sub-plan, the parent's remaining plan is re-injected into context. This maintains cross-level coherence.
- Key finding: 32% improvement on long-horizon tasks from structured context management alone (no model change).

### 4. Manager Agent (2510.02557) -- Dependency DAGs and Capability-Aware Delegation
- Task decomposition should produce a dependency graph (DAG), not just a flat list. Which tasks must complete before others start?
- Capability matching: for each sub-task, identify what capabilities are needed. In the whiteboarding context, this means each plan phase should specify what the executing agent needs to know.
- Key finding: "No dependency tracking between sub-tasks" is a red flag -- downstream tasks start before prerequisites complete.

### 5. H2R (2509.12810) -- Hierarchical Memory: Separate Planning Knowledge from Execution Knowledge
- Optimal memory unit is at the subgoal level -- task-level is too coarse (includes irrelevant info), action-level is too fine (too context-specific).
- High-level memory (planning insights: what worked, what to avoid) should be separate from low-level memory (detailed execution trajectories).
- Key finding: Hindsight reflection on completed work produces better reusable knowledge than storing raw trajectories.

### 6. Lingxi (2510.11838) -- Procedural Knowledge Over Declarative Knowledge
- Store the problem-solving process (how and why), not just the outcome (what). This enables transfer of strategies across similar problems.
- Different types of knowledge matter at different stages: "design patterns & coding practices" matter most during analysis; implementation-specific knowledge matters during fixing.
- Key finding: Knowledge-guided scaling (analyzing from multiple perspectives using retrieved knowledge) outperforms brute-force exploration by 6.3 percentage points.

### 7. CWM (2510.02387) -- Execution Trace Thinking
- Understanding what code DOES (not just what it looks like) via execution traces grounds reasoning in concrete behavior.
- Both successful and failed trajectories provide learning value for world modeling.
- Key finding: Trace-augmented reasoning -- predict what will happen, then derive the answer -- grounds reasoning in concrete program behavior rather than abstract pattern matching.

### 8. Gemini Robotics (2510.03342) -- Thinking Before Acting
- "Embodied Thinking" -- interleaving reasoning traces with actions -- improves multi-step task success from 0.26 to 0.55 progress score.
- Orchestrator/Executor separation: high-level planning in language while low-level execution translates to actions.
- Success detection between steps is mandatory. Cannot recover from failures mid-task without it.

---

## Current Skill Gaps

### Gap 1: Flat Phase Structure Without Granularity Control
The current skill has 6 phases (UNDERSTAND, EXPLORE, DETAIL, VALIDATE, SAVE, HANDOFF) at a single level of granularity. Every planning session follows the same depth regardless of task complexity. ReCode (2510.23564) shows that agents need to dynamically adjust granularity -- simple tasks should get shallow plans, complex tasks should get deep recursive decomposition. The complexity classification in Step 1b (simple/medium/complex) affects question count but never affects plan depth or detail level.

### Gap 2: No Goal Anchoring Mechanism
The skill produces a Problem Statement in Phase 1 but never explicitly re-references it during later phases. ReCAP (2510.23822) and COMPASS (2510.08790) both demonstrate that "goal anchoring" -- persistently re-stating the original objective -- prevents context drift during extended planning. The current skill's 6-phase sequential flow is exactly the pattern that causes context drift in long sessions.

### Gap 3: No Dependency Tracking in Plan Output
Phase 3 (DETAIL) produces sections with a "Dependencies" field, but there is no enforcement of a dependency DAG. The Manager Agent paper (2510.02557) shows that explicit dependency graphs prevent downstream tasks from starting before prerequisites complete. The current plan schema uses a flat numbered checklist that implies sequential ordering but does not capture parallel opportunities or hard dependencies.

### Gap 4: No Procedural Knowledge Capture
Plans capture WHAT to build (files, functions, patterns) but not HOW to approach the problem-solving (diagnostic reasoning, exploration paths, decision rationale). Lingxi (2510.11838) demonstrates that procedural knowledge -- the how and why -- is the most transferable artifact. The "Notes" section at the bottom of the plan schema is an afterthought, not a structured knowledge capture mechanism.

### Gap 5: No Execution Trace Reasoning
The skill never asks the LLM to mentally trace through what the proposed implementation will DO at runtime. CWM (2510.02387) shows that predicting execution behavior (not just structure) catches errors that structural analysis misses. Phase 3 has no "trace the happy path" or "trace the error path" step.

### Gap 6: Missing Strategic Oversight During Planning
The skill's phases flow linearly without any mechanism to detect "strategy drift" -- where the plan evolves away from the original problem statement. COMPASS (2510.08790) shows that a dedicated strategic oversight check (separate from tactical execution) improves accuracy by up to 20%. The VALIDATE phase checks user approval but not strategic coherence.

### Gap 7: Static vs Dynamic Context Not Separated in Plan Schema
The plan file schema mixes static context (problem statement, constraints, chosen approach) with dynamic context (implementation checklist, execution log). ReCAP (2510.23822) and COMPASS (2510.08790) both show that separating these enables better context management during execution. The building skill that consumes this plan would benefit from clearly delineated sections.

---

## Specific Proposals

### Proposal 1: Adaptive Plan Depth Based on Complexity Classification

- **Research basis:** ReCode (2510.23564) -- "Novel task with no prior experience: start at coarsest granularity, progressively refine. Well-understood task: act at fine granularity." Also: "Over-decomposition is a real failure mode -- set max decomposition depth."
- **Current gap:** Complexity classification (simple/medium/complex) in Step 1b only affects question count (2-3, 4-5, 6-8). Plan depth in Phase 3 is always the same regardless of complexity.
- **Proposed change:** After complexity classification in Step 1b, add a plan depth table that controls Phase 3 output:

```markdown
### Plan Depth by Complexity

| Complexity | Section Count | Detail Level | Max Checklist Items per Section |
|------------|--------------|--------------|--------------------------------|
| Simple     | 1-2          | File + function names only | 3-5 |
| Medium     | 3-4          | File + function + key logic | 5-8 |
| Complex    | 5-7          | File + function + logic + edge cases + traces | 8-12 |

**Over-decomposition guard:** If you find yourself creating more than 7 sections, STOP.
You are likely over-planning. Combine related sections or defer detail to implementation.
```

- **Expected impact:** Prevents two failure modes: (1) over-planning simple tasks (wasted time, cognitive overload), (2) under-planning complex tasks (missing edge cases discovered during implementation). The over-decomposition guard directly addresses ReCode's finding that agents get stuck planning instead of acting.

---

### Proposal 2: Goal Anchor Checkpoints Throughout Phases

- **Research basis:** ReCAP (2510.23822) -- "Always maintain the original goal as a persistent, uncompressible element." COMPASS (2510.08790) -- "Context drift: losing sight of the original goal is the primary failure mode."
- **Current gap:** Problem Statement is produced in Phase 1 output but never re-referenced. Phases 2-5 have no mechanism to check alignment with original intent.
- **Proposed change:** Add a Goal Anchor Check at the transition between each major phase. Insert after Phase 2 (EXPLORE) and before Phase 3 (DETAIL):

```markdown
### Goal Anchor Check (Before Proceeding)

Before generating implementation sections, re-read the Problem Statement from Phase 1.
Ask yourself:
1. Does the chosen approach DIRECTLY address the stated problem?
2. Have any sections crept in that serve a DIFFERENT problem?
3. Are the success criteria from Phase 1 still achievable with this approach?

If any answer is "no" → revise before proceeding. State the revision and rationale.

**Format:** "Goal anchor verified: [chosen approach] directly addresses [problem statement summary]."
```

Also add a lighter version before Phase 5 (SAVE):

```markdown
### Final Goal Anchor Check

Re-read the Problem Statement. For each plan section, verify it maps to at least one
success criterion. Remove any section that doesn't map. Flag any success criterion
with no corresponding section.
```

- **Expected impact:** Prevents strategy drift during extended planning sessions. COMPASS found up to 20% accuracy improvement from strategic oversight. The lightweight format (one sentence + check) adds minimal friction while providing a structural forcing function against drift.

---

### Proposal 3: Dependency DAG in Plan Schema

- **Research basis:** Manager Agent (2510.02557) -- "Represent task dependencies as a directed acyclic graph. Never start a task before its prerequisites are complete." Red flag: "No dependency tracking between sub-tasks causes downstream tasks to start before prerequisites complete."
- **Current gap:** Phase 3 sections have a "Dependencies" field but the plan schema in Phase 5 uses a flat numbered checklist. No explicit parallel opportunities or hard dependency edges are captured.
- **Proposed change:** Replace the flat Implementation Checklist in the plan schema with a dependency-aware format:

```markdown
## Implementation Checklist

### Phase 1: [Name] **Model:** [model]
**Depends on:** none (start here)
**Unlocks:** Phase 2, Phase 3
- [ ] [task]
- [ ] [task]

### Phase 2: [Name] **Model:** [model]
**Depends on:** Phase 1
**Unlocks:** Phase 4
- [ ] [task]

### Phase 3: [Name] **Model:** [model]
**Depends on:** Phase 1
**Unlocks:** Phase 4
- [ ] [task]

### Phase 4: [Name] **Model:** [model]
**Depends on:** Phase 2, Phase 3
**Unlocks:** none (final)
- [ ] [task]

## Dependency Graph
Phase 1 → Phase 2 → Phase 4
Phase 1 → Phase 3 ↗
```

Add to the DETAIL phase instructions:

```markdown
**Dependency Rule:** For each section, explicitly state:
1. What sections must complete BEFORE this one can start (hard dependencies)
2. What sections this one UNLOCKS (enables after completion)
3. What sections can run IN PARALLEL with this one (no shared dependencies)
```

- **Expected impact:** The building skill can use dependency information to parallelize work and prevent ordering errors. Plans become self-documenting about what can be worked on simultaneously, which is particularly valuable when the building skill auto-selects models per phase.

---

### Proposal 4: Procedural Knowledge Capture in Plan Notes

- **Research basis:** Lingxi (2510.11838) -- "Store the problem-solving process (how and why), not just the outcome (what). Procedural knowledge is the most transferable artifact." H2R (2509.12810) -- "Use hindsight reflection to extract structured, reusable insights."
- **Current gap:** The "Notes" section at the bottom of the plan schema captures "edge cases, gotchas, decisions made during planning" as an unstructured afterthought. No procedural knowledge is captured.
- **Proposed change:** Replace the Notes section with a structured Decision Log:

```markdown
## Decision Log

### Decision 1: [What was decided]
- **Alternatives considered:** [what else was on the table]
- **Rationale:** [WHY this choice, not just WHAT]
- **Risk:** [what could go wrong with this decision]
- **Reversal cost:** [how hard is it to change this later: low/medium/high]

### Decision 2: ...
```

Add to the EXPLORE phase (Step 2b), after the approach is chosen:

```markdown
**Record the decision:** After the user chooses an approach, capture not just the choice
but the full decision context. This is the most valuable part of the plan for future
reference -- it explains WHY this approach was chosen over alternatives.
```

- **Expected impact:** Plans become reusable knowledge artifacts. When similar features are planned later, the Decision Log provides procedural knowledge (the "how and why") that Lingxi showed is 6.3% more effective than raw outcome data. This also helps during building if assumptions need revisiting.

---

### Proposal 5: Execution Trace Step in DETAIL Phase

- **Research basis:** CWM (2510.02387) -- "Trace-augmented reasoning grounds decisions in concrete program behavior rather than abstract pattern matching." Gemini Robotics (2510.03342) -- "Thinking before acting improves multi-step success from 0.26 to 0.55."
- **Current gap:** Phase 3 (DETAIL) breaks the plan into sections with files, functions, and implementation details, but never traces through what the implementation will DO at runtime. No "happy path walkthrough" or "error path walkthrough" exists.
- **Proposed change:** Add a trace step after the DETAIL phase sections are complete but before VALIDATE:

```markdown
### Step 3b: Execution Trace (For Medium and Complex tasks)

After completing all sections, mentally trace through the implementation:

**Happy Path Trace:**
1. Start: [user/system triggers the feature]
2. Step through each section in dependency order
3. For each section: What data flows in? What data flows out? What state changes?
4. End: [expected outcome matches success criteria]

**Error Path Trace (pick the most likely failure):**
1. Start: [same trigger]
2. At step [N]: [what goes wrong]
3. What happens downstream? Does the error propagate? Is it caught?
4. End: [how does the system behave on failure?]

**If tracing reveals a gap:** Add a section to handle it, or add an edge case note to
the relevant section. Do NOT ignore gaps discovered during tracing.
```

- **Expected impact:** Catches design errors before implementation begins. CWM showed that execution trace reasoning grounds decisions in concrete behavior. This is especially valuable for plans involving data flow across multiple components, where structural analysis alone misses runtime interaction issues. The "error path" trace catches missing error handling -- the #1 category of post-implementation bugs.

---

### Proposal 6: Strategic Coherence Check Before VALIDATE

- **Research basis:** COMPASS (2510.08790) -- "Separate strategy from execution. Long-horizon agents need distinct strategic oversight and tactical execution -- combining them leads to drift." Table 1 in the paper shows four confusion scenarios where agents make wrong continue/revise decisions.
- **Current gap:** Phase 4 (VALIDATE) asks the user to confirm the plan but does not include any self-assessment of strategic coherence. The LLM presents the plan and asks "Does this look complete?" without first checking its own work.
- **Proposed change:** Add a self-check step before presenting to the user in Phase 4:

```markdown
### Step 4a: Strategic Coherence Self-Check (Before Presenting to User)

Before presenting the plan for user approval, verify:

| Check | Question | Pass? |
|-------|----------|-------|
| Scope | Does every section map to a success criterion from Phase 1? | |
| Completeness | Does every success criterion have at least one section? | |
| YAGNI | Is any section serving a hypothetical future need, not a stated requirement? | |
| Consistency | Do the sections use the same patterns/conventions found in Phase 1 codebase search? | |
| Ordering | Are dependencies between sections correctly captured? | |
| Feasibility | Has each section's approach been validated by research (Phase 2)? | |

**If any check fails:** Fix before presenting to user. State what you fixed and why.
```

- **Expected impact:** Reduces the burden on the user during validation. Currently, the user must catch all plan quality issues. This self-check catches structural problems (scope creep, missing coverage, YAGNI violations, dependency errors) before the user sees the plan, making their review focused on intent and priority rather than structural correctness.

---

### Proposal 7: Separate Static and Dynamic Sections in Plan Schema

- **Research basis:** COMPASS (2510.08790) -- "Separate static context (query, tools) from dynamic context (execution traces)." ReCAP (2510.23822) -- "Compress completed work, expand active work."
- **Current gap:** The plan schema mixes static context (Context, Constraints, Chosen Approach) with dynamic content (Implementation Checklist, Execution Log) in a single flat document. During building, the LLM must parse the entire document to find what is relevant to the current phase.
- **Proposed change:** Add clear section markers to the plan schema:

```markdown
# Plan: [Topic]

**Created:** YYYY-MM-DD
**Status:** ready

---
<!-- STATIC CONTEXT - Do not modify during building -->

## Context
[Problem statement from Phase 1]

## Constraints
- [constraint 1]

## Chosen Approach
**[Approach name]**
[Rationale]

## Decision Log
[From Proposal 4]

<!-- END STATIC CONTEXT -->

---
<!-- DYNAMIC CONTEXT - Updated during building -->

## Implementation Checklist
[Phases with dependency info from Proposal 3]

## Test Coverage
**Level:** [chosen level]

## Test Plan
- [ ] [tests]

## Execution Log
_Updated during /code-foundations:building_

<!-- END DYNAMIC CONTEXT -->
```

- **Expected impact:** The building skill can instruct its agents to "read the STATIC CONTEXT section for background" and "update the DYNAMIC CONTEXT section as you work." This mirrors COMPASS's separation of static context (fixed information) from dynamic context (execution traces), enabling better context management during long building sessions.

---

## Priority Ranking

| Rank | Proposal | Impact | Effort | Rationale |
|------|----------|--------|--------|-----------|
| 1 | **P2: Goal Anchor Checkpoints** | High | Low | Prevents the #1 failure mode (context drift) with minimal structural change. One sentence per phase transition. |
| 2 | **P6: Strategic Coherence Self-Check** | High | Low | Catches structural plan errors before user sees them. Reduces user cognitive load during validation. |
| 3 | **P1: Adaptive Plan Depth** | High | Medium | Prevents both over-planning and under-planning. Directly addresses the most common complaint about planning tools: "this is too simple/complex for this level of ceremony." |
| 4 | **P4: Procedural Knowledge Capture** | High | Medium | Transforms plans from disposable artifacts into reusable knowledge. Compound value: each plan makes future plans better. |
| 5 | **P3: Dependency DAG** | Medium | Medium | Enables parallel execution during building. Most impactful for complex multi-phase plans. |
| 6 | **P5: Execution Trace Step** | Medium | Medium | Catches a class of errors (runtime interaction bugs) that no other proposal addresses. Most valuable for data-flow-heavy features. |
| 7 | **P7: Static/Dynamic Section Markers** | Medium | Low | Small change with compound benefits. Makes plans more consumable by the building skill's agents. |

**Implementation recommendation:** Proposals 1, 2, and 6 can be implemented together as they modify different parts of the skill file with no overlap. Proposal 4 requires changing the plan schema (Phase 5), and Proposal 3 also changes the schema, so those two should be implemented together to avoid double-editing the schema section.
