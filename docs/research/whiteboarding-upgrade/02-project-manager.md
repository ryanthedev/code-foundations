# Project Manager Analysis: Whiteboarding Skill Improvements

## Persona Lens

As a senior project manager with 20 years in software delivery, the principles most relevant to producing high-quality implementation plans are:

1. **Work Breakdown Structure (WBS) discipline** -- every deliverable must decompose into concrete, estimable, assignable work packages with clear completion criteria.
2. **Dependency mapping and critical path analysis** -- plans fail when implicit dependencies are discovered mid-execution. Explicit dependency graphs prevent cascading delays.
3. **Risk identification at planning time** -- the cheapest time to find a risk is during planning. Every plan section should surface what could go wrong and what the fallback is.
4. **Validation separation** -- the person who writes the plan should not be the sole validator. Independent review catches assumptions the planner cannot see.
5. **Progressive elaboration** -- plans should detail near-term work precisely and defer far-term detail, because information improves over time.
6. **Replanning triggers** -- a plan without defined conditions for replanning is a plan that will be followed off a cliff.

The current whiteboarding skill is strong on discovery and approach comparison but weak on structural rigor in the DETAIL phase, has no concept of replanning or rollback, and lacks explicit dependency tracking between plan sections.

---

## Key Research Findings

### Paper 2503.09572 (Plan-and-Act)
- **Separation of planning and execution** improves long-horizon task success dramatically (57.58% on WebArena-Lite vs. prior methods). The planner generates high-level steps with explicit reasoning; the executor handles low-level actions.
- **Each plan step must include an explicit "Reasoning" field** explaining why the step is needed -- not just what to do.
- **Replanning is essential**, triggered when execution produces unexpected results. The replanner receives: original task + action history + current state + failure info, then generates a refined plan from the current state forward.
- **Plan step count should stay under 7** for manageable error propagation. Longer plans accumulate errors.
- **Vague plan steps are the primary failure mode** (e.g., "analyze the results" -- the executor cannot translate abstract instructions into concrete actions).

### Paper 2503.11951 (SagaLLM)
- **Every operation in a multi-step plan needs a defined compensating transaction** -- i.e., a rollback strategy. If step 3 fails, what happens to steps 1 and 2?
- **LLMs cannot reliably self-validate** (grounded in Godel's incompleteness theorems). Independent validation is architecturally essential.
- **Context loss in long workflows** causes contradictory decisions. Plans must persistently store goals, justifications, and dependencies in structured format.
- **Three state dimensions must be tracked**: Application State (what domain entities exist), Operation State (what was done and why), and Dependency State (what depends on what).
- **Dependency graphs** between operations enable determining the minimal affected set when something fails.

### Paper 2503.09501 (ReMA)
- **Meta-thinking (strategic oversight) should be separated from detailed execution**. A high-level agent generates strategy; a low-level agent executes. This decomposition improves out-of-distribution performance by up to 20%.
- **Applied to planning**: the whiteboarding phase is the meta-thinking layer. Plans that explicitly separate "what strategy to use" from "how to execute the strategy" produce better outcomes.

### Paper 2503.01935 (MultiAgentBench / MARBLE)
- **Cognitive Evolving Planning** significantly outperforms alternatives (including group discussion and naive planning) in coordination quality.
- **Optimal iteration count is 7** -- performance peaks then drops sharply. Plans with more than 7 phases risk coordination collapse.
- **Small teams win**: 3 agents achieve the best coordination-to-complexity ratio. This translates to planning: keep plan sections to 3-7 phases.
- **Group discussion in planning is counterproductive** -- it scores worst across all metrics. This validates the whiteboarding skill's one-question-at-a-time approach but suggests the skill should also discourage open-ended brainstorming sessions without structure.

### Paper 2503.00729 (CLEA)
- **Closed-loop planning with a critic** improves success rate by 67.3% over open-loop plans. The critic validates each action before execution.
- **44.4% of plan failures are due to outdated assumptions** -- the plan assumed conditions that no longer hold by execution time.
- **Sub-goal decomposition** (planning short action sequences toward sub-goals rather than full task plans) is more robust to environmental changes.
- **Belief state management** (FIFO history buffer with summarization) prevents context overflow in long-horizon tasks.

### Paper 2502.19411 (Code to Think, Think to Code)
- **Code-form plans improve instruction following by +5.7%** (CODEPLAN on AlpacaEval-2) and decision-making by +10.1% (ALFWorld). Using code-like structure (if/else, function decomposition) in plans -- even when the plan is not executable code -- improves reasoning organization.
- **Self-Planning + structured decomposition** is the recommended strategy for complex repository-level tasks.

### Paper 2502.12616 (QuaSAR)
- **Separating content from logical structure** (quasi-symbolic abstraction) improves reasoning accuracy by up to 8%. Applied to planning: separating "what we're building" from "how we reason about the build sequence" reduces planning errors.

---

## Current Skill Gaps

### Gap 1: No Dependency Tracking Between Sections
The DETAIL phase (Phase 3) produces sections with a `**Dependencies:** [what must be done first]` field, but there is no enforcement, no dependency graph, and no guidance on how to use this information. Dependencies are treated as documentation rather than as structural constraints that affect execution order and risk.

### Gap 2: No Replanning Triggers or Rollback Strategy
The plan assumes linear execution. There is no guidance on what happens when a phase fails during `/code-foundations:building`. No compensating actions are defined. No conditions are specified that should trigger plan revision. The building command has quality gates, but the plan itself does not anticipate failure scenarios.

### Gap 3: No Risk Identification
The YAGNI gate asks "is this section needed?" but never asks "what could go wrong with this section?" Plans produced by the whiteboarding skill contain zero risk information. From 20 years of PM experience: plans without risks are plans that will surprise you.

### Gap 4: Vague Implementation Details
The section template allows `**Implementation details:** [specific function/class/pattern]` but provides no enforcement against vague descriptions. Research (Plan-and-Act, 2503.09572) shows vague plan steps are the primary failure mode -- executors cannot translate abstract instructions into concrete actions.

### Gap 5: No Explicit Reasoning Per Section
Plan sections describe WHAT to do but not WHY. Research (Plan-and-Act, 2503.09572) shows that including explicit reasoning for each step helps both the executor and reviewers understand intent, improving execution accuracy.

### Gap 6: No Phase Count Guidance
The skill provides no guidance on how many phases/sections a plan should have. Research (MultiAgentBench, 2503.01935; Plan-and-Act, 2503.09572) converges on 7 as the maximum before error propagation and coordination overhead cause degradation.

### Gap 7: No Assumption Tracking
Research (CLEA, 2503.00729) shows 44.4% of plan failures stem from outdated assumptions. The current skill captures decisions but not the assumptions underlying those decisions. When assumptions change, the plan has no mechanism to identify which sections are affected.

### Gap 8: No Validation Separation
The skill validates the plan with the user (Phase 4), but there is no self-check mechanism. Research (SagaLLM, 2503.11951) demonstrates that self-validation is unreliable -- the same agent that produced the plan cannot reliably find its own errors.

---

## Specific Proposals

### Proposal 1: Add Dependency Graph to DETAIL Phase

- **Research basis:** SagaLLM (2503.11951) -- dependency graphs between operations enable determining the minimal affected set when something fails. CLEA (2503.00729) -- sub-goal decomposition with explicit dependencies is more robust than monolithic plans.
- **Current gap:** Dependencies field exists but is unstructured text with no enforcement or visualization.
- **Proposed change:** Add the following to Phase 3 (DETAIL), after the Section Template:

```markdown
### Dependency Graph (MANDATORY after all sections drafted)

After drafting all sections, construct a dependency graph:

| Section | Depends On | Blocks |
|---------|-----------|--------|
| Section 1 | (none) | Section 2, Section 3 |
| Section 2 | Section 1 | Section 4 |
| Section 3 | Section 1 | Section 4 |
| Section 4 | Section 2, Section 3 | (none) |

**Critical path:** Identify the longest dependency chain. This determines minimum elapsed time.

**Parallelizable sections:** Sections with no mutual dependencies can execute in parallel phases during building.

Write this table into the plan file under `## Dependency Graph`.
```

- **Expected impact:** Execution order becomes explicit. The building command can identify parallelizable work. Failed sections reveal their blast radius through the "Blocks" column.

---

### Proposal 2: Add Risk Register Per Section

- **Research basis:** CLEA (2503.00729) -- 44.4% of plan failures are from outdated assumptions. SagaLLM (2503.11951) -- every operation needs a defined compensating transaction (rollback).
- **Current gap:** Zero risk identification in the planning process.
- **Proposed change:** Add to the Section Template in Phase 3:

```markdown
### Section Template (updated)

```markdown
### Section N: [Name]

**Goal:** [what this section accomplishes]
**Reasoning:** [WHY this section is needed -- what problem it solves]

**Files to create/modify:**
- `path/to/file.ts` - [what changes]

**Implementation details:**
- [specific function/class/pattern]

**Dependencies:** [what must be done first]

**Assumptions:** [conditions that must be true for this section to succeed]
**Risk:** [what could go wrong + mitigation]
**If this fails:** [rollback strategy -- what to undo or how to recover]
```
```

- **Expected impact:** Forces identification of assumptions at planning time. When assumptions prove false during building, the plan shows which sections are affected and what to do. Rollback strategies prevent half-completed work from creating inconsistent state.

---

### Proposal 3: Add Phase Count Constraint

- **Research basis:** MultiAgentBench (2503.01935) -- optimal iteration count is 7, performance drops sharply beyond this. Plan-and-Act (2503.09572) -- plan step count should stay under 7 for manageable error propagation.
- **Current gap:** No guidance on how many sections a plan should have.
- **Proposed change:** Add to Phase 3 (DETAIL), before the Section Template:

```markdown
### Phase Count Constraint

| Complexity | Target Sections | Hard Maximum |
|-----------|----------------|--------------|
| Simple | 2-3 | 4 |
| Medium | 3-5 | 6 |
| Complex | 5-7 | 7 |

**If your plan exceeds 7 sections:** You are planning too granularly. Combine related sections or split into multiple plans (multi-phase delivery).

**If your plan has 1 section:** This is a task, not a plan. Execute directly or use `/code-foundations:building` without a plan file.
```

- **Expected impact:** Prevents over-decomposition that leads to coordination overhead and error accumulation. Research shows performance degrades beyond 7 units of work.

---

### Proposal 4: Add Explicit Reasoning Field to Section Template

- **Research basis:** Plan-and-Act (2503.09572) -- each plan step must have explicit Reasoning explaining why the step is needed. QuaSAR (2502.12616) -- separating content from logical structure improves reasoning accuracy.
- **Current gap:** Sections describe WHAT but not WHY.
- **Proposed change:** Add `**Reasoning:** [WHY this section is needed]` to the Section Template (already included in Proposal 2 above). Additionally, add to the anti-rationalization table:

```markdown
| "The reason is obvious" | If it's obvious, writing it takes 10 seconds. If it's wrong, the explicit reasoning lets someone catch it. |
```

- **Expected impact:** WHY serves as a self-check: if you cannot articulate why a section exists, it may not be needed (reinforces YAGNI). It also helps the building executor understand intent, reducing misinterpretation.

---

### Proposal 5: Add Replanning Triggers to Plan File Schema

- **Research basis:** Plan-and-Act (2503.09572) -- replanning is essential, triggered when execution produces unexpected results. CLEA (2503.00729) -- closed-loop planning with critic improves success rate by 67.3%. SagaLLM (2503.11951) -- plans need compensating transactions.
- **Current gap:** Plans assume linear execution with no adaptation mechanism.
- **Proposed change:** Add to the Plan File Schema (Phase 5), after `## Notes`:

```markdown
## Replanning Triggers

Conditions that should cause plan revision during building:

| Trigger | Affected Sections | Action |
|---------|------------------|--------|
| [condition 1, e.g., "API X is deprecated"] | Section 2, 4 | [replan/skip/substitute] |
| [condition 2, e.g., "test framework incompatible"] | Section 3 | [replan with alternative] |
| [condition 3, e.g., "performance target not met"] | Section 5 | [add optimization section] |

**Default triggers (always apply):**
- Build fails after implementation section -> Revert section, diagnose, replan
- POST-GATE reviewer finds architectural issue -> Replan affected sections
- New information invalidates an assumption -> Check Assumptions column, replan affected sections
```

- **Expected impact:** Transforms the plan from a static document into a living decision framework. The building command can check replanning triggers at each phase gate.

---

### Proposal 6: Add Assumption Tracking

- **Research basis:** CLEA (2503.00729) -- 44.4% of plan failures are from outdated assumptions. SagaLLM (2503.11951) -- persistent state tracking across long workflows prevents contradictory decisions.
- **Current gap:** Decisions are captured but not the assumptions behind them.
- **Proposed change:** Add to the Plan File Schema (Phase 5), after `## Chosen Approach`:

```markdown
## Key Assumptions

| # | Assumption | Verified? | If Wrong, Affects |
|---|-----------|-----------|-------------------|
| A1 | [e.g., "Database supports JSON columns"] | Yes/No/Untested | Section 2, 3 |
| A2 | [e.g., "API rate limit is 1000 req/min"] | Yes/No/Untested | Section 4 |
| A3 | [e.g., "Users have Node.js 18+"] | Yes/No/Untested | All sections |
```

Also add to Phase 3 guidance:

```markdown
### Assumption Extraction (after all sections drafted)

Review each section and extract assumptions into the Key Assumptions table. An assumption is:
- A fact you believe to be true but have not verified
- A condition that must hold for the approach to work
- An external dependency outside your control

**If an assumption is "Untested" and affects 3+ sections:** Verify it NOW before finalizing the plan. Use codebase search, web research, or ask the user.
```

- **Expected impact:** Makes invisible assumptions visible. During building, when something unexpected happens, the team can consult the assumptions table to find which assumptions were invalidated and which sections are affected.

---

### Proposal 7: Add Plan Self-Check Before User Validation

- **Research basis:** SagaLLM (2503.11951) -- LLMs cannot reliably self-validate, but structured checklists partially compensate. ReMA (2503.09501) -- separating meta-thinking from execution improves quality.
- **Current gap:** Phase 4 (VALIDATE) goes straight to user review. No structured self-check first.
- **Proposed change:** Add to Phase 4, before "Full Plan Review":

```markdown
### Plan Self-Check (before presenting to user)

Run through this checklist BEFORE presenting the plan for user review:

- [ ] Every section has a Reasoning field (not just Goal)
- [ ] Every section has specific file paths (not "relevant files")
- [ ] Every section has Dependencies filled in (even if "none")
- [ ] Dependency graph has no cycles
- [ ] Critical path identified
- [ ] Assumptions extracted and high-impact ones verified
- [ ] No section has vague implementation details (test: could a different developer execute this without asking questions?)
- [ ] Phase count is within limits (max 7)
- [ ] Replanning triggers identified for top 3 risks
- [ ] Each section's "If this fails" has a concrete action (not just "fix it")

**If any check fails:** Fix before presenting to user. Do NOT present an incomplete plan.
```

- **Expected impact:** Catches structural problems before they reach the user. The user's review time is spent on strategic decisions, not catching missing fields.

---

### Proposal 8: Encourage Code-Form Plan Structure for Complex Plans

- **Research basis:** Code to Think (2502.19411) -- code-form plans improve instruction following by +5.7% and decision-making by +10.1%. Even non-executable code-like structure helps reasoning organization.
- **Current gap:** Plans use only prose and markdown checklists. No guidance on when to use more structured representations.
- **Proposed change:** Add to Phase 3, as an optional enhancement:

```markdown
### Code-Form Plans (for complex/medium plans with conditional logic)

When a plan involves conditional paths, loops, or complex orchestration, consider expressing the execution flow in pseudocode alongside the prose plan:

```
# Phase 1: Set up database schema
create_migration(schema_changes)
run_migration()

# Phase 2: Implement API endpoints
for each endpoint in [users, posts, comments]:
    create_route(endpoint)
    create_handler(endpoint)
    create_tests(endpoint)

# Phase 3: Frontend integration
if spa_architecture:
    create_api_client()
    create_components()
else:
    create_server_rendered_views()
```

This is NOT code to execute. It is a structural representation that makes execution order, parallelism, and conditional branches explicit.

**Use when:** Plan has conditional paths, iteration over similar items, or complex ordering constraints.
**Do not use when:** Plan is simple linear sequence (prose checklist is clearer).
```

- **Expected impact:** Gives the building executor a clearer mental model of execution flow. Conditional branches and loops become explicit rather than buried in prose.

---

## Priority Ranking

| Rank | Proposal | Impact | Effort | Rationale |
|------|----------|--------|--------|-----------|
| 1 | **P2: Risk Register + Assumptions + Rollback** | High | Low | Addresses the #1 cause of plan failure (44.4% from outdated assumptions per CLEA). Three fields added to an existing template. |
| 2 | **P1: Dependency Graph** | High | Low | One table added after sections are drafted. Enables critical path analysis and blast radius assessment. Directly from SagaLLM's dependency state tracking. |
| 3 | **P5: Replanning Triggers** | High | Medium | Transforms static plans into adaptive frameworks. Requires new section in plan schema but dramatically improves building resilience. |
| 4 | **P4: Explicit Reasoning Field** | Medium | Low | One field per section. Research-backed (Plan-and-Act) improvement that also reinforces YAGNI by forcing justification. |
| 5 | **P7: Plan Self-Check** | Medium | Low | Structured checklist before user review. Catches quality issues before they propagate. |
| 6 | **P3: Phase Count Constraint** | Medium | Low | Simple constraint table. Prevents the documented performance degradation beyond 7 phases (MultiAgentBench). |
| 7 | **P6: Assumption Tracking** | Medium | Medium | Overlaps with P2 but adds a centralized tracking table. Most valuable for complex plans. |
| 8 | **P8: Code-Form Plans** | Low | Low | Optional enhancement for complex plans. Clear research backing but narrower applicability. |

**Implementation recommendation:** Proposals 1, 2, 4, and 5 can be implemented together as a single update to SKILL.md -- they are mostly additions to the existing Section Template and Plan File Schema. Proposal 7 (self-check) should follow immediately as it enforces the new fields. Proposals 3, 6, and 8 are independent and can be added in any order.
