# Discovery + Design: Phase 2 - Debug + review tasks

## Files Found
- `benchmarks/model-tiers/SCHEMA.md` — the pinned Phase-1 manifest contract (read first, per phase Produces). Defines task layout (`spec.md`, `starter/`, `hidden/`, `gold/`, `manifest.json`), the outputs→hidden merge execution contract, `test_dw_*`/`test_offdw_*` naming, and rung-3/4 `report_file`/`answer_key` fields.
- `benchmarks/model-tiers/tasks/{01-heartbeat-message,02-cas-refcount-quota,02-cas-bounded-concurrency}/` — Phase-1 exemplars (layout, manifest shape, flat-module starters, `install: "true"` offline convention).
- `references/dispatch-templates.md` § REVIEW — the exact REVIEW dispatch the rung-4 specs must mirror: independent-critic preamble ("You did not write this code…"), per-DW `PREMISE/EVIDENCE/TRACE/VERDICT` template, edge-cases block, "How to run the suite / Run these directly via Bash", zero intent-framing (no plan Context, no Progress, no discovery).
- `.code-foundations/build/2026-07-03-model-tier-benchmark-phase-1-discovery.md` — Phase-1 screening table (theGrid rejected as non-portable Swift/macOS; upublish-family accepted) and validation-evidence conventions this file follows.
- Grug memos (read via grug MCP): `thegrid/stale-write-first-apply-regression-md.md`, `upublish/spa-routing-fallback-gap.md`, `upublish/root-apex-deep-path-fallback-not-cas-aware.md`, `upublish/settings-storage-meter-double-counts-cas-archived-versions.md`.
- Real corpus sources read for faithful reconstruction:
  - `~/repos/upublish-backend` — plan `2026-05-20-kv-key-format-fix.md` (Status: complete) + fix commit `1ddc131` and its parent (buggy `site:${nsId}:${slug}` constructions in namespace-sites.ts/billing.ts/space.ts; worker reads `site:${nsName}:${slug}`).
  - `~/repos/upublish-backend` — buggy stats queries at `f4a7f67^` (`listRootNamespacesWithStats`/`listNamespacesForUser` add an archived `site_versions` subquery with no dedup awareness) and the correct gate `sumUniqueStorageForSpace`; fix commit `f4a7f67`.
  - `~/repos/meeseeks` — plan `2026-06-28-meeseeks-cron-loop-manager.md` Phase 1 + committed `src/core/{types,ports,loop}.ts` and `test/core/loop.test.ts`.
  - `~/repos/upublish.skill` — plan `2026-06-20-cross-client-publish-progress-timeouts.md` Phase 2 + committed `lib/publish.ts` hashing region (`listFiles`, `hashFiles`, `hashFileChunkedYielding`, `collectFilesWithHashes`, exclusion helpers).

## Current State
`tasks/` holds only the three Phase-1 build-rung tasks. No `03-*`/`04-*` dirs exist. bun 1.3.14 on PATH; all Phase-1 tasks run offline with `install: "true"`.

## Gaps
1. **DW-2.1 requires the failing repro command "recorded in manifest", but SCHEMA.md's pinned manifest has no repro field.** Resolution: add an additive, rung-3-only `toolchain.repro` field (shell command expected to exit non-zero on the clean starter). This is plan-mandated (DW-2.1), additive (no pinned field changes), and invisible to rungs 1-2. SCHEMA.md itself is Phase-1 file scope (`benchmarks/model-tiers/SCHEMA.md`), outside this phase's `tasks/03-*, 04-*` scope — the one-line doc amendment is flagged in this build's output for the orchestrator rather than edited here.
2. **Rung-4 tasks need a runnable `toolchain.test_hidden` (required manifest field) although their real grading is the Phase-3 judge fact-match.** Resolution: each rung-4 hidden suite is a machine-checkable report gate — asserts `outputs/report.md` exists (post-merge sibling), is non-empty, carries an explicit overall PASS/FAIL verdict and one verdict per DW item. Judge grading stays Phase 3; this keeps the manifest contract uniform.
3. **meeseeks DW-1.1 says "compile under `tsc --strict`"** — tsc is not runnable offline in a bare fixture (no committed node_modules; hidden suites must run offline). Fixture reduction (recorded): the task's DW-1.1 is restated as "strict-clean with no `any` anywhere in the core modules" — the half of the DW that is verifiable from artifacts alone and the half the planted violation targets. Scope-preserving reduction, same precedent as Phase 1's heartbeat extraction.

## Code Standards
`docs/code-standards.md` Part 2 (Benchmark harnesses) applied: task dirs `NN-slug`; spec.md never hints at hidden contents or gold; `hidden/` never shown to the agent; `test_dw_*`/`test_offdw_*` naming with dirty tests per DW; validation commands recorded verbatim in this file before being treated as evidence (pre-registration). Python harness conventions do not apply — these are TS/bun-native task fixtures (Part 2's own carve-out, per Phase-1 discovery).

## Test Infrastructure
- `bun test` (bun 1.3.14) for all four tasks — subject-language-native, offline, self-contained flat modules (rung 3) / src-test layout (rung 4, legal because rung-4 outputs is only `report.md`, so the outputs→hidden flat merge never has to resolve module siblings).
- Rung-3 hidden dirs pre-seed a copy of every starter module (SCHEMA.md execution contract: outputs overwrite "any starter copy of the same filename"), so a fix touching a subset of files still runs the full hidden suite.

## Assumption Verification (from dispatch)

Assumption: "Selected corpus phases / documented bugs port into isolated workspaces" (Medium).

| Candidate | Verdict | Evidence |
|---|---|---|
| theGrid stale-write cascade (rung 3, plan-named) | **SWAPPED OUT** | Swift/macOS (`GridApply.applyLayoutBody`, `getSpaceReadOnly` over live window-server state). Phase 1 already rejected theGrid as non-portable; the dispatch's approach notes pre-authorize this exact swap. Reconstructing Swift logic in TS would be an invented task, which the plan forbids ("corpus is the population"). |
| upublish storage-meter double-count (grug-listed fallback) | **SWAPPED IN** (as `03-storage-meter-dedup`) | Real TS + bun:sqlite (`listNamespacesForUser`/`listRootNamespacesWithStats` at `f4a7f67^`), pure SQL over an in-memory DB — deterministic by construction (STABILIZE: no timing, no I/O races). Fix commit `f4a7f67` gives a faithful gold. |
| upublish KV key format (rung 3, plan-named) | **PORTS** (as `03-kv-key-mismatch`) | Real plan `2026-05-20-kv-key-format-fix.md` + fix commit `1ddc131`. Server-write/worker-read key mismatch reconstructs over an in-memory KV — deterministic. The real-world constraint that forces the server-side fix (worker only knows the namespace *name* from the hostname) is preserved by the worker module's signature. |
| meeseeks Phase 1 core (rung 4) | **PORTS** (as `04-loop-core-review`) | 524 lines of pure TS (`src/core/`), zero infra imports, real committed tests. Phase-1 screening already called it portable. |
| upublish.skill hash-progress Phase 2 (rung 4) | **PORTS** (as `04-hash-progress-review`) | `lib/publish.ts` hashing region is node:fs/crypto only; tests run against temp dirs. HIGH-difficulty real phase with 6 crisp DW items. |

Both rungs keep ≥2 tasks → no UPDATE_PLAN needed.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-2.1 | Both rung-3 tasks: failing repro command recorded in manifest and reproduces 5/5 times on clean starter | COVERED | `toolchain.repro` in both 03-* manifests; T-2.1 loop: 5× run of the repro command on a clean starter copy per task, all 5 exiting non-zero, outputs recorded below |
| DW-2.2 | Both rung-4 tasks: ≥3 planted violations each, with location, severity, 5-point anchors in answer-key.json | COVERED | T-2.4 programmatic check on both 04-* `answer-key.json`: `defects.length ≥ 3` and every defect has `id, kind, location, severity, anchors[5], detectable_via` |
| DW-2.3 | Every planted violation has recorded evidence it is detectable from task artifacts alone | COVERED | T-2.3: `detection-evidence.md` per task — per defect: the artifact trail (spec DW text + file:line) plus a witness command run at authoring time with its output |
| DW-2.4 | Self-verifiable gold validation: rung-3 gold fixes pass hidden suites from clean starters (outputs recorded); rung-4 gold findings enumerate every answer-key defect 1:1 by inspection | COVERED | T-2.2 per rung-3 task: copy gold over clean starter → `toolchain.test_hidden` green (also recorded: pristine starter FAILS the hidden suite — the bug-detection proof); rung-4: gold/report.md ↔ answer-key mapping table below |
| DW-2.5 | Both rung-4 specs mirror build's REVIEW dispatch (suite-first, per-DW verdict + evidence, PASS/FAIL) with zero plan/intent context | COVERED | T-2.5 grep assertions on both 04-*/spec.md: required strings present (`You did not write this code`, `PREMISE`, `EVIDENCE`, `TRACE`, `VERDICT`, `PASS`, `FAIL`, suite-first instruction); forbidden strings absent (`Plan Context`, `Progress`, `Goal:`, `Completed`, `discovery`) |

**All items COVERED:** YES

## Design Decisions

**Task roster (4 tasks):**

| Task | Rung | Source (repo / plan / phase) | Shape |
|---|---|---|---|
| `03-kv-key-mismatch` | 3 | upublish-backend / `2026-05-20-kv-key-format-fix.md` / Phase 1: Server — standardize KV key writes | Server writes KV under `site:{nsId}:{slug}`, worker reads `site:{nsName}:{slug}` → every published site's metadata unreachable except `_root` (dual-write workaround). Multi-file fix (namespace-sites, billing, space). |
| `03-storage-meter-dedup` | 3 | upublish-backend code / cross-repo plan `../upublish/.code-foundations/plans/2026-06-22-storage-meter-dedup-fix.md` / Phase 1 (backend stats dedup) | Stats queries add archived `site_versions` bytes with no dedup awareness → settings meter ~2x real usage, false "over cap", while the publish gate (`sumUniqueStorageForSpace`) is correct. |
| `04-loop-core-review` | 4 | meeseeks / `2026-06-28-meeseeks-cron-loop-manager.md` / Phase 1: Core domain + ports | Real core (`types/ports/loop`) with 5 planted violations; visible suite green. |
| `04-hash-progress-review` | 4 | upublish.skill / `2026-06-20-cross-client-publish-progress-timeouts.md` / Phase 2: Hashing instrumentation (lib core) | Real hashing module with 4 planted violations; visible suite green. |

**Rung-3 layout:** flat starter modules (merge-contract-friendly); `starter/` includes the *visible* legacy tests that miss the bug in exactly the documented real-world way (kv: unit tests assert each side's own key format, no cross-boundary roundtrip; meter: stats tests seed prefix-era fixtures where live+archived genuinely is correct) plus `repro.test.ts`, the failing end-to-end repro. `hidden/` = copy of every starter module + `hidden.test.ts` (fix regression + preserved behavior + dirty edges). `answer-key.json` = `{defects:[{id, kind:"root-cause", location, severity, anchors[5], detectable_via}], allowed_change_scope:[...]}` — `allowed_change_scope` feeds Phase 4's diff-scope check so a rewrite-everything "fix" fails (phase edge case).

**Rung-3 fix-direction forcing:** hidden tests call the worker/gate read paths by their real contracts (worker gets only the namespace *name*; gate function signature pinned), so only the historically-correct fix direction passes — mirroring why the real fixes went server-side / stats-side.

**Rung-4 spec = REVIEW dispatch:** each `spec.md` is a verbatim-shaped § REVIEW prompt: independent-critic preamble, suite-first first action, the source phase's ACTUAL DW items (fixture-path-adapted only) each with `PREMISE/EVIDENCE/TRACE/VERDICT` slots, the phase's edge cases block (requirements, not intent), files list, exact suite command, and "write review to outputs/report.md with per-DW verdicts + overall PASS/FAIL". No plan Context/Progress/Goal/discovery anywhere.

**Rung-4 planted violations** (stratified across files and kinds per SWR-Bench; reviewer sees a full workspace, never a diff; each violation's would-catch visible test is weakened in a realistic way — incomplete grep lists, dropped assertions — so the suite is green):

*04-loop-core-review (5):*
| ID | Kind | Plant |
|---|---|---|
| LC-1 | dw-unmet (DW-1.3) | `resolveStop` applies the default iteration cap only when NO other condition is set: `cfg.maxIterations ?? ((cfg.maxTokens ?? cfg.predicate) ? MAX_SAFE_INTEGER : DEFAULT)` — a predicate-only loop is unbounded; visible `predicate_only_still_bounded` test removed |
| LC-2 | hidden-defect | `applyEvent` usage fold drops `inputTokens` — budget undercount, max-tokens trips late; visible usage test asserts with `inputTokens: 0` |
| LC-3 | dw-unmet (DW-1.2) | predicate trip guard dropped (`state.predicateTripped` without `cfg.predicate !== undefined`) — a stale flag stops a loop that configured no predicate; visible ignored-when-not-configured test removed |
| LC-4 | dw-unmet (DW-1.4) | `ports.ts` type-imports `Database` from `bun:sqlite` (a "row-type convenience") — infra import in core; visible boundaries test greps an incomplete list that omits `bun:` |
| LC-5 | dw-unmet (DW-1.1) | `RunEvent` `tool_use.input?: any` (was `unknown`) — strict-clean-no-`any` violated; nothing greps for `any` |

*04-hash-progress-review (4):*
| ID | Kind | Plant |
|---|---|---|
| HP-1 | dw-unmet (DW-2.3) | Opening `{completed: 0, …}` report removed — first report fires after file 1; visible tests assert monotonicity + final totals only |
| HP-2 | dw-unmet (DW-2.4) | `yieldToEventLoop` = `Promise.resolve()` (microtask) while its doc comment still claims a macrotask — the loop is never actually released; visible test only awaits resolution |
| HP-3 | hidden-defect | `completedBytes += entry.size` (statSync estimate) instead of the hashed byte count — violates the authoritative-bytes contract (TOCTOU); invisible to tests whose files never change mid-run |
| HP-4 | dw-unmet (DW-2.2) | `matchesIgnore` drops the `dir/` trailing-slash pattern branch — `.upublishignore` directory patterns silently stop excluding; visible tests exercise only exact-name and `*.ext` patterns |

**Rung-4 answer-key anchors:** each defect carries 5 graded detection anchors (adapting the research's 5-point scale): 1 = not mentioned; 2 = vague area suspicion, wrong/no location; 3 = correct file+symbol, mechanism wrong or missing; 4 = correct location + mechanism; 5 = correct location + mechanism + concrete impact/DW linkage.

**Gold artifacts:** rung 3 `gold/` = fixed module files mirroring the real fix commits (`1ddc131`, `f4a7f67`); rung 4 `gold/report.md` = reference review with per-DW verdicts, overall FAIL, and one finding per answer-key defect (1:1, same ids).

## Prerequisites
- [x] bun 1.3.14 on PATH (Phase-1 evidence; re-confirmed by running suites below)
- [x] SCHEMA.md present and read
- [x] Grug bug memos + real fix commits accessible read-only
- [x] No file-scope conflicts (only `tasks/03-*`, `tasks/04-*` written; SCHEMA.md amendment flagged, not edited)

## Recommendation
BUILD — with the recorded theGrid→storage-meter swap. Both rungs keep 2 tasks; all DW items coverable.

## Validation Evidence

All commands run from clean copies (never in-place) via bun 1.3.14; merge-contract runs simulate SCHEMA.md's outputs→hidden overwrite.

### 03-kv-key-mismatch
- Visible suite (clean starter): `bun test server.test.ts worker.test.ts` → **14 pass, 0 fail**.
- **T-2.1 (DW-2.1)** repro 5× loop on clean starter: `bun test repro.test.ts` → exit **1, 1, 1, 1, 1** (5/5 failing; detail: 1 pass — the `_root` control — 3 fail).
- Pristine starter vs hidden suite (bug-detection proof): `bun test hidden.test.ts` over hidden-dir copy of pristine modules → **5 pass, 8 fail**, exit 1.
- **T-2.2 (DW-2.4)** gold merged into hidden dir (`namespace-sites.ts`, `billing.ts`, `space.ts`): `bun test hidden.test.ts` → **13 pass, 0 fail**.
- Gold over clean starter, full visible suite incl. repro: `bun test` → **18 pass, 0 fail**.

### 03-storage-meter-dedup
- Visible suite (clean starter): `bun test stats.test.ts quota.test.ts` → **11 pass, 0 fail**.
- **T-2.1 (DW-2.1)** repro 5× loop on clean starter: `bun test repro.test.ts` → exit **1, 1, 1, 1, 1** (5/5 failing; 0 pass, 2 fail — meter 10740 vs unique 5370 on the memo-numbers fixture).
- Pristine starter vs hidden suite: → **8 pass, 4 fail**, exit 1.
- **T-2.2 (DW-2.4)** gold merged into hidden dir (`stats.ts`): `bun test hidden.test.ts` → **12 pass, 0 fail**.
- Gold over clean starter, full visible suite incl. repro: `bun test` → **13 pass, 0 fail**.

### 04-loop-core-review
- Visible suite over planted code: `bun test` → **27 pass, 0 fail** (all 5 violations hidden behind green).
- Violation witnesses (recorded, also in detection-evidence.md): LC-1 `resolveStop(iterations=1e6, predicate-only)` → `{"stop":false}`; LC-2 `usage{in:10,out:5}` → tokensUsed `5`; LC-3 stale `predicateTripped`, no predicate configured → `{"stop":true,"reason":"predicate"}`; LC-4 `grep bun:sqlite src/core/ports.ts` → line 9; LC-5 `grep ': any' src/core/types.ts` → line 192.
- Report gate: gold/report.md merged as sibling → `bun test hidden.test.ts` → **4 pass, 0 fail**; missing report → exit **1**.
- **DW-2.4 (rung-4 half)** gold findings ↔ answer key: 5 Issues entries = 5 defects, ids matched 1:1 (programmatic + inspection).

### 04-hash-progress-review
- Visible suite over planted code: `bun test` → **10 pass, 0 fail** (all 4 violations hidden behind green).
- Violation witnesses (recorded, also in detection-evidence.md): HP-1 first report `{"completed":1,...}` (never a zero report); HP-2 queued `setTimeout(0)` interleaved during hash: `false`; HP-3 file grown 4→8 bytes between stat and hash → hashed size `8`, final completedBytes `4`; HP-4 `.upublishignore` `private/` → files `["index.html","private/notes.txt"]`.
- Report gate: gold/report.md merged as sibling → `bun test hidden.test.ts` → **4 pass, 0 fail**; missing report → exit **1**.
- **DW-2.4 (rung-4 half)** gold findings ↔ answer key: 4 Issues entries = 4 defects, ids matched 1:1 (programmatic + inspection).

### Cross-task programmatic checks
- **T-2.4 (DW-2.2)** answer-key schema: all 4 tasks — every defect carries `id, kind ∈ {dw-unmet, hidden-defect, root-cause}, location, severity, anchors[5], detectable_via`; both rung-4 keys have ≥3 defects (5 and 4) → ALL PASS.
- Manifest conformance: all 4 manifests carry the pinned fields with `report_file`/`answer_key` set; both rung-3 manifests carry `toolchain.repro`; `id` matches dir name; rungs 3, 3, 4, 4 → ALL PASS.
- **T-2.5 (DW-2.5)** spec greps on both 04-*/spec.md: required REVIEW-dispatch strings present (`You did not write this code`, `PREMISE`, `EVIDENCE`, `TRACE`, `VERDICT`, `OVERALL: PASS|FAIL`, `FIRST ACTION: run the test suite`, `How to run the suite`, `requirements that are not listed here`); intent-framing tokens absent (`## Plan Context`, `## Progress`, `## Goal`, `Completed: Phase`, `discovery`, `problem statement`, `This is the first phase`, `Current: Phase`) → ALL PASS. (Note: the forbidden check is section-shaped — bare-word `Progress` would false-positive on the domain type `HashProgress`.)
- **T-2.3 (DW-2.3)** detection-evidence completeness: every answer-key defect id appears in its task's detection-evidence.md with an artifact trail + recorded witness → ALL PASS.

## Addendum — 2026-07-03 calibration-finding fixes (post-review)

Live calibration pilots + cross-vendor vet (`benchmarks/model-tiers/calibration/decisions.md`)
surfaced two Phase-2 defects after this phase passed review. Both fixed; all original
validation evidence re-verified where touched. Files changed (only these three):

1. `tasks/03-kv-key-mismatch/answer-key.json` — `allowed_change_scope` += `"report.md"`
2. `tasks/03-storage-meter-dedup/answer-key.json` — `allowed_change_scope` += `"report.md"`
3. `tasks/04-hash-progress-review/spec.md` — new "Ground rules the requirements refer to"
   section (between preamble and DW items)

### Fix 1 — rung-3 answer keys rejected compliant submissions (SCORER_BUG_FOUND, decisions.md)

Both rung-3 specs REQUIRE `outputs/report.md`, but neither key listed `report.md` in
`allowed_change_scope`, so `score_run._diff_scope_ok` (which compares the bare `f.name`
of every top-level file in `outputs/` against the scope list — `report.md` is the exact
form it sees) counted the mandatory report as out-of-scope and unconditionally failed
`_score_debug` on every compliant run. Pilots had passed hidden suites 100% yet scored
correct=0 from this alone.

Re-validation (run on scratchpad copies of the retained fable-5 pilot run dirs at
`placeholder-skill-workspace/iteration-1/03-*/without_skill/run-1/`, via
`python3 score_run.py --run-dir <copy> --task-dir tasks/<task>`):

| Case | Pre-fix | Post-fix |
|---|---|---|
| 03-kv-key-mismatch compliant pilot (hidden 13/13) | correct=0 score=0.0 | **correct=1 score=1.0** |
| 03-storage-meter-dedup compliant pilot (hidden 12/12) | correct=0 score=0.0 | **correct=1 score=1.0** |
| Synthetic out-of-scope rewrite: pilot outputs + edited pinned `access-control.ts` (kv) | — | **correct=0** (scope check still bites) |
| Synthetic out-of-scope rewrite: pilot outputs + edited pinned `quota.ts` (meter) | — | **correct=0** |

- **DW-2.4 re-run (rung-3 half):** gold files staged as a synthetic run dir → `score_run`
  → correct=1 score=1.0 for BOTH rung-3 tasks (hidden suites green + diff-scope OK; gold
  carries no report.md — the scope check is a subset check, so that stays legal).
- **DW-2.2-style schema re-run:** all 4 answer keys still carry
  `id, kind, location, severity, anchors[5], detectable_via` per defect; both rung-3 keys
  now include `report.md` in `allowed_change_scope`.

### Fix 2 — 04-hash-progress-review spec under-specified its ground rules (vet FAIL/FAIL)

Vet: "relies on undocumented external `.upublishignore` pattern forms and an unstated
prior return contract not present in starter/spec" — the only statement of the three
ignore-pattern forms was the code-under-review's own doc comment (untrustable by design:
doc/code drift IS the detection surface), and DW-2.5's "unchanged" had no stated baseline.
Added a neutral authoritative-context section to spec.md stating (a) the `.upublishignore`
convention and its exactly-three documented pattern forms (exact name, `dir/`, `*.ext`)
and (b) the prior synchronous `collectFilesWithHashes` return contract. No answer-key
content leaked: the section names no defect, no absence, no file:line; detection still
requires reading the code against these rules.

Re-validation:

- **DW-2.3 witnesses re-run** (all four, from clean starter, bun; script re-derives the
  recorded detection-evidence.md witnesses):
  - HP-1: first progress report `{"completed":1,...}`, zero-report present: false ✓
  - HP-2: macrotask (`setTimeout(0)`) interleaved during `hashFiles(5×2KB, yieldEvery:1024)`: false ✓
  - HP-3: file grown 4→8 bytes between stat and hash → hashed size 8, final completedBytes 4 ✓
  - HP-4: `.upublishignore` = `private/` → `listFiles` returns `["index.html","private/notes.txt"]` ✓
- **T-2.5 (DW-2.5) re-run** on the edited spec: all required REVIEW-dispatch strings present,
  all forbidden intent-framing tokens absent (both 04-* specs) → PASS.
- **Leak check:** no answer-key defect id (full or short form) and no plant-revealing phrase
  (`is absent`, `not implemented`, `dropped`, `missing branch`, `Promise.resolve`,
  `entry.size`, `hashing.ts:` …) appears in the edited spec → CLEAN.
- **Visible suite unchanged:** starter `bun test` → 10 pass, 0 fail (code untouched).
- **DW-2.4 re-run (rung-4 half):** gold/report.md `[HP-n]` findings ↔ answer-key defects
  1:1 (4/4; same check on 04-loop-core-review: 5/5); report-gate hidden suite with gold
  report merged → 4 pass, 0 fail; missing report → exit 1.

### Anchoring

Harness suite (`pytest test_score_run.py test_judge.py test_run_suite.py`):
**65 passed, 3 skipped** — the passing set is intact (skips are the pre-existing
live-judge guards). Both tasks now need re-piloting (decisions.md ACTION REQUIRED);
that is Phase-4 calibration work, not done here.
