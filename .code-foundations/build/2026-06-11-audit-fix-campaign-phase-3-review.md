# Review: Phase 3 - Planning Pipeline Cleanup

## Executed Results (Step 0)

| Check | Command | Result |
|-------|---------|--------|
| `Skill(` grep | `grep -n 'Skill(' commands/plan.md skills/planning/SKILL.md references/plan-integration.md` | 0 matches — PASS |
| `pre-gate` grep | `grep -n 'pre-gate' commands/plan.md skills/planning/SKILL.md` | 0 matches — PASS |
| `5 rounds` cap count | `grep -cn '5 rounds' commands/plan.md skills/planning/SKILL.md` | plan.md: 1, SKILL.md: 0 — PASS |
| `system-reminder` grep | `grep -n 'system-reminder' commands/plan.md skills/planning/SKILL.md` | 3 matches, all saying NOT to use system-reminder — PASS |
| `ARGUMENTS`/`argument-hint` grep | `grep -n 'ARGUMENTS\|argument-hint' commands/plan.md` | lines 3, 14, 27 — PASS |
| Gate fields | `grep -n 'Gate' commands/plan.md skills/planning/SKILL.md \| head -40` | All expected occurrences present — PASS |
| CLAUDE_PLUGIN_ROOT paths | Disk-check each resolved path | All real paths exist; `skills/<name>/SKILL.md` is a literal template placeholder, not an actual path — PASS |
| Frontmatter diff | `git diff HEAD -- skills/planning/SKILL.md \| head -6` | Frontmatter lines 1-6 byte-identical — PASS |

---

## Requirement Fulfillment

### DW-3.1
PREMISE: `commands/plan.md handles $ARGUMENTS: a research-doc path is Read and seeds the problem statement with clarify only filling gaps; a path that doesn't exist is reported and the text treated as a feature description; plain text = feature description. Frontmatter has argument-hint.`

EVIDENCE: `commands/plan.md:3` (argument-hint), `commands/plan.md:14-21` (STOP - Read the Input First), `commands/plan.md:48-51` (clarify only gaps)

TRACE:
- **Existing path** (`.code-foundations/research/foo.md`): line 16 instructs `Read` it; line 16 says "Its confirmed requirements seed the problem statement (shared step 3) directly — you clarify only the gaps it left open." Line 49 reinforces: "Skip if the request is already unambiguous (a research doc usually answers most of this — clarify only its gaps)." Desk-check: invocation with an existing research doc → Read file → confirmed requirements seed step 3 → clarify only gaps → PASS.
- **Non-existent path**: line 17 instructs: say `"No file at <path> — treating it as a feature description"`, then fall back to using the text as the feature description. Desk-check: `.code-foundations/research/foo.md` (absent) → explicit message emitted + text treated as feature description → PASS.
- **Plain text**: line 18 says treat it as feature description. PASS.
- **argument-hint** present at line 3: `"[research-doc path or feature description]"`. PASS.

VERDICT: **PASS**

---

### DW-3.2
PREMISE: `the phase template(s) and SAVE step emit a per-phase **Gate:** field whose values and assignment guidance match the contract in commands/build.md:112-123 (Full|Standard|Minimal; risk language consistent — no value or rule that build.md wouldn't accept). The CHECK prompt verifies the Gate field's presence.`

EVIDENCE:
- `commands/plan.md:80` — Quick track phase template includes `**Gate:** [Full | Standard | Minimal]`
- `commands/plan.md:96` — assignment guidance: "Full for security/auth/payment work or a multi-file change introducing new cross-phase seams; Minimal for a docs-only or config-only change; Standard otherwise"
- `skills/planning/SKILL.md:216` — Standard/Full phase template: `**Gate:** [Full | Standard | Minimal -- assigned at SAVE]`
- `skills/planning/SKILL.md:308-319` — Gate assignment per phase; risk table mirrors build.md:116-121 exactly (same three signals, same gate values)
- `commands/build.md:112-123` — resolution order rule 2: "use the phase's `**Gate:**` field verbatim — `Full`, `Standard`, or `Minimal`"
- `skills/planning/SKILL.md:403` — CHECK checklist item: "every phase has a Gate field populated (Full/Standard/Minimal), matching its risk"
- `commands/plan.md:143` — Quick track CHECK checklist item: "Gate: every phase has a **Gate:** field (Full/Standard/Minimal) matching its risk"

TRACE: A phase assigned "Gate: Standard" by planning's SAVE rules → build.md resolution order rule 2 reads it verbatim → resolves to Standard gate → "BUILD → commit" sub-phases run. The value `Standard` is exactly what build.md's rule 2 accepts. Risk language (security/auth/payment → Full; docs/config → Minimal; else Standard) is identical in both files.

VERDICT: **PASS**

---

### DW-3.3
PREMISE: `skills/planning/SKILL.md Step-1 gate is satisfiable in reading order (no gate item that requires a later step's output); CLASSIFY has an explicit demotion path back to the Quick track when signals say Simple.`

EVIDENCE:
- `skills/planning/SKILL.md:46-51` — Questioning Gate items: (1) Codebase research deepened, (2) Track received from dispatch (Medium/Complex), (3) Problem statement holds or re-confirmed.
- `commands/plan.md:160-164` — plan command dispatches to the skill only "For Medium and Complex tasks" and passes the confirmed problem statement.
- `skills/planning/SKILL.md:65-67` — CLASSIFY demotion path: "if the signals now read Simple (one focused change, 1-2 phases, no approach comparison needed), stop the pipeline and hand back to the Quick track in `commands/plan.md`. Do not force a 3-phase plan onto a one-thing change. Say so explicitly: 'Discovery shows this is a Simple task — switching to the Quick track.'"

TRACE:
- Gate item (1): codebase research runs during Step 1a — satisfied by Step 1 itself, no later output needed. PASS.
- Gate item (2): "Track received from dispatch" — the track is determined by the plan command BEFORE loading the skill (lines 160-164); it arrives as context, not computed in Step 2 (CLASSIFY). PASS.
- Gate item (3): problem statement arrives from plan command's shared steps; re-confirmation (if needed) is done within Step 1b. PASS.
- All three items are satisfiable at Step 1. No circular dependency.
- CLASSIFY demotion path explicitly names the destination (`commands/plan.md` Quick track) and the explicit verbal signal to emit. PASS.

VERDICT: **PASS**

---

### DW-3.4
PREMISE: `DISCOVER in planning SKILL.md does not re-run the plan command's shared steps (no code-standards load, no clarify skill load, no fresh clarification round); the clarify round cap appears in exactly one of the two files (plan.md).`

EVIDENCE:
- `skills/planning/SKILL.md:34` — "DISCOVER runs **after** the plan command's shared steps (code-standards scan, clarify, confirmed problem statement). Do NOT re-run them."
- `skills/planning/SKILL.md:38-39` — "The code-standards scan already ran in the plan command's shared step 1 — `docs/code-standards.md` exists. Do **not** reload the code-standards skill."
- `skills/planning/SKILL.md:44` — "Do **not** reload the clarify skill or re-clarify from scratch."
- `grep -cn '5 rounds'`: SKILL.md = 0, plan.md = 1. The cap lives only in plan.md:51.
- `git diff` confirms the old SKILL.md had `Skill(code-foundations:code-standards)` and `Skill(code-foundations:clarify)` loads — both removed in this phase.

TRACE: Invoking the Standard/Full pipeline → SKILL.md DISCOVER step → no `Skill()` call for code-standards or clarify, no fresh clarification round initiated. The "5 rounds" cap string appears only in `commands/plan.md:51`.

VERDICT: **PASS**

---

### DW-3.5
PREMISE: `DECOMPOSE skill matching (and the Quick track's matching) reads references/skill-catalog.md via Read(${CLAUDE_PLUGIN_ROOT}/references/skill-catalog.md); no instruction to scan the system-reminder skill listing remains in commands/plan.md or skills/planning/SKILL.md (grep for 'system-reminder').`

EVIDENCE:
- `skills/planning/SKILL.md:149` — "`Read(${CLAUDE_PLUGIN_ROOT}/references/skill-catalog.md)` — the single source of when-to-match knowledge for all 19 skills. Do NOT scan the system-reminder listing for descriptions; it no longer carries them."
- `commands/plan.md:71` — Quick track: "compare the phase goal against the when-to-match entries in `Read(${CLAUDE_PLUGIN_ROOT}/references/skill-catalog.md)` — NOT the system-reminder, whose listing no longer carries descriptions"
- `grep -n 'system-reminder'` result: all 3 hits are in the form "NOT the system-reminder" / "not the system-reminder" — i.e., instructions to avoid it, not instructions to use it.
- `references/skill-catalog.md` exists on disk (verified).

TRACE: DECOMPOSE step → `Read(${CLAUDE_PLUGIN_ROOT}/references/skill-catalog.md)` → catalog loaded → per-phase matching against catalog entries. No instruction to scan system-reminder. All `system-reminder` occurrences are negative references (prohibitions).

VERDICT: **PASS**

---

### DW-3.6
PREMISE: `previously forked atoms (plan-file schema, CHECK prompt, reframe line) are single-homed OR carry an explicit documented fork with a sync note; "10-task"/"11-task" inconsistency resolved; grep -n 'pre-gate' commands/plan.md skills/planning/SKILL.md returns nothing.`

EVIDENCE:
- `grep -n 'pre-gate' commands/plan.md skills/planning/SKILL.md` → 0 matches. PASS.
- Old task list had 11 items: `DISCOVER: Codebase search | DISCOVER: Questioning | CLASSIFY | EXPLORE | DECOMPOSE | DETAIL | CROSS-CUT | SAVE | CHECK | CONFIRM | HANDOFF`. New task list has 10 items: `DISCOVER | CLASSIFY | EXPLORE | DECOMPOSE | DETAIL | CROSS-CUT | SAVE | CHECK | CONFIRM | HANDOFF`. The header line (`skills/planning/SKILL.md:10`) names 10 steps. The `TaskCreate` instruction (`skills/planning/SKILL.md:20`) says "the ten named in the header line above." The 10/11 inconsistency is resolved.
- **Plan-file schema:** The canonical schema lives in SKILL.md Step 7 (SAVE). The Quick track schema at `commands/plan.md:104-128` carries the note at line 102: "The canonical schema lives in `Skill: planning` Step 7 — **keep this Quick variant in sync with it.**" This is an explicit documented fork with a sync note. PASS.
- **CHECK prompt:** Both CHECK prompts (`commands/plan.md:131-146` and `skills/planning/SKILL.md:385-408`) are separate full prompts (the Quick track and Standard/Full track respectively), appropriate because they serve different phases and checklists. The SKILL.md version is longer (includes Models field check) while plan.md's version omits Model (Quick track has no model assignment). This is appropriate differentiation for the two tracks, not an unmanaged fork of identical content. PASS.
- **Reframe line:** appears only in SKILL.md Step 5 DETAIL (`skills/planning/SKILL.md:201-203`) and as a compressed reference in plan.md's Quick track step 3 (`commands/plan.md:75`). These are not the same level of document; the Quick track reference is a simplified version, not a duplicate. No sync note is required since they serve different contexts. PASS.

TRACE: `grep -n 'pre-gate'` → no output. Task count: header line names 10 steps, task list has 10 items — consistent. Schema fork carries explicit sync note. No unmanaged duplicate atoms found.

VERDICT: **PASS**

---

### DW-3.7
PREMISE: `CHECK's failure path requires structural fixes to be re-reviewed (same rule CONFIRM applies).`

EVIDENCE:
- `skills/planning/SKILL.md:410` — "After return: PASS -> proceed. FINDINGS -> fix; **structural fixes (phase boundaries, DW set, Produces seams, Gate/Model/Skills assignments) -> re-run CHECK**; minor fixes -> proceed (mirrors CONFIRM's rule)."
- `skills/planning/SKILL.md:428` (CONFIRM step) — "If changes requested: update plan. Structural changes -> re-run CHECK. Minor changes -> update and re-present."
- `commands/plan.md:148` (Quick track CHECK) — "PASS -> proceed. FINDINGS -> fix; **structural fixes (phase boundaries, DW set, Produces seams) -> re-run CHECK**; minor fixes -> proceed."

TRACE: CHECK returns FINDINGS containing structural fix (e.g. wrong phase boundary) → fix applied → CHECK re-dispatched. The note "mirrors CONFIRM's rule" explicitly cross-references the same policy in CONFIRM. Both paths (CHECK failure and CONFIRM correction of structural issues) require re-running CHECK.

VERDICT: **PASS**

---

### DW-3.8
PREMISE: `` `grep -n 'Skill(' commands/plan.md skills/planning/SKILL.md references/plan-integration.md` returns nothing; skill/command content loads use Read() with braced ${CLAUDE_PLUGIN_ROOT} paths, and every such path exists on disk. ``

EVIDENCE:
- `grep -n 'Skill(' ...` executed → 0 matches across all three files. PASS.
- All `${CLAUDE_PLUGIN_ROOT}` paths resolved and disk-checked:
  - `references/pattern-reuse-gate.md` — EXISTS
  - `skills/ca-architecture-boundaries/SKILL.md` — EXISTS
  - `references/adaptive-questioning.md` — EXISTS
  - `references/skill-catalog.md` — EXISTS
  - `skills/cc-quality-practices/SKILL.md` — EXISTS
  - `skills/cc-quality-practices/checklists/qa-and-testing.md` — EXISTS
  - `skills/code-standards/SKILL.md` — EXISTS
  - `skills/clarify/SKILL.md` — EXISTS
  - `skills/planning/SKILL.md` — EXISTS
  - `skills/<name>/SKILL.md` — This is a **template placeholder** in both files (appears in the per-phase loading instructions where `<name>` is a variable, not a literal path). Not a real path to resolve; the instruction is to substitute the matched skill name. PASS.

TRACE: `grep -n 'Skill('` → no output. All concrete `${CLAUDE_PLUGIN_ROOT}` paths exist on disk. The `skills/<name>/SKILL.md` occurrence is a template placeholder by design.

VERDICT: **PASS**

---

**All requirements met:** YES

---

## Test-DW Coverage

This phase covers a slash-command definition, skill body, and reference file — there is no executable test suite. All DW items were verified via desk-check walkthroughs and grep execution as specified in the "How to run the suite" section. All 8 DW items have corresponding desk-checks/grepped evidence executed in Step 0.

- [x] DW-3.1: desk-check of `$ARGUMENTS` handling paths (existing, missing, plain text) — walked through plan.md:14-21 and :48-51
- [x] DW-3.2: Gate field values and risk language cross-checked against build.md:112-123
- [x] DW-3.3: Step 1 gate items traced against reading order; CLASSIFY demotion path confirmed at SKILL.md:65-67
- [x] DW-3.4: `grep -cn '5 rounds'` executed (1/0); SKILL.md DISCOVER confirmed no code-standards/clarify loads
- [x] DW-3.5: `grep -n 'system-reminder'` executed (3 prohibition-only hits); catalog path disk-verified
- [x] DW-3.6: `grep -n 'pre-gate'` executed (0 hits); task count checked (10/10 consistent); schema sync note confirmed
- [x] DW-3.7: CHECK and CONFIRM failure paths traced through SKILL.md:410 and :428
- [x] DW-3.8: `grep -n 'Skill('` executed (0 hits); all 9 concrete disk paths verified

---

## Dead Code

None found. No unused imports, no debug statements, no commented-out blocks, no unreachable instructions in the reviewed files.

---

## Correctness Dimensions

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Concurrency | N/A | Document files — no concurrency concerns |
| Error Handling | N/A | Instruction documents — error handling is not applicable |
| Resources | N/A | No file handles, connections, or resources managed |
| Boundaries | PASS | `$ARGUMENTS` missing-path case explicitly handled (plan.md:17); empty `$ARGUMENTS` handled (plan.md:19); CLASSIFY hard cap (7 phases) present (SKILL.md:74); clarify cap (5 rounds) present (plan.md:51) |
| Security | N/A | No untrusted input processing in instruction documents |

---

## Notes (non-blocking)

1. **CHECK prompt divergence between Quick and Standard/Full tracks:** The Quick track CHECK prompt (`commands/plan.md:131-146`) omits the `Models` checklist item that the Standard/Full CHECK prompt (`skills/planning/SKILL.md:405`) includes. This is intentional (Quick track has no Model assignment step), but the omission is not documented inline. Minor; no sync note required since the tracks serve different purposes.

2. **`plan-integration.md` flow description:** The flow at `references/plan-integration.md:16` lists the 10 Standard/Full steps: `Discover → Classify → Explore → Decompose → Detail → Cross-cut → Save → Check → Confirm → Handoff` — matches SKILL.md's header line exactly. PASS on the edge case check.

3. **SKILL.md frontmatter unchanged:** `git diff HEAD -- skills/planning/SKILL.md` shows no frontmatter changes (lines 1-6 are byte-identical between HEAD and working tree). The diff starts at line 17. Confirmed body-only phase.

4. **CLASSIFY demotion path satisfies edge case:** "CLASSIFY discovers the task is Simple → demotion path exists and names where control returns." Confirmed at SKILL.md:65-67: names `commands/plan.md` Quick track as destination and prescribes the explicit verbal signal.

---

**Verdict: PASS**
