# Discovery + Design: Phase 6 - Skill bodies — APOSD, CA, GoF, misc

## Files Found

- skills/aposd-designing-deep-modules/SKILL.md (164 lines)
- skills/aposd-designing-deep-modules/checklists.md (85 lines)
- skills/aposd-reviewing-module-design/SKILL.md (229 lines)
- skills/aposd-reviewing-module-design/checklists.md (107 lines)
- skills/aposd-simplifying-complexity/SKILL.md (230 lines)
- skills/aposd-simplifying-complexity/checklists.md (100 lines)
- skills/aposd-verifying-correctness/SKILL.md (202 lines)
- skills/aposd-verifying-correctness/checklists.md (98 lines)
- skills/ca-architecture-boundaries/SKILL.md (152 lines)
- skills/gof-design-patterns/SKILL.md (103 lines)
- skills/gof-design-patterns/references/foundations.md (198 lines)
- skills/gof-design-patterns/references/creational.md (93 lines) — REAL ORPHAN
- skills/gof-design-patterns/references/structural-behavioral.md (192 lines) — REAL ORPHAN
- skills/gof-design-patterns/references/implementation-and-review.md (192 lines) — REAL ORPHAN
- skills/gof-design-patterns/references/techniques.md (225 lines)
- skills/clarify/SKILL.md (194 lines)
- skills/code-clarity-and-docs/SKILL.md (223 lines)
- skills/code-clarity-and-docs/checklists.md (170 lines)
- skills/code-standards/SKILL.md (124 lines)
- skills/code-standards/references/section-templates.md (303 lines)
- skills/performance-optimization/SKILL.md (305 lines)
- skills/performance-optimization/checklists.md (126 lines)

## Current State

All 19 skills have valid frontmatter (Phase 1 complete), `disable-model-invocation: true` (Phase 4 complete). The skill bodies contain the issues documented in the plan — discipline-theater constructs, duplicate encodings, drift items in checklists but not SKILL.mds, and a few structural fixes needed.

## Gaps

| Gap | Observed |
|-----|----------|
| RF-8 not in aposd-designing-deep-modules SKILL.md | Only in checklists.md; SKILL.md Red Flags table stops at RF-7 (Granularity Mismatch) |
| SF-1 not in aposd-reviewing-module-design SKILL.md | Only in checklists.md Quick Reference; SKILL.md Red Flags Quick Reference missing it |
| RF-7 not in aposd-simplifying-complexity SKILL.md | Only in checklists.md; SKILL.md Red Flags table stops at RF-6 |
| EH-5 not in aposd-verifying-correctness SKILL.md | Only in checklists.md EH section; SKILL.md Error Handling dimension stops at 4 checks |
| aposd-designing-deep-modules discipline-theater | Process Integrity Checks self-assessed section (lines 103-113), scripted impatience reply, Emergency Bypass Criteria section, "Time bound: 1-2 hours" |
| aposd-simplifying-complexity duplicate gates | "Do NOT present" appears twice (line 15 + line 163); "Show Your Work" + "This prevents claiming" framing; TC-1..3 self-assessed items in checklists.md |
| aposd-simplifying-complexity Quick Reference duplicate | Quick Reference block is 3rd encoding of the error hierarchy (already in table + decision procedure) |
| aposd-reviewing-module-design duplicates | "Common Evaluation Mistakes" Myth/Reality table; Quick Reference (lines 198-219) duplicates evaluation checklist headings; "Red Flags Quick Reference" (lines 70-84) duplicates per-chapter tables; checklists.md has duplicate IDs at Quick Reference section |
| aposd-verifying-correctness Quick Checklist | Lines 133-145 duplicate the per-dimension detect triggers; per-dimension "Red flag:" rationalization lines in SKILL.md already in checklists.md |
| ca-architecture-boundaries polarity | Phase 3 items are phrased as bad-when-checked ("SRP: Classes serving multiple actors?"); Phase 1/2 items are good-when-checked |
| ca-architecture-boundaries duplicate SRP question | Phase 1 "Map actors" and Phase 3 "SRP: Classes serving multiple actors?" are the same question |
| ca-architecture-boundaries grep scope | `grep -r "instanceof\|getType()\|typeof.*===" src/` — no "domain dirs" scope annotation, no "adapt paths" note |
| gof-design-patterns 3 real orphans | creational.md, structural-behavioral.md, implementation-and-review.md — selection content duplicates SKILL.md and techniques.md |
| gof foundations.md Myth/Reality table | Lines 171-180 |
| gof techniques.md duplicate By Symptom | Section 7 "By Symptom" (lines 163-179) near-verbatim duplicates SKILL.md's Pick by Symptom table |
| clarify 70% stat appears twice | Line 11 and line 176 Anti-Patterns table |
| clarify "even frontier models" time-sensitive | Not present (already says "even frontier models" but doesn't use that phrase — actual text says "even frontier models proceed without clarification") — must check if removal needed |
| clarify adaptive-questioning coupling undocumented | File referenced but relationship to plan pipeline not described; SKILL.md doesn't name its plan-pipeline role |
| code-clarity-and-docs (CHECKER) chain target undefined | Chain row "code-clarity-and-docs (CHECKER)" points to itself with undefined mode |
| code-clarity-and-docs checklists.md status | CF-1..6 and PC-1..4 are "Did I" self-assessed; needs conversion or deletion |
| code-standards two length targets | SKILL.md says "under 300 lines"; section-templates.md line 303 says "150-250 / over 300 is filler" |
| code-standards no base-commit failure path | Missing: "No base-commit header / commit unknown / not a git repo → treat as Generate" |
| code-standards section-templates linked twice | Lines 66 and 115 both link to section-templates.md |
| code-standards no ToC in section-templates.md | File is 303 lines, validator requires ToC for >100-line references |
| performance-optimization PRIORITY ORDER duplicate | Quick Reference at lines 261-281 restates the 7-step decision tree (primary workflow lines 64-92) |
| performance-optimization checklist link wrong path | Line 287: `${CLAUDE_PLUGIN_ROOT}/skills/performance-optimization/checklists.md` should be `${CLAUDE_SKILL_DIR}/checklists.md` |
| performance-optimization Myth/Reality table | Lines 35-42 |
| performance-optimization latency/before-after in SKILL.md | Latency table and 4 before/after examples should be in checklists.md |
| performance-optimization M-2/TP-2 "Did I" items | checklists.md items need to be artifact assertions |

## Code Standards

Key conventions from docs/code-standards.md:
- Braced vars: `${CLAUDE_SKILL_DIR}` inside SKILL.md bodies
- No banned constructs: Myth/Reality tables, self-assessed "Did I" checklists, self-directed STOP sections, scripted pushback, human-time bounds
- Checklist items must be externally checkable assertions about artifacts, phrased so checked = satisfied
- References > 100 lines need a Contents/ToC heading
- One canonical home per fact
- Chain/handoff tables: Read() braced paths only

## Test Infrastructure

No test runner — tests are grep assertions + validate_skill MCP tool + recorded triage table per plan convention.

## Orphan Triage Table

| File | Content Assessment | Disposition | Reason |
|------|--------------------|-------------|--------|
| skills/aposd-designing-deep-modules/checklists.md | ~90% duplicate of SKILL.md; unique item: RF-8 (module absorbs failures silently) | FOLD RF-8 into SKILL.md, then DELETE file | Only unique content is RF-8; rest is "Did I" rewrites of SKILL.md content; folding eliminates the orphan |
| skills/aposd-reviewing-module-design/checklists.md | Contains unique SF-1 item + real checklist items (per-chapter dimension checks) | FOLD SF-1 into SKILL.md; KEEP checklists.md (linked) | The per-chapter itemized checks (CS-1..3, MD-1..4, IH-1..4, LA-1..3, TA-1..4) are genuinely checkable; SF-1 is the only drift item; delete Quick Reference section from checklists.md (duplicate IDs) |
| skills/aposd-simplifying-complexity/checklists.md | Contains real checkable items plus TC-1..3 self-assessed | FOLD RF-7 into SKILL.md; KEEP checklists.md (linked); convert TC-1..3 to artifact assertions or delete | TC-4..8 are outcome checks, keep those; TC-1..3 are "Did I" self-assessed |
| skills/aposd-verifying-correctness/checklists.md | Contains unique EH-5 + full dimension checklists | FOLD EH-5 into SKILL.md; KEEP checklists.md (linked) | The itemized dimension checks (RC-1..4, CS-1..4, EH-1..5, RM-1..5, BC-1..5, SE-1..5, QV-1..6) are checkable artifact assertions |
| skills/gof-design-patterns/references/creational.md | Selection checklist + Creational decision tree + quick reference — the decision tree and quick ref duplicate SKILL.md/techniques.md; selection checklist has 5 "Did I" items | DELETE | Unique: none. The Creational Pattern Decision Tree duplicates techniques.md §2; the quick ref duplicates techniques.md §Creational Pattern Selection; the selection checklist is "Did I" self-assessed (banned) |
| skills/gof-design-patterns/references/structural-behavioral.md | Structural + Behavioral decision trees + quick refs — duplicate techniques.md | DELETE | Unique: none. Both trees and quick refs are duplicated verbatim in techniques.md §3/§4 and §Structural/Behavioral Pattern Selection |
| skills/gof-design-patterns/references/implementation-and-review.md | Implementation checklist + code review checklist + quick decision matrix + relationship guide | DELETE (fold unique items) | Quick Decision Matrix (§3) duplicates techniques.md §6 "Quick Lookup by Problem". Pattern Relationships (§4) duplicates techniques.md §5. Implementation/review checklists are "Did I" self-assessed (banned). No unique load-bearing content survives. |
| skills/code-clarity-and-docs/checklists.md | CF-1..6 "Did I write comment BEFORE" = self-assessed; PC-1..4 also "Did I"; rest are mix | KEEP (linked via ${CLAUDE_SKILL_DIR}/checklists.md); convert CF/PC items | Most of checklists.md (VC, NM, CQ, RF tables) is genuinely checkable artifact review; CF-1..6 and PC-1..4 need conversion to artifact assertions |

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-6.1 | RF-8, SF-1, RF-7, EH-5 present in their respective SKILL.mds (grep each); quick-reference duplicate blocks removed (each fact one encoding per file) | COVERED | grep -n "RF-8\|absorbs failures silently" aposd-designing-deep-modules/SKILL.md → hit; grep -n "SF-1\|Silent Failure\|Silent failure" aposd-reviewing-module-design/SKILL.md → hit; grep -n "RF-7\|masked without observability\|escape hatch" aposd-simplifying-complexity/SKILL.md → hit; grep -n "EH-5\|silently continue" aposd-verifying-correctness/SKILL.md → hit; grep -c "Quick Reference" aposd-verifying-correctness/SKILL.md → 0; Quick Reference block deleted from aposd-simplifying-complexity |
| DW-6.2 | discipline-theater gone: no scripted impatience reply, no Emergency Bypass section, no "Show Your Work" framing, no double withholding gates, no Process-Integrity/TC-1..3 self-checks (grep 'Did I' over scope → nothing in SKILL.mds) | COVERED | grep -rn "impatience\|Emergency Bypass\|Show Your Work\|Process Integrity" skills/aposd-designing-deep-modules/ → nothing; grep -rn "Did I" skills/aposd-*/SKILL.md skills/performance-optimization/SKILL.md → nothing; TC-1..3 converted or removed from checklists.md |
| DW-6.3 | creational.md/structural-behavioral.md/implementation-and-review.md resolved (deleted or linked, recorded); foundations.md trimmed; zero Myth/Reality tables in scope (grep 'Reality' → nothing) | COVERED | ls skills/gof-design-patterns/references/creational.md → file not found; ls structural-behavioral.md → file not found; ls implementation-and-review.md → file not found; grep -rn "Myth\|Reality" skills/gof-design-patterns/references/foundations.md → nothing; grep -rn "Myth\|Reality" skills/performance-optimization/ skills/aposd-reviewing-module-design/ → nothing |
| DW-6.4 | performance-optimization states priority workflow once; latency table + before/after examples live in checklists.md; checklist link uses ${CLAUDE_SKILL_DIR} | COVERED | grep -c "PRIORITY ORDER" performance-optimization/SKILL.md → 0 (Quick Reference block removed); grep -n "Sentinel\|Loop Unswitching\|Strength Reduction\|Page Fault" performance-optimization/SKILL.md → nothing; grep -n "CLAUDE_SKILL_DIR" performance-optimization/SKILL.md → match |
| DW-6.5 | ca polarity uniform (every checklist item checked=satisfied); clarify 70%-stat single-homed (grep -c '70%' clarify/SKILL.md = 1) and adaptive-questioning relationship documented | COVERED | grep -c "70%" skills/clarify/SKILL.md → 1; grep -n "plan pipeline\|plan's clarifier" skills/clarify/SKILL.md → hit; Phase 3 items rephrased to checked=satisfied |
| DW-6.6 | code-standards has one length target (grep for '150-250' → nothing), base-commit failure path present, section-templates.md has a Contents heading | COVERED | grep -n "150-250" skills/code-standards/references/section-templates.md → nothing; grep -n "No base-commit\|commit unknown\|not a git" skills/code-standards/SKILL.md → hit; grep -n "^# " skills/code-standards/references/section-templates.md → ToC heading present |
| DW-6.7 | code-clarity checklists triaged (artifact checks or deleted; linked if kept); "(CHECKER)" chain target defined or removed | COVERED | grep -n "CHECKER" skills/code-clarity-and-docs/SKILL.md → nothing OR defined mode; checklists.md kept and linked via ${CLAUDE_SKILL_DIR}/checklists.md; CF items converted |
| DW-6.8 | zero banned constructs in scope; grep -rn 'Skill(' scope → nothing; all Read() targets exist; validate_skill zero errors on every touched skill | COVERED | grep -rn "Myth\|Reality\|Did I\|impatience\|Emergency Bypass\|Show Your Work" across all touched SKILL.mds → nothing; validate_skill run on all touched skills → zero errors |

**All items COVERED:** YES

## Design Decisions

### aposd-designing-deep-modules
- Delete the "Process Integrity Checks" self-assessment section entirely (SKILL.md lines 103-113): self-assessed compliance items are a banned construct; the Mandatory Output Format (which follows) is the real external check
- Delete scripted impatience reply: one sentence embedded in the deleted section; no replacement needed
- Delete "Emergency Bypass Criteria" section: human ceremony, no place in a skill
- Delete "Time bound" sentence from Design-It-Twice Workflow: human-time bound, banned
- Fold RF-8 from checklists.md into SKILL.md Red Flags table
- Delete checklists.md: after folding RF-8, the remaining content is all "Did I" rewrites of SKILL.md plus duplicates of the Emergency Bypass section — no unique checkable artifact assertions remain
- Chain target "cc-pseudocode-programming": convert to Read() braced path

### aposd-reviewing-module-design
- Fold SF-1 (Silent Failure) into SKILL.md Red Flags Quick Reference table — it's currently only in checklists.md Quick Reference
- Delete the "Common Evaluation Mistakes" table (Myth/Reality pattern is banned; rows like "Length ≠ complexity" and "Deep > small" are already captured in the Depth vs Length Rule table — no novel facts)
- Delete the Quick Reference block (lines 198-219): duplicates the five evaluation checklist headings verbatim; the checklist sections carry the content
- In checklists.md: delete the "Quick Reference: Red Flags" section (lines 54-66): duplicate IDs (IH-1/IH-2, LA-1, TA-1..4 reused); after SF-1 is folded, the checklist already has those items in their per-chapter homes
- Chain: add mutual handoff note to aposd-simplifying (assessment vs transformation)

### aposd-simplifying-complexity
- Fold RF-7 (error masked without observability) from checklists.md into SKILL.md Red Flags table
- Keep ONE presentation gate: the technique-analysis output table (lines 148-157) is the evidence requirement; delete the top-of-file STOP "Do NOT present" sentence (line 15) — it's a duplicate that runs before the table appears; keep the Transformation Checklist gate (line 163) which is the operative single gate
- Delete "Mandatory Output: Show Your Work" header + "This prevents claiming hierarchy application without evidence." rationale sentence — the table stands on its own as an evidence format
- Delete Quick Reference block (lines 203-221): 3rd encoding of the error hierarchy; table + decision procedure carry it
- In checklists.md: convert TC-1..3 "Did I" → delete (TC-1: walked through hierarchy = artifact: technique-analysis table exists; TC-2: documented why rejected = artifact: Gate Check column shows FAIL where rejected; TC-3: verified validation gates = artifact: Gate Check column)
- Chain: name the target: "Verify interface simplified" → `Read(${CLAUDE_PLUGIN_ROOT}/skills/aposd-verifying-correctness/SKILL.md)`
- Add escape-hatch note for legitimately unsatisfied checklist items

### aposd-verifying-correctness
- Fold EH-5 (silent error-path continuation) into SKILL.md Error Handling section
- Delete Quick Checklist table (lines 133-145): the Output Format is the gate artifact; the table just repeats detection triggers already in the per-dimension sections
- In checklists.md: the QV-1..6 "Quick Verification Summary" section is also a duplicate — delete it (per-dimension checklists RC/CS/EH/RM/BC/SE already cover the same)
- The per-dimension "Red flag:" rationalization quotes in SKILL.md (6 lines): these are unique detect criteria not in checklists.md — keep them but unify: move them into the verify list as "detect:" markers rather than inline red flag quotes

### ca-architecture-boundaries
- Phase 3 items: rephrase to checked=satisfied polarity: "SRP: Classes serving multiple actors?" → "SRP: Each class responsible to exactly one actor?"; "OCP: Simple extensions require modifying existing code?" → "OCP: Simple extensions do NOT require modifying existing code?"; "DIP: Business logic importing concrete infrastructure?" → "DIP: Business logic imports only abstractions (no concrete infrastructure)?"
- Remove duplicate SRP question: Phase 1 "Map actors (who requests changes?) → find SRP violations" is the discovery step; Phase 3 "SRP: Classes serving multiple actors?" is the verify step — these serve different purposes, so keep both but scope them clearly; the plan says "merge" so keep only the verify form in Phase 3 and drop the SRP-violation call-out from Phase 1's map-actors item
- Scope the grep block: add "Adapt paths to your project" comment and scope instanceof/typeof grep to domain dirs: `src/domain/` or equivalent

### gof-design-patterns
- DELETE creational.md, structural-behavioral.md, implementation-and-review.md (orphan triage above)
- foundations.md: trim to operative rules — delete the Myth/Reality table (lines 170-180) and educational history prose (What Design Patterns ARE/ARE NOT, Gang of Four history, Pattern Classification, When to Use, Common Misconceptions sections); keep Key Principles section (program-to-interface, composition-over-inheritance, encapsulate-what-varies, loose-coupling) and the 3 operative principles
- techniques.md: Section 7 "By Symptom" (lines 163-179) is near-verbatim duplicate of SKILL.md's Pick by Symptom table — SKILL.md is canonical, delete Section 7 from techniques.md

### clarify
- Single-home the 70% statistic: it appears in line 11 (intro) and line 176 (Anti-Patterns table). The table row uses it as a label "70% default execution bias" — this is the reference location. Remove it from the intro sentence, using "models overwhelmingly proceed without asking" instead
- Document the adaptive-questioning.md shared-reference relationship: add a one-line note near the existing link noting it is shared with the plan pipeline
- Name clarify's role: in the intro paragraph, add that this skill serves as the plan pipeline's clarifier

### code-clarity-and-docs
- checklists.md: CF-1..6 are "Did I write comment BEFORE" — these are process-compliance, not artifact checks. Convert to artifact assertions: "Every new class/method in the diff has an interface comment" and similar. PC-1..4 same pattern — convert PC-1 "Did I update comments for changed code?" → "All changed code has current comments". Link via `${CLAUDE_SKILL_DIR}/checklists.md`
- Chain "(CHECKER)": remove the mode tag, just say `code-clarity-and-docs`. The skill is already pointing back at itself for audit use; the "(CHECKER)" tag is undefined. Simpler: the audit use-case is described in the SKILL.md body via the Red Flags and checklists sections. Drop the chain row "code-clarity-and-docs (CHECKER)" entirely or replace with "Done (pre-commit gate)" — the second row already says that. Remove the redundant first chain row.
- AI config table: compress from 10-tool inventory to "any AI config files present (CLAUDE.md, AGENTS.md, editor rule files)"

### code-standards
- section-templates.md line 303: "Aim for 150-250 lines total. Over 300 means you're including filler." → "Aim for under 300 lines. Trim filler aggressively."
- SKILL.md: add base-commit failure path to the Decide step: if no `<!-- base-commit: ... -->` header, or if the commit sha is unknown / repo is not git, treat as Generate
- section-templates.md: add Contents heading at top
- Remove duplicate section-templates.md link: keep the link in the Write step (line 66), remove from the Sections summary (line 115 — just say "See the templates file" without the full braced path)

### performance-optimization
- Delete the Quick Reference block (lines 261-281): PRIORITY ORDER summary duplicates the 7-step decision tree
- Move latency table (lines 46-55) and 4 before/after code examples (Sentinel/Loop Unswitching/Strength Reduction/Page Fault) to checklists.md
- Delete Myth/Reality table (lines 34-42): replace with 2 declarative sentences
- checklists.md M-2/TP-2: convert from "Did I" to artifact assertions
- checklists.md: add an "After Making Changes" section (currently in SKILL.md lines 236-243) and point SKILL.md there
- Fix checklist link: `${CLAUDE_PLUGIN_ROOT}/skills/performance-optimization/checklists.md` → `${CLAUDE_SKILL_DIR}/checklists.md`

## Prerequisites
- [x] Required files exist (all listed files confirmed present)
- [x] Dependencies available (validate_skill MCP tool available)
- [x] Phase 3 complete (adaptive-questioning.md stays at plugin root — confirmed)
- [x] Phase 4 complete (all frontmatter flags already set — do NOT touch)

## Recommendation
BUILD

All 22+ files exist, all prerequisites met, all DW items have clear test cases, no blockers.
