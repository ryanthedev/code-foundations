# Blind Evaluation: Plans X, Y, Z

## Blind Scores (before reading skill files)

| Criterion | X | Y | Z |
|-----------|---|---|---|
| Pre-gate clarity | 9 | 6 | 7 |
| Scope boundaries | 9 | 7 | 7 |
| Verification anchors | 8 | 6 | 7 |
| Signal-to-noise | 7 | 7 | 8 |
| Human reviewability | 8 | 7 | 8 |
| Phase boundaries | 8 | 5 | 8 |
| Non-discoverable decisions | 9 | 5 | 6 |
| **TOTAL** | **58** | **43** | **51** |

## Per-Plan Commentary

### Plan X (plan-B.md)

**Strengths:**
- Each phase has Goal, Why, Scope IN/OUT, Constraints, Approach notes, File hints, Depends-on/Unlocks, Done-when, Difficulty, and Uncertainty. This is the richest phase template and it maps directly to what the pre-gate agent, implementation agent, and post-gate agent each need.
- Approach notes are genuinely non-discoverable. "Use three-point estimation as the primary technique -- user chose this over pure story points because it produces time ranges" is exactly the kind of decision a pre-gate agent cannot reconstruct from codebase search.
- File hints are directional, not prescriptive. "skills/cc-construction-prerequisites/SKILL.md -- good structural reference" tells the pre-gate where to start without mandating a specific file.
- Uncertainty fields flag the real unknowns ("The right granularity for solo planning poker adaptation") which directs pre-gate investigation.
- The Assumptions table and Decision Log at plan level capture rationale that would otherwise be lost between the planning session and the building session.
- Rejected Approaches with rationale prevent the pre-gate agent from re-considering already-rejected paths.
- The Fallback in the Chosen Approach section gives the building orchestrator a recovery path without needing to pause for replanning.

**Weaknesses:**
- At ~200 lines before the meta-commentary, it is the longest plan. Some fields feel slightly redundant -- the "Why" field per phase often restates what "Goal" already implies ("All downstream phases depend on the core estimation logic existing" is inferable from the dependency chain).
- Approach notes are present on every phase even when some phases have no non-discoverable decisions ("Phase 3: Research Backing" approach notes just restate which sources to cite, which is arguably a constraint, not an approach note).
- The plan includes a Success Criteria section at the top AND Done-when per phase. The top-level success criteria are useful for human readers but the post-gate agent only sees per-phase criteria, so the top-level ones are not consumed by the pipeline. Not harmful, but it is mild duplication.

### Plan Y (plan-A.md)

**Strengths:**
- Lean and fast to read. A human can scan this plan in under 2 minutes and understand the shape of the work.
- Clean 4-field phase template (Goal, Scope IN/OUT, Constraints, Done-when) is simple and unambiguous.
- Test Coverage and Test Plan are well-defined.
- Notes section captures useful context (PERT formula, solo planning poker adaptation, estimation antipatterns).

**Weaknesses:**
- Phases 3 and 4 introduce scope creep. Phase 3 modifies the whiteboarding skill and Phase 4 modifies the building skill's model auto-detection logic. Both violate the plan's own stated constraint ("Must not duplicate what whiteboarding already does"). More critically, modifying two existing skills is a different kind of work than creating a new skill, and the plan does not acknowledge this risk.
- Phase 3 ("Add an estimation hook to the whiteboarding skill so that after phases are defined") is vague about WHERE in the whiteboarding flow this hook goes. The pre-gate agent will need to read the entire whiteboarding SKILL.md and guess at the insertion point. Contrast with Plan X, which explicitly says "integration is additive -- estimation adds an optional section to the plan file" without requiring whiteboarding modification.
- Phase 4 ("Update the building skill's model auto-detection to factor in effort estimates") contradicts Plan X's approach of keeping estimation decoupled. This is a design decision that should have been settled during approach selection, not embedded as a phase.
- No Approach notes, File hints, Depends-on/Unlocks, Difficulty, or Uncertainty fields. The pre-gate agent gets Goal/Scope/Constraints/Done-when and nothing else. For Phase 1 (creating a new skill), this is enough. For Phase 3 (modifying an existing skill with a specific integration pattern), the pre-gate agent is flying blind on the user's intent.
- No Assumptions table. The plan assumes building's model auto-detection needs explicit estimation awareness, but this is unverified. Plan X flags this as an assumption with a fallback.
- 4 phases for what is essentially 2.5 phases of real work (create skill files, then modify two existing skills). Phases 3 and 4 are both "modify an existing skill" which could have been one phase with clear scope boundaries.

### Plan Z (plan-C.md)

**Strengths:**
- Good phase decomposition. Phase 3 (Whiteboarding Integration) is correctly scoped as haiku-level work (small addition, 10-15 lines). Phase 4 (Documentation) is also haiku. This shows thoughtful model selection.
- The plan explicitly states "Changes to building skill (not needed -- building already reads Model field from plan files)" in Phase 3's Scope OUT. This is a critical design decision that prevents scope creep.
- Test Coverage is honestly "None" with a clear justification (no runtime code). This is more accurate than Plan X's "100%" which then redefines what 100% means for markdown files.
- Tasks are listed explicitly per phase, which gives the building orchestrator concrete task counts for model auto-detection.
- Notes section is practical and specific (cold-start limitation, PERT formula, output format recommendation).

**Weaknesses:**
- Tasks per phase blur the line between WHAT and HOW. "Define the estimation workflow phases: SCOPE, CLASSIFY, ESTIMATE, CALIBRATE, OUTPUT" is prescribing the internal structure of the SKILL.md, which is exactly what the pre-gate agent should design using its loaded skills. If the pre-gate agent discovers a better workflow structure, it is now in conflict with the plan.
- No Approach notes field. The decision to NOT modify the building skill is captured in Phase 3's Scope OUT, but the general principle ("estimation output writes into plan file's phase sections, which building already reads") is only in the Chosen Approach section at the top. The pre-gate agent for Phase 3 may not re-read the top-level approach section.
- Constraints at the phase level are thin. Phase 1 has "YAML frontmatter must match the pattern" and "Output format must not conflict with existing plan file fields" -- these are discoverable by the pre-gate agent. The genuinely non-discoverable decisions (three-point as primary technique, solo dev adaptation, confidence intervals over point estimates) are in the top-level Constraints section but not repeated or referenced at the phase level where the pre-gate agent will look.
- No Uncertainty fields. Phase 1 has real uncertainty (how to adapt planning poker for solo devs) but it is not flagged.
- Missing Depends-on/Unlocks for Phase 3 is odd -- it says "Depends-on: Phase 1 (estimation skill must exist to reference)" but Phase 2 (checklists and hard-data) is not a dependency, which is correct, but it means Phase 3 could theoretically execute in parallel with Phase 2. The building skill serializes all phases anyway, so this is harmless, but it shows the dependency chain was not fully thought through.

## Winner and Why

**Plan X wins by a clear margin.**

The core question is: "Could a pre-gate agent with fresh context read this phase and immediately know what to discover, what decisions are already made, and what pseudocode to write?" Plan X answers this question most completely for every phase.

The key differentiators:

1. **Approach notes preserve user intent.** Plan X is the only plan that consistently separates "what the user decided" from "what the codebase can reveal." The pre-gate agent does not have access to the planning conversation. Without approach notes, it must guess at why three-point estimation was chosen over story points, why integration is additive rather than embedded, why the difficulty derivation rule should be mechanical. Plan Y and Z bury these decisions in top-level sections that the pre-gate agent may not re-read when focused on a single phase.

2. **File hints accelerate discovery without mandating.** "Look at skills/cc-construction-prerequisites/SKILL.md as a structural reference" is genuinely useful to a pre-gate agent with fresh context. It saves 2-3 minutes of grep-and-read that would otherwise be spent finding a good reference file. Plans Y and Z provide no file hints.

3. **Uncertainty fields direct investigation.** When the pre-gate agent reads "Uncertainty: The right granularity for solo planning poker adaptation," it knows to spend extra time on that question and flag it in the pseudocode. Without this signal, the pre-gate agent treats all tasks as equally certain.

4. **Phase dependencies are explicit and clean.** "Depends on: Phase 1 | Unlocks: Phase 2" with the Assumptions table creates a traceable chain. The building orchestrator and the human reviewer can both verify the plan's logic.

Plan X's weakness (verbosity, occasional redundancy between Goal and Why) is a much smaller problem than Plan Y's weakness (missing non-discoverable decisions, scope creep into modifying existing skills) or Plan Z's weakness (prescriptive tasks that conflict with pre-gate agent autonomy).

## After Reading Skill Files

### Which skill file produced which plan?

- **Plan Y** was produced by **Candidate A (minimal)** -- the current whiteboarding skill. The lean 4-field template (Goal, Scope, Constraints, Done-when) and the absence of approach notes, file hints, difficulty, and uncertainty fields are the giveaway. The meta-commentary confirms this.

- **Plan X** was produced by **Candidate B (contract)** -- the contract-oriented whiteboarding upgrade. The rich phase template with Goal, Why, Scope, Constraints, Approach notes, File hints, Depends-on/Unlocks, Done-when, Difficulty, Uncertainty is the signature. The Assumptions table, Decision Log, and Rejected Approaches sections at the plan level are also Candidate B features.

- **Plan Z** was produced by **Candidate C (adaptive)** -- the complexity-adaptive whiteboarding skill. The `**Complexity:** medium` field in the header, the explicit Tasks per phase, and the medium-track template structure (Goal, Scope, Tasks, Constraints, Depends-on/Unlocks, Done-when) match the Candidate C Medium template.

### Was my ranking correct?

Yes. B > C > A, which maps to X > Z > Y. No surprises.

### Surprises

1. **Plan Y (Candidate A / current skill) produced the most scope-creepy plan.** Despite the current skill's emphasis on minimal phases, it produced 4 phases where 3 would suffice, AND two of those phases modify existing skills rather than keeping the estimation skill standalone. The minimal template did not prevent bad phase decomposition -- it just prevented the plan from flagging the risk.

2. **Plan Z (Candidate C / adaptive) was more conservative than Plan X (Candidate B / contract) about modifying existing skills.** Plan Z explicitly says "Changes to building skill (not needed)" in Phase 3's Scope OUT. Plan X says the same thing but in a different way (integration section in SKILL.md, not modifying building). Both avoided the trap that Plan Y fell into. The adaptive skill's complexity classification likely helped -- Medium track produces more disciplined scoping than either the minimal or contract approach for this particular task.

3. **The Tasks field in Candidate C is a double-edged sword.** It gives the building orchestrator concrete task counts for model auto-detection (useful), but it also prescribes internal structure that the pre-gate agent should design (harmful). The contract approach (Candidate B) avoids this by using Approach notes for strategic decisions and leaving tactical decomposition to the pre-gate agent.

4. **Candidate B's self-check phase caught a real gap** (missing backwards-compatibility criterion in Phase 2's Done-when). Neither Candidate A nor C has a self-check mechanism. This is a genuine quality improvement.

## Recommended Hybrid

The final skill should take the best elements from each candidate:

### From Candidate B (contract) -- the winner:
- **Phase template with Approach notes, File hints, Difficulty, Uncertainty.** These four fields are the biggest differentiator. They capture what the pre-gate agent cannot discover on its own.
- **Self-check phase before user validation.** Catches structural gaps (constraint coverage, scope coherence, dependency chains) before the user sees the plan. Worth the 2 minutes.
- **Assumptions table and Decision Log at plan level.** Preserves planning rationale across context refresh.
- **Rejected Approaches with rationale.** Prevents re-exploration of dead ends.
- **Fallback in Chosen Approach.** Gives the building orchestrator a recovery path.

### From Candidate C (adaptive) -- the runner-up:
- **Complexity classification with track-specific templates.** Simple tasks should NOT get the full contract treatment. The Simple track (flat checklist, 30-50 words/phase, no approach comparison) is a genuine improvement for small tasks. The signal table (files, patterns, cross-cutting concerns, uncertainty) is a good classification mechanism.
- **Model recommendation per phase based on task/file counts.** Plan Z correctly assigned haiku to Phases 3 and 4. Plan X assigned sonnet to everything. The adaptive skill's model recommendation logic produced better results here.
- **Hard phase cap of 7.** Reasonable guard rail.

### From Candidate A (minimal) -- specific elements only:
- **The 50-75 word discipline for simple phases.** Candidate A's insistence on brevity is the right instinct for Simple track. For Medium/Complex, Candidate B's 100-150 word range is better.
- **The anti-rationalization entries about pre-gate agent autonomy** ("Pre-gate designs better than you can -- it has the codebase AND the skills"). Candidate A has the clearest, most aggressive version of this message. It should be preserved in the hybrid.

### What to AVOID from each:

- **From B:** The "Why" field per phase. In practice it restates what Goal already says or what Depends-on/Unlocks already implies. Cut it.
- **From C:** The "Tasks" field listing explicit task bullets. This prescribes HOW, not WHAT. The building orchestrator can count Done-when items for model auto-detection instead.
- **From A:** The complete absence of Approach notes, File hints, Difficulty, and Uncertainty. The minimal approach works for Simple tasks but fails for Medium/Complex.

### Recommended template (Medium/Complex track):

```markdown
### Phase N: [Name]
**Model:** [recommended model]

**Goal:** [What this phase accomplishes and why -- 1-2 sentences]

**Scope:**
- IN: [what this phase covers]
- OUT: [what is explicitly excluded]

**Constraints:**
- [non-discoverable requirements]

**Approach notes:** [ONLY non-discoverable user decisions -- omit if none]
- [decision + rationale]

**File hints:**
- `path/to/area/` -- [why relevant]

**Depends on:** [Phase X] | **Unlocks:** [Phase Y]

**Done when:**
- [ ] [verifiable criterion]
- [ ] [verifiable criterion]

**Difficulty:** LOW / MEDIUM / HIGH
**Uncertainty:** [what could change -- or "None"]
```

This is Candidate B's template with "Why" removed. The Simple track uses Candidate C's flat checklist template (Goal + task bullets + Done-when). The classification step uses Candidate C's signal table. The self-check uses Candidate B's checklist. Total: the best of all three.
