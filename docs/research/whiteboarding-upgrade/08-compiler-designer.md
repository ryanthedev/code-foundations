# Compiler Designer Analysis: Whiteboarding Skill Improvements

## Persona Lens

A compiler transforms a high-level specification (source code) into executable instructions (machine code) through a disciplined pipeline: lexing, parsing into an AST, semantic analysis (type checking, dependency resolution), intermediate representation, optimization passes, and code generation. Each phase has well-defined inputs, outputs, and invariants. The whiteboarding skill performs an analogous transformation -- it takes a vague feature request (high-level specification) and must produce an implementation-ready plan (executable steps). The question is: where does the current pipeline lose fidelity, introduce ambiguity, or fail to enforce invariants that a compiler would never tolerate?

Key compiler/PL principles applied here:
- **AST-like hierarchical decomposition**: Plans should have a typed tree structure, not flat checklists
- **Dependency resolution via topological sort**: Task ordering should be derived from dependency edges, not ad-hoc sequencing
- **Type systems as contracts**: Intermediate representations between planning and execution need enforceable schemas
- **Optimization passes**: Plans should undergo explicit refinement passes (dead-code elimination = YAGNI, constant folding = collapsing trivially sequential steps)
- **Formal verification**: Plans should have checkable properties before execution begins

## Key Research Findings

### 2511.02424 - ReAcTree: Hierarchical Agent Trees with Control Flow
- **Finding 1**: Flat, monolithic task trajectories cause hallucination and logical failures as context grows. Hierarchical decomposition into isolated subgoal contexts nearly doubles success rates (31% to 61%).
- **Finding 2**: Three control flow types (sequence, fallback, parallel) from behavior trees provide robust, interpretable execution semantics for coordinating subtasks.
- **Finding 3**: Dynamic decomposition at runtime outperforms static up-front decomposition because task complexity is only revealed during execution.
- **Finding 4**: Each subgoal node should have isolated context -- only its own history, not the entire task trajectory.

### 2511.17198 - HTAM: Hierarchical Task Abstraction Mechanism
- **Finding 1**: The most effective architecture for specialized domains directly mirrors the domain's intrinsic task-dependency graph, not social roles or generic reasoning loops.
- **Finding 2**: Organizing work into processing layers where each layer operates on preceding layers' outputs naturally prevents dependency violations.
- **Finding 3**: Plan&Execute with a rigid predetermined plan fails because it cannot adapt to intermediate results -- but the answer is not no structure, it is layered structure with within-layer flexibility.

### 2603.01327 - SWE-Adept: Structured Issue Resolution
- **Finding 1**: Hypothesis-driven branching with Git-based checkpointing enables exploring multiple solution strategies without losing progress. Limiting to 3 hypotheses max is optimal.
- **Finding 2**: Structured to-do lists with explicit progress tracking outperform free-form "think-and-edit" loops. The to-do list is dynamic -- expandable when feedback reveals missing steps.
- **Finding 3**: Semantic checkpointing (naming steps by meaning, not by hash) enables agents to reason about and reference prior states.
- **Finding 4**: Two-stage filtering (structural info first, full content later) minimizes wasted context. This applies to planning too: lightweight assessment before deep investigation.

### 2603.02070 - Exploring Plan Space through Conversation
- **Finding 1**: LLMs should not perform actual planning computation -- they should translate between natural language and formal representations while delegating computation to reliable solvers.
- **Finding 2**: Users ask fewer but richer questions when given suggested questions (11.4 vs 22.8), and each question effectively multiplexes into many formal queries (41.7 average).
- **Finding 3**: Context should be reset per decision epoch to prevent hallucination accumulation, while maintaining coherence within each epoch.
- **Finding 4**: Six structured question types for goal conflicts (why unsolvable, how to fix, why-not, what-if, can, how) provide a complete vocabulary for exploring the plan space.

### 2603.01912 - ViviDoc: Structured Intermediate Representations
- **Finding 1**: A structured intermediate representation (DocSpec) between planning and execution creates a "contract" that constrains the error-prone intent-to-code translation. The DocSpec decomposes into State, Render, Transition, Constraint components.
- **Finding 2**: Human review should be placed at maximum leverage points: after planning (before code) and after output (final review).
- **Finding 3**: The intermediate representation must be both human-readable and machine-parseable -- it serves as a contract between pipeline stages.

### 2603.02050 - Human-Agent Collaboration Modes
- **Finding 1**: Users want fluid switching between handoff (delegate sub-task) and concurrent (work together) collaboration modes. Forcing one mode frustrates.
- **Finding 2**: Routine/mechanical sub-tasks should be handed off to AI entirely; subjective/taste-dependent decisions should remain with the human.

## Current Skill Gaps

### Gap 1: Flat Phase Structure Without Dependency Edges
The current whiteboarding skill produces a flat checklist of phases (Phase 1, Phase 2, ...) with implicit ordering. There are no explicit dependency edges between tasks. A compiler would never emit instructions without first resolving the dependency graph. The plan says `**Dependencies:** [what must be done first]` in the section template, but this is freeform text, not a structured DAG that can be validated.

### Gap 2: No Intermediate Representation Contract
The plan file schema (Phase 5) jumps from "Chosen Approach" directly to "Implementation Checklist." There is no structured intermediate representation that serves as a typed contract between planning and execution. The `/code-foundations:building` command receives a markdown file with conventions but no schema enforcement. ViviDoc's DocSpec pattern shows this gap costs controllability.

### Gap 3: No Control Flow Type Annotations
All plan phases are implicitly sequential. There is no mechanism to express that some phases can run in parallel, that some are fallback alternatives, or that some are conditional. ReAcTree shows that annotating subtasks with control flow types (sequence, fallback, parallel) dramatically improves execution success.

### Gap 4: No Goal-Conflict Analysis
The current skill asks questions about constraints and success criteria but does not explicitly check whether constraints conflict with each other or with the chosen approach. The plan space exploration paper (2603.02070) shows that understanding goal conflicts (via MUS/MCS analysis) is fundamental to producing feasible plans. The YAGNI gate is a weak proxy -- it catches unnecessary features but not infeasible combinations.

### Gap 5: No Hypothesis Branching in Approach Selection
Step 2b generates 2-3 approaches and picks one. But SWE-Adept shows that for uncertain problems, the plan should preserve the ability to branch to alternatives during execution. The current skill treats approach selection as a one-time, irreversible decision.

### Gap 6: No Explicit Complexity Budget
The skill classifies complexity (simple/medium/complex) for question count but does not propagate this into the plan structure. A compiler allocates registers and manages stack frames based on function complexity. Plans should have explicit complexity budgets -- estimated context window usage, number of files touched, expected agent count for building.

### Gap 7: Static Decomposition Only
HTAM and ReAcTree both show that static up-front decomposition fails when task complexity is only revealed during execution. The current skill produces a fully-specified plan and hands it off. There is no mechanism for the building phase to signal "this phase is more complex than planned, decompose further."

## Specific Proposals

### Proposal 1: Task Dependency Graph in Plan File Schema

- **Research basis:** 2511.17198 (HTAM) -- "aligning agent architecture with a domain's intrinsic task dependencies is a superior strategy"; 2511.02424 (ReAcTree) -- hierarchical decomposition with isolated subgoal contexts doubles success rates
- **Current gap:** The plan file has flat numbered phases with freeform `**Dependencies:**` text. No topological validation is possible.
- **Proposed change:** Add a `## Dependency Graph` section to the plan file schema, after `## Implementation Checklist`. Each phase gets an ID and explicit `depends_on` references:

```markdown
## Dependency Graph

| Phase | ID | Depends On | Control Flow |
|-------|-----|-----------|--------------|
| Database schema | P1 | -- | -- |
| API endpoints | P2 | P1 | sequence |
| Frontend components | P3 | P2 | parallel(P3a, P3b) |
| Integration tests | P4 | P2, P3 | sequence |
```

Add to the DETAIL phase instructions:
```
### Dependency Validation (MANDATORY)

After defining all sections, construct the dependency graph:
1. Assign each section an ID (P1, P2, ...)
2. For each section, list which other sections it depends on
3. Verify NO circular dependencies exist
4. Verify the graph has a valid topological ordering
5. Identify which sections can execute in parallel (no shared dependencies)

**If circular dependency found:** Refactor sections to break the cycle. This indicates entangled concerns.
```

- **Expected impact:** Plans become topologically sortable. The building command can validate execution order. Parallel-capable phases are identified up front, enabling multi-agent execution during building.

### Proposal 2: Control Flow Type Annotations on Plan Phases

- **Research basis:** 2511.02424 (ReAcTree) -- behavior tree control flow nodes (sequence, fallback, parallel) provide "robust and interpretable execution logic"; choosing the right control flow type is critical for success
- **Current gap:** All phases are implicitly sequential. No mechanism for expressing parallelism, fallbacks, or conditionals.
- **Proposed change:** Add a `**Control Flow:**` field to each phase in the plan file schema, with these types:

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Control Flow:** sequence | parallel | fallback | conditional
```

Add to DETAIL phase instructions:
```
### Control Flow Selection (Per Phase)

For each section, determine the control flow type:

| Situation | Control Flow | Rationale |
|-----------|-------------|-----------|
| Steps must complete in order | sequence | Default; most common |
| Independent tasks on separate files | parallel | Can be executed by separate agents |
| Multiple possible implementations | fallback | Try approach A; if it fails, try B |
| Depends on runtime discovery | conditional | Only execute if condition met |

**Default to sequence if uncertain.** Parallel and fallback require justification.
```

- **Expected impact:** The building command can dispatch parallel phases to separate agents. Fallback phases provide built-in recovery paths. Plans become more expressive without more complexity.

### Proposal 3: Structured Intermediate Representation (Plan Contract)

- **Research basis:** 2603.01912 (ViviDoc) -- "The DocSpec serves as a contract between pipeline stages... This decomposition isolates the most error-prone step, the translation from intent to code, and constrains it with a structured specification rather than ambiguous natural language"; 2603.01327 (SWE-Adept) -- semantic checkpointing enables reasoning about prior states
- **Current gap:** The plan file is markdown with conventions but no enforceable schema. The building command interprets it heuristically.
- **Proposed change:** Add a `## Contract` section to each phase in the plan file schema that specifies preconditions, postconditions, and invariants:

```markdown
### Phase N: [Name]
**Model:** [recommended model]

**Contract:**
- **Preconditions:** [what must be true before this phase starts]
  - File `X` exists with function `Y`
  - Test suite passes
- **Postconditions:** [what must be true after this phase completes]
  - New endpoint responds to GET /api/resource
  - All existing tests still pass
- **Invariants:** [what must remain true throughout]
  - No breaking changes to public API
```

Add to DETAIL phase instructions:
```
### Contract Specification (Per Phase)

For each section, define the contract:
1. **Preconditions**: What files, functions, or states must exist before starting?
2. **Postconditions**: What observable outcome proves this phase succeeded?
3. **Invariants**: What existing behavior must NOT break?

Postconditions must be TESTABLE -- they should map to assertions, not descriptions.
Bad: "The authentication system works"
Good: "POST /api/auth/login returns 200 with valid JWT when given valid credentials"
```

- **Expected impact:** The building command can verify preconditions before starting a phase and postconditions after completing it. Invariants feed directly into the POST-GATE reviewer. Plans become self-validating.

### Proposal 4: Goal-Conflict Detection During Approach Selection

- **Research basis:** 2603.02070 -- "Minimal Unsolvable Subsets as Explanation Primitive: MUS and MCS provide a principled, minimal explanation for why goals conflict and what to do about it"; six structured question types for exploring conflicts
- **Current gap:** The skill checks constraints individually but never checks whether constraints conflict with each other or with the chosen approach.
- **Proposed change:** Add a conflict detection step after Step 2b (Generate Alternatives) and before the Decision:

```markdown
### Step 2c: Conflict Analysis (MANDATORY for Medium/Complex)

Before selecting an approach, check for conflicts:

1. List all constraints from Phase 1
2. List all properties of the chosen approach
3. For each constraint pair, ask: "Can both be satisfied simultaneously?"
4. For each constraint vs approach property, ask: "Does this approach violate this constraint?"

**Conflict Resolution Template:**
| Constraint A | Constraint B | Conflict? | Resolution |
|-------------|-------------|-----------|------------|
| Real-time updates | No WebSocket dependency | YES | Use SSE instead |
| 100% test coverage | Ship by Friday | TENSION | Prioritize critical path tests |

**If unresolvable conflict found:** Surface it to the user via AskUserQuestion:
"These constraints conflict: [A] vs [B]. Which takes priority?"

**Do NOT proceed to Phase 3 with unresolved conflicts.**
```

- **Expected impact:** Prevents plans that are internally inconsistent. Surfaces trade-offs explicitly rather than discovering them during implementation. Reduces rework from infeasible plans.

### Proposal 5: Fallback Approach Preservation

- **Research basis:** 2603.01327 (SWE-Adept) -- "explore multiple competing hypotheses on isolated branches rather than iterating destructively on a single solution. This preserves the ability to revert and reuse partial progress"; limiting to 3 hypotheses max is optimal
- **Current gap:** Step 2b generates 2-3 approaches, picks one, and discards the others. If the chosen approach fails during building, there is no structured fallback.
- **Proposed change:** Modify the plan file schema to preserve rejected approaches as structured fallbacks:

```markdown
## Chosen Approach

**[Approach name]**
[Rationale from Phase 2]

## Fallback Approaches

### Fallback 1: [Name]
**Trigger:** [Under what conditions should we switch to this approach]
**Key difference from primary:** [What changes in the plan]
**Reusable phases:** [Which phases from the primary plan carry over]
**Phases that change:** [Which phases need new implementation]

### Fallback 2: [Name]
...
```

Add to the anti-rationalization table:
```
| "We committed to an approach, changing now wastes work" | Sunk cost fallacy. SWE-Adept research shows hypothesis branching with checkpoint reuse outperforms single-path commitment. Fallback approaches preserve partial progress. |
```

- **Expected impact:** Building can switch approaches without restarting planning. Fallback triggers make the switch decision explicit rather than a judgment call under pressure.

### Proposal 6: Complexity Budget and Decomposition Triggers

- **Research basis:** 2511.02424 (ReAcTree) -- "Dynamic expansion: agents decide at runtime whether to act or decompose further"; 2511.17198 (HTAM) -- layered structure where each layer has bounded scope
- **Current gap:** Complexity classification (simple/medium/complex) only affects question count. It does not propagate into plan structure or create runtime decomposition triggers.
- **Proposed change:** Add complexity budgets to the plan file schema and decomposition triggers to each phase:

```markdown
## Complexity Budget

| Metric | Budget | Rationale |
|--------|--------|-----------|
| Total phases | [N] | Based on complexity classification |
| Max files per phase | [M] | >6 files = should split phase |
| Max tasks per phase | [K] | >6 tasks = should split phase |
| Estimated total files | [F] | Informs model selection |

### Phase N: [Name]
**Model:** [recommended model]
**Decomposition trigger:** If this phase touches >6 files or reveals >6 new tasks, split into sub-phases before proceeding.
```

Add to DETAIL phase instructions:
```
### Complexity Budget (After All Sections Defined)

Validate the plan against these thresholds:

| Classification | Max Phases | Max Tasks/Phase | Max Files/Phase |
|---------------|-----------|----------------|----------------|
| Simple | 3 | 3 | 3 |
| Medium | 5 | 5 | 5 |
| Complex | 8 | 6 | 6 |

**If any phase exceeds its budget:** Split it into sub-phases. A phase that touches too many files is doing too much -- it has low cohesion.

**If total phases exceed budget:** Re-examine scope. Either reduce scope or upgrade complexity classification.
```

- **Expected impact:** Prevents monolithic phases that overwhelm the building agent. Enforces the compiler principle that each compilation unit should have bounded complexity. Provides explicit signals for when the building command should request further decomposition.

### Proposal 7: Structured Question Types for Plan Space Exploration

- **Research basis:** 2603.02070 -- users ask "fewer but richer questions" (11.4 vs 22.8) when given suggested question types; six structured question types (why, how, why-not, what-if, can, how) provide complete coverage of plan-space exploration
- **Current gap:** Phase 1 questions are generic (what outcome, what constraints, what does done look like). They do not help the user reason about trade-offs or explore the plan space systematically.
- **Proposed change:** Add structured question types to Phase 2, after research and before approach generation:

```markdown
### Step 2a-bis: Plan Space Exploration (Medium/Complex Only)

After research but before generating approaches, help the user explore the plan space with targeted questions. Use these question types:

| Type | Template | Purpose |
|------|----------|---------|
| Why-not | "Why not use [existing pattern/library]?" | Surfaces hidden constraints |
| What-if | "What if we [relaxed constraint X]?" | Reveals flexibility in requirements |
| Can | "Can we achieve [goal] without [costly element]?" | Tests necessity of expensive parts |
| Trade-off | "Which matters more: [property A] or [property B]?" | Resolves ambiguity in priorities |

Ask 1-2 of these based on research findings. Each question should reference specific codebase or web research results.
```

- **Expected impact:** Questions become informed by research rather than generic. Users make better decisions because questions target specific trade-offs discovered during research. Aligns with the finding that fewer, richer questions outperform many generic ones.

## Priority Ranking

| Rank | Proposal | Impact | Effort | Rationale |
|------|----------|--------|--------|-----------|
| 1 | **P3: Plan Contracts** | High | Medium | Directly addresses the highest-failure-rate step (intent to code translation). Postconditions make plans self-validating. Immediately usable by the building command's POST-GATE. |
| 2 | **P1: Dependency Graph** | High | Medium | Enables topological validation, parallel execution identification, and prevents the most common plan-execution failure: wrong ordering. Foundation for P2. |
| 3 | **P4: Goal-Conflict Detection** | High | Low | Low implementation cost (add one step to Phase 2). Prevents the costliest failure mode: building a plan that is internally contradictory. |
| 4 | **P6: Complexity Budget** | Medium | Low | Simple thresholds that catch over-scoped phases. Directly feeds model auto-detection (haiku/sonnet/opus). Small addition to the DETAIL phase. |
| 5 | **P2: Control Flow Types** | Medium | Medium | Valuable for multi-agent building but requires building command changes to fully leverage. Worth adding to plans now for documentation value. |
| 6 | **P5: Fallback Preservation** | Medium | Low | Low-cost insurance against approach failure. Most value on complex/uncertain projects. |
| 7 | **P7: Structured Question Types** | Low-Medium | Low | Improves question quality but the current generic questions already work. Most value for complex projects where trade-offs are non-obvious. |
