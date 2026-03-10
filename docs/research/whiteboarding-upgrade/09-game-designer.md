# Game Designer Analysis: Whiteboarding Skill Improvements

## Persona Lens

As a game designer who has shipped AAA titles, I see implementation plans as **quest chains**: each phase is a quest with prerequisites, clear objectives, completion criteria, and fallback paths. The best quest designs share traits with the best software plans: they decompose complex goals into a dependency graph where each node has a clear "done" state, constraints propagate from global (the whole campaign) to local (this encounter), and the player always knows what to do next even when things go wrong.

The current whiteboarding skill produces plans that are *linear checklists*. From a quest design perspective, this is like a quest chain with no branching, no fallback strategies, no explicit constraint tracking, and no way to handle "what if Phase 2 fails?" That works for simple side quests. For raid-level content (complex features), it breaks down.

---

## Key Research Findings

### 2603.04750 - HiMAP-Travel: Hierarchical Multi-Agent Planning for Long-Horizon Constrained Travel
**Core finding:** Sequential LLM agents suffer from "Constraint Drift under Long Tool Traces" -- as context grows during plan execution, attention to global constraints (budget, diversity, temporal feasibility) degrades measurably. On 5-day trip plans, budget satisfaction drops from 98% (Day 1) to 42% (Day 5) for sequential planners, but stays above 90% throughout when using hierarchical coordinator-executor architecture. The fix: structurally separate global constraint ownership (coordinator) from local execution (parallel executors), with a bargaining protocol for when executors hit infeasible allocations.

**Key numbers:** +8.67pp improvement over sequential baseline; 93% variance reduction; budget violations reduced 67%; 2.5x latency reduction through parallelization.

### 2603.05294 - StructuredAgent: AND/OR Trees for Long-Horizon Web Tasks
**Core finding:** Representing plans as AND/OR trees -- where AND nodes are required subgoals and OR nodes are alternative strategies -- enables dynamic plan revision, error back-propagation, and interpretable plans that support human intervention. The framework maintains the planning tree while the LLM handles only local decisions (node expansion, repair), preventing context overflow. Structured memory tracks which candidates satisfy which constraints, preventing greedy premature termination.

**Key insight:** Separating planning structure (maintained by framework) from local reasoning (handled by LLM) is essential. LLMs cannot reliably manage entire plan trees in context.

### 2603.03784 - DEVS: Specification-Driven Generation via Staged Decomposition
**Core finding:** Complex system generation succeeds when decomposed into two stages: (1) structural synthesis (what components exist and how they connect) and (2) behavioral synthesis (what each component does). Critically, parent modules should be conditioned on *actual* child interfaces, not planned interfaces, because "semantic drift" during implementation causes integration failures. Trace-based conformance testing validates behavior against specification-derived constraints when no ground truth exists.

**Key pattern:** Adaptive interface resolution -- generating parent from actual child implementations prevents integration failures from semantic drift.

### 2603.03024 - MA-CoNav: Master-Slave Multi-Agent with Reflection
**Core finding:** Hierarchical (master-subordinate) agent architecture drastically outperforms flat parallel collaboration (25.6% vs 8.4% SR for complex tasks; single agents: 0%). Dual-level reflection matters: local reflection catches immediate errors before action; global reflection extracts transferable lessons post-task. Structured experience memory (encoding failures as tuples of scene, erroneous action, cause, corrective action) enables retrieval-augmented error prevention.

**Key numbers:** Removing task planning drops SR to 5.2%. Removing reflection drops SR by 8.4 percentage points.

### 2603.04746 - Human-Agentic AI Teaming: Continuous Alignment
**Core finding:** For agentic systems with open-ended action capabilities, alignment is not a one-time configuration but must be continuously maintained. Team Situation Awareness (shared understanding of state) divergence predicts coordination failures. Checkpoint cadence matters: too infrequent allows drift, too frequent adds overhead. The paper estimates 10-20% of total task time should go to meaningful review at checkpoints.

### 2603.04659 - GIANT: Plan Globally, Act Locally
**Core finding:** In multi-agent systems, combining long-horizon strategic planning with short-horizon tactical adjustment outperforms either alone. The global plan provides direction; the local policy handles dynamic interactions. When deviation from global plan exceeds a threshold, replan from current position.

### 2603.02688 - RAG for Robots: Retrieval Over Internal Knowledge
**Core finding:** For novel tasks with available documentation, retrieving and interpreting procedural documents outperforms relying on internal knowledge (F1=0.537 vs 0.446). The primary bottleneck is not retrieval but cross-modal grounding -- mapping abstract representations to concrete reality. This parallels how whiteboarding plans often fail not because the plan is wrong, but because the plan's abstractions don't map cleanly to the actual codebase.

---

## Current Skill Gaps

### Gap 1: No Constraint Classification or Tracking
The current whiteboarding skill captures "Constraints" as a flat list in the problem statement. It does not distinguish between **global constraints** (must hold across the entire plan -- e.g., "no new dependencies," "budget of 3 days") and **local constraints** (per-phase -- e.g., "this file must stay backward compatible"). HiMAP-Travel (2603.04750) shows this distinction is critical: mixing global and local constraints in a flat list causes drift during execution.

### Gap 2: No Fallback Strategies
Plans are linear sequences. There is no mechanism for "if Approach A fails at Phase 2, try Approach B." StructuredAgent (2603.05294) shows that AND/OR decomposition -- where required steps (AND) coexist with alternative strategies (OR) -- dramatically improves robustness. In game design terms: the current skill builds quest chains with no alternative quest paths.

### Gap 3: No Dependency Graph Between Phases
The plan template lists phases sequentially (Phase 1, Phase 2, ...) but never states *why* that order matters. There is no explicit "Phase 3 depends on Phase 1 and Phase 2" notation. This means the building skill cannot parallelize independent phases or know which phases to re-plan when a dependency fails. GIANT (2603.04659) and HiMAP-Travel (2603.04750) both show that explicit dependency information enables parallelization and targeted replanning.

### Gap 4: No Interface Contracts Between Phases
DEVS (2603.03784) shows that integration failures come from "semantic drift" -- Phase 2 produces something slightly different from what Phase 3 expects. The current plan template has "Dependencies: [what must be done first]" but no explicit specification of *what* Phase 1 produces that Phase 2 consumes. In game design: no quest gives a reward item that the next quest requires as input. The connection is implicit.

### Gap 5: No Risk Assessment or Reflection Points
MA-CoNav (2603.03024) shows dual-level reflection improves success by 8.4 percentage points. The current skill has no mechanism for: (a) identifying which phases are highest-risk before building, or (b) defining what to check after each phase completes. The YAGNI Gate is the closest, but it asks "is this needed?" not "what could go wrong here?"

### Gap 6: No Replanning Triggers
The human-agentic teaming paper (2603.04746) emphasizes that alignment must be continuously maintained with explicit triggers for resynchronization. The current whiteboarding skill produces a static plan with no guidance on when the builder should stop and replan versus push forward.

---

## Specific Proposals

### Proposal 1: Constraint Classification System

- **Research basis:** 2603.04750 (HiMAP-Travel) -- structural separation of global vs. local constraints prevents drift; budget satisfaction on Day 5 improves from 42% to 91%.
- **Current gap:** Constraints are a flat list with no classification. During building, global constraints are forgotten as context grows.
- **Proposed change:** Replace the flat `## Constraints` section in the plan file schema with a classified constraint system. Add to the DETAIL phase (Phase 3) a constraint classification step.

Add after line 283 (before the YAGNI Gate):

```markdown
### Constraint Classification (MANDATORY)

Before finalizing sections, classify all constraints:

```markdown
## Constraints

### Global Constraints (Must hold across ALL phases)
- [ ] [constraint] — **Enforced by:** [how the builder checks this]

### Per-Phase Constraints
| Phase | Local Constraint | Verification |
|-------|-----------------|--------------|
| Phase 1 | [constraint] | [how to check] |
| Phase 2 | [constraint] | [how to check] |
```

**Rules:**
- Budget, dependency limits, API compatibility, performance targets = GLOBAL
- File-specific requirements, function signatures, test coverage = LOCAL
- Every global constraint must have an explicit enforcement mechanism
- Global constraints must be restated in the plan file header (not buried in phase details)
```

Update the Plan File Schema (line 388-393) to include:

```markdown
## Global Constraints (Checked After EVERY Phase)
- [ ] [constraint] — Enforcement: [mechanism]

## Per-Phase Constraints
[listed within each phase]
```

- **Expected impact:** Prevents constraint drift during long building sessions. The builder agent can check global constraints after each phase commit, catching violations early rather than discovering them at final verification.

### Proposal 2: AND/OR Phase Decomposition with Fallback Paths

- **Research basis:** 2603.05294 (StructuredAgent) -- AND/OR trees enable error back-propagation and fallback exploration; plans become robust to single-point failures.
- **Current gap:** Plans are purely sequential AND-chains. If Phase 2 fails, there is no guidance on alternatives.
- **Proposed change:** Add an optional `**Fallback:**` field to each phase in the plan template, and introduce OR-node notation for phases with alternative approaches.

Add to the Section Template (after line 279):

```markdown
**Fallback:** [What to do if this phase fails]
- Alt approach: [brief description]
- Scope reduction: [what to cut if this is too hard]
- Skip condition: [when this phase can be skipped entirely]
```

Add to Phase 3 instructions (around line 256):

```markdown
### Identifying Critical Phases

For each section, classify:

| Phase | Type | Fallback? |
|-------|------|-----------|
| Phase 1 | REQUIRED (AND) | Alt approach: [X] |
| Phase 2 | REQUIRED (AND) | Scope reduction: [Y] |
| Phase 3 | ALTERNATIVE (OR with Phase 4) | If fails, try Phase 4 |
| Phase 4 | ALTERNATIVE (OR with Phase 3) | If fails, try Phase 3 |

**OR phases:** When two approaches could work, list both. Builder tries the recommended one first; if it fails, switches to the alternative without replanning the entire feature.
```

- **Expected impact:** Reduces the cost of Phase-level failure from "replan everything" to "try the fallback." In game design terms: this is the difference between a game-over screen and a respawn checkpoint.

### Proposal 3: Explicit Phase Dependencies and Interface Contracts

- **Research basis:** 2603.03784 (DEVS) -- adaptive interface resolution (conditioning parent on actual child interfaces) prevents integration failures; 2603.04750 (HiMAP-Travel) -- explicit dependency information enables parallelization.
- **Current gap:** Phases have `Dependencies: [what must be done first]` but no specification of what each phase produces or consumes. No parallelization guidance.
- **Proposed change:** Replace the informal dependency line with a structured dependency and interface specification.

Replace the Section Template dependency line (line 278) with:

```markdown
**Produces:** [concrete output — e.g., "UserService class with create/read/update methods"]
**Consumes:** [what this phase needs from earlier phases — e.g., "Database schema from Phase 1"]
**Depends on:** [Phase numbers] | **Parallel with:** [Phase numbers that can run simultaneously]
```

Add to the Plan File Schema, after the Implementation Checklist:

```markdown
## Dependency Graph

```
Phase 1 ──→ Phase 3
Phase 2 ──→ Phase 3
Phase 1 ──┐
           ├──→ Phase 4
Phase 2 ──┘
```

**Parallel groups:** [Phase 1, Phase 2] can execute simultaneously.
**Sequential gates:** Phase 3 requires Phase 1 + Phase 2 complete.
```

- **Expected impact:** Enables the building skill to parallelize independent phases (or at least signal to the user that they can be built in any order). Interface contracts catch integration mismatches before they happen -- the builder can verify "does Phase 1's actual output match what Phase 2 expects?" before proceeding.

### Proposal 4: Risk-Rated Phases with Reflection Checkpoints

- **Research basis:** 2603.03024 (MA-CoNav) -- dual-level reflection improves SR by 8.4pp; structured experience memory enables error prevention; 2603.04746 (Human-AI Teaming) -- checkpoint cadence of every major decision point; 10-20% of task time on review is necessary cost.
- **Current gap:** No risk assessment. No reflection points. The building skill's POST-GATE is the only checkpoint, applied uniformly regardless of risk.
- **Proposed change:** Add a risk rating to each phase during whiteboarding, with corresponding reflection depth.

Add to Phase 3 (DETAIL), after the Section Template:

```markdown
### Risk Rating (Per Phase)

| Risk Level | Signal | Reflection Depth |
|------------|--------|------------------|
| LOW | Well-understood pattern, < 2 files | Quick self-check: "Does output match spec?" |
| MEDIUM | Some unknowns, 2-5 files | Verify interface contracts + run affected tests |
| HIGH | New pattern, > 5 files, or touches critical path | Full review: check global constraints, verify interfaces, run all tests, consider rollback |

**Rate each phase:**
```markdown
### Phase N: [Name] — Risk: HIGH
**Risk factors:** [why this phase is risky]
**What could go wrong:** [specific failure modes]
**Rollback plan:** [how to undo this phase if it breaks things]
```

**Rule:** HIGH-risk phases get extra time budgeted. Don't let a HIGH-risk phase run without a rollback plan.
```

- **Expected impact:** Front-loads risk awareness into the plan. The builder knows which phases need extra care before starting. Rollback plans prevent the "we broke everything and can't undo it" failure mode that kills projects.

### Proposal 5: Replanning Triggers

- **Research basis:** 2603.04746 (Human-AI Teaming) -- continuous alignment requires explicit triggers for resynchronization, not just periodic checkpoints; 2603.04750 (HiMAP-Travel) -- cooperative bargaining protocol where executors can reject infeasible sub-goals and trigger re-planning.
- **Current gap:** The plan is static once saved. There is no guidance on when the builder should stop building and return to whiteboarding. The building skill's gates check quality but don't check plan validity.
- **Proposed change:** Add a "Replanning Triggers" section to every plan.

Add to the Plan File Schema (after Test Plan, before Notes):

```markdown
## Replanning Triggers

Conditions that should halt building and return to whiteboarding:

| Trigger | Detection | Response |
|---------|-----------|----------|
| A global constraint becomes infeasible | [specific signal] | Re-whiteboard constraints |
| Phase dependency produces different interface than expected | Interface mismatch at consumption point | Re-whiteboard affected phases |
| Effort exceeds 2x estimate for any phase | Phase taking much longer than planned | Re-whiteboard scope |
| New requirement discovered during building | User or codebase reveals unknown unknown | Add to plan or re-whiteboard |
```

Also add to the Anti-Rationalization Table:

```markdown
| "The plan says X but reality is Y, I'll just adjust" | Plan drift is constraint drift. If reality diverges from plan, STOP and update the plan file. Silent adjustments compound. |
```

- **Expected impact:** Prevents the most common failure mode in long builds: the plan stops matching reality but the builder keeps going. Explicit triggers give permission to pause and replan, which feels like "going backward" but actually prevents far more expensive rework.

### Proposal 6: Pre-Execution Grounding Check

- **Research basis:** 2603.02688 (RAG for Robots) -- primary bottleneck is cross-modal grounding (mapping abstract plan to concrete reality), not the plan itself; grounding gap accounts for 0.448 F1 loss vs only 0.091 F1 loss from imperfect retrieval.
- **Current gap:** The whiteboarding skill searches the codebase in Phase 1 (UNDERSTAND) and Phase 2 (EXPLORE), but the plan itself uses abstract descriptions ("create UserService class") without verifying these abstractions map to the actual codebase structure. The building skill then has to do this grounding on the fly.
- **Proposed change:** Add a grounding verification step to Phase 4 (VALIDATE), before the plan is saved.

Add to Phase 4, after the Test Coverage Question:

```markdown
### Grounding Check (MANDATORY)

Before saving, verify the plan's abstractions match codebase reality:

| Plan Reference | Codebase Reality | Match? |
|----------------|-----------------|--------|
| "Modify UserController" | `src/controllers/user.controller.ts` exists, handles routes X, Y, Z | Yes |
| "Add to existing auth middleware" | `src/middleware/auth.ts` -- uses pattern A, exports B | Yes |
| "Create new database migration" | Migrations use [tool], naming pattern is [X] | Yes |

**If any reference doesn't match:** Update the plan to use actual file paths, actual class names, actual patterns. Abstract plans that don't ground to real code produce integration failures.
```

- **Expected impact:** Eliminates the class of errors where plans reference files, classes, or patterns that don't exist or work differently than assumed. This is the "grounding gap" that 2603.02688 identifies as the primary bottleneck -- not the plan quality, but the plan-to-reality mapping.

---

## Priority Ranking

| Rank | Proposal | Impact | Effort |
|------|----------|--------|--------|
| 1 | **Proposal 1: Constraint Classification** | Prevents the #1 failure mode (constraint drift) identified across multiple papers | Low -- restructures existing content |
| 2 | **Proposal 5: Replanning Triggers** | Prevents silent plan drift, the #2 failure mode | Low -- adds a new section to plan template |
| 3 | **Proposal 3: Dependencies and Interface Contracts** | Enables parallelization, prevents integration failures | Medium -- new template fields + dependency graph |
| 4 | **Proposal 6: Pre-Execution Grounding Check** | Eliminates plan-to-reality mapping errors before building starts | Low -- adds verification step to VALIDATE |
| 5 | **Proposal 4: Risk-Rated Phases** | Front-loads risk awareness, prevents "everything broke" scenarios | Medium -- new rating system per phase |
| 6 | **Proposal 2: AND/OR Fallback Paths** | Reduces cost of phase failure from "replan everything" to "try alternative" | Medium-High -- requires conceptual shift in how plans are structured |

**Rationale for ranking:** Proposals 1 and 5 address the most common and most damaging failure modes (constraint drift and silent plan divergence) with the least implementation effort. Proposal 3 has the highest structural impact by enabling the building skill to reason about phase relationships. Proposal 6 is a quick win that catches a specific class of errors. Proposals 4 and 2 are higher-effort but provide defense-in-depth.

**Game design analogy:** Proposals 1-3 are like fixing your quest tracker so players always know their objectives and which quests can be done in parallel. Proposals 4-6 are like adding difficulty ratings, respawn checkpoints, and a minimap -- they make the experience more forgiving and navigable, but the core quest chain has to work first.
