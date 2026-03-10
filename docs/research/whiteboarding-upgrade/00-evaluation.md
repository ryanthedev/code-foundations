# Blind Evaluation of Three Synthesis Documents

**Evaluator posture:** Which synthesis would produce the best upgraded whiteboarding skill if handed to an implementer today?

---

## Scores

| Criterion | X | Y | Z |
|-----------|---|---|---|
| Evidence quality | 9 | 7 | 9 |
| Implementability | 8 | 9 | 9 |
| Signal-to-noise | 10 | 4 | 8 |
| Intellectual honesty | 10 | 5 | 8 |
| Coherence | 9 | 6 | 8 |
| Respect for existing design | 10 | 4 | 8 |
| Practical wisdom | 10 | 5 | 9 |
| **TOTAL** | **66** | **40** | **59** |

---

## Per-Synthesis Commentary

### X (66/70)

**Strengths:** This is an exceptional document. Every accepted proposal includes the strongest counterargument considered, followed by a counter-counter -- genuine adversarial reasoning, not performative skepticism. The "Proposals I Killed" section is as valuable as the accepted proposals because it explains WHY 63 proposals were rejected, organized into clear categories (weak evidence, academic not practical, too much ceremony, already handled, contradicts philosophy). The Part 4 "Uncomfortable Truth" section is remarkable -- it correctly identifies that the whiteboarding skill is mostly fine and that the real bottleneck is the plan-execution gap in the building command, not the planning skill itself. This is the kind of insight that prevents an upgrade from making things worse.

**Weaknesses:** The implementation specs are slightly less precise than Z's -- they say "add to Phase 3 Section Template" but don't always reference line numbers. The adaptive ceremony table (Change 5) is somewhat vague on what "Detail Level" means in practice. Minor issues given the overall quality.

### Y (40/70)

**Strengths:** The most comprehensive and organized of the three. The tiered structure (Tier 1 / Tier 2 / Tier 3) with persona consensus counts is clear. The consolidated implementation plan at the end maps every change to a specific phase. The final updated Section Template and Plan File Schema are ready to copy-paste. The evidence strength summary table is a useful reference.

**Weaknesses:** This synthesis has a serious accumulation problem. It accepts 7 Tier 1 proposals, 7 Tier 2 proposals, and 10 Tier 3 "interesting ideas worth considering." That is 24 changes to a skill that currently works. The updated Plan File Schema is enormous -- Commander's Intent, Global Constraints, Fallback Approaches, Assumptions table, Risks table, Decision Log, Dependency Graph, Replanning Triggers, Static/Dynamic markers, per-phase Requires/Produces/Context Forward, per-phase Reasoning, per-phase If-this-fails, per-phase Difficulty. A plan produced by this upgraded skill would be 3-4x longer than the current output. The synthesis acknowledges the "add more structure vs reduce ceremony" tension but then resolves it by adding nearly all the structure. The constraint pre-allocation (1.6) and inter-phase context handoff (1.7) are treated as must-haves despite weaker evidence than claimed -- CogWriter's constraint pre-allocation is about text generation constraints, not software constraints (X correctly identified this). The Decision Log replacing Notes adds ~200 words per decision for a plan consumed once. The Feasibility Gate with goal relaxation imports household-robot research into software planning. This synthesis treats consensus count as a proxy for importance, which leads it to accept proposals that many personas mentioned but that don't actually address the whiteboarding skill's real gaps.

### Z (59/70)

**Strengths:** The evidence-first approach is rigorous. Part 1 (Evidence Map) lays out every quantified finding before making any proposals, which disciplines the analysis. The "Why this beats alternatives" section for each change shows the author understood that many proposals are the same insight in different clothing -- and chose the minimum viable version. The cuts section is thorough and well-reasoned. The implementation specs include line number references, making them directly actionable. The 7-change set is lean and coherent.

**Weaknesses:** Cut the pre-mortem question, which X correctly identified as a near-zero-cost upgrade to an existing question (replacing "What could go wrong?" with a research-proven reformulation). The reasoning -- "it's a user-interaction change, not a plan structure change" -- is technically true but misses that the whiteboarding skill IS a user-interaction skill. The cut of the dependency DAG summary section is defensible but the inline-only approach may be harder for the building command to parse than a consolidated summary. Z also cut constraint classification (global vs local) as redundant with the mapping table, but X's plan self-check explicitly checks that "every constraint from Phase 1 maps to at least one phase" -- which is a lighter-weight version of the same insight that Z achieved through a heavier mapping table. There is a slight tension in Z's own system.

---

## Winner and Why

**X wins decisively.** It is the only synthesis that demonstrates genuine critical judgment rather than aggregation. The key differentiators:

1. **It correctly identifies what NOT to change.** The insight that "the whiteboarding skill is mostly fine" and that the real problem is the plan-execution gap in the building command is the most important conclusion across all three documents. Y and Z both treat the upgrade as "which of these 70 proposals to accept" -- X questions whether the problem is even in the right skill.

2. **It accepts 7 changes and kills 63.** Y accepts 24. Z accepts 7. But X's 7 are better justified than Z's 7 because X shows the adversarial reasoning for each acceptance AND each rejection. Z's cuts are well-reasoned but the acceptances lack the "strongest counterargument I considered" structure that makes X's reasoning auditable.

3. **It respects the existing design.** X explicitly categorizes rejected proposals that "contradict skill philosophy" (fallback preservation, progressive detail resolution, configuration-as-first-class-output). Y accepts fallback approaches and progressive detail without acknowledging the philosophical tension with the skill's decisive-planning identity.

4. **The tensions section is honest.** X flags 4 genuine tensions and states positions with appropriate uncertainty ("I'm not fully confident"). Y's tensions section resolves every tension with "these are NOT contradictory" -- which is suspicious. Real tensions are contradictory; that is what makes them tensions.

5. **Part 4 is uniquely valuable.** No other synthesis contains anything like the "Uncomfortable Truth" section. The observation that "personas overfit to their research papers" is correct and explains why consensus count is an unreliable quality signal.

---

## Recommended Hybrid

Use X as the basis. Pull the following from Z:

1. **Line number references in implementation specs.** Z's specs reference specific line numbers in the current SKILL.md (e.g., "modify the Section Template, currently at line ~265"). X's specs say "add to Phase 3 Section Template" without line references. The line numbers make implementation faster.

2. **The Evidence Map format from Z Part 1.** X cites evidence inline per proposal. Z's consolidated evidence table (organized by theme) is a better reference artifact to keep alongside the synthesis. Include it as an appendix.

3. **Z's "Phase Count Limits" table.** X's adaptive ceremony table includes max phases, but Z's standalone table with Target and Hard Maximum columns is cleaner and easier to enforce.

4. **Z's conditional fallback scoping.** Z limits the "If this fails" field to MEDIUM/HIGH difficulty phases only. X does not include a fallback field at all (rejected it). The compromise position: add Z's conditional fallback for HIGH-uncertainty phases only (not MEDIUM), since X's own tension analysis acknowledged this might be worth the cost for high-uncertainty work.

Do NOT pull from Y:

- Commander's Intent section (redundant with existing Problem Statement + Constraints)
- Assumption Register (ceremony without payoff, as X argued)
- Risk Register (same)
- Inter-phase Produces/Consumes/Context Forward fields (these belong in the building skill, not whiteboarding, as X correctly identified)
- Decision Log replacing Notes (over-engineering for a plan consumed once)
- Replanning Triggers table (belongs in building skill)
- Feasibility Gate with goal relaxation (household-robot research applied to software planning)
- Static/Dynamic HTML comment markers (invisible to humans, building command already knows)
