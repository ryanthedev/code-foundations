# Discovery + Design: Phase 2 - Build orchestration repair

## Files Found

All four scope files exist and were read in full:

- `commands/build.md` (295 lines) — orchestrator. Gate Policy Detection (99-126), Model Resolution (87-98), Skill Resolution (67-86), Execution Loop (169-241), SKIP path (200), 3-sample (215), VERIFY Skill() loads (249-250), Crisis Invariants (11-21).
- `references/dispatch-templates.md` (234 lines) — `§ FULL_BUILD`, `§ MINIMAL_BUILD`, `§ REVIEW`, `§ CATCHUP_REVIEW`. Substitution rules at top (19-25). Skill() lines at 68, 70, 113, 115, 181, 183, and the Substitution-rule prose at 22.
- `agents/post-gate-agent.md` (179 lines) — fixed `scratch.sh` (43), fixed review path (110, 186), Skill() prose (18), observed-behavior branch (59/79) vs coverage rule (165/82), edge-case standing gap (Step 4 / verdict rules), self-check checklist (170-176).
- `agents/build-agent.md` (208 lines) — Skill() prose (14), code-standards row "Required YES" + if-missing branch (29), self-check checklist (88-94), deterministic count rule (46), minimal-mode output gap (175-203 vs 64).

Supporting (read, not edited): `references/commit-format.md` (execution-log entry format), `docs/code-standards.md`, grug memo `build-command-progressive-disclosure`, `.skill-audit/AUDIT-REPORT.md` (findings 2,3,4,14,15 + banned-constructs list), plan Phase 2 (lines 60-91).

## Current State

The pipeline machinery is internally contradictory exactly as the audit (P0-2/3/4 + P1 #14/#15) describes:

- **Gate keyed off skill presence.** `build.md:119` forces Full when "Phase has a `**Skills:**` field"; `:122` requires "No Skills" for Minimal. Combined with the `:75` mandate "Every phase MUST have at least one skill" (enforced in Skill Resolution, which runs BEFORE Gate Detection per `:69`), every phase ends up Full. Standard/Minimal/Catch-up are dead policy and the `:138` worked example (Full+Minimal+Full) is unreachable.
- **REVIEW model nullified.** `build.md:91` mandates a one-tier REVIEW downgrade, but `§ REVIEW` (`dispatch-templates.md:136`) says `model: [from plan's **Model:** field, or omit]` — following the template ignores the downgrade. `§ CATCHUP_REVIEW:195` gets it right ("resolved REVIEW model … downgraded one tier").
- **3-sample race.** `build.md:215` dispatches three identical REVIEW prompts, but `post-gate-agent.md:43` hard-codes `scratch.sh` and `:110/:186` hard-codes one review path → samples overwrite each other; "record all three" is impossible.
- **`§ MINIMAL_BUILD` has no DW-IDs section** though `build-agent.md:46` enforces a DW count check and minimal-mode TDD says "write tests from DW items."
- **post-gate dead evidence branch.** `:59/:79` allow "observed behavior" as evidence, but `:82/:165` "ANY DW item without test coverage → FAIL" means that allowance can never yield PASS. Injected `## Edge cases` (`dispatch-templates.md:157-161`) has no standing in Verdict Rules (`:162-168`), while `:99/:104` forbid failing on uncovered edge cases — a contradiction with the template's "same standing as DW items" claim.
- **Self-check checklists** at `build-agent.md:88-94` and `post-gate-agent.md:170-176` are banned constructs (code-standards "Voice and constructs": self-assessed compliance checklists).
- **Skill() invocation form** appears in all four files (grep confirms 9 hits across prose + template lines).
- **Standard-gate invariant wording bug** at `build.md:16`: "BUILD before REVIEW (Full/Standard gate) — Minimal gate phases skip discovery." Standard has no REVIEW (`:106` Standard = BUILD → commit), and discovery is skipped only in Minimal — so the parenthetical mis-scopes both clauses.
- **SKIP path** (`build.md:200`) marks the task complete and proceeds but appends NO execution-log entry, so a skipped phase leaves no trace for the Progress block / trust report.
- **build-agent code-standards row** (`:29`) says "Required YES" yet carries an if-missing branch — contradictory. Minimal mode (`:64`) skips discovery but the Output template (`:184-203`) demands discovery artifacts.

## Gaps

| # | Plan/audit expectation | Reality | Action |
|---|------------------------|---------|--------|
| 1 | Gate keys off `**Gate:**` field + risk fallback | Keys off skill presence | Rewrite Gate Policy Detection resolution order |
| 2 | Skills don't force Full | Skills force Full | Remove the "has Skills" Full-trigger + "No Skills" Minimal condition; keep the every-phase-skill mandate |
| 3 | `§ REVIEW` names resolved REVIEW model | Names plan model | Change placeholder + add downgrade note |
| 4 | 3-sample yields 3 distinct files | Fixed paths | Parameterize scratch + review paths via prompt; templates carry `-sample-K` placeholders |
| 5 | `§ MINIMAL_BUILD` has DW-IDs section | Absent | Add DW-IDs section to template |
| 6 | Observed-behavior reconciled; edge cases have standing | Dead branch + no standing | State the coverage rule once (observed behavior satisfies non-testable DW items); give prompt-listed edge cases DW standing |
| 7 | SKIP path logs | No log entry | Add execution-log append to SKIP path |
| 8 | Zero `Skill(` calls | 9 hits | Convert to `Read(${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md)` |
| 9 | Self-checks removed; invariant fixed | Present; mis-scoped | Delete both checklists; fix `build.md:16` |
| 10 | build-agent code-standards "If present"; minimal output variant | "Required YES" + minimal gap | Mark "If present"; add minimal-mode output variant |

## Code Standards

`docs/code-standards.md` applies directly. Key conventions for this phase:

- **File references in commands/agents/references** → `${CLAUDE_PLUGIN_ROOT}/...` braced; never bare relative or unbraced.
- **Progressive-disclosure single-home/inline/duplicate rules** (cited verbatim in the standard): Gate Policy, Model Resolution, Skill Resolution, Execution Loop stay INLINE in build.md; REVIEW debias rule stays DUPLICATED (build.md + `§ REVIEW`); commit recipe lives only in `commit-format.md`. My edits must preserve all three.
- **Banned constructs:** self-assessed compliance checklists → replace with checkable gates or delete. This is the authority for DW-2.9's self-check removals.
- **No stated item counts**, no CRISIS/STOP shouting added, **state a rule once neutrally.**
- **Dispatch/agent seam contract:** "paths written by parallel-dispatched agents must be parameterized per sample" — directly governs DW-2.4.
- The `Skill(code-foundations:<name>)` cross-skill-handoff guidance in code-standards still references the Skill() form, but this is a v5 campaign convention change (assumption verified below): converting to `Read()` in the four scope files is in-scope; code-standards itself is OUT (skill bodies / docs untouched this phase). No contradiction introduced because the four files are not cross-skill handoffs — they are dispatch/load instructions.

## Test Infrastructure

No automated test framework — this is a markdown plugin. Per the plan's stated test convention: **the DW items ARE the tests**, each an executable grep or a desk-checkable assertion. Evidence types:

- **grep assertions** (DW-2.8): runnable `grep` returning empty/expected.
- **Desk-checks** (DW-2.1, DW-2.4): record the substitution/walkthrough in this file as test evidence — walk the worked example through the new rules line by line; substitute K=1,2,3 and show three distinct paths.
- **Structural assertions** (DW-2.3/2.5/2.6/2.7/2.9): grep for presence/absence of the required text after edits.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases (evidence) |
|-------|---------------|--------|------------------------|
| DW-2.1 | Gate resolution keys off `**Gate:**` with risk fallback; worked example (Full+Minimal+Full) reachable | COVERED | Desk-check walkthrough (below, recorded after edit): assign Gate fields to a 3-phase plan and trace resolution → Full, Minimal, Full. grep confirms new resolution order text present. |
| DW-2.2 | skill presence no longer forces Full; mandate + gate policy coexist | COVERED | grep: no "Phase has a `**Skills:**` field" Full-trigger and no "No Skills" Minimal condition remain in Gate Policy; `:75` skill mandate text still present. |
| DW-2.3 | `§ REVIEW` model placeholder names resolved REVIEW model | COVERED | grep `§ REVIEW` block: placeholder reads "resolved REVIEW model per Model Resolution"; "from plan's **Model:** field" gone from that block. |
| DW-2.4 | 3-sample yields 3 distinct review + scratch files (prompt-supplied) | COVERED | Desk-check K=1,2,3 substitution producing 3 distinct paths (recorded below). grep: `-sample-K`/`scratch-K` placeholders in templates; post-gate paths parameterized as prompt-supplied. |
| DW-2.5 | `§ MINIMAL_BUILD` carries explicit DW-IDs section | COVERED | grep: `## Done-When Items (DW-IDs)` present inside `§ MINIMAL_BUILD`. |
| DW-2.6 | observed-behavior branch reconciled; edge cases have verdict standing | COVERED | grep: single coverage rule stating observed behavior satisfies non-testable DW items; Verdict Rules reference prompt-listed edge cases as findings. |
| DW-2.7 | SKIP path appends execution-log entry | COVERED | grep: SKIP path step includes execution-log append. |
| DW-2.8 | zero `Skill(` calls remain | COVERED | `grep -n 'Skill(' commands/build.md references/dispatch-templates.md agents/*.md` returns nothing. |
| DW-2.9 | self-check checklists removed; Standard-gate invariant wording fixed | COVERED | grep: no "Self-Check Before" sections in either agent; `build.md:16` no longer claims Standard has REVIEW; count rule at build-agent `:46` retained. |

**All items COVERED:** YES (count: 9 DW items in prompt = 9 in table)

## Design Decisions

Most of this phase is mechanical text correction. Two decisions are genuinely non-mechanical and get the design-it-twice treatment (aposd-designing-deep-modules). The "module interface" here is the *rule text a downstream reader (orchestrator/agent at runtime) must execute* — depth = the reader carries low cognitive load and cannot mis-resolve.

### Design A: Gate-resolution rule text (DW-2.1/2.2)

**What I'm designing:** the resolution-order block that replaces the skill-keyed rules, kept short enough to stay inline (Uncertainty flag in plan).

Approaches considered:
1. **Verbatim risk prose** — paste the approach-note sentence as one numbered list. Simple, but mixes the override, the field, and four risk sub-rules into prose the reader must parse each time.
2. **Two-tier: field-first, then a compact risk table.** Resolution order (1) Pipeline override (2) `**Gate:**` field verbatim (3) absent → risk-rule table → default Standard. The table makes each risk → gate mapping a separate visually-bounded row.
3. **Decision-tree pseudocode** — `if Pipeline … elif Gate field … elif security/auth/payment … elif multi-file+seams … elif docs/config-only … else Standard`. Maximally unambiguous but verbose and reads like code in a prose command.

| Criterion | A (prose) | B (field + table) | C (tree) |
|-----------|-----------|-------------------|----------|
| Interface simplicity (reader parses once) | Med | High | Med |
| Information hiding (one home, no echo) | High | High | High |
| Caller ease (cannot mis-resolve) | Low | High | High |
| Inline brevity (Uncertainty constraint) | High | High | Low |
| Matches existing build.md voice (tables) | Low | High | Low |

**Choice: B.** Loses to C on raw unambiguity (C's explicit elif chain leaves zero gaps), but B wins on brevity + house voice (build.md already uses the gate-level table at `:103`) and keeps the four risk mappings as bounded rows. **Sacrificed from C:** the literal short-circuit ordering is conveyed by "first match wins" prose rather than elif syntax — acceptable because the existing block already used "first match wins." Pipeline override stays topmost per the approach note. The every-phase-skill mandate (`:75`) stays untouched in Skill Resolution; only its gate *consequence* is removed — that's how the mandate and gate policy "coexist without contradiction" (DW-2.2).

Depth check: interface = one resolution-order list + one risk table; hidden detail = none leaked elsewhere (single home preserved); common case (field present) = read the field, done.

### Design B: post-gate observed-behavior / coverage reconciliation (DW-2.6)

**What I'm designing:** one rule that resolves the dead branch — when may a DW item PASS without an automated test?

Approaches considered:
1. **Delete the observed-behavior branch** — make every DW item require an automated test. Simplest verdict logic, but the plan's own test convention (DW items can be desk-checkable, not all automatable) makes this wrong for this very repo, and the dispatch note says "reconcile," not "delete the allowance."
2. **Observed behavior counts as coverage for non-testable DW items.** State once: a DW item is covered by (a) a passing automated test, OR (b) recorded observed behavior when the item is not testable by an automated test. Then the coverage-FAIL rule reads "no test AND no recorded observed behavior → FAIL."
3. **Two verdict tiers** (tested vs observed) with different confidence labels. More faithful but adds a verdict dimension the gate doesn't need — over-generalization.

| Criterion | A (delete) | B (observed = coverage for non-testable) | C (two tiers) |
|-----------|-----------|------------------------------------------|---------------|
| Resolves dead branch | Yes (by removal) | Yes (by reconciliation) | Yes |
| Fits this repo's DW-as-desk-check convention | No | Yes | Yes |
| Verdict-rule simplicity | High | High | Low |
| Matches dispatch instruction ("reconcile … satisfies coverage") | No | Yes | Partial |

**Choice: B.** Loses to A on absolute simplicity, but A contradicts the plan's test convention and the explicit dispatch instruction. **Sacrificed:** a reviewer must now judge "is this DW item automatable?" — mitigated by stating it as: prefer an automated test; observed behavior is the fallback only when no automated test can exercise the item. Edge-case standing (same DW item): the `§ REVIEW`/`§ CATCHUP_REVIEW` injected `## Edge cases` section already claims "same standing as DW items"; I make the agent's Verdict Rules honor that by adding "ANY prompt-listed edge case left unhandled → FAIL," while the anti-overcorrection rule keeps *unlisted* edge cases as non-blocking Notes. This removes the `:99/:104` contradiction by scoping it to *prompt-listed* cases only.

### Mechanical decisions (no design-it-twice needed)

- **Skill() → Read() conversion (DW-2.8):** prose mentions of "execute every `Skill()` and `Read()` line" become "execute every `Read()` line"; template `- Skill(code-foundations:<name>)` lines become `- Read(${CLAUDE_PLUGIN_ROOT}/skills/<name>/SKILL.md)`; the Substitution-rule prose at `dispatch-templates.md:22` is updated to describe emitting a SKILL.md `Read()` line then checklist `Read()` lines. VERIFY's two `Skill()` loads (`build.md:249-250`) become `Read()` of those skills' SKILL.md. Checklist `Read()` lines stay as-is (dispatch instruction).
- **3-sample paths (DW-2.4):** templates `§ REVIEW` (and the security branch) gain `-sample-K` review path + `scratch-K.sh` placeholders; post-gate-agent treats scratch + review paths as **prompt-supplied** (Scratch Script Pattern and Output use a `[scratch path from prompt]` / `[review path from prompt]` placeholder, defaulting to the non-sampled names for single-review). build.md:215 references the per-sample substitution.
- **SKIP log (DW-2.7):** SKIP path step appends an execution-log entry (a one-line SKIP variant of the commit-format entry — "SKIPPED per build agent: [reason]"); the commit recipe stays single-homed in commit-format.md (no recipe duplication, just the append instruction).
- **Self-checks (DW-2.9):** delete `build-agent.md:88-94` and `post-gate-agent.md:170-176`; keep build-agent's deterministic count rule (already in the Done-When Traceability section at `:46`). Fix `build.md:16` wording.
- **build-agent code-standards row + minimal output (file hints):** `:29` "Required YES" → "If present"; add a minimal-mode output variant (Recommendation N/A, Artifacts "none (minimal gate)", route missing code-standards note to final Output).

## Prerequisites

- [x] All four scope files exist
- [x] Phase 1 complete (clean textual base)
- [x] Assigned skills loaded (aposd-designing-deep-modules, code-clarity-and-docs)
- [x] grug memo + code-standards read (progressive-disclosure constraints understood)
- [x] Assumption verified (Read()-loaded SKILL.md ≡ Skill()-loaded — see below)

## Assumption Verification

**Assumption (HIGH):** Read()-loaded SKILL.md is behaviorally equivalent to Skill()-loading; nothing in the four scope files depends on Skill-tool side effects.

**Verified TRUE.** Grep of all `Skill(` occurrences shows every one is either (a) prose telling an agent to "execute every Skill()/Read() line" to load checklist content into context, or (b) a template line that loads a skill's instructional content. None invoke a Skill-tool *side effect* (no model-invocation dependency, no sub-agent spawn, no tool-permission grant keyed on Skill()). The content of SKILL.md lands in context identically whether reached via Skill() or Read(). The VERIFY-step loads (`build.md:249-250`) likewise only need the skill's guidance text in context. No invalidation found — proceeding with conversion.

## Recommendation

**BUILD.** All 9 DW items are COVERED with desk-check or grep evidence. No new scope, no missing prerequisites, no cross-phase seam conflict (the Gate contract this phase Produces is authored here for Phase 3 to copy). Edits stay within the four scope files and honor the progressive-disclosure inline/single-home/duplicate constraints.

---

# Test Evidence (recorded after implementation)

## DW-2.1 desk-check — worked example (Full + Minimal + Full) reachable

Take a 3-phase plan with these fields, and trace the new resolution order (build.md "Resolution order", first match wins): (1) Pipeline override → (2) `**Gate:**` field verbatim → (3) risk fallback → Standard.

| Phase | Fields present | Resolution step that fires | Resolved gate |
|-------|----------------|----------------------------|---------------|
| 1 | `**Gate:** Full` (no Pipeline) | Step 2: field verbatim = Full | **Full** |
| 2 | `**Gate:** Minimal` (no Pipeline) | Step 2: field verbatim = Minimal | **Minimal** |
| 3 | `**Gate:** Full` (no Pipeline) | Step 2: field verbatim = Full | **Full** |

Result: **Full + Minimal + Full** — reachable. Each phase also carries skills (every-phase-skill mandate at build.md:75 retained), yet skills no longer enter the resolution order, so they do not force Full. The same sequence is also reachable in a pre-v5 plan with NO `**Gate:**` fields via the risk fallback: Phase 1 multi-file-with-new-seams → Full; Phase 2 docs/config-only → Minimal; Phase 3 multi-file-with-new-seams → Full. **PASS.**

Contrast (old rules, for the record): under the deleted rule 2 "Phase has a `**Skills:**` field → Full" plus rule 3 "Minimal requires No Skills", every phase resolved to Full because Skill Resolution gives every phase a skill — Minimal was unreachable. That contradiction is now gone (DW-2.2).

## DW-2.4 desk-check — K=1,2,3 substitution yields 3 distinct paths

The orchestrator (build.md:214) substitutes `K`=1,2,3 into the `§ REVIEW` review-path and scratch-path placeholders; the post-gate-agent uses the prompt-supplied paths (no hard-coding).

| K | Review path (Output section) | Scratch path (How-to-run section) |
|---|------------------------------|-----------------------------------|
| 1 | `.code-foundations/build/<plan>-phase-N-review-sample-1.md` | `scratch-1.sh` |
| 2 | `.code-foundations/build/<plan>-phase-N-review-sample-2.md` | `scratch-2.sh` |
| 3 | `.code-foundations/build/<plan>-phase-N-review-sample-3.md` | `scratch-3.sh` |

Three distinct review files and three distinct scratch scripts → no overwrite, no race; "record all three" is satisfiable. Single (non-sampled) review drops the suffix → `…-review.md` / `scratch.sh`. **PASS.**

## grep evidence summary

| DW | Assertion | Result |
|----|-----------|--------|
| DW-2.1 | new resolution order (`Plan-declared gate`, `Risk fallback`, `first match wins`) present | PASS (build.md:110,113,114) |
| DW-2.2 | skill-keyed Full-trigger + No-Skills Minimal condition removed; `:75` mandate retained | PASS (greps empty; mandate at :75) |
| DW-2.3 | `§ REVIEW` model = "resolved REVIEW model per … Model Resolution … downgraded one tier" | PASS (templates:148) |
| DW-2.4 | `-sample-K` review + `scratch-K.sh` placeholders in templates; post-gate paths prompt-supplied; build.md references substitution | PASS (templates:143,186,203; post-gate:41,177; build.md:214) |
| DW-2.5 | `§ MINIMAL_BUILD` contains `## Done-When Items (DW-IDs)` | PASS (templates, MINIMAL block) |
| DW-2.6 | observed-behavior allowed only for non-testable DW items (Step 2 + Verdict Rules); prompt-listed edge cases → FAIL | PASS (post-gate:86,88,171,174) |
| DW-2.7 | SKIP path appends a SKIP execution-log entry | PASS (build.md:199) |
| DW-2.8 | `grep -n 'Skill(' commands/build.md references/dispatch-templates.md agents/*.md` returns nothing | PASS (exit 1, no matches) |
| DW-2.9 | no "Self-Check Before" sections in either agent; count rule retained (build-agent:46,88); build.md:16 invariant fixed | PASS (grep empty; :46/:88 present; :16 reads "Full gate only") |

## Skill checklist application notes

- **aposd RF-7 (Granularity Mismatch) / RF-3 (Single-Use):** the per-sample path convention is defined once in `§ REVIEW` and *referenced* (not re-specified) by build.md and post-gate-agent — the path logic lives at the template (the dispatch surface), callers receive it. No knowledge duplicated across the seam beyond the one deliberately-duplicated debias rule.
- **aposd IH (information hiding):** gate resolution is a single inline block; the risk table hides the four mappings behind "first match wins". Reader's common case (field present) needs only step 2.
- **code-clarity "different words" / no-stale:** edited comments/prose describe the new behavior (e.g. build.md:16 now matches the gate table at :106); no comment restates code; banned self-check constructs removed per code-standards.
- **code-clarity RF-12 (version/seam sync):** the path-naming convention (`-sample-K`, `scratch-K.sh`) is identical in all three files that mention it — verified by grep.
