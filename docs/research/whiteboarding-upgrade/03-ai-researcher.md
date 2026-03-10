# AI/LLM Researcher Analysis: Whiteboarding Skill Improvements

## Persona Lens

Current AI planning research reveals several critical findings about how LLMs decompose tasks -- findings that directly inform how the whiteboarding skill should structure its planning output. The core tension: LLMs are surprisingly good at *formulating* plans but consistently fail at *executing* them. This means the whiteboarding skill's output format -- the plan file itself -- is the primary lever for improving downstream execution quality. Research also shows that top-down hierarchical decomposition, dependency-aware ordering, and forced continuation (preventing premature termination) dramatically improve agentic task completion.

## Key Research Findings

### 2504.01848 - PaperBench (OpenAI, 2025)
- **Plan-execution gap is the core bottleneck.** Agents can formulate correct multi-step plans but fail to execute them. The intervention point is not better planning but better step-by-step execution scaffolding (Section 5.2).
- **Agents quit early.** Removing early termination ability tripled scores for o3-mini (2.6% to 8.5%) and nearly doubled o1 (13.2% to 24.4%). Agents claim completion or unsolvability prematurely.
- **No time/effort management.** Agents fail to strategize about how to allocate effort across components. They spend all time on the first component and ignore others.
- **Hierarchical rubrics enable partial credit.** Decomposing tasks into weighted hierarchical trees of binary leaf criteria enables granular measurement and progress tracking (8,316 leaf nodes across 20 papers).
- **Agent performance plateaus after ~1 hour** despite having 12+ hours available. Humans start slower but surpass agents at longer horizons because they strategize about remaining work.

### 2504.17192 - PaperCoder / Paper2Code (ICLR 2026)
- **Top-down decomposition into Plan -> Analyze -> Generate** dramatically outperforms single-pass generation. PaperCoder achieves 88% best-ranking in human evaluations vs baselines.
- **Planning decomposes into 4 sequential substeps:** (1) overall plan, (2) architecture design (file list, class diagram, sequence diagram), (3) logic design (execution order, file dependencies, per-file logic), (4) configuration generation.
- **Logic design (execution/dependency order) is critical.** Without it, code generation produces import errors and cross-file inconsistencies. Sequential dependency-aware generation is essential.
- **Configuration as first-class output.** Generating config.yaml alongside code separates parameters from implementation, enabling iteration without code changes.
- **Analysis stage bridges plan and execution.** Per-file specs (functional goals, I/O behaviors, inter-file dependencies, algorithmic constraints) reduce ambiguity at generation time. Only 0.81% of code lines needed fixing post-generation.

### 2503.24235 - Test-Time Scaling Survey
- **Problem-adaptive compute allocation.** Easy problems need less reasoning; hard problems need more. The whiteboarding skill should help classify problem difficulty and allocate proportional planning effort.
- **Verification is the bottleneck.** The quality of the verifier limits search-based scaling. Applied to planning: the quality of plan validation/review gates limits plan quality.
- **Hybrid scaling (breadth + depth)** outperforms pure parallel or pure sequential approaches for complex problems. Plans should explore multiple approaches (breadth) while deeply analyzing the chosen one (depth).

### 2505.05622 - CityNavAgent (Hierarchical Semantic Planning)
- **3-level hierarchical decomposition** (landmark -> object -> motion) reduces exponential action space to tractable sub-goals. Applied to planning: decompose features into strategic -> tactical -> operational levels.
- **Planning frequency decreases at higher levels.** High-level goals are set once; low-level actions are planned per-step. Plans should distinguish stable strategic decisions from volatile implementation details.
- **Memory of successful trajectories** dramatically improves performance (-16.6% SR without it). Plans should reference successful patterns from previous implementations.

### 2504.02605 - Multi-SWE-bench
- **Richer descriptions correlate with higher success.** When issue descriptions are longer and more detailed, agents succeed more often. Plan sections with more implementation detail yield better execution.
- **Multi-file patches are dramatically harder.** Performance drops significantly when changes touch multiple files. Plans should explicitly flag multi-file coordination points.
- **Fixed workflows beat unconstrained agents** for unfamiliar domains. Structured plan execution outperforms free-form exploration.

### 2504.19678 - Autonomous AI Agents Survey
- **Multi-agent coordination degrades beyond 7 iterations.** For building workflows with multiple phases, keep iteration count bounded.
- **Subagent-based planning prevents mode-switching deadlocks.** The whiteboarding -> building handoff should use clean context boundaries.

### 2503.15478 - SWEET-RL
- **Credit assignment across turns matters.** In multi-step execution, knowing which step caused success/failure is critical. Plans should make per-phase success criteria explicit and independently verifiable.

### 2505.04921 - Multimodal Reasoning Survey
- **Adaptive reasoning depth based on task complexity.** Simple tasks need fast/shallow planning; complex tasks need deliberate/deep planning. Supports the whiteboarding skill's existing complexity classification but suggests it should more aggressively adjust planning depth.

## Current Skill Gaps

### Gap 1: Plan Output Lacks Execution-Critical Structure
The current plan file schema (Phase 3: DETAIL) produces sections with "Files to create/modify," "Implementation details," and "Dependencies." But it lacks:
- **Dependency ordering** between phases (which phase must complete before which)
- **Per-file dependency graphs** (which file imports from which)
- **Estimated effort distribution** across phases
- **Explicit success criteria** per phase that are independently verifiable

### Gap 2: No Mechanism to Prevent Plan-Execution Gap
PaperBench shows that the gap between planning and execution is the core failure mode. The current skill produces a plan and hands off to `/code-foundations:building`, but the plan format does not enforce:
- **Micro-step granularity** in task descriptions
- **Binary pass/fail criteria** for each task (not vague descriptions)
- **Forced completion signals** (no way for the executing agent to skip phases)

### Gap 3: No Analysis Stage Between Plan and Execution
PaperCoder's analysis stage -- per-file implementation specs between planning and coding -- reduced execution errors to 0.81% of code lines. The current whiteboarding skill jumps from high-level plan directly to implementation checklist with no intermediate analysis.

### Gap 4: Missing Effort/Complexity Estimation Per Phase
PaperBench shows agents fail to allocate effort across components. The current skill assigns a model recommendation (haiku/sonnet/opus) per phase but does not estimate relative effort, expected difficulty, or time allocation.

### Gap 5: No Hierarchical Task Decomposition Beyond Two Levels
CityNavAgent and PaperBench both show that hierarchical decomposition (3+ levels) dramatically reduces execution complexity. Current plans have only two levels: Phase -> Tasks. There is no intermediate "sub-goal" level for complex phases.

### Gap 6: No Pattern Memory Integration
CityNavAgent's global memory graph improved success rate by 16.6%. The current skill searches for patterns (Step 1a) but does not systematically record or reference outcomes of previous plans for similar features.

## Specific Proposals

### Proposal 1: Add Dependency Graph to Plan Output

- **Research basis:** 2504.17192 (PaperCoder) -- Logic Design stage determines execution order and file dependencies; without it, generation produces import errors and inconsistencies.
- **Current gap:** Plan phases list "Dependencies: [what must be done first]" as free text. No structured dependency graph. No execution ordering.
- **Proposed change:** Add to the Plan File Schema in Phase 5 (SAVE), after the Implementation Checklist:

```markdown
## Dependency Graph

### Phase Ordering
Phase 1 → Phase 2 → Phase 3
(Phase 2 depends on Phase 1's data layer; Phase 3 depends on Phase 2's API)

### File Dependencies (per phase)
Phase 1:
1. `src/types.ts` (no deps)
2. `src/db/schema.ts` (imports: types.ts)
3. `src/db/queries.ts` (imports: schema.ts, types.ts)

Phase 2:
4. `src/api/handlers.ts` (imports: queries.ts, types.ts)
5. `src/api/routes.ts` (imports: handlers.ts)
```

Also add to the DETAIL phase (Phase 3) Section Template:

```markdown
**File ordering:** [numbered list of files in implementation order, with import dependencies noted]
```

- **Expected impact:** Eliminates cross-file dependency errors during building execution. Gives the executing agent a concrete sequence rather than requiring it to infer order from vague descriptions.

### Proposal 2: Add Per-Phase Binary Success Criteria

- **Research basis:** 2504.01848 (PaperBench) -- Hierarchical rubrics with binary leaf criteria enable granular progress measurement. Per-turn credit assignment (2503.15478, SWEET-RL) requires independently verifiable success signals per step.
- **Current gap:** Phase tasks are described as checklist items ("[ ] Specific task with file path") but lack explicit pass/fail criteria. The building workflow's POST-GATE checks are generic skill checklists, not plan-specific verification.
- **Proposed change:** Add to the Section Template in Phase 3 (DETAIL):

```markdown
**Success criteria (binary):**
- [ ] [Specific, testable condition]: e.g., "User model has `email` and `passwordHash` fields"
- [ ] [Specific, testable condition]: e.g., "`POST /api/users` returns 201 with valid payload"
- [ ] [Specific, testable condition]: e.g., "Unit test `user.create.test.ts` passes"
```

Add to Phase 5 Plan File Schema, within each phase:

```markdown
**Verification:**
- [ ] [Binary criterion 1]
- [ ] [Binary criterion 2]
```

And add this rule to Phase 3:
> **Every task must have at least one binary success criterion.** If you cannot define a testable pass/fail condition, the task is underspecified -- break it down further.

- **Expected impact:** Makes plan-execution gap visible. The building agent can verify each step was completed correctly before proceeding. Prevents premature "done" claims (the primary failure mode found in PaperBench).

### Proposal 3: Add Analysis Stage Between DETAIL and SAVE

- **Research basis:** 2504.17192 (PaperCoder) -- The analysis stage generates per-file implementation specs (functional goals, I/O behaviors, inter-file dependencies, algorithmic constraints), reducing post-generation fixes to 0.81% of code lines.
- **Current gap:** Phase 3 (DETAIL) produces section-level descriptions. No per-file analysis. The building agent must infer implementation specifics from high-level descriptions.
- **Proposed change:** Insert a new Phase 3b: ANALYZE after Phase 3 (DETAIL), before VALIDATE:

```markdown
## Phase 3b: ANALYZE (Per-File Specs)

For each file listed in the plan, generate a brief implementation spec:

### File Spec Template
**File:** `path/to/file.ts`
**Purpose:** [1 sentence]
**Exports:** [functions/classes/types this file exposes]
**Imports from:** [other project files this depends on]
**Key logic:** [algorithm, data flow, or pattern to implement]
**Constraints:** [edge cases, error handling, performance requirements]
**Estimated size:** [small (<50 lines) / medium (50-200) / large (200+)]

### When to Include File Specs
| Plan Complexity | File Spec Requirement |
|----------------|----------------------|
| Simple (1-3 files) | Optional -- inline in section details |
| Medium (4-8 files) | Required for new files only |
| Complex (9+ files) | Required for all files |
```

- **Expected impact:** Bridges the plan-execution gap by giving the building agent per-file implementation guidance. Reduces ambiguity at the point of code generation. Aligns with PaperCoder's demonstrated improvement.

### Proposal 4: Add Effort Distribution Estimation

- **Research basis:** 2504.01848 (PaperBench) -- Agents fail to strategize about effort allocation, spending all effort on the first component and ignoring others. Performance plateaus after ~1 hour despite 12+ hours available.
- **Current gap:** Phases have model recommendations (haiku/sonnet/opus) but no effort estimates. No guidance for the building agent to pace itself across phases.
- **Proposed change:** Add to Phase 3 (DETAIL), after the YAGNI Gate:

```markdown
### Effort Distribution

After defining all sections, estimate relative effort:

| Phase | Estimated Effort | Risk Level | Notes |
|-------|-----------------|------------|-------|
| Phase 1: [name] | 20% | Low | Straightforward data layer |
| Phase 2: [name] | 50% | High | Core business logic, most edge cases |
| Phase 3: [name] | 30% | Medium | Integration, depends on Phase 2 quality |

**Rules:**
- Effort must sum to 100%
- Flag any phase over 40% effort -- consider splitting
- Flag any phase marked "High Risk" -- add extra success criteria
```

Add to Plan File Schema:

```markdown
## Effort Distribution
| Phase | Effort | Risk |
|-------|--------|------|
```

- **Expected impact:** Prevents the "all effort on first phase" failure mode. Gives the building agent explicit pacing guidance. Surfaces phases that are too large and should be split.

### Proposal 5: Enforce Micro-Step Granularity for Complex Plans

- **Research basis:** 2504.01848 (PaperBench) -- Forced piecemeal execution (IterativeAgent) tripled scores for weak agents. 2505.05622 (CityNavAgent) -- 3-level hierarchical decomposition reduces exponential complexity. 2504.17192 (PaperCoder) -- Sequential dependency-aware generation with full context of prior outputs.
- **Current gap:** Tasks in the plan are single-level checklist items. Complex phases may have tasks that are themselves multi-step, but no mechanism forces further decomposition.
- **Proposed change:** Add to Phase 3 (DETAIL), modifying the Section Template:

```markdown
### Granularity Gate

For each task in the checklist:
- Can this task be completed in a single focused action (one file, one function, one test)?
  - YES → Keep as-is
  - NO → Decompose into sub-tasks

**Maximum task scope:** A single task should touch at most 1-2 files and produce a verifiable output.

**Complex phase template (when a phase has >5 tasks):**
### Phase N: [Name]
#### Sub-goal N.1: [Name]
- [ ] Task N.1.1: [specific action]
- [ ] Task N.1.2: [specific action]
**Checkpoint:** [what must be true before proceeding to N.2]

#### Sub-goal N.2: [Name]
- [ ] Task N.2.1: [specific action]
...
```

- **Expected impact:** Prevents the executing agent from facing tasks that are too large to complete in a single action, which PaperBench identifies as the primary cause of plan-execution gap. The checkpoint mechanism prevents premature advancement.

### Proposal 6: Add Cross-File Coordination Flags

- **Research basis:** 2504.02605 (Multi-SWE-bench) -- Multi-file patches are dramatically harder; performance drops significantly when changes touch >1 file. 2504.17192 (PaperCoder) -- Logic design stage explicitly models inter-file dependencies.
- **Current gap:** Plan sections list files to modify but do not flag when changes in one file require coordinated changes in another.
- **Proposed change:** Add to Phase 3 (DETAIL), Section Template:

```markdown
**Cross-file coordination:**
- [ ] `file-a.ts` ↔ `file-b.ts`: [what must stay in sync, e.g., "type definitions must match API response shape"]
```

And add to Crisis Invariants:

```markdown
| **Flag cross-file dependencies** | Multi-file changes fail 2-3x more often than single-file; explicit coordination prevents drift |
```

- **Expected impact:** Makes multi-file coordination points visible to the building agent. Reduces the highest-failure-rate scenario identified in Multi-SWE-bench.

### Proposal 7: Add Configuration-as-First-Class-Output

- **Research basis:** 2504.17192 (PaperCoder) -- Configuration generation as a planning substep separates parameters from implementation, enabling researchers to iterate without code changes.
- **Current gap:** No guidance on whether the plan should produce configuration files, environment variables, or other parameter surfaces.
- **Proposed change:** Add to Phase 3 (DETAIL), after Section Template:

```markdown
### Configuration Surface

If the feature involves configurable parameters (API keys, feature flags, thresholds, model settings):

**Create a Configuration section in the plan:**
```
## Configuration
| Parameter | Default | Source | Notes |
|-----------|---------|--------|-------|
| MAX_RETRIES | 3 | env var | Configurable per environment |
| API_BASE_URL | /api/v1 | config file | Must match client expectations |
```

**Rule:** Hardcoded values that a user might want to change → extract to configuration. Identify these during planning, not during implementation.
```

- **Expected impact:** Prevents hardcoded values that require code changes to modify. Surfaces configuration decisions during planning when they are cheapest to make.

## Priority Ranking

| Rank | Proposal | Impact Rationale |
|------|----------|-----------------|
| 1 | **Proposal 2: Per-Phase Binary Success Criteria** | Directly addresses the #1 failure mode (premature completion claims) found in PaperBench. Highest leverage change. |
| 2 | **Proposal 5: Micro-Step Granularity for Complex Plans** | Forced piecemeal execution tripled agent scores. Second-highest-leverage structural change. |
| 3 | **Proposal 1: Dependency Graph in Plan Output** | Eliminates cross-file ordering errors demonstrated as critical by PaperCoder. Essential for multi-file features. |
| 4 | **Proposal 4: Effort Distribution Estimation** | Directly prevents "all effort on first phase" failure mode. Low implementation cost, high diagnostic value. |
| 5 | **Proposal 3: Analysis Stage (Per-File Specs)** | Demonstrated 0.81% fix rate in PaperCoder. High impact but adds planning time; best for medium/complex plans. |
| 6 | **Proposal 6: Cross-File Coordination Flags** | Targets highest-failure-rate scenario in Multi-SWE-bench. Focused and easy to add. |
| 7 | **Proposal 7: Configuration-as-First-Class-Output** | Good practice but lower priority than structural improvements to plan format. |
