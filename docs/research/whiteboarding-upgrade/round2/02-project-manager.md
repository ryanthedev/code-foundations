# Whiteboarding Plan Granularity: A Project Manager's Analysis

**Perspective:** Senior PM, 20 years in software delivery
**Question:** How detailed should a whiteboarding plan be, given that independent subagents consume it?

---

## 1. What the Building Architecture Already Handles

The building skill's execution architecture solves several planning concerns that whiteboarding does NOT need to duplicate:

**Discovery and reality-checking.** The pre-gate agent searches the codebase, verifies file existence, identifies gaps between plan assumptions and reality, and writes a discovery document. The plan does not need to describe current codebase state in detail -- pre-gate will map it fresh with up-to-date information.

**Design decomposition to pseudocode.** Pre-gate loads `cc-pseudocode-programming` and `aposd-designing-deep-modules`, then produces implementation-ready pseudocode from plan-level descriptions. The plan does not need function signatures, class hierarchies, or step-by-step logic -- that is pre-gate's job.

**Quality verification.** Post-gate loads `aposd-verifying-correctness`, `cc-quality-practices`, `aposd-reviewing-module-design`, and `cc-defensive-programming`. It checks spec match, dead code, correctness across 6 dimensions, and defensive programming. The plan does not need to specify quality criteria per phase -- the gate skills encode them.

**Sequencing enforcement.** TaskCreate with blockedBy chains makes phase ordering structural, not advisory. The plan does not need to explain WHY Phase 2 depends on Phase 1 -- the orchestrator enforces it mechanically.

**Model selection.** Auto-detection resolves haiku/sonnet/opus per phase based on task count, file count, and keyword signals. The plan can override but does not need to justify model choices -- the algorithm handles defaults.

**Test coverage enforcement.** The VERIFY phase checks test coverage against the plan's declared level. The plan needs only to STATE the level (100%, backend only, etc.), not describe how to verify it.

**What this means for planning:** At least half of what a traditional PM would put in a handoff document is already encoded in the execution architecture. The plan is not the only source of truth -- it is one input alongside discovery findings, pseudocode, and skill checklists.

---

## 2. The Right Level of Detail

### What the Plan MUST Contain (Subagent-Critical)

These items cannot be discovered by pre-gate because they represent user intent and design decisions that were made during whiteboarding:

| Element | Why Subagents Need It | Current Template Status |
|---------|----------------------|------------------------|
| **Problem context** (what and why) | Frames all downstream decisions | Present (Context section) |
| **Chosen approach + rationale** | Pre-gate needs to know the architectural direction, not rediscover it | Present (Chosen Approach) |
| **Phase boundaries** (what goes in each phase) | Orchestrator creates TaskCreate chains from these | Present (Implementation Checklist) |
| **File paths per phase** | Pre-gate verifies these exist; implementation agent targets them | Present (Files list) |
| **Acceptance criteria / success definition** | Post-gate needs to know what "correct" means beyond generic quality | Partially present (Test Plan) |
| **Constraints and non-goals** | Prevents scope creep across all agents | Present (Constraints) but no explicit non-goals |
| **Test coverage level** | VERIFY phase gates on this | Present (Test Coverage) |

### What the Plan Should HINT At (Discovery Fuel)

These items help pre-gate search more effectively but do not need to be exhaustive:

| Element | Right Level | Wrong Level |
|---------|-------------|-------------|
| Implementation approach per phase | "Use the existing EventEmitter pattern in src/events/" | Full pseudocode with function bodies |
| Edge cases | "Handle the case where user has no subscription" | Exhaustive error matrix |
| Dependencies between phases | "Phase 2 needs the types defined in Phase 1" | Detailed interface contracts |
| Patterns to follow | "Match the pattern in src/routes/auth.ts" | Copy-pasted code examples |

### What the Plan Should NOT Contain (Pre-Gate Territory)

| Over-specification | Why It Hurts |
|-------------------|-------------|
| Function signatures and class hierarchies | Pre-gate discovers actual codebase state; plan signatures become stale immediately |
| Step-by-step implementation logic | This is literally pseudocode -- pre-gate's job |
| Current file contents or structure descriptions | Pre-gate reads the actual files; plan descriptions are snapshots that rot |
| Detailed error handling strategy | `cc-defensive-programming` skill handles this during post-gate |
| Performance considerations | `cc-performance-tuning` and `aposd-optimizing-critical-paths` handle this during VERIFY |

---

## 3. PM Argument: Optimal Granularity for Independent Executor Handoff

### From WBS Theory

A Work Breakdown Structure decomposes deliverables to the level where work packages can be independently estimated and assigned. The key principle: **decompose to the level where the executor can succeed without calling back to the planner.**

In traditional PM, this is the "8/80 rule" -- work packages should be between 8 and 80 hours. Below 8 hours, you are micromanaging. Above 80, you have hidden complexity.

For this system, the equivalent question is: **can the pre-gate agent, given this phase description, produce correct pseudocode without needing to ask the user?**

If yes -- the plan is detailed enough.
If no -- the plan needs more detail in that specific area.

### The Independent Executor Problem

The building architecture has a specific constraint that most PM handoff documents do not: **the executor has zero shared context with the planner.** Each subagent starts fresh. It reads files, not conversation history.

This changes the calculus. In a human team, an architect can write a terse design doc because the developers can walk over and ask questions. Here, there is no walk-over. The pre-gate agent has exactly three inputs: the plan file, the phase description, and whatever it finds by searching the codebase.

This means the plan must be **self-contained at the phase level** -- each phase description must make sense without reading the full conversation that produced it.

### Critical Path Implications

The building skill's phase chain (PRE-GATE -> IMPLEMENT -> POST-GATE -> CHECKPOINT) means that a single unclear phase description blocks the entire pipeline. Pre-gate returns UPDATE_PLAN, the orchestrator pauses, the user must intervene. This is the most expensive failure mode because it breaks flow and requires context-switching.

The plan should front-load clarity on the phases most likely to cause UPDATE_PLAN returns: phases with novel patterns, external dependencies, or architectural decisions.

### The Goldilocks Zone

From the research, three findings converge on the same conclusion:

1. **Plan-and-Act (2503.09572):** Plans with explicit "Reasoning" fields per step outperform bare task lists. The planner should state WHY, not just WHAT. But the plan should be 4-7 steps, not 20.

2. **ReMA (2503.09501):** Separating meta-thinking (strategy) from execution reasoning improves OOD performance by up to 20%. The plan is meta-thinking; pseudocode is execution reasoning. Mixing them degrades both.

3. **CLEA (2503.00729):** Sub-goal decomposition with short action sequences outperforms full-task plans because shorter sequences are more robust to environmental changes. Pre-gate discovery IS the environment observation that makes plans adaptive.

4. **SagaLLM (2503.11951):** Independent validation agents need full visibility into intent, not just outputs. Post-gate needs to know what "correct" means for THIS phase, not just generic quality. Plans should include phase-level acceptance criteria.

5. **MultiAgentBench (2503.01935):** Small teams (3 agents) outperform larger ones. The building architecture already has exactly 3 agents per phase (pre-gate, implementation, post-gate). Plans should not try to coordinate more complexity than this pipeline can handle -- keep phases small enough for 3 agents to handle.

The optimal plan is: **enough intent and constraints for pre-gate to produce correct pseudocode on the first attempt, but no implementation detail that pre-gate should discover fresh.**

---

## 4. Concrete Recommendation: Updated Section Template

The current template (whiteboarding SKILL.md lines 264-279) is close but needs adjustments. Here is the recommended revision:

```markdown
### Phase N: [Name]

**Goal:** [What this phase accomplishes — one sentence stating the deliverable]

**Why:** [Why this phase exists — what user-visible or architectural outcome it enables.
This is the "Reasoning" field that Plan-and-Act research shows improves executor performance.]

**Files to create/modify:**
- `path/to/file.ts` - [what changes, at the level of "add validation endpoint" not "add function validateInput(req: Request): boolean"]
- `path/to/other.ts` - [what changes]

**Approach:**
- [Key design decision: "Use EventEmitter pattern matching src/events/notifications.ts"]
- [Key constraint: "Must maintain backward compatibility with v2 API"]
- [Pattern to follow: "Match error handling in src/middleware/errors.ts"]

**Acceptance criteria:**
- [What "done" means for THIS phase specifically]
- [Observable behavior, not implementation detail]
- [Example: "Health endpoint returns 200 with version field" not "healthHandler function exists"]

**NOT in scope:** [Explicit exclusions to prevent scope creep in implementation agent]

**Dependencies:** [What must be done first — only list cross-phase dependencies]
```

### What Changed From Current Template

| Current | Recommended | Rationale |
|---------|-------------|-----------|
| No "Why" field | Added **Why** | Plan-and-Act research: explicit reasoning per step improves executor accuracy |
| "Implementation details" (vague) | **Approach** (design decisions + patterns to follow) | Separates meta-thinking from execution reasoning (ReMA finding) |
| No acceptance criteria | Added **Acceptance criteria** | SagaLLM finding: independent validators need intent, not just outputs |
| No explicit exclusions | Added **NOT in scope** | Building anti-rationalization table already warns about scope creep; this makes the boundary explicit |
| "specific function/class/pattern" | Removed function-level detail | Pre-gate territory; plan-level signatures go stale |

### Section Size Guidance

The current template says "200-300 words each." This is roughly correct but should be qualified:

- **Simple phase (1-2 files, mechanical):** 100-150 words. Pre-gate can fill gaps from codebase search.
- **Medium phase (3-5 files, clear pattern):** 200-300 words. Current template range.
- **Complex phase (6+ files, novel pattern, architectural):** 300-400 words. Front-load the WHY and APPROACH sections because pre-gate has more to get right.

If a phase description exceeds 400 words, the phase is too large. Split it.

---

## 5. Research Backing

### Direct Support for Plan-Executor Separation

**Plan-and-Act (2503.09572)** demonstrates that separating planning from execution improves multi-step task completion. Their architecture mirrors building's structure: a planner generates numbered steps with reasoning, an executor handles actions. Key finding: plans with explicit "Reasoning" fields per step outperform bare task lists. The whiteboarding plan is the planner output; pre-gate + implementation agents are the executor.

**ReMA (2503.09501)** shows that decomposing reasoning into meta-thinking (strategy/planning) and execution reasoning produces up to 20% improvement on out-of-distribution tasks. The whiteboarding plan IS meta-thinking. Pseudocode IS execution reasoning. Mixing them in the plan document degrades both. This validates keeping implementation detail out of the plan.

### Direct Support for Independent Validation

**SagaLLM (2503.11951)** establishes that LLMs cannot reliably self-validate (citing Godel's incompleteness as the theoretical basis). Independent validation agents need "full visibility into intent" to catch errors. The post-gate agent IS the independent validator. It needs the plan's acceptance criteria to know what "correct" means beyond generic quality checklists. This is the strongest argument for adding explicit acceptance criteria per phase.

### Direct Support for Short Sub-Goal Sequences

**CLEA (2503.00729)** shows that sub-goal decomposition with short action sequences outperforms full-task planning because shorter sequences are more robust to environmental changes. Building's phase structure already does this. The implication for whiteboarding: keep phases small (the 400-word / split-if-larger rule). Pre-gate discovery is the "environment observation" step that keeps each phase grounded in current reality.

### Direct Support for Small Team Coordination

**MultiAgentBench (2503.01935)** finds that 3 agents achieve the best coordination-to-complexity ratio, and adding agents increases coordination cost faster than capability. Building already uses exactly 3 agents per phase. The plan should not try to encode coordination logic between agents -- the orchestrator handles that. Plans should focus on WHAT and WHY, leaving HOW-TO-COORDINATE to the building skill.

### Indirect Support

**Code-Enhanced Reasoning (2502.19411):** Non-executable code representations (pseudocode, templates) improve reasoning organization even without execution. This validates the pre-gate agent writing pseudocode as a separate artifact from the plan. The plan should describe intent; pseudocode should describe structure.

**QuaSAR (2502.12616):** Separating content from logical structure improves reasoning accuracy. The plan is content (what to build); the building skill's gate structure is logical structure (how to verify). Mixing them in the plan would be the anti-pattern this research warns against.

**MAPoRL (2502.18439):** Co-training produces better collaboration than prompting alone. The building skill's agent templates with baked-in skills are the equivalent of co-training -- agents are specialized for their role. Plans should not try to replicate skill knowledge (e.g., defensive programming guidance) because agents already have it.
