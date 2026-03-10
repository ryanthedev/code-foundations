# Synthesis B: Bottom-Up Distillation of 70 Proposals from 88 Papers

**Approach:** Start from quantified research findings. Work backwards to the minimum set of changes.

---

## Part 1: Evidence Map

Every concrete, quantified finding across all 10 analyses. Numbers or it didn't happen.

### Context & Constraint Management
| Finding | Source | Paper |
|---------|--------|-------|
| 42.36% of all failures in multi-step agent tasks caused by context/session loss | 01-cognitive-scientist | VulnBot 2501.13411 |
| 44.4% of plan failures due to outdated assumptions | 02-project-manager | CLEA 2503.00729 |
| Budget constraint satisfaction drops from 98% (Day 1) to 42% (Day 5) for sequential planners; stays >90% with hierarchical constraint separation | 09-game-designer | HiMAP-Travel 2603.04750 |
| 93% variance reduction + 67% fewer budget violations with structural separation of global vs local constraints | 09-game-designer | HiMAP-Travel 2603.04750 |
| 32% improvement on long-horizon tasks from structured context management alone (no model change) | 07-ux-designer | ReCAP 2510.23822 |
| Separating strategic oversight from execution improves accuracy by up to 20% | 07-ux-designer | COMPASS 2510.08790 |

### Plan Verification & Quality
| Finding | Source | Paper |
|---------|--------|-------|
| Plan quality is the single strongest predictor of both user trust and task performance | 01-cognitive-scientist | Plan-Then-Execute 2502.01390 |
| Removing plan review step dropped accuracy from 0.61 to 0.45 (16pp drop) | 01-cognitive-scientist | CogWriter 2502.12568 |
| LLMs failed 7/10 reactive planning trials without external validator; succeeded 10/10 with one | 10-failure-analyst | ALAS 2505.12501 |
| Self-assessed progress is unreliable 67% of the time | 10-failure-analyst | Step-Wise PDDL 2603.06064 |
| Closed-loop planning with critic improves success rate by 67.3% over open-loop | 02-project-manager | CLEA 2503.00729 |
| Constraint pre-allocation improved satisfaction by +0.16 average accuracy over baseline | 01-cognitive-scientist | CogWriter 2502.12568 |

### Hierarchical Decomposition & Dependency
| Finding | Source | Paper |
|---------|--------|-------|
| Hierarchical subgoal decomposition: 40% success rate vs 6% for flat methods (34pp improvement) | 05-agile-coach | STEP 2506.21030 |
| Flat trajectories: hierarchical decomposition nearly doubles success rates (31% to 61%) | 08-compiler-designer | ReAcTree 2511.02424 |
| Optimal phase/iteration count is 7; performance drops sharply beyond this | 02-project-manager | MultiAgentBench 2503.01935 |
| Plan step count should stay under 7 for manageable error propagation | 02-project-manager | Plan-and-Act 2503.09572 |
| AND/OR tree decomposition recovered from 50%+ of failures via OR fallback nodes | 10-failure-analyst | StructuredAgent 2603.05294 |

### Effort Allocation & Adaptive Ceremony
| Finding | Source | Paper |
|---------|--------|-------|
| Difficulty-weighted effort allocation improves efficiency by up to 193.8% | 04-systems-architect | Plan-and-Budget 2505.16122 |
| Same pipeline for all queries wastes 55-94% of compute budget | 01-cognitive-scientist | MaAS 2502.04180 |
| User involvement helps for high-risk tasks but hurts for low-risk tasks (involvement fatigue) | 01-cognitive-scientist | Plan-Then-Execute 2502.01390 |
| Adaptive compute: 50-90% token reduction on easy tasks while preserving quality on hard tasks | 04-systems-architect | Thinkless 2505.13379 |
| MAS advantages diminish as LLMs improve (10.7% benefit with ChatGPT drops to 3.0% with Gemini-2.0-Flash) | 04-systems-architect | Single-vs-Multi 2505.18286 |
| Hybrid cascade reduces cost by up to 88.1% while improving accuracy 1.1-12% | 04-systems-architect | Single-vs-Multi 2505.18286 |

### Plan-Execution Gap
| Finding | Source | Paper |
|---------|--------|-------|
| Removing early termination ability tripled scores (2.6% to 8.5% for o3-mini; 13.2% to 24.4% for o1) | 03-ai-researcher | PaperBench 2504.01848 |
| Observation-expectation monitoring catches 20-30% of steps that would otherwise fail silently | 01-cognitive-scientist | DoT 2502.04392 |
| Per-file analysis stage reduced post-generation fixes to 0.81% of code lines | 03-ai-researcher | PaperCoder 2504.17192 |
| Vague plan steps are the primary failure mode in plan execution | 02-project-manager | Plan-and-Act 2503.09572 |
| Goal relaxation when plan is infeasible: +52.45% success rate over baselines | 05-agile-coach | ContextMatters 2506.15828 |
| Milestone-level guidance: 4-23% absolute success rate improvement | 06-military-strategist | HiPlan 2508.19076 |
| Code-form plans improve instruction following by +5.7% and decision-making by +10.1% | 02-project-manager | Code-to-Think 2502.19411 |
| 15-30% hallucination rates in LLM-generated plans (referencing non-existent code) | 01-cognitive-scientist | PlanGenLLMs 2502.11221 |

### Collaboration & Questioning
| Finding | Source | Paper |
|---------|--------|-------|
| Users ask fewer but richer questions when given suggested question types (11.4 vs 22.8) | 08-compiler-designer | Plan-Space 2603.02070 |
| 10-20% of total task time should go to meaningful review at checkpoints | 09-game-designer | Human-AI Teaming 2603.04746 |
| Group discussion in planning is counterproductive; scores worst across all metrics | 02-project-manager | MultiAgentBench 2503.01935 |

---

## Part 2: Minimum Viable Upgrades

Seven changes. Each one must point to quantified evidence. Pareto applied ruthlessly.

### Change 1: Add "Done When" Success Criteria to Each Phase

**What:** Add a `**Done when:**` field to each plan phase requiring externally verifiable criteria.

**Evidence:**
- Self-assessed progress is unreliable 67% of the time (PDDL 2603.06064)
- Observation-expectation monitoring catches 20-30% of silent failures (DoT 2502.04392)
- Vague plan steps are the primary failure mode in execution (Plan-and-Act 2503.09572)
- LLMs without external validators fail 7/10 trials (ALAS 2505.12501)
- Removing early termination tripled scores -- agents claim "done" prematurely (PaperBench 2504.01848)

**Why this beats alternatives:** Six different analyses proposed some version of "expected outcomes," "success criteria," "postconditions," or "milestone verification." They are all the same thing. One field. Maximum convergence across proposals.

---

### Change 2: Add Difficulty + Uncertainty Rating Per Phase

**What:** Add `**Difficulty:** LOW/MEDIUM/HIGH` and `**Uncertainty:** [what we don't know]` to each phase. Front-load HIGH-difficulty phases. Use difficulty (not just file/task count) for model selection.

**Evidence:**
- Difficulty-weighted effort allocation improves efficiency by up to 193.8% (Plan-and-Budget 2505.16122)
- Same pipeline for all queries wastes 55-94% of compute (MaAS 2502.04180)
- 50-90% token reduction on easy tasks with adaptive compute (Thinkless 2505.13379)
- User involvement hurts for low-risk tasks (Plan-Then-Execute 2502.01390)

**Why this beats alternatives:** Multiple proposals suggested "risk registers," "effort estimation," "adaptive ceremony," and "complexity budgets." The common denominator is: tag each phase with how hard it is. Everything else follows from that signal. One field enables all the downstream adaptations without prescribing them.

---

### Change 3: Add Plan Self-Check Gate Before User Validation

**What:** Before presenting the plan to the user, run a structured checklist: constraint coverage, dependency ordering, file existence, no vague steps, phase count within limits.

**Evidence:**
- Plan quality is the single strongest predictor of trust and performance (Plan-Then-Execute 2502.01390)
- Removing plan review dropped accuracy from 0.61 to 0.45 (CogWriter 2502.12568)
- LLMs cannot reliably self-validate but structured checklists partially compensate (SagaLLM 2503.11951)
- Closed-loop planning with critic improves success by 67.3% (CLEA 2503.00729)
- 15-30% hallucination rates in LLM plans -- referencing non-existent code (PlanGenLLMs 2502.11221)

**Why this beats alternatives:** Four analyses proposed variants of "plan review," "plan verification gate," "strategic coherence check," and "plan integrity check." They overlap almost entirely. One checklist. Run it once. The user's review then catches intent alignment, not structural errors.

---

### Change 4: Add Phase Dependencies ("Depends on" / "Unlocks")

**What:** Each phase gets `**Depends on:** [phase IDs]` and `**Unlocks:** [phase IDs]`. After all phases are defined, draw a simple dependency summary.

**Evidence:**
- Hierarchical decomposition: 40% vs 6% success rate (STEP 2506.21030)
- Flat to hierarchical nearly doubles success (31% to 61%) (ReAcTree 2511.02424)
- 42.36% of failures from context loss -- dependency tracking prevents downstream breakage (VulnBot 2501.13411)
- 2.5x latency reduction through parallelization enabled by dependency graphs (HiMAP-Travel 2603.04750)

**Why this beats alternatives:** All 10 analyses proposed some form of dependency graph. The disagreement was only on format (table vs ASCII art vs DAG notation). The minimum viable version: two fields per phase plus a summary. No new section, no complex notation. The building command can already use phase ordering; explicit dependencies just make it correct.

---

### Change 5: Cap Plan Phases at 7

**What:** Add a hard maximum: Simple plans 2-3 phases, Medium 3-5, Complex 5-7. If >7, combine phases or split into multiple plans.

**Evidence:**
- Optimal iteration count is 7; performance drops sharply beyond (MultiAgentBench 2503.01935)
- Plan step count under 7 for manageable error propagation (Plan-and-Act 2503.09572)
- Over-decomposition is a documented failure mode (ReCode 2510.23564)

**Why this beats alternatives:** Three different analyses converged on the number 7 independently. This is a one-line constraint with zero implementation cost that prevents a documented failure mode. No reason not to include it.

---

### Change 6: Add Constraint-to-Phase Mapping

**What:** After defining phases, map every constraint from Phase 1 to the specific phase(s) that must satisfy it. Any unmapped constraint = plan gap.

**Evidence:**
- Constraint pre-allocation improved satisfaction by +0.16 accuracy (CogWriter 2502.12568)
- Constraint satisfaction drops from 98% to 42% over 5 phases without structural tracking (HiMAP-Travel 2603.04750)
- 44.4% of plan failures from outdated/untracked assumptions (CLEA 2503.00729)
- 93% variance reduction with global/local constraint separation (HiMAP-Travel 2603.04750)

**Why this beats alternatives:** Several analyses proposed "constraint classification," "assumption registers," "cross-cutting constraint sections," and "constraint pre-allocation." The underlying insight is identical: constraints stated once and never referenced again get violated. The minimum fix: a mapping table. Not a new section -- a step in Phase 3 that produces a table connecting constraints to phases.

---

### Change 7: Add "If This Fails" Fallback Per Phase (Medium/High Difficulty Only)

**What:** For phases rated MEDIUM or HIGH difficulty (from Change 2), add `**If this fails:** [fallback strategy]`.

**Evidence:**
- AND/OR fallback nodes recovered from 50%+ of failures (StructuredAgent 2603.05294)
- Goal relaxation for infeasible plans: +52.45% success over baselines (ContextMatters 2506.15828)
- LRCP local-first recovery hierarchy prevents cascading failures (ALAS 2505.12501)
- Plans without fallbacks: one blocked step stalls the entire plan (StructuredAgent 2603.05294)

**Why this beats alternatives:** Multiple analyses proposed "replanning triggers," "branch plans," "disruption recovery protocols," "assumption registers with fallbacks." The kernel: when something breaks, what do you do? One field. Applied only to non-trivial phases (gated by difficulty rating from Change 2). Avoids the overhead of full replanning trigger tables for simple work.

---

## Part 3: Implementation Spec

### Change 1: "Done When" Success Criteria

**Placement:** Phase 3 (DETAIL) -- modify the Section Template (currently at line ~265). Also modify the Plan File Schema (Phase 5, ~line 404).

**In Phase 3 Section Template, add after `**Dependencies:**`:**

```markdown
**Done when:**
- [ ] [externally verifiable criterion, e.g., "tests pass", "API returns 200", "component renders"]
- [ ] [second criterion if needed]

> Every phase must have at least one criterion that can be checked by running a command or reading output. "Looks correct" is not a criterion.
```

**In Phase 5 Plan File Schema, add to each phase block after `**Details:**`:**

```markdown
**Done when:**
- [ ] [verifiable criterion]
```

---

### Change 2: Difficulty + Uncertainty Rating

**Placement:** Phase 3 (DETAIL) -- add to Section Template, after `**Goal:**` (currently ~line 267).

**In Phase 3 Section Template, add after `**Goal:**`:**

```markdown
**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [what we don't know that could change this phase — or "None: well-understood pattern"]
```

**Also add to Phase 3, after the YAGNI Gate (~line 288), a new instruction:**

```markdown
### Difficulty Review (After All Sections Defined)

Review difficulty ratings across all sections:
- If the hardest phase is NOT in the first half of the plan, consider reordering to front-load uncertainty
- If all phases are LOW, verify complexity classification is correct — this may be simpler than assessed
- If all phases are HIGH, the plan may be under-decomposed — consider splitting phases

**Model selection override:**
- HIGH difficulty or significant uncertainty → opus (regardless of task/file count)
- LOW difficulty AND tasks <= 2 AND files <= 2 → haiku
- Otherwise → sonnet
```

**In Phase 5 Plan File Schema, add to each phase block after `**Model:**`:**

```markdown
**Difficulty:** [LOW / MEDIUM / HIGH]
```

---

### Change 3: Plan Self-Check Gate

**Placement:** Phase 4 (VALIDATE) -- insert as new Step 4a, before the "Full Plan Review" section (~line 325).

```markdown
### Step 4a: Plan Self-Check (MANDATORY before presenting to user)

Before asking the user to review, verify the plan yourself:

- [ ] Every constraint from Phase 1 is mapped to at least one phase (Change 6 table complete)
- [ ] Every phase has at least one "Done when" criterion that is externally verifiable
- [ ] No phase references files, functions, or libraries that don't exist without marking them as CREATE/NEW/INSTALL
- [ ] Dependencies between phases have no circular references
- [ ] Phase count is within limits (max 7)
- [ ] No phase has vague implementation details (test: could a different agent execute this without asking questions?)
- [ ] HIGH-difficulty phases have a fallback strategy

**If any check fails:** Fix before presenting to user. Do NOT rely on the user to catch structural problems.
```

---

### Change 4: Phase Dependencies

**Placement:** Phase 3 (DETAIL) -- modify the Section Template (~line 265), adding fields. Also add a summary step after all sections are defined.

**In Phase 3 Section Template, replace the existing `**Dependencies:**` line with:**

```markdown
**Depends on:** [Phase IDs, or "none — start here"]
**Unlocks:** [Phase IDs, or "none — final phase"]
```

**After the YAGNI Gate (~line 288), add:**

```markdown
### Dependency Summary (After All Sections Defined)

List the critical path (longest sequential chain) and any phases that can execute in parallel:

**Critical path:** Phase X → Phase Y → Phase Z
**Parallel groups:** [Phase A, Phase B] can execute simultaneously
```

**In Phase 5 Plan File Schema, replace `**Dependencies:**` in the phase template with:**

```markdown
**Depends on:** [phase IDs]
**Unlocks:** [phase IDs]
```

---

### Change 5: Phase Count Cap

**Placement:** Phase 3 (DETAIL) -- add before the Section Template (~line 256).

```markdown
### Phase Count Limits

| Complexity | Target | Hard Maximum |
|-----------|--------|-------------|
| Simple | 2-3 | 4 |
| Medium | 3-5 | 6 |
| Complex | 5-7 | 7 |

If your plan exceeds 7 phases, you are over-decomposing. Combine related phases or split into separate plans.
If your plan has 1 phase, this is a task, not a plan — execute directly.
```

---

### Change 6: Constraint-to-Phase Mapping

**Placement:** Phase 3 (DETAIL) -- add as Step 3a, before the Section Template (~line 256).

```markdown
### Step 3a: Constraint Mapping (Before Writing Sections)

Map every constraint and success criterion from Phase 1 to the phase(s) that must satisfy it:

| Constraint / Success Criterion | Owning Phase(s) | How Verified |
|-------------------------------|-----------------|-------------|
| [constraint 1] | Phase N | [verification method] |
| [constraint 2] | Phase M, Phase P | [verification method] |

**Rules:**
- Every constraint MUST appear in at least one phase. Unmapped constraint = plan gap.
- If a constraint spans all phases (e.g., "no breaking changes"), mark it as GLOBAL and check it after every phase.
- If a constraint cannot be mapped, it is either too vague (refine it) or infeasible (flag it to user).
```

---

### Change 7: Fallback for Medium/High Difficulty Phases

**Placement:** Phase 3 (DETAIL) -- add to Section Template, after the new `**Done when:**` field. Conditional on difficulty rating.

```markdown
**If this fails:** _(required for MEDIUM/HIGH difficulty)_
- [Fallback approach, scope reduction, or escalation path]
- [Signal that triggers the fallback: specific error, test failure, or blocker]
```

---

## Part 4: What I Cut and Why

### Cut: Dependency DAG as a separate visual section (proposed by 8 of 10 analyses)
**Why:** The "Depends on / Unlocks" fields per phase (Change 4) capture the same information inline, which is where the building agent actually reads it. A separate ASCII-art DAG section is redundant with the per-phase fields. The dependency summary (critical path + parallel groups) is a two-line addition, not a full section. Separate DAG sections add maintenance burden without adding information.

### Cut: Assumption Register / Tracking Table (proposed by 4 analyses)
**Why:** Subsumed by the Constraint-to-Phase Mapping (Change 6). Assumptions that matter are constraints. Assumptions that don't constrain anything don't belong in the plan. Adding both an "Assumptions" table and a "Constraints" mapping creates overlap. The mapping table already forces you to identify what each constraint depends on being true.

### Cut: Inter-phase Context Summaries / "Carry Forward" / "Produces/Consumes" fields (proposed by 5 analyses)
**Why:** The "Depends on / Unlocks" fields (Change 4) plus "Done when" criteria (Change 1) together establish what flows between phases. If Phase 2 depends on Phase 1 and Phase 1's "Done when" says "User model exported from types.ts," then Phase 2 knows what it gets. Separate "Produces" and "Context Forward" fields restate what the dependency + done-when already specify. Three proposals for context management can be collapsed into two fields that already exist.

### Cut: Replanning Triggers section (proposed by 4 analyses)
**Why:** Subsumed by the per-phase fallback (Change 7). A phase-level "if this fails" is actionable. A separate replanning trigger table at the end of the plan is a document that nobody reads during a crisis. The fallback field is right next to the phase that might fail -- where the builder actually needs it.

### Cut: Commander's Intent / Goal Anchoring Checkpoints (proposed by 2 analyses)
**Why:** The Plan Self-Check (Change 3) already requires verifying that every phase maps to a success criterion from Phase 1 and that every constraint is covered. This IS goal anchoring -- it just doesn't have a military name. Adding a "Commander's Intent" section is adding a new concept to learn for the same effect as checking constraints against the problem statement.

### Cut: Per-File Implementation Specs / Analysis Stage (proposed by 2 analyses)
**Why:** The evidence (PaperCoder's 0.81% fix rate) is strong, but this proposal nearly doubles the size of the planning phase. The whiteboarding skill already struggles with plans that are too long (LLM length bias, PlanGenLLMs 2502.11221). Per-file specs are better suited to the building command's PRE-GATE phase, where the agent is about to write code and has full context of the target file. Adding them to the plan creates stale specs that drift before execution.

### Cut: Code-Form Plan Structure (proposed by 1 analysis)
**Why:** Evidence is real (+5.7% instruction following, +10.1% decision-making) but applies to execution, not planning. The whiteboarding plan is consumed by the building skill which already structures execution. Adding pseudocode to the plan adds a format that may confuse rather than help. Marginal benefit doesn't justify the cognitive overhead of a second representation format.

### Cut: Vertical Slice Validation (proposed by 1 analysis)
**Why:** Good practice but not quantified with independent evidence. The constraint mapping (Change 6) and plan self-check (Change 3) together catch the same issues: phases that don't map to success criteria get flagged, phases with no verifiable output get flagged. Vertical slicing is an architectural style preference, not a plan quality gate.

### Cut: Adaptive Decomposition Depth / Plan Depth Tables (proposed by 3 analyses)
**Why:** The phase count cap (Change 5) and difficulty rating (Change 2) together handle this. Simple plans get 2-3 phases, complex plans get 5-7 phases. HIGH-difficulty phases get deeper detail. Adding another table specifying "Level 1: Goal, Level 2: Subgoals, Level 3: Tasks" per complexity level creates process overhead that the phase count cap already constrains. The agent doesn't need to be told how many levels to decompose to -- it needs to be told when to stop (max 7 phases, tasks must be single-action verifiable via "Done when").

### Cut: Procedural Knowledge Capture / Decision Log (proposed by 2 analyses)
**Why:** The plan already captures "Chosen Approach" with rationale. A structured Decision Log with reversal costs and alternatives considered adds ~200 words per decision point. The knowledge value is real (Lingxi showed 6.3pp improvement) but the ROI is low for this skill: whiteboarding plans are consumed once by the building command, not referenced repeatedly. If reuse becomes a pattern, this should be reconsidered.

### Cut: Structured Question Types for Plan Space Exploration (proposed by 1 analysis)
**Why:** The evidence (fewer but richer questions: 11.4 vs 22.8) is real but the current one-question-at-a-time approach with multiple choice already achieves a similar effect. Adding a taxonomy of question types (why-not, what-if, can, trade-off) adds cognitive load to the questioning phase. The existing approach works. Don't fix what isn't broken.

### Cut: Execution Trace Step (proposed by 1 analysis)
**Why:** Interesting idea (CWM showed trace-augmented reasoning grounds decisions in behavior) but adds significant planning time for uncertain benefit in this context. Traces are most valuable at implementation time, not planning time. The building command's POST-GATE is the right place for runtime reasoning.

### Cut: Pre-Mortem Question (proposed by 1 analysis)
**Why:** Compelling from a failure prevention standpoint, but it's a user-interaction change, not a plan structure change. The current questioning flow already asks "What could go wrong?" for medium+ complexity (question 5). Moving it to a mandatory post-approach question changes the conversation flow for marginal gain. The plan self-check (Change 3) catches structural failures; the pre-mortem catches user-level fears. The latter is already partially covered.

### Cut: Static/Dynamic Section Markers in Plan Schema (proposed by 1 analysis)
**Why:** HTML comments in markdown (`<!-- STATIC CONTEXT -->`) are invisible to humans and add noise. The building command already knows which sections to read vs update. This is a consumption-side optimization that belongs in the building skill's instructions, not in the plan format.

### Cut: Constraint Classification (Global vs Local) (proposed by 2 analyses)
**Why:** The constraint-to-phase mapping (Change 6) already handles this. A constraint mapped to "all phases" IS a global constraint. A constraint mapped to "Phase 2" IS a local constraint. Explicit classification labels add a concept without adding information beyond what the mapping table already shows.

### Cut: Risk Register as Separate Section (proposed by 4 analyses)
**Why:** The difficulty + uncertainty rating (Change 2) and fallback field (Change 7) together capture risk information where it's actionable -- at the phase level. A separate risk register table at the plan level duplicates information and creates a section that must be kept in sync with per-phase ratings. Per-phase risk fields beat a centralized risk table because the building agent reads phases sequentially, not risk registers.
