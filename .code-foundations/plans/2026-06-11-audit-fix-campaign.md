# Plan: Audit Fix Campaign — code-foundations v4.17.0 → v5.0.0
**Created:** 2026-06-11
**Status:** in-progress
**Started:** 2026-06-11
**Current Phase:** 1
**Complexity:** complex
**Workspace:** branch: feature/audit-fix-campaign (baseline 9798c47)
---
## Context
The 2026-06 full skill-craft audit (`.skill-audit/AUDIT-REPORT.md`) found the plugin unshippable: 6 P0 blockers (invalid YAML in 2 skills + 9 gof refs; build gate policy that collapses to always-Full; REVIEW-model rule nullified by its own template; 3-sample security REVIEW racing on fixed paths; plan.md unable to receive its documented research-doc argument; cc-debugging failing its own workflow behaviorally), systemic P1s (orphaned bundled files with proven drift in ~10 skills; seam divergences; 4 internal contradictions), and P2 debt (banned constructs, duplicated STOP blocks, wrong counts, textbook bloat).

Mid-planning decision (supersedes the audit's trigger-tuning recommendations): the domain skills are workflow-injected, not organically triggered. All 19 skills get `disable-model-invocation: true` (still slash-invocable); every workflow `Skill()` load converts to `Read()` of the SKILL.md path; plan's skill matching moves to a bundled catalog. This removes ~1.1k tokens/session of listing cost and makes the audit's largest defect class (false-positive triggering) structurally impossible. Trigger re-probing is dropped from the verification bar accordingly.

## Constraints
- Bundled-file references use braced vars: `${CLAUDE_SKILL_DIR}` inside SKILL.md bodies, `${CLAUDE_PLUGIN_ROOT}` in commands/agents/templates (grug: plugin-root-must-be-braced). Never bare relative, never unbraced.
- Respect grug `build-command-progressive-disclosure`: Gate Policy/Model Resolution/Skill Resolution/Execution Loop stay inline in build.md; the REVIEW debias rule stays deliberately duplicated; commit recipe lives only in references/commit-format.md.
- Gate redesign = per-phase `**Gate:**` field set at plan SAVE; build validates and falls back to risk rules when absent.
- Orphan files = per-skill triage: fold unique facts into SKILL.md; keep+link checklists.md only where build's checklist-resolution consumes it; delete dead weight.
- welc-legacy-code is the structural model for skill bodies; `validate_skill` output is normative; `docs/code-standards.md` governs all edits.
- Working tree (uncommitted commands/plan.md + skills/planning/SKILL.md changes) is the base; build branches from it.

## Chosen Approach
**C — Mechanical-first hybrid** — Phase 1 greens the validator floor with deterministic, line-cited fixes (unblocking the 2 YAML-dead skills and all eval tooling), then artifact-clustered judgment phases touch each file's judgment edits exactly once; verification last against a clean baseline. **Fallback:** validator errors that survive Phase 1 fold into their artifact's cluster phase.

## Rejected Approaches
- **A — Severity-ordered (P0→P1→P2):** same files churn across 3 phases with 3 reviews each; gate-redesign work splits across tiers.
- **B — Pure artifact clusters:** validator floor stays red until mid-campaign; verify diffs against a dirty baseline.

---
## Implementation Phases

### Phase 1: Mechanical floor sweep
**Model:** sonnet
**Skills:** none -- deterministic text repairs with exact audit line citations; no design judgment
**Gate:** Full (bootstrapping: this campaign runs under pre-fix build.md, whose rules force Full for the first phase; the Gate field becomes operative for new plans after Phase 2 ships)

**Goal:** Apply every deterministic, line-cited audit fix so the validator floor is green and the two YAML-dead skills are parseable and testable.

**Scope:**
- IN: Quote 11 unquoted YAML descriptions (performance-optimization/SKILL.md:3, code-clarity-and-docs/SKILL.md:3, 9 gof reference files); delete all `Total items: N` lines (7 files); retitle 4 commands `# Command: <name>`; cc-debugging SKILL.md:123 path → `${CLAUDE_SKILL_DIR}/checklists.md`; gof SKILL.md:95 routing text → `${CLAUDE_SKILL_DIR}/references/`; delete 23 `CSO KEYWORDS` sections.
- OUT: any wording judgment, any structural move, frontmatter flags and description grammar (Phase 4 rewrites all descriptions), debug.md cleanup (Phase 5 rewrites the file).

**Edge cases:** quoting must preserve exact description text (only add quotes); a description containing double quotes needs single-quote or escaped style.

**File hints:** `skills/*/SKILL.md`, `skills/gof-design-patterns/references/gof-*.md`, `commands/*.md` -- audit report cites exact lines.
**Depends on:** nothing | **Unlocks:** Phases 2, 4, 5
**Produces:** `validate_skill` zero errors across all 19 skill dirs; clean textual base every later phase edits on top of.

**Done when:**
- [ ] DW-1.1: `validate_skill` returns zero errors for all 19 skill dirs
- [ ] DW-1.2: `python3 -c "import yaml..."` strict-parses frontmatter of performance-optimization and code-clarity-and-docs
- [ ] DW-1.3: `grep -rn "Total items" skills/` returns nothing
- [ ] DW-1.4: 4 command files titled `# Command: <name>`
- [ ] DW-1.5: `grep -rn "CSO KEYWORDS" skills/` returns nothing
- [ ] DW-1.6: `grep -rn 'description: [^"|>].*: ' skills/` returns nothing

**Difficulty:** LOW
**Uncertainty:** None

### Phase 2: Build orchestration repair
**Model:** opus
**Skills:** aposd-designing-deep-modules, code-clarity-and-docs
**Gate:** Full

**Goal:** Make the build pipeline's gate/model/dispatch machinery internally consistent: gate policy keyed off a plan-declared field, templates that match the rules they implement, parallel dispatch that cannot race.

**Scope:**
- IN: `commands/build.md`, `references/dispatch-templates.md`, `agents/build-agent.md`, `agents/post-gate-agent.md`.
- OUT: plan-side files (Phase 3); skill bodies.

**Constraints:** Preserve the progressive-disclosure decisions (Context). Skills no longer influence gate selection — DW-2.2.
**Edge cases:** plan files written before v5 have no `Gate:` field → risk fallback must produce a defined gate for every phase; SKIP path still logs; 3-sample with K=3 must produce 3 distinct review files.

**Approach notes:** Gate contract (user-chosen): resolution order (1) phase `**Gate:**` field verbatim (Full/Standard/Minimal); (2) absent → risk rules: security/auth/payment → Full; multi-file with new seams → Full; docs/config-only → Minimal; else Standard. Catch-up unchanged. Per-sample paths: `<plan>-phase-N-review-sample-K.md`, `scratch-K.sh`, substituted via dispatch prompt.
**File hints:** `commands/build.md:75,91,119-138,202,215`; `references/dispatch-templates.md:89-160,193-195`; `agents/post-gate-agent.md:43,59-110,163-176`; `agents/build-agent.md:29,46,64,88-94,175-203`.
**Depends on:** Phase 1 | **Unlocks:** Phase 3
**Produces:** The Gate contract — field name `**Gate:**`, values `Full|Standard|Minimal`, resolution order + risk-fallback text as written in build.md (Phase 3 copies its semantics verbatim into plan SAVE) — and the per-sample path placeholder convention.

**Done when:**
- [ ] DW-2.1: Gate resolution keys off `**Gate:**` with risk fallback; the worked example (Full+Minimal+Full) is reachable under the written rules
- [ ] DW-2.2: skill presence no longer forces Full; "every phase MUST have at least one skill" and gate policy coexist without contradiction
- [ ] DW-2.3: `§ REVIEW` model placeholder names the resolved REVIEW model (one-tier downgrade preserved)
- [ ] DW-2.4: 3-sample dispatch yields 3 distinct review files + scratch scripts (paths prompt-supplied)
- [ ] DW-2.5: `§ MINIMAL_BUILD` carries an explicit DW-IDs section
- [ ] DW-2.6: post-gate observed-behavior branch reconciled with coverage rule; prompt-listed edge cases have explicit verdict standing
- [ ] DW-2.7: SKIP path appends an execution-log entry
- [ ] DW-2.8: zero `Skill(` calls remain in build.md/templates/agents — all converted to `Read(${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md)`
- [ ] DW-2.9: agent self-check checklists removed; Standard-gate invariant wording fixed (build.md:16,195)

**Difficulty:** HIGH
**Uncertainty:** risk-fallback wording must stay short enough to live inline per the progressive-disclosure memo.

### Phase 3: Plan pipeline repair
**Model:** opus
**Skills:** aposd-simplifying-complexity, code-clarity-and-docs
**Gate:** Full

**Goal:** Make plan command and planning skill a single coherent pipeline: research-doc intake works, the plan emits the Gate field build consumes, shared machinery has one home, and the skill catalog drives matching.

**Scope:**
- IN: `commands/plan.md`, `skills/planning/SKILL.md` (body; frontmatter flags are Phase 4), `references/plan-integration.md`.
- OUT: build-side files; CLAUDE.md (Phase 7).

**Constraints:** Quick track and pipeline SAVE both emit `**Gate:**` per phase using Phase 2's contract semantics verbatim.
**Edge cases:** $ARGUMENTS = research doc path that doesn't exist → say so, fall back to treating text as feature description; non-git repo at code-standards step; CLASSIFY discovers task is Simple → demote to Quick track explicitly.

**Approach notes:** DISCOVER 1a/1b shrink to their delta (deepen research; re-confirm only on contradiction) — clarify cap lives only in plan.md. Tie-breakers scoped: "Default to Quick" routes tracks; "choose higher" only refines Medium-vs-Complex. Shared atoms forked between Quick track and pipeline (schema, check prompt) get one home (reference or plan.md) — planner's call per progressive-disclosure reasoning, recorded in the diff.
**File hints:** `commands/plan.md:7,13,21,35-37,61,85-131`; `skills/planning/SKILL.md:3,9,22,33-74,117,131-133,165-172,188,320-414`; `references/plan-integration.md:10-14`.
**Depends on:** Phases 2, 4 (consumes Gate contract + skill-catalog) | **Unlocks:** Phases 6, 7
**Produces:** Plan schema emitting `**Gate:**` per phase; DECOMPOSE matching procedure reading `references/skill-catalog.md`; seam-consistent command/skill pair.

**Done when:**
- [ ] DW-3.1: plan.md handles `$ARGUMENTS` (research-doc path → Read + seed problem statement, clarify only gaps) with `argument-hint` frontmatter
- [ ] DW-3.2: phase template + Quick track + SAVE emit `**Gate:**` matching Phase 2's contract; CHECK checklist verifies it
- [ ] DW-3.3: Step-1 gate satisfiable in reading order; explicit demotion path to Quick exists
- [ ] DW-3.4: DISCOVER no longer re-runs shared steps; clarify cap single-homed
- [ ] DW-3.5: DECOMPOSE matching reads `references/skill-catalog.md`, not the system-reminder listing
- [ ] DW-3.6: forked atoms single-homed (or fork documented); "10-task" count fixed; "pre-gate" terminology replaced
- [ ] DW-3.7: CHECK structural fixes re-reviewed (mirrors CONFIRM's rule)
- [ ] DW-3.8: zero `Skill(` calls remain in plan.md/planning SKILL.md — converted to `Read()` braced paths

**Difficulty:** HIGH
**Uncertainty:** how much Quick-track machinery to extract vs duplicate-consciously — resolved in-phase, recorded in Decision Log addendum.

### Phase 4: Invocation surface
**Model:** sonnet
**Skills:** oberskills:skill-craft
**Gate:** Full

**Goal:** Internalize all 19 skills (workflow-injected, slash-invocable, never auto-triggered) and create the catalog that replaces listing-based matching.

**Scope:**
- IN: frontmatter of all 19 skills; new `references/skill-catalog.md`.
- OUT: SKILL.md bodies (Phases 5/6); command/agent loading (Phases 2/3).

**Constraints:** Verify the flag mechanics on ONE skill before mass application (DW-4.2). Descriptions stay honest one-to-two-sentence capability statements (serve the slash menu + catalog; no trigger-noun stuffing, no workflow steps); `validate_skill` limits still apply.
**Edge cases:** any third-party reference to auto-triggering these skills (CLAUDE.md, READMEs) noted for Phase 7's doc pass.

**File hints:** `skills/*/SKILL.md` frontmatter; `references/skill-catalog.md` (new).
**Depends on:** Phase 1 | **Unlocks:** Phase 3, Phase 7
**Produces:** `references/skill-catalog.md` — one line per skill: `code-foundations:<name> — <when to match>` (consumed by Phase 3's DECOMPOSE matching and Phase 7's CLAUDE.md update).

**Done when:**
- [ ] DW-4.1: all 19 skills carry `disable-model-invocation: true`
- [ ] DW-4.2: verified on one skill before rollout: slash invocation still works; skill absent from model's Skill-tool listing (method + result recorded in execution log)
- [ ] DW-4.3: `references/skill-catalog.md` covers all 19 skills, one matching line each
- [ ] DW-4.4: every description rewritten as a capability statement ≤ 2 sentences; no `Triggers on:` lists remain
- [ ] DW-4.5: `validate_skill` zero errors ×19 after the rewrite

**Difficulty:** MEDIUM
**Uncertainty:** exact behavior of `disable-model-invocation` in current Claude Code build — DW-4.2 resolves it first.

### Phase 5: Skill bodies — CC family
**Model:** opus
**Skills:** oberskills:skill-craft, code-clarity-and-docs
**Gate:** Full

**Goal:** Bring the 8 cc-* skills, welc-legacy-code, and commands/debug.md to the welc structural standard: one home per fact, checkable gates instead of shouting, reachable bundled files, and a cc-debugging that survives its pressure eval.

**Scope:**
- IN: `skills/cc-*` (8), `skills/welc-legacy-code`, `commands/debug.md`.
- OUT: frontmatter descriptions (Phase 4); aposd/misc skills (Phase 6).

**Constraints:** Orphan triage per locked rule, disposition recorded per file. debug.md keeps only command-specific triage and Reads the cc-debugging skill — no duplicated methodology.
**Approach notes:** cc-foundations.md is canonical for shared numeric thresholds (routine length, cohesion spectrum): reconcile each CC skill's inline numbers to it and add one `Read(${CLAUDE_PLUGIN_ROOT}/references/cc-foundations.md)` pointer per CC skill that quotes those numbers; Phase 7 then makes CLAUDE.md's claim true rather than deleting it.
**Edge cases:** cc-debugging gate-ification must not reintroduce self-assessed compliance constructs — gates must be artifact-checkable (e.g., "before any Edit: failing-test output captured in the transcript").

**File hints:** audit report §P0-6, §P1-7/10/13/16, §P2; `skills/cc-debugging/SKILL.md:15,110-123`, `skills/cc-routine-and-class-design/SKILL.md:8-43,95-107,320-350`, `skills/cc-defensive-programming/SKILL.md:8-89`, `skills/cc-pseudocode-programming/SKILL.md:8-58,153-166`, `skills/cc-quality-practices/SKILL.md:83-100,179-215`, `commands/debug.md`.
**Depends on:** Phase 1 | **Unlocks:** Phase 7
**Produces:** CC bodies conforming to docs/code-standards.md; cc-debugging whose pressure eval (`.skill-audit/cc-debugging/evals.json`) passes.

**Done when:**
- [ ] DW-5.1: orphan disposition recorded + applied for all 10 files' bundles (fold / link via `${CLAUDE_SKILL_DIR}` / delete)
- [ ] DW-5.2: debug.md is a thin wrapper; exactly one canonical 7-step list exists across cc-debugging files
- [ ] DW-5.3: cc-debugging STABILIZE/SEARCH are artifact-checkable gates; pressure eval re-run verdict COMPLIANT with expectations ≥5/6
- [ ] DW-5.4: 8-param verdict consistent; routine-length thresholds match cc-foundations.md everywhere
- [ ] DW-5.5: zero banned constructs in scope files (no Myth/Reality tables, no self-assessed checklists, no duplicated STOP/Crisis-Invariant blocks — each invariant stated exactly once per file)
- [ ] DW-5.6: cc-quality-practices delegates debugging methodology to cc-debugging; its language-notes.md deleted
- [ ] DW-5.7: chain/handoff references use `Read()` braced paths

**Difficulty:** HIGH
**Uncertainty:** DW-5.3 may need 2 eval iterations; cap at 3 per skill-craft doctrine, then redesign the gate.

### Phase 6: Skill bodies — APOSD, CA, GoF, misc
**Model:** sonnet
**Skills:** oberskills:skill-craft, code-clarity-and-docs
**Gate:** Full

**Goal:** Same standard applied to the remaining 11 skills: drift items folded in, duplicates and discipline-theater removed, real orphans resolved.

**Scope:**
- IN: `skills/aposd-*` (4), `ca-architecture-boundaries`, `gof-design-patterns`, `clarify`, `code-clarity-and-docs`, `code-standards`, `performance-optimization`.
- OUT: frontmatter (Phase 4); CC family (Phase 5).

**Constraints:** Orphan triage rule as Phase 5. gof pattern files keep convention routing (verified working) — only the 3 real orphans need disposition.
**Edge cases:** clarify's `${CLAUDE_PLUGIN_ROOT}/references/adaptive-questioning.md` coupling — move into the skill dir or document the plugin-only coupling. This phase runs after Phase 3 (see Depends on), so it sees the final planning-checkpoint references and owns the coordination if the file moves.

**File hints:** audit report skill sections; `skills/aposd-designing-deep-modules/SKILL.md:104-153`, `skills/aposd-simplifying-complexity/SKILL.md:15,146-166,203-228`, `skills/aposd-reviewing-module-design/SKILL.md:69-81,183-217`, `skills/aposd-verifying-correctness/SKILL.md:132-179`, `skills/gof-design-patterns/references/{foundations,creational,structural-behavioral,implementation-and-review}.md`, `skills/performance-optimization/SKILL.md:8-56,179-292`, `skills/ca-architecture-boundaries/SKILL.md:113-140`, `skills/code-standards/{SKILL.md,references/section-templates.md}`.
**Depends on:** Phases 1, 3 (adaptive-questioning.md coordination — this phase runs after the planning checkpoints are final) | **Unlocks:** Phase 7
**Produces:** remaining bodies conforming to docs/code-standards.md; drift items (RF-8, SF-1, RF-7, EH-5) folded into their SKILL.mds.

**Done when:**
- [ ] DW-6.1: four drift items present in their SKILL.mds; quick-reference duplicates removed (one encoding per fact)
- [ ] DW-6.2: discipline-theater gone (impatience script, emergency bypass, show-your-work framing, doubled withholding gates, Process-Integrity/TC self-checks)
- [ ] DW-6.3: gof 3 real orphans resolved; foundations.md trimmed to operative rules; Myth/Reality table gone
- [ ] DW-6.4: performance-optimization states the priority workflow once; latency table + before/after examples moved to checklists.md
- [ ] DW-6.5: ca checklist polarity uniform (checked = satisfied); clarify 70%-stat single-homed; adaptive-questioning coupling resolved
- [ ] DW-6.6: code-standards has one length target + missing/invalid base-commit failure path; section-templates.md has a ToC
- [ ] DW-6.7: code-clarity-and-docs checklists triaged; "(CHECKER)" chain target defined or removed
- [ ] DW-6.8: zero banned constructs in scope files

**Difficulty:** MEDIUM
**Uncertainty:** None

### Phase 7: Verify and publish
**Model:** sonnet
**Skills:** oberskills:skill-craft
**Gate:** Full

**Goal:** Prove the audit findings closed with the same instruments that found them, update the docs layer, bump and publish.

**Scope:**
- IN: full-suite re-verification; `CLAUDE.md`; `.claude-plugin/plugin.json`; commit + push.
- OUT: new features.

**Constraints:** Verification uses skill-eval MCP tools — verdicts from tool output only. Trigger probes intentionally dropped (skills no longer model-invocable — supersedes the original success criterion).
**Edge cases:** regression sweep must cover files edited by EVERY phase, not just skills/ (commands, agents, references).
**Approach notes:** Version 5.0.0 — removing auto-trigger is a user-visible behavior change (breaking by semver intent).
**File hints:** `CLAUDE.md` (gate table, flow diagram, "All CC skills reference cc-foundations.md" claim, invocation model, version), `.claude-plugin/plugin.json`.
**Depends on:** Phases 3, 4, 5, 6 | **Unlocks:** done
**Produces:** published v5.0.0 on origin/main; closure evidence appended to `.skill-audit/AUDIT-REPORT.md`.
**Rollback:** `git revert` the publish commit and push — marketplace tracks main, so revert un-publishes; version stays burned (next bump 5.0.1).

**Done when:**
- [ ] DW-7.1: `validate_skill` ×19: zero errors; remaining warnings each carry a written justification
- [ ] DW-7.2: behavioral re-runs green: cc-debugging pressure COMPLIANT (from Phase 5, re-confirmed), welc regression eval still passes
- [ ] DW-7.3: fresh-agent regression sweep over the campaign diff finds no reintroduced banned constructs, unquoted descriptions, bare-relative paths, or `Skill(` workflow calls
- [ ] DW-7.4: CLAUDE.md accurate (workflow, gate table incl. Gate field, invocation model, no false claims); docs/code-standards.md consistent with shipped conventions
- [ ] DW-7.5: plugin.json at 5.0.0; commit pushed to origin/main

**Difficulty:** MEDIUM
**Uncertainty:** None

---
## Test Coverage
**Level:** Full re-audit (chosen during clarification — validator + behavioral evals + regression sweep; trigger probes dropped with invocation internalization)

## Test Plan
- [ ] Per-DW: every DW above is an executable or desk-checkable assertion (grep / validate_skill / strict YAML parse / eval verdict / template desk-check) — build agents cite the evidence per DW
- [ ] Integration: after Phase 2, desk-check the dispatch templates — substituting K=1,2,3 into the 3-sample dispatch yields three distinct review + scratch paths; the `§ REVIEW` model placeholder names the resolved REVIEW model, not the plan model
- [ ] Integration: after Phase 3, a dry-run plan→build seam check — author a 2-phase toy plan with `Gate: Standard` + missing Gate, confirm build.md's resolution text yields Standard and the risk fallback respectively (desk-check against the written rules)
- [ ] Integration: after Phase 4, DW-4.2's single-skill flag verification before rollout
- [ ] Dirty: cc-debugging pressure eval (TIME/AUTHORITY/SIMPLICITY) — the eval that failed pre-campaign must pass (DW-5.3)
- [ ] Dirty: regression sweep greps target the *defect patterns*, not the fixed instances: `description: [^"|>].*: `, `Total items`, `\| Myth \| Reality \|`, `Skill(code-foundations:`, unbraced `$CLAUDE_PLUGIN_ROOT`
- [ ] Dirty: welc behavioral eval re-run (the pre-campaign PASS must not regress)
- [ ] Manual: slash-invoke one internalized skill (`/code-foundations:cc-debugging`) and confirm it loads

## Assumptions
| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|---|---|---|---|
| `disable-model-invocation: true` keeps slash invocability and drops the listing from model context | MED-HIGH | Phase 4 (DW-4.2, single skill first) | Keep flags off; revert to lean-description strategy (clarify Option 3) |
| Read()-loaded SKILL.md is behaviorally equivalent to Skill()-loading | HIGH | Phase 2 (first conversion, spot-check a dispatch) | Re-introduce Skill() for agent dispatch only; flags stay |
| Claude Code's lenient YAML parser means quoting changes nothing for current users | HIGH | Phase 1 (slash-invoke after quoting) | n/a — quoting is strictly additive |
| Uncommitted plan.md/planning working-tree changes are wanted as the base | MED | Phase 1 (user confirms at build branch creation) | Stash and re-apply after campaign |
| Saved behavioral evals (.skill-audit/) remain valid fixtures | HIGH | Phase 5 | Re-author the affected eval |

## Decision Log
| Decision | Alternatives Considered | Rationale | Phase |
|---|---|---|---|
| Campaign architecture C (mechanical-first hybrid) | A severity-ordered; B pure clusters | Validator floor green in cheapest phase; judgment edits touch each file once; survives 4/5 pre-mortem failures | all |
| Internalize all 19 skills (`disable-model-invocation`) | Hybrid (4 stay triggerable); lean descriptions | Skills are workflow-injected by design; ~1.1k tokens/session saved; false-positive triggering eliminated structurally | 2,3,4 |
| Gate = plan-declared `**Gate:**` field + risk fallback | Risk rules only; codify always-Full | Planner has the risk context at SAVE; decision visible and reviewable in the plan file | 2,3 |
| Orphans = per-skill triage | Link everything; merge-and-delete | Preserves build's checklist-resolution where consumed; kills drift where not | 5,6 |
| Version 5.0.0 | 4.18.0 minor | Auto-trigger removal is user-visible behavior change | 7 |
| Verification = full re-audit minus trigger probes | Validator-only; spot checks | Same instruments that found the defects prove closure; probes meaningless without a trigger surface | 7 |

---
## Notes
- planning/SKILL.md is touched by Phase 3 (body) and Phase 4 (frontmatter) — disjoint regions, rebase-trivial.
- DAG (post-CHECK): 1 → {2, 4, 5}; {2, 4} → 3; 3 → 6; {3, 4, 5, 6} → 7. Phase 6 serialized after Phase 3 so the adaptive-questioning.md coupling is resolved against final planning-checkpoint references.
- The audit's Phase-4-era trigger findings (exclusion clauses, mutual exclusions) are intentionally NOT implemented — superseded by internalization. The catalog file carries the disambiguation knowledge instead.
- Build runs on a feature branch off the current working tree; per-phase commits per references/commit-format.md.
---
## Execution Log

### Phase 1: Mechanical floor sweep (Gate: Full)
- [x] BUILD: Discovery + design + TDD implementation complete
- [x] REVIEW: Verification passed
- [x] Committed
Commit: fd92f15
Summary: Validator floor is green across all 19 skills — every description is valid quoted YAML (performance-optimization and code-clarity-and-docs are parseable again), Total-items counts and CSO KEYWORDS sections are gone, commands are titled as commands, and the cc-debugging/gof bundled-file paths use braced ${CLAUDE_SKILL_DIR} vars. Later phases edit on a clean textual base; skill resolution deviation: Phase 1 ran with no skills (mechanical work, reason recorded).

### Phase 2: Build orchestration repair (Gate: Full)
- [x] BUILD: Discovery + design + TDD implementation complete
- [x] REVIEW: Verification passed (9/9 DW)
- [x] Committed
Commit: d471854
Summary: Build pipeline is internally consistent — gate policy resolves from the per-phase **Gate:** field (contract authored at commands/build.md:112-123, values Full|Standard|Minimal, risk fallback for field-less plans; Phase 3 must copy these semantics verbatim into plan SAVE), § REVIEW dispatches the one-tier-downgraded model, 3-sample REVIEW uses per-sample -sample-K paths (post-gate-agent paths are prompt-supplied), § MINIMAL_BUILD carries DW-IDs, observed-behavior evidence and prompt-listed edge cases have defined verdict standing, SKIP logs, and all skill loading in build files is Read(${CLAUDE_PLUGIN_ROOT}/...) form.

### Phase 4: Invocation surface (Gate: Full)
- [x] BUILD: Discovery + design + TDD implementation complete
- [x] REVIEW: Verification passed (4/4 DW in scope; DW-4.2 verified via official docs + orchestrator validator)
- [x] Committed
Commit: feaf4c7
Summary: All 19 skills carry disable-model-invocation: true (slash-invocable, never auto-triggered, descriptions out of model context); descriptions are lean ≤2-sentence capability statements; references/skill-catalog.md (19 entries, family-grouped, with disambiguation notes) is now the single home for when-to-match knowledge — Phase 3 must wire plan DECOMPOSE matching to read it. Validator zero errors ×19.

### Phase 3: Plan pipeline repair (Gate: Full)
- [x] BUILD: Discovery + design + TDD implementation complete
- [x] REVIEW: Verification passed (8/8 DW + edge cases)
- [x] Committed
Commit: a88ddd1
Summary: plan.md accepts $ARGUMENTS research-doc paths (seed + clarify-gaps, missing-path fallback) with argument-hint; plan SAVE and Quick track emit per-phase **Gate:** matching build.md's contract byte-for-byte; DECOMPOSE matching reads references/skill-catalog.md via braced Read(); seam divergences closed (clarify cap single-homed in plan.md, tie-breakers scoped, Step-1 gate order-satisfiable, Simple-demotion path, pre-gate terminology gone, schema fork sync-noted); zero Skill() calls remain in plan-side files. Note: BUILD agent falsely claimed docs/code-standards.md absent — content unaffected (verified by REVIEW), but flagged for the Phase 7 regression sweep.

### Phase 5: Skill bodies — CC family (Gate: Full)
- [x] BUILD: Discovery + design + TDD implementation complete
- [x] REVIEW: Verification passed (7/7 DW; eval evidence verified on disk)
- [x] Committed
Commit: 3911d2c
Summary: CC family conforms to the welc standard — cc-debugging's STABILIZE/SEARCH are artifact-checkable preconditions and its pressure eval passes COMPLIANT 6/6 ×2 (fixture re-authored to inject the skill, mirroring the production Read()-injection path; eval runs under .skill-audit/cc-debugging/workspace/iteration-4/); debug.md is an 18-line wrapper; 12 orphan files deleted, 5 checklists linked; banned constructs, duplicate STOP blocks, and the 8-param contradiction removed; thresholds reconciled to cc-foundations.md with Read() pointers in all CC SKILL.mds (-3,739 lines net). Live runtime confirmation: domain skills no longer appear in the session skill listing; commands remain visible.
