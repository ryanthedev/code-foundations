# Failure Analyst Analysis: Whiteboarding Skill Improvements

## Persona Lens
What failure modes threaten plan quality, and how can the skill prevent them?

Plans fail not because they lack detail, but because they contain unexamined assumptions, miss cross-cutting constraints, lack verification mechanisms, and provide no recovery path when reality diverges from expectations. The whiteboarding skill currently produces plans that are structurally reasonable but brittle -- they assume linear execution, ignore constraint drift over long implementations, provide no mechanism for the plan to verify itself, and treat decomposition as a flat checklist rather than a dependency graph with failure alternatives.

## Key Research Findings

### 1. Self-Verification is Impossible Without External Validators
**Paper:** ALAS (2505.12501) -- Chang & Geng, Stanford
LLMs cannot reliably verify their own output. This is not a capability gap but a structural limitation analogous to Godel's incompleteness. ALAS found that standalone LLMs failed 7/10 reactive planning trials, while systems with external validator agents succeeded 10/10. The failure mode: when an LLM generates a plan and then checks it, it applies the same biases and blind spots that produced errors in the first place.

**Implication for whiteboarding:** The current skill has no verification step for the plan itself. Phase 4 (VALIDATE) asks the *user* to confirm, but the user suffers from the same information asymmetry -- they see the plan and think "looks reasonable" without systematic checking.

### 2. Constraint Drift Causes Failures in Long-Horizon Plans
**Paper:** HiMAP-Travel (2603.04750) -- Bui, Li, Liu
Sequential LLM agents drift from global constraints as context grows. When a plan has N phases, by phase N the agent has forgotten the constraints from phases 1-3. HiMAP's solution: structural separation of global constraints (owned by a coordinator) from local execution (handled by phase-level executors). Budget violations, diversity requirement misses, and cross-phase conflicts all stem from this drift.

**Implication for whiteboarding:** The current skill produces a flat list of phases with no explicit constraint tracking. A plan for a feature with a performance budget, API rate limits, or cross-cutting concerns (auth, error handling) has no mechanism to ensure each phase respects global constraints.

### 3. Plans Without Fallback Alternatives Are Brittle
**Paper:** StructuredAgent (2603.05294) -- Lobo et al.
AND/OR tree decomposition outperforms flat task lists because OR nodes provide fallback strategies when the primary approach fails. Without alternatives, a single blocked step stalls the entire plan. Error back-propagation through OR trees successfully recovered from failures in 50%+ of cases.

**Implication for whiteboarding:** The current skill picks ONE approach in Phase 2 and decomposes only that approach. If implementation reveals the chosen approach is infeasible at phase 3 of 5, there is no documented fallback. The plan must be entirely redone.

### 4. Agentic Planning Gains Require Externally Grounded Feedback
**Paper:** Step-Wise PDDL Simulation (2603.06064) -- Gobel et al.
Agentic iteration only provides large gains when feedback is externally grounded (compiler errors, test failures), not when it is self-assessed. LLM agents incorrectly judged problems "unsolvable" 67% of the time. Self-assessed progress is unreliable.

**Implication for whiteboarding:** Plans should include explicit verification checkpoints with externally grounded criteria (tests pass, build succeeds, benchmark meets threshold) rather than subjective assessments ("implementation looks correct").

### 5. Context Loss is the #1 Failure Mode in Multi-Phase Work
**Paper:** VulnBot (2501.13411) -- Kong et al.
42.36% of all failures in autonomous penetration testing were caused by context/session loss. The solution: phase specialization with inter-phase summarization that compresses and forwards critical findings.

**Implication for whiteboarding:** The plan file currently serves as context preservation, but it lacks explicit "carry-forward" fields that identify what information from early phases is critical for later phases. When `/code-foundations:building` executes phase 4, it may not know that a decision in phase 1 constrains phase 4's options.

### 6. Compartmentalized Context Prevents Arithmetic/Logical Degradation
**Paper:** ALAS (2505.12501) -- Chang & Geng
When an LLM receives the entire problem context, arithmetic accuracy and constraint tracking degrade. ALAS found that giving each agent only task-relevant facts prevented travel time miscalculations that occurred in monolithic planning. The LLM treated a 60-minute journey as 30-45 minutes when the context was too large.

**Implication for whiteboarding:** Plan phases should be designed to be independently comprehensible. Each phase should contain its own constraints, inputs, and expected outputs rather than requiring the executor to hold the full plan in context.

### 7. Plans That Lose Domain-Specific Details Fail During Implementation
**Paper:** VerilogCoder (AAAI 2025, doi:10.1609/aaai.v39i1.32007)
Traditional high-level LLM plans lose signal transition details needed for Verilog implementation. TCRG-based planning that included domain-specific information (circuit signals, state transitions) improved pass rates by 33.9%. The failure: plans that are "correct at the right level of abstraction" but miss implementation-critical details.

**Implication for whiteboarding:** The current DETAIL phase template captures files and implementation details but has no checklist for domain-specific concerns. A plan for a database migration needs different detail than a plan for a UI feature, but the template is generic.

### 8. Schema-Gated Execution Prevents Drift Between Intent and Action
**Paper:** Talk Freely, Execute Strictly (2603.06394) -- Strickland et al.
Separating conversational authority (understanding what the user wants) from execution authority (what actually runs) with machine-checkable schemas prevents both LLM hallucination and parameter drift. No system in their survey achieved both high execution determinism and high conversational flexibility without schema gating.

**Implication for whiteboarding:** Plan files should include machine-checkable success criteria for each phase, not just prose descriptions. "Add authentication" is conversational. "All routes in /api/v2/* return 401 without valid JWT; test: `npm test -- --grep auth` passes" is schema-gated.

### 9. Weak Planner, Strong Executor is Optimal
**Paper:** Plan and Budget (2505.16122) -- Lin et al.
Decomposition planning should be done by a deliberately weaker model. A planner that can solve the task itself tends to over-specify or shortcut. The planner's job is to identify sub-problems and difficulty, not to solve them. Front-loading compute on early sub-questions (where uncertainty is highest) via cosine/polynomial decay scheduling improved efficiency by up to 193.8%.

**Implication for whiteboarding:** The skill already assigns model recommendations per phase, but it does not explicitly front-load planning effort on the highest-uncertainty phases. The current approach treats all phases equally in planning depth.

### 10. Hypothesis Branching Outperforms Linear Execution
**Paper:** SWE-Adept (2603.01327) -- He & Roy
For complex issues, exploring multiple competing hypotheses on isolated branches with checkpoint-based rollback outperforms iterating destructively on a single solution. Limiting to 3 hypotheses max was optimal -- more hypotheses degraded resolve rate.

**Implication for whiteboarding:** Plans for features with significant technical uncertainty should identify decision points where the implementation might need to branch, and pre-plan the fallback strategy.

### 11. Plans Need Disruption Recovery Protocols
**Paper:** ALAS (2505.12501) -- Chang & Geng
The LRCP (Local Reactive Compensation Protocol) shows that disruption recovery should follow a hierarchy: (1) local retry/rollback within affected component, (2) reorder neighboring components, (3) bounded replanning. Global replanning should be the last resort, not the default.

**Implication for whiteboarding:** The current plan file has no "what if this phase fails" section. When phase 3 of 5 fails during building, the builder has no guidance on whether to retry, skip, reorder, or replan.

## Current Skill Gaps

| Gap | Failure Mode | Evidence |
|-----|-------------|----------|
| No plan self-verification | Plans contain logical inconsistencies, impossible dependencies, or constraint violations that only surface during implementation | ALAS: 7/10 failure rate without external validation |
| No constraint tracking across phases | Global constraints (performance budgets, API limits, security requirements) violated by individual phases that are locally correct | HiMAP: constraint drift is the primary failure in long-horizon plans |
| No fallback alternatives | Single-approach plans stall entirely when one step is blocked | StructuredAgent: OR nodes recovered from 50%+ failures |
| No externally grounded checkpoints | "Done" is assessed subjectively, not by testable criteria | 2603.06064: self-assessed progress is unreliable 67% of the time |
| No inter-phase dependency tracking | Phase N breaks because it unknowingly depends on a decision in phase M | VulnBot: 42% of failures from context loss |
| No phase-level self-containment | Executor must hold entire plan in context, causing degradation | ALAS: context erosion causes arithmetic errors |
| No uncertainty-weighted planning | All phases get equal planning depth regardless of risk | 2505.16122: front-loading effort on uncertain phases improves efficiency 193.8% |
| No disruption recovery guidance | Builder has no guidance when a phase fails | ALAS LRCP: local-first recovery prevents cascading failures |

## Specific Proposals

### Proposal 1: Add a Plan Verification Gate After Phase 3

- **Research basis:** ALAS (2505.12501) -- external verification catches what self-assessment misses. LLMs cannot reliably verify their own output. Also: 2603.06064 -- self-assessed progress is wrong 67% of the time.
- **Failure mode addressed:** Plans with internal contradictions, impossible dependencies, or constraint violations that surface only during implementation.
- **Proposed change:** Add a new step between Phase 3 (DETAIL) and Phase 4 (VALIDATE) called "VERIFY PLAN INTEGRITY." This step should include a machine-checkable checklist:

```markdown
### Plan Integrity Check (MANDATORY before Phase 4)

Before presenting the plan to the user, verify:

| Check | Method |
|-------|--------|
| **Dependency ordering** | For each phase, confirm all listed dependencies are completed in earlier phases |
| **File conflict detection** | No two phases modify the same file in incompatible ways without explicit sequencing |
| **Constraint coverage** | Every constraint from the Problem Statement appears in at least one phase's success criteria |
| **Testability** | Every phase has at least one externally verifiable criterion (test passes, build succeeds, metric met) |
| **Import/API consistency** | New functions/types created in phase N and consumed in phase M exist in the plan with matching signatures |

If ANY check fails, fix the plan before presenting to user. Do NOT ask the user to verify plan integrity -- that is YOUR job.
```

- **Expected impact:** Catches the class of errors where plans "look reasonable" but contain structural flaws. Prevents the 7/10 failure rate observed in unvalidated LLM plans.

### Proposal 2: Add Cross-Cutting Constraints Section to Plan File Schema

- **Research basis:** HiMAP-Travel (2603.04750) -- structural separation of global vs. local constraints prevents drift. Plans fail when global constraints are stated once at the top and then forgotten during per-phase planning.
- **Failure mode addressed:** Individual phases are locally correct but violate global constraints (performance budgets, security requirements, API rate limits, backward compatibility).
- **Proposed change:** Add a `## Cross-Cutting Constraints` section to the plan file schema, between `## Chosen Approach` and `## Implementation Checklist`:

```markdown
## Cross-Cutting Constraints

Constraints that span multiple phases. Each phase MUST check these before marking complete.

| Constraint | Applies To | Verification |
|-----------|-----------|-------------|
| [e.g., Response time < 200ms] | All API phases | [e.g., Run benchmark after each phase] |
| [e.g., No breaking changes to public API] | Phases 2, 3, 4 | [e.g., Run API compatibility check] |
| [e.g., All new code has error handling] | All phases | [e.g., Review for uncaught exceptions] |
```

Also add to Phase 3 DETAIL questioning: "What constraints apply across ALL phases? (performance, security, compatibility, style)"

- **Expected impact:** Makes global constraints structurally visible at the phase level, preventing the constraint drift that is the primary cause of long-horizon plan failures.

### Proposal 3: Add Fallback Strategies to Each Phase

- **Research basis:** StructuredAgent (2603.05294) -- AND/OR tree decomposition with OR nodes for alternatives recovers from 50%+ of failures. SWE-Adept (2603.01327) -- hypothesis branching with max 3 alternatives is optimal.
- **Failure mode addressed:** Plan stalls when a single approach fails at phase N, with no documented alternative. The entire plan must be redone.
- **Proposed change:** Extend the Phase 3 Section Template to include an optional fallback:

```markdown
### Section N: [Name]

**Goal:** [what this section accomplishes]

**Files to create/modify:**
- `path/to/file.ts` - [what changes]

**Implementation details:**
- [specific function/class/pattern]

**Dependencies:** [what must be done first]

**Risk level:** [Low/Medium/High]

**If this approach fails:**
- [Fallback strategy -- alternative approach, skip conditions, or escalation path]
- [Signal that triggers fallback: specific error, test failure, or blocker]
```

Only require fallback documentation for Medium/High risk sections. Low risk sections can omit it.

- **Expected impact:** Reduces plan brittleness. When a phase fails during building, the executor has pre-analyzed guidance rather than needing to stop and re-plan from scratch.

### Proposal 4: Add Externally Grounded Success Criteria Per Phase

- **Research basis:** 2603.06064 -- self-assessed progress is unreliable (67% error rate on solvability judgments). 2603.06394 -- schema-gated execution with machine-checkable specs prevents drift between intent and action.
- **Failure mode addressed:** Phases are marked "done" based on subjective assessment ("looks correct") rather than objective verification. Errors propagate to later phases.
- **Proposed change:** Modify the plan file phase template to require a `**Done when:**` field with externally verifiable criteria:

```markdown
### Phase N: [Name]
**Model:** [recommended model]
- [ ] [Specific task with file path]

**Done when:**
- [ ] `npm test -- --grep "phase-n-feature"` passes
- [ ] `npm run build` succeeds with no new warnings
- [ ] [specific behavioral criterion verifiable by running the code]

**Files:**
- `path/to/file.ts`
```

Add to Phase 3 instructions: "For each section, define at least one machine-verifiable completion criterion. 'Looks correct' is NOT a valid criterion."

- **Expected impact:** Prevents the dominant failure mode of self-assessed progress. Each phase completion is gated on external evidence (tests, builds, benchmarks), not LLM self-evaluation.

### Proposal 5: Add Inter-Phase Dependency and Carry-Forward Fields

- **Research basis:** VulnBot (2501.13411) -- 42.36% of failures caused by context loss between phases. Phase specialization with inter-phase summarization is the fix. Also: ALAS (2505.12501) -- compartmentalized context prevents degradation.
- **Failure mode addressed:** Phase N makes decisions that constrain phase M, but this is not documented. When the builder reaches phase M (potentially after a context reset), the constraint is lost.
- **Proposed change:** Add two fields to the phase template:

```markdown
### Phase N: [Name]
**Model:** [recommended model]
**Depends on:** [Phase X: specific output needed]
**Carry forward:** [Decisions/artifacts from this phase that later phases MUST know about]

- [ ] [Specific task]

**Files:**
...
```

Add to Phase 3 instructions: "For each section, explicitly list: (1) what it needs from earlier phases, (2) what decisions it makes that later phases must respect. These fields are critical for context recovery after `/clear`."

- **Expected impact:** Addresses the #1 failure mode (42% of failures). When building resumes after context loss, the carry-forward fields provide the minimum information needed to maintain plan coherence.

### Proposal 6: Add Uncertainty-Weighted Planning Depth

- **Research basis:** Plan and Budget (2505.16122) -- front-loading compute on high-uncertainty sub-problems improved efficiency by 193.8%. Early reasoning steps have the highest epistemic uncertainty. Also: ALAS (2505.12501) -- commonsense agent adds realistic slack to specifications.
- **Failure mode addressed:** All phases receive equal planning depth, causing under-specification of risky phases and over-specification of trivial ones.
- **Proposed change:** Add an uncertainty classification step to Phase 3:

```markdown
### Uncertainty Assessment (Before Detailing Sections)

For each planned section, classify uncertainty:

| Section | Uncertainty | Why | Planning Depth |
|---------|-----------|-----|---------------|
| [Section 1] | Low | [Pattern exists in codebase] | Brief (1-2 details) |
| [Section 2] | High | [No precedent, new API, complex interaction] | Deep (full details + fallback + risks) |
| [Section 3] | Medium | [Similar pattern but new context] | Standard |

**Front-load detail on High-uncertainty sections.** These are where plans fail.
```

- **Expected impact:** Concentrates planning effort where it has the highest marginal value. Prevents the common failure of spending equal time on trivial and risky phases, leaving risky phases under-specified.

### Proposal 7: Add Pre-Mortem Question to Phase 2

- **Research basis:** Multiple papers document that LLM plans fail on predictable failure modes that could have been anticipated. ALAS (2505.12501) identifies four fundamental deficits. VerilogCoder (AAAI 2025) shows that domain-specific details lost during planning cause implementation failures.
- **Failure mode addressed:** Plans that look complete but have predictable failure modes that nobody asked about. The "unknown unknowns" that APOSD identifies as the worst complexity symptom.
- **Proposed change:** Add a mandatory pre-mortem question after approach selection in Phase 2:

```markdown
### Pre-Mortem (MANDATORY after approach selection)

Before proceeding to DETAIL, ask via `AskUserQuestion`:

"Imagine this approach has failed 6 months from now. What is the most likely reason?"

Record the answer. Then address it:
- If the failure mode is already covered by the plan, note where
- If NOT covered, add a section or constraint to address it
- If it reveals a fundamental assumption, validate that assumption BEFORE detailing

This is NOT optional. Plans that skip pre-mortem have the highest rework rates.
```

- **Expected impact:** Surfaces the dominant failure modes before they are baked into the plan. Pre-mortem analysis is one of the most effective techniques in failure prevention (Klein, 2007) and directly addresses APOSD's "unknown unknowns."

### Proposal 8: Add Disruption Recovery Guidance to Plan File

- **Research basis:** ALAS (2505.12501) LRCP -- disruption recovery should follow a hierarchy: local retry, reorder, bounded replan. Global replan should be last resort. StructuredAgent (2603.05294) -- error back-propagation through alternatives.
- **Failure mode addressed:** When a phase fails during building, the builder has no guidance. Common failure: entire plan is scrapped and re-done when a local fix would suffice.
- **Proposed change:** Add a `## If Things Go Wrong` section to the plan file schema:

```markdown
## If Things Go Wrong

Recovery hierarchy for each phase:

| Phase | Local Fix | Reorder Option | Replan Trigger |
|-------|----------|---------------|---------------|
| Phase 1 | [retry with X] | [can swap with Phase 2 if Y] | [replan if Z] |
| Phase 2 | [fallback to Y] | [N/A - depends on Phase 1] | [replan if entire approach invalid] |
| ... | ... | ... | ... |

**Rules:**
1. Try local fix first (retry, alternative implementation within same phase)
2. Try reordering (swap independent phases) second
3. Replan only if the chosen approach is fundamentally invalid
4. NEVER scrap the entire plan without first trying steps 1-2
```

- **Expected impact:** Prevents the most expensive failure mode: scrapping a mostly-good plan because one phase hit a snag. Provides structured recovery that preserves completed work.

## Priority Ranking

Ranked by impact on failure prevention, considering both frequency and severity of the failure mode addressed:

| Rank | Proposal | Failure Frequency | Failure Severity | Effort |
|------|----------|------------------|-----------------|--------|
| 1 | **P4: Externally Grounded Success Criteria** | Very High (every phase) | High (errors propagate) | Low |
| 2 | **P2: Cross-Cutting Constraints** | High (any multi-phase plan) | High (constraint violations) | Low |
| 3 | **P5: Inter-Phase Dependencies** | Very High (42% of failures) | High (context loss) | Low |
| 4 | **P1: Plan Verification Gate** | High (structural flaws) | Very High (entire plan invalid) | Medium |
| 5 | **P7: Pre-Mortem Question** | Medium (unknown unknowns) | Very High (fundamental flaws) | Low |
| 6 | **P6: Uncertainty-Weighted Planning** | Medium (under-specified phases) | Medium (rework) | Low |
| 7 | **P3: Fallback Strategies** | Medium (blocked phases) | High (plan stalls) | Medium |
| 8 | **P8: Disruption Recovery Guidance** | Medium (phase failures) | Medium (unnecessary replanning) | Medium |

Proposals 1-3 (P4, P2, P5) are highest priority because they address the most frequent failure modes with the lowest implementation effort -- they are additions to the plan file template, not changes to the workflow. Proposal P7 (Pre-Mortem) is exceptionally high-value for its cost: a single question that surfaces fundamental assumptions.
