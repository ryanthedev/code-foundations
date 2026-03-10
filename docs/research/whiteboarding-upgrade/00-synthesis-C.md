# Synthesis C: Adversarial Design Review of 70 Whiteboarding Upgrade Proposals

**Reviewer posture:** Skeptical senior engineer. The current whiteboarding skill is a working system that ships plans. The burden of proof is on every proposal to demonstrate it earns its keep. Most won't.

**Source material:** 10 expert analyses (cognitive scientist, project manager, AI researcher, systems architect, agile coach, military strategist, UX designer, compiler designer, game designer, failure analyst), citing 88 research papers, producing 70 proposals total.

---

## Part 1: Proposals That Survived Scrutiny

I accepted 7 changes. Each one had to clear three bars: (1) strong research evidence that isn't a stretch, (2) clear practical benefit for an LLM planning software features, and (3) ceremony cost proportional to the benefit.

---

### 1. Per-Phase Verifiable Success Criteria ("Done When")

**Who proposed it:** AI researcher (Proposal 2), systems architect (Proposal 5), military strategist (Proposal 6), failure analyst (Proposal 4), compiler designer (Proposal 3). 5/10 personas converged independently.

**Why they converged:** This is genuinely important, not just obvious-sounding. PaperBench (2504.01848) found that agents claim completion prematurely -- forced continuation tripled scores. The failure analyst's citation of 2603.06064 (self-assessed progress is unreliable 67% of the time) is damning. The current plan schema has no way for the building command to objectively verify that a phase succeeded. "Did you modify the files?" is not verification.

**Strongest counterargument I considered:** The current building workflow already has POST-GATE checks via skill checklists. Adding per-phase success criteria to the plan duplicates this. COUNTER-COUNTER: The POST-GATE checks are generic (does the code have good error handling?). They don't check plan-specific outcomes (does the API actually return the right shape?). These are complementary, not redundant.

**Why I accepted:** The cost is one field per phase. The benefit is that building can fail-fast on phases that didn't actually work. This is the single highest-leverage change because it addresses the root cause of plan-execution gap.

**SKILL.md implementation -- add to Phase 3 Section Template (after Dependencies):**

```markdown
**Done when:**
- [ ] [Specific, verifiable criterion -- e.g., "tests in `user.test.ts` pass"]
- [ ] [Specific, verifiable criterion -- e.g., "`POST /api/users` returns 201"]

Every task must have at least one verifiable criterion.
If you cannot state a testable pass/fail condition, the task is underspecified -- break it down further.
```

**SKILL.md implementation -- add to Plan File Schema, within each phase:**

```markdown
**Done when:**
- [ ] [Binary criterion 1]
- [ ] [Binary criterion 2]
```

---

### 2. Dependency Graph Between Plan Phases

**Who proposed it:** Cognitive scientist (Proposal 5), project manager (Proposal 1), AI researcher (Proposal 1), systems architect (Proposal 1), UX designer (Proposal 3), compiler designer (Proposal 1), game designer (Proposal 3), failure analyst (Proposal 5). 8/10 personas.

**Why they converged:** This is the single most proposed change across all analyses. The convergence is genuine because the gap is obvious: the current plan schema uses implicit linear ordering (Phase 1, Phase 2, Phase 3) but never states which phases actually depend on which. This means parallel-executable phases are serialized unnecessarily, and when a phase fails, there's no way to know which downstream phases are affected.

**Strongest counterargument I considered:** Most plans the whiteboarding skill produces are small (3-5 phases) and genuinely sequential. A dependency graph adds template complexity for minimal benefit on typical use cases. COUNTER-COUNTER: Even for sequential plans, writing "Depends on: Phase 1" takes 5 seconds and makes the ordering explicit rather than implicit. For the minority of plans that DO have parallelizable work, this is high-value. The cost-benefit ratio is favorable because the cost is near-zero.

**Why I accepted:** Near-zero ceremony cost. The building command can immediately use this information. Multiple independent research threads (PaperCoder, VulnBot, HTAM) confirm that dependency-aware ordering prevents cross-file integration errors. The simplest version (just "Depends on" and "Unlocks" per phase) is enough.

**SKILL.md implementation -- add to Phase 3 Section Template:**

```markdown
**Depends on:** [Phase numbers, or "none"]
**Unlocks:** [Phase numbers that can start after this completes]
```

**SKILL.md implementation -- add to Phase 3 instructions, after all sections are drafted:**

```markdown
### Dependency Check (After All Sections Drafted)

Review all sections and verify:
1. Every phase lists its dependencies (even if "none")
2. No circular dependencies exist
3. Phases with no mutual dependency are noted as parallelizable

Write dependency summary into plan file.
```

**SKILL.md implementation -- add to Plan File Schema, after Implementation Checklist:**

```markdown
## Phase Dependencies

Phase 1 → Phase 2 → Phase 4
Phase 1 → Phase 3 → Phase 4

**Parallelizable:** Phase 2 and Phase 3 (no mutual dependency)
**Critical path:** Phase 1 → Phase 2 → Phase 4
```

---

### 3. Difficulty/Uncertainty Rating Per Phase

**Who proposed it:** Systems architect (Proposal 2), failure analyst (Proposal 6), cognitive scientist (Proposal 4 -- as part of risk-adaptive ceremony), agile coach (Proposal 6). 4/10 personas.

**Why they converged:** The current model recommendation heuristic (haiku if <=2 tasks, opus if >=6 tasks) is a size proxy, not a difficulty proxy. A 2-file change to a critical authentication system is harder than a 6-file rename. Plan and Budget (2505.16122) shows that difficulty-weighted allocation improved efficiency by 193.8%. Thinkless (2505.13379) shows adaptive compute allocation reduces token usage 50-90% on easy tasks while preserving quality on hard tasks.

**Strongest counterargument I considered:** The LLM producing the plan is bad at estimating difficulty -- it will mark everything "MEDIUM" and this field becomes decoration. COUNTER-COUNTER: Even imperfect difficulty ratings are better than the current size-only heuristic. And the "Uncertainty" sub-field (what we don't know that could change this) is more actionable than difficulty because it points to specific unknowns. If the LLM can articulate what's unknown, that's valuable even if the difficulty label is imprecise.

**Why I accepted:** Replaces an existing weak heuristic (file/task count) with a slightly better one (difficulty + uncertainty), at near-zero additional cost. The uncertainty field also front-loads risk identification, which several other proposals wanted.

**SKILL.md implementation -- modify Section Template in Phase 3, add after Goal:**

```markdown
**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [What we don't know that could change this phase's plan]
```

**SKILL.md implementation -- modify Model Recommendations in Phase 5:**

```markdown
If difficulty == HIGH or significant uncertainty noted:
  → opus (regardless of task/file count)

If difficulty == LOW and tasks <= 2 AND files <= 2:
  → haiku

Otherwise:
  → sonnet
```

---

### 4. Plan Self-Check Before User Validation

**Who proposed it:** Project manager (Proposal 7), UX designer (Proposal 6), cognitive scientist (Proposal 3), failure analyst (Proposal 1). 4/10 personas.

**Why they converged:** The current Phase 4 (VALIDATE) goes straight to "Does this plan look complete?" for the user. Research from Plan-Then-Execute (2502.01390) shows users develop false confidence from plausible-sounding plans. CogWriter (2502.12568) shows removing plan review dropped accuracy from 0.61 to 0.45. The user's job should be checking strategic intent, not catching missing fields.

**Strongest counterargument I considered:** LLMs can't reliably self-validate (the failure analyst's own ALAS citation says so). A self-check is the same biased agent checking its own work. COUNTER-COUNTER: The key insight is that a STRUCTURED checklist partially compensates for self-validation weakness. "Does every phase have a Done-when field?" is a mechanical check, not a judgment call. The LLM can reliably check format compliance even if it can't reliably check semantic correctness.

**Why I accepted:** This is a lightweight forcing function that catches structural problems (missing fields, orphaned constraints) before the user sees the plan. It doesn't pretend to catch semantic errors. The checklist should be SHORT and focus on checkable properties.

**SKILL.md implementation -- add to Phase 4, before "Full Plan Review":**

```markdown
### Plan Self-Check (Before Presenting to User)

Before presenting the plan for user review, verify:

- [ ] Every phase has a "Done when" field with at least one testable criterion
- [ ] Every phase has Dependencies listed (even if "none")
- [ ] Every constraint from Phase 1 maps to at least one phase
- [ ] Every phase maps to at least one success criterion from Phase 1
- [ ] No phase has vague implementation details (test: could a different agent execute this without asking questions?)
- [ ] Phase count is 7 or fewer

If any check fails, fix before presenting to user.
```

---

### 5. Adaptive Ceremony by Complexity

**Who proposed it:** Cognitive scientist (Proposal 4), agile coach (Proposal 6), UX designer (Proposal 1). 3/10 personas directly, but several others implied it.

**Why they converged:** The current skill applies the same 6-phase ceremony to a config file rename and an architecture migration. The complexity classification already exists but only affects question count. Plan-Then-Execute (2502.01390) found that user involvement on low-risk tasks is actively counterproductive (involvement fatigue). MaAS (2502.04180) showed query-dependent processing saves 55-94% overhead.

**Strongest counterargument I considered:** The current skill is already pretty good about this -- simple tasks get 2-3 questions and can produce short plans. Making this more formal adds a table to the skill that the LLM has to parse and follow, and the LLM might get confused about which row to apply. COUNTER-COUNTER: The current skill says "200-300 words per section" regardless of complexity. That's clearly wrong for simple tasks. A lightweight table that adjusts section count and detail level is worth the small parsing cost.

**Why I accepted:** This directly addresses the most common complaint with planning tools: "this is overkill for what I'm doing." The implementation should be a SIMPLE table, not a complex conditional system.

**SKILL.md implementation -- add to Phase 3, before Section Template:**

```markdown
### Plan Depth by Complexity

| Complexity | Sections | Detail Level | Approach Count |
|------------|----------|--------------|----------------|
| Simple     | 1-2      | Files + key changes only | 1-2 (skip if obvious) |
| Medium     | 3-5      | Files + logic + edge cases | 2-3 |
| Complex    | 5-7      | Full detail + traces | 3 + research |

**Hard maximum: 7 sections.** If exceeding 7, either reduce scope or split into multiple plans.

**Simple exit ramp:** If complexity is Simple and the approach is obvious, skip section-by-section user confirmation. Write a flat checklist plan directly.
```

---

### 6. Executability Grounding Check

**Who proposed it:** Cognitive scientist (Proposal 6), game designer (Proposal 6), failure analyst (via plan verification). 3/10 personas directly.

**Why they converged:** PlanGenLLMs (2502.11221) documents 15-30% hallucination rates in LLM-generated plans. The RAG for Robots paper (2603.02688) found the primary bottleneck is not plan quality but plan-to-reality mapping (grounding gap). Plans that reference files, functions, or patterns that don't exist are common and waste building time.

**Strongest counterargument I considered:** The current skill already does codebase search in Phase 1 (Pattern Discovery). Adding another grounding check in Phase 3 or 4 is redundant. COUNTER-COUNTER: Phase 1 searches for existing PATTERNS. Phase 3 then writes plan steps that reference specific FILES and FUNCTIONS. The grounding gap occurs in between -- the plan says "modify UserController" but no such file exists, or the plan says "use library X" but it's not in package.json. These are different checks.

**Why I accepted:** Cheap to add, catches a real and documented failure mode. The implementation should be lightweight -- not a full table for every reference, but a quick scan instruction.

**SKILL.md implementation -- add to Phase 3, after writing each section:**

```markdown
### Grounding Check (Per Section)

After writing each section, verify references exist:
- Search for each referenced file path
- Confirm referenced functions/classes exist or mark as "CREATE NEW"
- Check that referenced libraries are in the dependency file

If a reference doesn't exist, explicitly mark it:
- File: "CREATE: `path/to/new-file.ts`"
- Library: "INSTALL: `library-name`" as a prerequisite task
```

---

### 7. Pre-Mortem Question

**Who proposed it:** Failure analyst (Proposal 7) explicitly. Military strategist and project manager touched on risk identification but not in the pre-mortem format.

**Why this one specifically:** This is the lowest-cost, highest-yield risk identification mechanism proposed. One question: "Imagine this approach has failed 6 months from now. What is the most likely reason?" It leverages the user's domain knowledge rather than asking the LLM to guess at risks (which it does poorly). Gary Klein's pre-mortem technique is well-established in project management literature.

**Strongest counterargument I considered:** This is yet another question in a process that already has 2-8 questions. It slows down planning. And users will give vague answers ("it'll be too slow") that don't help. COUNTER-COUNTER: This replaces the current "What could go wrong?" question (question 5, Medium complexity) with a more effective formulation. It's not an addition; it's an upgrade to an existing question. The pre-mortem framing ("imagine it has failed") is research-proven to surface more specific concerns than "what could go wrong?"

**Why I accepted:** Near-zero cost (replaces an existing question), potentially high yield, and it's the user who answers -- not the LLM guessing at risks.

**SKILL.md implementation -- replace question 5 in the Medium question sequence:**

```markdown
**Medium (add these):**
4. Who/what will use this?
5. Imagine this approach has failed 6 months from now. What is the most likely reason?
```

**SKILL.md implementation -- add to Phase 2, after approach selection:**

```markdown
### Pre-Mortem (After Approach Selection)

If the user's pre-mortem answer identified a failure mode not covered by the plan:
- Add a constraint, section, or mitigation to address it
- If it reveals an untested assumption, verify before proceeding to DETAIL
```

---

## Part 2: Proposals I Killed

### (a) Weak Evidence

**Constraint Pre-Allocation (Cognitive Scientist P1).** CogWriter (2502.12568) is about constrained long-form TEXT generation (write a story with exactly 3 paragraphs about dogs). Mapping constraints to plan sections is a stretch -- software constraints (performance, backward compatibility) aren't "allocated" to sections the way word-count constraints are allocated to paragraphs. The analogy doesn't hold.

**Code-Form Plans / Pseudocode (Project Manager P8).** Code to Think (2502.19411) showed +5.7% improvement on instruction following benchmarks. That's a small effect, and the benchmark is AlpacaEval, not software planning. Writing pseudocode for a plan adds ceremony and is redundant with the implementation details field.

**Hierarchical Memory / Prior Plan Reference (Military Strategist P7, UX Designer P4 via procedural knowledge).** HiPlan's milestone library is built from hundreds of prior demonstrations. A typical project has 2-10 prior plans in docs/plans/. There's not enough data for a meaningful library. The current Phase 1 pattern discovery already searches the codebase. Adding a "check docs/plans/" step is harmless but unlikely to provide value until a project has dozens of plans.

**Progress Contribution Percentages (Systems Architect P5).** Asking the LLM to estimate "Phase 1 contributes 30% of total progress" is fantasy precision. The LLM has no basis for these numbers. They'll be wrong and potentially misleading.

**Effort Distribution Percentages (AI Researcher P4).** Same problem. "Phase 1: 20%, Phase 2: 50%" -- based on what? The LLM is guessing, and wrong effort estimates could cause the building agent to artificially rush or dawdle.

### (b) Academic Not Practical

**AND/OR Tree Phase Decomposition (Game Designer P2, Failure Analyst P3, Compiler Designer P2).** StructuredAgent (2603.05294) uses AND/OR trees for web navigation tasks where the agent has real alternative paths (click this button OR that button). In software planning, phases are almost never true OR alternatives -- you don't build "either the database schema OR the API endpoints." You build both. The rare cases where genuine alternative approaches exist are already handled by the approach comparison in Phase 2. Adding OR-node notation to every phase template is ceremony without payoff.

**Control Flow Type Annotations (Compiler Designer P2).** Labeling phases as "sequence | parallel | fallback | conditional" sounds elegant but the building command doesn't support parallel execution. This is designing for a capability that doesn't exist. When the building command gains parallel support, THEN add this.

**Structured Intermediate Representation / Plan Contracts (Compiler Designer P3).** ViviDoc's DocSpec works for UI generation where the domain has a fixed decomposition (State, Render, Transition, Constraint). Software features don't have a universal decomposition schema. Enforcing preconditions/postconditions/invariants per phase is the same as "Done when" (which I accepted) plus over-engineering.

**Goal-Conflict Detection via MUS/MCS Analysis (Compiler Designer P4).** The paper (2603.02070) is about formal constraint solving in scheduling problems. Asking an LLM to check "can constraint A and constraint B be satisfied simultaneously?" is asking it to do the thing it's bad at. If constraints genuinely conflict, the user knows. If they subtly conflict, the LLM won't catch it either.

**Execution Trace Step (UX Designer P5).** CWM (2510.02387) is about understanding EXISTING code through execution traces, not mentally tracing PLANNED code that doesn't exist yet. Asking the LLM to trace through a happy path and error path of code it hasn't written is speculative reasoning that's likely to produce confident-sounding but wrong predictions. The research doesn't support this application.

**Context Scoping Per Phase (Agile Coach P3).** STEP Planner's (2506.21030) context pruning works because the framework controls what each subgoal node sees. In the whiteboarding skill, there's no framework -- it's an LLM reading a markdown file. Adding "Context" and "Excludes" fields to each phase doesn't actually prevent the LLM from reading the whole plan. The mechanism doesn't match the architecture.

### (c) Adds Too Much Ceremony

**Full Risk Register (Military Strategist P5, Systems Architect P6, Project Manager P2).** A risk register with Likelihood/Impact/Mitigation/Owner Phase for every risk is PM ceremony imported wholesale into an LLM planning context. The pre-mortem question (which I accepted) surfaces the TOP risk cheaply. A full register is over-engineering -- the LLM will produce boilerplate risks ("the API might be slow," "the library might have bugs") that don't help.

**Assumption Register (Military Strategist P3, Project Manager P6, Failure Analyst indirectly).** A table of assumptions with Confidence/Verify-Before-Phase/If-Wrong is structurally appealing but ceremony-heavy. Most "assumptions" are obvious ("the database exists," "Node.js is installed") or unknowable ("the API supports batch operations" -- which you should verify during research, not track in a table). The uncertainty field I accepted in the difficulty rating covers the important case: "what don't we know?"

**Replanning Triggers Table (Project Manager P5, Game Designer P5).** A table of conditions-that-should-cause-replanning is trying to pre-plan the replanning. The building workflow already has quality gates (POST-GATE). If POST-GATE fails, the building command handles it. Adding a separate replanning triggers table to the plan is redundant with the building workflow's existing failure handling.

**Inter-Phase Context Summaries / Carry-Forward Fields (Cognitive Scientist P7, Military Strategist P4, Failure Analyst P5).** Adding "Context Forward: key decisions made / files created / unexpected findings" to each phase is a field that gets filled in DURING building, not during planning. The whiteboarding skill can't fill this in. It's the building command's responsibility. This proposal is aimed at the wrong skill.

**Commander's Intent (Military Strategist P1).** A "priority of constraints" hierarchy and "key judgment the implementer will face" sounds useful but in practice the LLM planner doesn't know what the key implementation judgment will be. It's a prediction about the future that will likely be wrong. The existing Problem Statement + Constraints already capture intent. Adding another "Intent" section is redundant.

**Constraint Classification (Game Designer P1).** Splitting constraints into "Global" and "Per-Phase" with enforcement mechanisms is structurally clean but adds template complexity. The plan self-check I accepted already verifies that every constraint maps to at least one phase. That's sufficient.

**Analysis Stage / Per-File Specs (AI Researcher P3).** PaperCoder's analysis stage works because it generates specs for CODE FILES that will be mechanically generated. Whiteboarding plans are consumed by an intelligent agent (the building command), not a code generator. The agent can infer per-file details from the section-level plan. Adding per-file specs (Purpose, Exports, Imports, Key logic, Constraints, Estimated size) for every file is massive ceremony for medium/complex plans.

**Hierarchical Section Decomposition with Dual Validation (Agile Coach P1).** STEP Planner's 3-4 level decomposition works in embodied AI where the action space is huge (thousands of possible physical actions). Software planning's action space is much smaller (modify files, create files, run commands). Two levels (Phase -> Tasks) is sufficient for 90% of plans. The 7-section hard cap I accepted prevents over-decomposition at the phase level, and the "Done when" criteria prevent under-specification at the task level.

**Feasibility Gate with Goal Relaxation (Agile Coach P2).** ContextMatters (2506.15828) is about household robot task planning where "fork unavailable, try spoon" is a meaningful relaxation. In software, goal relaxation is a human decision ("we can't do real-time, should we do polling?") that already happens naturally during the questioning phase. Formalizing it with a Functionality/Feasibility axis and a structured relaxation protocol is over-engineering an interaction that already works.

### (d) Already Handled by Existing Skill Features

**Explicit Reasoning Field Per Section (Project Manager P4).** The current Section Template has "Goal: [what this section accomplishes]." Adding "Reasoning: [WHY this section is needed]" is redundant with the YAGNI Gate, which already asks "Is this section actually needed?" If a section passes YAGNI, its reason for existing is implicit in its goal. Anti-rationalization table entry "The reason is obvious" is cute but not worth the field.

**Phase Count Constraint (Project Manager P3).** The adaptive ceremony table I accepted already caps sections at 7 for complex plans and 1-2 for simple plans. A separate "Phase Count Constraint" section is redundant.

**Vertical Slice Validation (Agile Coach P4).** The plan self-check I accepted includes "Every phase maps to at least one success criterion." That IS vertical slice validation -- every phase delivers toward a stated outcome. A separate vertical-slice table with "User-Observable Output" and "Can Be Tested Independently?" adds form without substance.

**Goal Anchor Checkpoints (UX Designer P2).** The plan self-check I accepted includes "Every constraint from Phase 1 maps to at least one phase" and "Every phase maps to at least one success criterion." This IS goal anchoring -- it verifies alignment with the original problem statement. A separate "Goal Anchor Check: re-read the Problem Statement" instruction is trust-the-process theater rather than a structural forcing function.

**Static/Dynamic Section Markers (UX Designer P7).** HTML comments in a markdown plan file (<!-- STATIC CONTEXT -->) are invisible to the LLM reading the plan. They don't change behavior. The building command already knows which parts of the plan to read vs. update.

### (e) Contradicts Skill Philosophy

**Fallback Approach Preservation (Compiler Designer P5).** The current skill deliberately picks ONE approach and commits. Preserving rejected approaches as structured fallbacks in the plan file contradicts the skill's philosophy of decisive planning. If the approach fails during building, the correct action is to return to whiteboarding and re-plan -- not to have a pre-cached Plan B sitting in the file. Pre-cached fallbacks also create a perverse incentive to half-commit to the primary approach.

**Procedural Knowledge Capture / Decision Log (UX Designer P4).** The current Notes section captures "decisions made during planning" informally. Replacing it with a structured Decision Log (alternatives considered, rationale, risk, reversal cost) for every decision is ceremony that contradicts the skill's lightweight philosophy. The plan file is an execution artifact, not a knowledge management system.

**Progressive Detail Resolution (Systems Architect P4).** The proposal says Phase 1 gets FULL detail, Phase 4+ gets SKETCH ("Goal, approach direction, key constraints. Details TBD during building."). This contradicts the skill's core value proposition: producing IMPLEMENTATION-READY plans. A plan where later phases say "details TBD" is not implementation-ready -- it's a half-plan that defers the hard work. The building command needs concrete tasks, not sketches.

**Configuration-as-First-Class-Output (AI Researcher P7).** The whiteboarding skill produces plans, not architecture documents. A "Configuration Surface" table (Parameter, Default, Source) belongs in the implementation phase, not the planning phase. The planner doesn't know what the right defaults are yet.

---

## Part 3: Tensions and Trade-offs

### Tension 1: Structured Fallbacks vs. Committed Plans

The compiler designer, game designer, and failure analyst all want fallback strategies in the plan. The military strategist wants "branches and sequels." But the whiteboarding skill's existing philosophy is decisive: pick an approach, commit, plan it in detail. These are genuinely opposing philosophies.

**Case for fallbacks:** Research shows single-path plans are brittle. When a phase fails, having a documented alternative saves full replanning time. SWE-Adept found hypothesis branching outperformed linear execution.

**Case against:** Documenting fallbacks for every phase is a massive ceremony increase. It encourages half-commitment to the primary approach. And in practice, when a plan fails during building, the failure mode is usually not "wrong approach" but "missed edge case in the right approach" -- fallback approaches don't help with that.

**My position:** I didn't accept fallbacks, but I'm not fully confident. For HIGH-uncertainty phases specifically, a one-line "If this approach fails" note might be worth the cost. The difficulty/uncertainty rating I accepted creates a natural hook for this: if a phase is marked HIGH uncertainty, maybe it should have a fallback. But I'm not adding it now -- let the uncertainty rating prove its value first.

### Tension 2: Plan Verification Depth vs. Planning Speed

Four personas want some form of plan self-check before user validation. The question is how deep. The cognitive scientist wants a 6-criterion review (completeness, executability, constraint coverage, dependency order, conciseness, risk). The project manager wants a 10-item checklist. The failure analyst wants a 5-item integrity check.

**My position:** I accepted a short self-check (6 items). But there's a real risk that a 6-item checklist becomes a 12-item checklist in the next iteration, then a 20-item checklist, and planning time doubles. The forcing function is: the self-check should only contain items that are MECHANICALLY CHECKABLE (does this field exist? does this constraint map?). Any item requiring judgment ("is this section vague?") is unreliable and should be removed.

### Tension 3: Front-Loading Detail vs. Progressive Refinement

The systems architect wants later phases planned at lower resolution ("SKETCH: Goal, approach direction, key constraints"). The agile coach wants hierarchical decomposition with 3-4 levels for complex tasks. Meanwhile, the skill's existing philosophy is that the plan should be implementation-ready with concrete tasks and file paths.

**My position:** The current philosophy is right for this tool. Progressive refinement makes sense when the planner is iterating over days. The whiteboarding skill runs in a single session and hands off to building. A plan with "Phase 4: TBD" is not a plan -- it's a promise to plan later. BUT: the adaptive ceremony table I accepted does reduce detail for simple tasks, which is a mild form of progressive refinement applied to complexity, not to phase position.

### Tension 4: Constraint Tracking Granularity

The game designer wants global vs. local constraint classification with enforcement mechanisms per constraint. The failure analyst wants cross-cutting constraints with per-phase verification. The cognitive scientist wants constraint pre-allocation. These are three different levels of granularity for essentially the same insight: constraints get lost during long plans.

**My position:** The plan self-check I accepted ("every constraint from Phase 1 maps to at least one phase") handles this at the cheapest level. Full constraint classification or pre-allocation tables are more ceremony than the problem warrants for most plans. If constraint drift proves to be a real problem in practice, escalate to the game designer's classification scheme.

---

## Part 4: The Uncomfortable Truth

### Is the Problem Actually the Skill?

After reading 70 proposals and 88 paper citations, here is what I actually believe:

**The whiteboarding skill is mostly fine.** Its core structure (search before ask, compare approaches, YAGNI gate, one question at a time, save to file) is sound and already better than most planning approaches. The anti-rationalization table is genuinely excellent -- it catches the most common planning failure modes.

**The real problem is not task decomposition quality. It's the plan-execution gap.** PaperBench (2504.01848) found this clearly: agents can formulate correct plans but fail to execute them. They quit early, they spend all effort on the first component, they claim completion prematurely. No amount of plan improvement fixes an execution problem.

**The 7 changes I accepted are aimed at the handoff point** -- making the plan more consumable by the building command, not making the planning process more elaborate. "Done when" criteria, dependency graphs, grounding checks -- these are all about making the plan file a better CONTRACT between whiteboarding and building. They don't add ceremony to the planning conversation.

**What would actually move the needle** is not in scope for whiteboarding:
1. The building command needs to enforce "Done when" criteria at phase boundaries (building skill change, not whiteboarding).
2. The building command needs forced continuation -- don't let the agent claim "done" without checking criteria (building skill change).
3. Context refresh between phases during building needs to carry forward dependency information (building skill change).

**The personas overfit to their research papers.** The cognitive scientist sees CogWriter and proposes constraint pre-allocation. The military strategist sees military doctrine and proposes Commander's Intent. The compiler designer sees compiler pipelines and proposes formal contracts. Many proposals are "my field's solution applied to your problem" rather than "your problem's solution informed by my field." The 8/10 convergence on dependency graphs is the exception -- that's a genuine gap everyone independently identified.

**The LLM planning limitation that no proposal addresses:** LLMs are bad at estimating what they don't know. Every proposal for risk registers, assumption tracking, uncertainty ratings, and pre-mortem analysis assumes the LLM can accurately identify what's uncertain. It often can't. The pre-mortem question I accepted works because it asks the USER to identify the risk, not the LLM. Most other risk-identification proposals ask the LLM to do something it's structurally bad at.

**Bottom line:** Make the 7 accepted changes. They're cheap, they improve the plan-to-building handoff, and they don't slow down the planning conversation. Then invest engineering effort in the building command's ability to USE these improved plans. The whiteboarding skill is not the bottleneck.
