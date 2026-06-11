# Discovery + Design: Phase 3 - Plan pipeline repair

## Files Found
- `commands/plan.md` (149 lines) — router + Quick track. Frontmatter `description: "Plan features and implementation"`, no `argument-hint`, no `$ARGUMENTS` handling.
- `skills/planning/SKILL.md` (434 lines) — Standard/Full pipeline. Frontmatter already rewritten by Phase 4 (10-step list dropped from description); BODY still stale.
- `references/plan-integration.md` (77 lines) — chain reference; "Expected Flow" still shows pre-staging steps.
- `commands/build.md:101-125` — authoritative Gate contract (read; values Full|Standard|Minimal, resolution order, risk fallback table).
- `references/skill-catalog.md` (19 entries) — single home for when-to-match knowledge; DECOMPOSE must Read this.
- `references/plan-schema.md` — MISSING (candidate new file per fork decision below).
- `commands/research.md` — frontmatter style reference (concrete trigger-bearing description, no argument-hint of its own).

## Current State
- **DW-3.1 (ARGUMENTS):** plan.md has zero `$ARGUMENTS` / `argument-hint` / research-doc handling. Confirmed via grep (empty). Audit P0-5 finding #5.
- **DW-3.2 (Gate):** `grep 'Gate:'` returns nothing in either file. Neither Quick track nor SAVE emits `**Gate:**`. Phase template lacks the field.
- **DW-3.3 (Step-1 gate / demotion):** planning Step-1 Questioning Gate (SKILL.md:50-54) lists "Complexity classified (Medium/Complex)" but CLASSIFY is Step 2 (SKILL.md:64) — unsatisfiable in reading order (audit finding #12). No explicit Simple-demotion path in CLASSIFY.
- **DW-3.4 (clarify cap):** `grep '5 rounds'` = 1 hit (plan.md:37 only). planning 1b is uncapped — already single-homed in plan.md. DISCOVER 1a/1b (SKILL.md:34-44) still re-describe the shared code-standards scan + clarify load.
- **DW-3.5 (catalog matching):** DECOMPOSE (SKILL.md:150) instructs "Read the system-reminder ... find every line with a skill name ... and its description". Descriptions no longer appear in the reminder (Phase 4). plan.md:57 Quick decompose has the same "available skill descriptions in the system-reminder" instruction. Neither reads skill-catalog.md.
- **DW-3.6 (forks/terminology):** "pre-gate"/"post-gate" at SKILL.md:132,134,160. "10-task pipeline" at plan.md:131 (SKILL.md:22 lists 11 tasks). Quick-track schema (plan.md:85-106) omits `## Notes` vs full schema (SKILL.md:357). Forked atoms: plan-file schema, CHECK agent prompt, reframe line.
- **DW-3.7 (CHECK re-review):** Quick track step 6 (plan.md:125) "FINDINGS -> fix issues, then proceed" — no re-review of structural fixes. CONFIRM (SKILL.md:415) has "Structural changes -> re-run CHECK". CHECK step itself (Step 8) has no fix-path rule at all.
- **DW-3.8 (Skill()):** 9 `Skill(` occurrences across the two files (none in plan-integration.md). All must convert to braced `Read()`.

## Gaps
| Gap | Plan assumption | Reality |
|---|---|---|
| Gate field | build consumes `**Gate:**` | plan emits none |
| ARGUMENTS | research→plan handoff documented | plan.md has no input step |
| Catalog | DECOMPOSE reads catalog | reads system-reminder (now description-less) |
| Skill() invocation | Read() form everywhere | 9 Skill() calls remain (broken post-Phase 4) |
| plan-integration flow | 10-step staged pipeline | shows old pre-staging flow |

## Code Standards
No `docs/code-standards.md` in repo (this is a prompt/markdown plugin, not a code project). Conventions inferred from the files themselves: `# Command: <name>` title (Phase 1), braced `Read(${CLAUDE_PLUGIN_ROOT}/...)` for cross-file loads, `**Field:**` phase-header syntax, DW-{phase}.{item} IDs. No code-standards.md found — noted.

## Test Infrastructure
No automated test framework for markdown prompt files. Test convention per the plan: **the DW items ARE the tests** — executable grep assertions + recorded desk-checks (walk an invocation through the edited text). RED = grep/desk-check currently fails; GREEN = passes after edit. There is a validator (`validator green ×19` from Phase 1) — will run it as a regression check that edits don't break structure.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-3.1 | plan.md handles $ARGUMENTS (research path → Read+seed; non-path → feature desc); argument-hint frontmatter; missing-file edge | COVERED | T1: `grep 'argument-hint' commands/plan.md` = 1; T2: `grep '\$ARGUMENTS' commands/plan.md` ≥1; T3 desk-check: walk a research-doc path invocation → Read + seed problem statement, clarify gaps only; T4 desk-check: walk a non-existent path → falls back to feature-description text |
| DW-3.2 | phase template + Quick track + SAVE emit `**Gate:**` matching build.md:112-123; CHECK verifies presence | COVERED | T5: `grep 'Gate:' commands/plan.md skills/planning/SKILL.md` shows field in Quick schema, phase template, SAVE guidance; T6 desk-check: walk a Gate-bearing phase through build.md resolution order rule 2 (verbatim values Full/Standard/Minimal); T7: CHECK checklists in both files name the Gate field |
| DW-3.3 | Step-1 gate satisfiable in reading order; explicit demotion path in CLASSIFY | COVERED | T8 desk-check: read SKILL.md top→bottom, Step-1 gate items all satisfiable before CLASSIFY runs; T9: CLASSIFY contains explicit "Simple → demote to Quick track" path |
| DW-3.4 | DISCOVER no longer re-runs shared steps; clarify cap ONLY in plan.md (grep '5 rounds' = 1) | COVERED | T10: `grep -c '5 rounds' across both` = 1; T11 desk-check: DISCOVER 1a/1b read as delta (deepen research, re-confirm only on contradiction), no re-run of code-standards scan / clarify-from-scratch |
| DW-3.5 | DECOMPOSE reads skill-catalog.md via braced Read(); no system-reminder skill-scan instruction remains | COVERED | T12: `grep 'skill-catalog' both` shows braced Read in DECOMPOSE (SKILL.md) + Quick decompose (plan.md); T13: no remaining "skill name ... in the system-reminder" matching instruction for DECOMPOSE/Quick decompose |
| DW-3.6 | forked atoms single-homed or fork documented w/ sync note; "10-task" fixed; "pre-gate" gone (grep returns nothing) | COVERED | T14: `grep 'pre-gate' both` = empty; T15: `grep '10-task\|10 task' both` = empty (replaced w/ correct count); T16: fork decision recorded (below) + sync note added in both files |
| DW-3.7 | CHECK structural fixes re-reviewed (mirror CONFIRM's rule) | COVERED | T17: Quick step 6 + planning Step 8 CHECK fix-path say "structural fixes → re-run CHECK" mirroring CONFIRM:415 |
| DW-3.8 | grep 'Skill(' across all three files returns nothing — all braced Read() | COVERED | T18: `grep 'Skill(' commands/plan.md skills/planning/SKILL.md references/plan-integration.md` = empty |

**All items COVERED:** YES

## Design Decisions

### D1 — Fork resolution (DW-3.6): document the fork, extract only the truly-shared atom

The plan offers two options: (A) extract shared plan-file schema + CHECK prompt to a new `references/plan-schema.md` consumed by both; or (B) consciously document the fork. **Decision: hybrid — document the schema/CHECK-prompt fork with sync notes, extract nothing new.**

Reasoning (aposd + progressive-disclosure ethos):
- The two schemas are **deliberately not identical**: Quick omits Chosen Approach / Rejected Approaches / Assumptions / Decision Log; full includes them. The two CHECK prompts differ the same way (Quick checklist is a strict subset). Extracting to a shared file would force a conditional ("if Quick, skip these rows") that every reader must mentally filter — and the schema is **point-of-decision content** the ethos says stays inline. A third file the author must cross-reference mid-write ADDS cognitive load (aposd: change amplification + cognitive load), the opposite of the goal.
- A new `references/plan-schema.md` would be a shallow pass-through (aposd red flag) — it carries no logic, just text two callers already hold inline at their decision point.
- What IS a genuine single-home win: the **`**Gate:**` field rule** and the **phase template's Gate line**. Those get ONE canonical statement (build.md:112-123 is already the home for Gate *semantics*); plan-side files reference it rather than restating the resolution table. The reframe line is near-identical but trivial (one sentence) — left inline in both, not worth a file.
- Therefore: add a one-line **sync note** at each forked location ("Quick schema is the full schema minus Chosen Approach/Rejected/Assumptions/Decision Log — keep in sync with planning SKILL.md Step 7") so future edits don't re-diverge. This satisfies "give each fact ONE home, with the lighter file pointing to it": the **heavier** schema (planning Step 7) is the canonical one; the Quick schema points to it as "the full schema minus the Medium/Complex-only sections."

### D2 — Gate field home (DW-3.2)
build.md:112-123 is the home for Gate *resolution semantics*. Plan-side emits the field + a one-line assignment rule that mirrors the risk language (Full = security/auth/payment or new cross-phase seams; Minimal = docs/config-only; Standard = otherwise) and points to build.md for the contract. SAVE owns assignment for the pipeline; Quick track assigns inline. Phase templates (both files) gain a `**Gate:**` line.

### D3 — Catalog matching (DW-3.5)
Replace the "scan the system-reminder for skill descriptions" instruction in DECOMPOSE (SKILL.md:150) and Quick decompose (plan.md:57) with `Read(${CLAUDE_PLUGIN_ROOT}/references/skill-catalog.md)`. The SAVE/CHECK *validation* lines that say "matches an available skill in the system-reminder" stay as-is for name-existence checks (the reminder still lists names, just not descriptions) — but reword to "available skill (see references/skill-catalog.md)" to avoid implying descriptions live in the reminder. Decision: point validation at the catalog too, since the catalog is the authoritative 19-skill roster.

### D4 — DISCOVER delta (DW-3.4)
Shrink SKILL.md 1a/1b to their delta: 1a → "code-standards scan already ran in the plan command's shared steps; deepen codebase research only (pattern reuse, prior art)"; 1b → "the problem statement arrives confirmed; re-confirm ONLY if discovery contradicts it — do not re-clarify from scratch." Remove the `Skill(code-standards)` and `Skill(clarify)` loads from DISCOVER (they ran in plan.md already). The 5-round cap stays solely in plan.md.

### D5 — Step-1 gate ordering (DW-3.3)
Reword the Questioning Gate item "Complexity classified (Medium/Complex)" → "Track received from dispatch (Medium/Complex)" since the plan command's router already classified and dispatched. Add to CLASSIFY an explicit demotion: "If signals actually read Simple, stop the pipeline and hand back to the Quick track — do not force a 3-phase plan onto a one-thing change."

### D6 — Terminology (DW-3.6)
"pre-gate" → "build-agent"; "post-gate" → "post-gate-agent" (the actual agent definition names) at SKILL.md:132,134,160. "10-task pipeline" (plan.md:131) → "11-step pipeline" (matching SKILL.md:22's 11-task list) — or simpler, "no full planning pipeline" to avoid pinning a brittle count. Decision: use "no multi-step pipeline" (count-free, won't re-stale).

### D7 — CHECK re-review (DW-3.7)
Quick step 6 and planning Step 8: change "FINDINGS -> fix issues, then proceed" to mirror CONFIRM:415 — "FINDINGS → fix; structural fixes → re-run CHECK, minor → proceed."

### D8 — plan-integration.md (DW-3.8 + scope)
Update "Expected Flow" to the staged pipeline (Discover→Classify→Explore→Decompose→Detail→Cross-cut→Save→Check→Confirm→Handoff) and the Quick track's staged steps. No Skill() in this file currently, so DW-3.8 is already satisfied here — but the flow text is stale (Approach notes mandate).

## Prerequisites
- [x] Required files exist (plan.md, planning/SKILL.md, plan-integration.md)
- [x] build.md:112-123 Gate contract available to copy
- [x] skill-catalog.md exists (19 entries)
- [x] Phase 4 frontmatter on planning confirmed not-to-touch (BODY only)

## Recommendation
**BUILD.** All 8 DW items are COVERED with grep assertions + desk-checks. Fork resolved by documenting the deliberate Quick/full schema divergence with sync notes (D1) rather than extracting a shallow shared file — recorded above. No new file created; scope stays in the three named files.
