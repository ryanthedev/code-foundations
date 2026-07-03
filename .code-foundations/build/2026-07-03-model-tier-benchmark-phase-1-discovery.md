# Discovery + Design: Phase 1 - Build-rung tasks from corpus

## Files Found
- `benchmarks/concise-doctrine/` and `benchmarks/tdd-vs-siv/` — both exist (the plan's file hint referenced `benchmarks/tdd-vs-siv/tasks/` as the layout exemplar; confirmed present, not a dead reference).
- `benchmarks/tdd-vs-siv/tasks/{01-duration,02-rpn,03-inventory,04-password}/{spec.md,hidden/test_hidden.py,starter/}` — the exact layout convention this phase's tasks must follow (spec.md with DW items + "Output paths"; hidden/test_hidden.py with `test_dw_*` / `test_offdw_*` naming; starter/ only for modify-kind tasks).
- `benchmarks/model-tiers/` did not exist — created fresh (`tasks/01-heartbeat-message/`, `tasks/02-cas-refcount-quota/`, `tasks/02-cas-bounded-concurrency/`, each with `starter/`, `hidden/`, `gold/`).
- Corpus: 115 plan files across `~/repos/*/.code-foundations/plans/` (theGrid, upublish, upublish-backend, upublish.skill, upublish-website, code-foundations, meeseeks, oberskills, design-for-ai, penman).

## Current State
No prior `benchmarks/model-tiers/` content existed. `docs/code-standards.md` Part 2 (Benchmark harnesses) and the two shipped exemplars (`tdd-vs-siv`, `concise-doctrine`) define the house conventions this phase must follow.

## Gaps
- The plan's pinned manifest schema (`{id, rung, source{repo,plan,phase}, toolchain{install,test_hidden}, starter_dir, report_file?, answer_key?}`) is richer than either exemplar's manifest (tdd-vs-siv's `tasks/manifest.json` has no `source`/`toolchain`/rung fields — it's flat `{kind,impl,tests,hidden}`). SCHEMA.md (this phase's own deliverable) had to be authored from scratch; no existing file to extend.
- No prior `gold/` directory convention in either exemplar (tdd-vs-siv has no committed gold solutions; concise-doctrine's gold lives implicitly in arm files). This phase introduces `gold/` per task as the DW-1.2 evidence artifact.

## Code Standards
`docs/code-standards.md` Part 2 (Benchmark harnesses) applied:
- Task dirs `NN-slug`; `spec.md` (DW items only, no hidden-test contents); `hidden/` never shown to the agent; `starter/` for modify-kind tasks.
- Hidden tests bucket `test_dw_*` (spec-stated behavior) / `test_offdw_*` (preserved/existing behavior + dirty edges not exemplified in spec) — verified against ground truth by running the gold solution and a pristine-starter offdw-only pass.
- Python conventions (venv, docstrings, `Path`) apply to the *harness* layer (Phases 3-5), not to these TS-native task fixtures — Part 2's own text: "New suites follow them" for orchestrator/harness code; tasks here are subject-language-native (TS/bun), matching "hidden test suite in the task's native toolchain" (research doc, Suite design table).
- Pre-registration: this phase's validation commands (gold-vs-hidden, offdw-vs-pristine, sabotage-vs-hidden) are recorded verbatim in this discovery file before being treated as passing evidence.

## Test Infrastructure
- `bun test` (bun 1.3.14 confirmed installed) is the native toolchain for all three tasks — matches corpus reality (~80% TS, upublish-family repos all use bun:test).
- Each task is built as a fully self-contained bun workspace (own `package.json` + `tsconfig.json`) so `toolchain.install` / `toolchain.test_hidden` from manifest.json are real, runnable, offline commands — no dependency on the source repos' own node_modules or bun:sqlite global state.

## Corpus Screening (Assumption Verification)

Assumption under test: "Selected corpus phases port into isolated workspaces" (Medium confidence).

| Candidate | Repo | Plan / Phase | Model/Gate | Portability verdict |
|---|---|---|---|---|
| theGrid concurrency fixes (P1-P4, P7) | theGrid | `2026-06-12-thegrid-concurrency-correctness-fixes.md` | opus/Full | **Rejected** — Swift/macOS window-manager (`Package.swift`, AXUIElement/CGWindow/NSWorkspace live-window state). Not portable to an offline, self-contained fixture without heavy OS-API mocking; violates the edge case "starter must build/test green" for a repo needing live macOS window state. |
| CAS dedup/resume Phase 1 (schema, refcounts, hybrid quota) | upublish-backend | `2026-06-03-cas-dedup-resume.md` Phase 1 | opus/Full | **Accepted** (as `02-cas-refcount-quota`). Pure `bun:sqlite` + SQL — no R2/KV/Workers bindings. Verified against the actual landed commit (`543f338`, "feat(db): CAS foundation — blobs/version_files tables, refcounts, hybrid unique-bytes quota") for a faithful gold solution. Reduced the `namespaces` join layer (incidental multi-tenancy plumbing, not exercised by any DW item) to keep the fixture self-contained — noted as a deliberate, scope-preserving fixture reduction, not a new requirement. |
| CAS diff bounded-concurrency Phase 1 (backend) | upublish-backend | `2026-06-20-cas-diff-bounded-concurrency.md` Phase 1 | opus/Full | **Accepted** (as `02-cas-bounded-concurrency`). `computeCasDiff`/`verifyNeededBlobs` already take injected pure interfaces (`headBlob: (hash) => Promise<boolean>`, `R2Client.headObject`) — no live R2 needed. Verified against the actual fix commit (`db44ccd`) for a byte-faithful gold `mapWithConcurrency` helper + two call-site rewires. |
| CAS diff bounded-concurrency Phase 2 (heartbeat relabel) | upublish.skill | same plan, Phase 2 | sonnet/Standard | **Accepted** (as `01-heartbeat-message`, the easy task). Verified against the actual fix commit (`aaf72ba`) — a single-function message-formatting change, extracted into a pure `heartbeatMessage()` function (the original lives inside a `setInterval` closure over module state; extracting to a pure function is a scope-preserving fixture reduction, not new behavior). |
| meeseeks Phase 1 (core domain + ports) | meeseeks | `2026-06-28-meeseeks-cron-loop-manager.md` Phase 1 | opus/Full | Screened, not selected — pure/portable but thinner on "genuinely multi-step" agentic surface (mostly interface definitions + one pure function) vs the two CAS phases' richer multi-seam, production-bug-fix shape. |

Both hard-build phases and the easy-build phase are sourced from real, `Status: complete` corpus plans with actual landed commits — not invented tasks. No candidate had to be swapped after the initial screen (theGrid was rejected at screening, before any fixture-authoring effort, per the plan's own fallback path).

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-1.1 | All three task dirs (1 easy, 2 hard) exist with spec.md, starter/, hidden/, manifest.json conforming to SCHEMA.md | COVERED | Manifest schema validation script (`validate_manifests.sh` inline check) run against all three `manifest.json` files; directory listing confirms all four required members per task |
| DW-1.2 | Each gold solution passes its hidden suite from a clean starter copy (command output recorded); each pristine starter is green before the task change | COVERED | Per task: (a) copy `gold/` files over `starter/`, run `bun test hidden/` → full green, command output captured in this file; (b) run `bun test hidden/ -t offdw` (or filtered) against the untouched `starter/` → green, proving pristine-starter sanity |
| DW-1.3 | Each hidden suite contains ≥1 dirty test per DW item; each hard task touches ≥2 modules/seams | COVERED | Per-task DW-to-dirty-test mapping table (below, in each task's own section); hard-task file-count diff (starter vs gold) ≥2 files, recorded per task |
| DW-1.4 | Each manifest records its source corpus phase (repo, plan file, phase number) | COVERED | `manifest.json` `source{repo,plan,phase}` field inspected per task (shown in the screening table above) |

**All items COVERED:** YES

## Design Decisions

**SCHEMA.md contract** (the phase's own Produces item, authored fresh): manifest.json = `{id, rung, source{repo,plan,phase}, toolchain{install,test_hidden}, starter_dir, report_file?, answer_key?}` exactly as pinned in the plan. Added an "Execution contract" section spelling out how `outputs/` merges with `hidden/` before `toolchain.test_hidden` runs (needed because — unlike tdd-vs-siv's Python convention where the grader imports the module by name from a shared sys.path — TS/bun hidden tests must resolve sibling imports, so the contract states outputs/ files are copied into the same directory as the hidden test file before the test command runs).

**gold/ directory**: introduced (not present in either exemplar) as the artifact DW-1.2 validates against — each task's `gold/` holds the complete starter-plus-fix file set, letting the validation script apply it mechanically (copy over starter, run hidden suite) rather than hand-verifying.

**Rung-2 multi-seam check**: implemented as a file-count/name diff between `starter/` and `gold/` (excluding boilerplate `package.json`/`tsconfig.json`) rather than a git-diff line-count heuristic — simpler, deterministic, and matches the DW-1.3 wording ("≥2 modules/seams") directly.

**Per-task DW numbering**: task-local Done-When items use `DW-E1.*` (easy), `DW-H1.*` (hard: refcount/quota), `DW-H2.*` (hard: bounded concurrency) — distinct from this build phase's own `DW-1.1..1.4` to avoid collision when both appear in this same discovery file.

## Validation Evidence (DW-1.2, DW-1.3)

All commands run from a scratch copy (never in-place) via bun 1.3.14.

### 01-heartbeat-message
- Gold vs hidden (full suite): `bun test hidden.test.ts` → `6 pass, 0 fail, 12 expect() calls`.
- Pristine starter vs offdw subset: `bun test hidden.test.ts -t offdw` → `3 pass, 0 fail` (after
  reclassifying one boundary case from `offdw` to `dw` — the 0/0-files edge depends on the fix, not
  preserved behavior; caught by running the offdw filter and seeing it fail before the rename).
- Sabotage (flip `===` to `!==` in the done-check): `bun test hidden.test.ts` → `1 pass, 5 fail`,
  exit 1 — suite detects the break.
- Dirty-per-DW: DW-E1.1 ↔ `test_offdw_completed_exceeding_total_is_dirty_data_not_done`; DW-E1.2 ↔
  `test_offdw_in_progress_message_unaffected_by_the_fix`.

### 02-cas-refcount-quota
- Gold vs hidden (full suite): `bun test hidden.test.ts` → `23 pass, 0 fail, 37 expect() calls`.
- Pristine starter vs `hidden/pristine.test.ts` (only imports `migrate`/`sumStorageForSpace`, the
  starter's existing exports — the full hidden.test.ts cannot even load against the starter, since
  bun resolves static imports for `referenceBlobs`/`dereferenceVersion`/`sumUniqueStorageForSpace`/
  `projectUniqueStorage` at module-load time before any `-t` filter applies; confirmed by trying
  and observing `SyntaxError: Export named 'projectUniqueStorage' not found`) →
  `3 pass, 0 fail, 5 expect() calls`.
- Sabotage (drop the `refcount > 0` guard from the decrement WHERE clause): `bun test
  hidden.test.ts` → `21 pass, 1 fail` (`test_dw_H1_3_refcount_never_goes_negative` catches the
  guard removal — refcount goes to -1), exit 1.
- Multi-seam: gold differs from starter in 2 files (`schema.ts`, `db.ts`) — meets the ≥2 requirement.
- Dirty-per-DW: DW-H1.1 ↔ `test_offdw_bad_storage_format_value_rejected_by_check_constraint`;
  DW-H1.2 ↔ injected PK-collision failure inside the DW test itself, plus
  `test_offdw_referenceBlobs_empty_files_is_noop`; DW-H1.3 ↔ `test_dw_H1_3_refcount_never_goes_negative`
  (corrupted-state fixture) and `test_offdw_dereferenceVersion_on_nonexistent_version_returns_empty`;
  DW-H1.4 ↔ `test_offdw_sumUniqueStorageForSpace_empty_space_is_zero`; DW-H1.5 ↔
  `test_offdw_project_empty_incoming_returns_base_unchanged`.

### 02-cas-bounded-concurrency
- Gold vs hidden (full suite): `bun test hidden.test.ts` → `15 pass, 0 fail, 25 expect() calls`.
- Pristine starter vs `hidden/pristine.test.ts` (only imports `computeCasDiff`/`verifyNeededBlobs`,
  the starter's existing exports — the full hidden.test.ts fails to load against the starter with
  `error: Cannot find module './concurrency.ts'`, confirmed by trying) → `5 pass, 0 fail, 7 expect()
  calls`.
- Sabotage (revert `computeCasDiff` to the sequential for-loop): `bun test hidden.test.ts` →
  `14 pass, 1 fail` (`test_dw_H2_4_computeCasDiff_runs_headBlob_bounded_and_parallel` catches it —
  max-in-flight drops to 1), exit 1.
- Multi-seam: gold differs from starter in 3 files (`concurrency.ts` new, `manifest-diff.ts` and
  `cas-publish.ts` modified) — meets the ≥2 requirement.
- Dirty-per-DW: DW-H2.1 ↔ `test_offdw_mapWithConcurrency_rejection_propagates_not_caught`; DW-H2.2
  ↔ `test_offdw_computeCasDiff_headBlob_throw_propagates` and
  `test_offdw_computeCasDiff_empty_manifest_returns_empty_needed`; DW-H2.3 ↔
  `test_dw_H2_3_rejected_head_is_missing_not_thrown`/`test_dw_H2_3_null_head_is_missing` (dirty
  inputs) and `test_offdw_verifyNeededBlobs_empty_needed_is_ok_empty_sizes`; DW-H2.4 is itself the
  regression/dirty concurrency-detection test.

### Manifest schema conformance (DW-1.1, DW-1.4)
All three `manifest.json` files checked programmatically against SCHEMA.md's required fields
(`id, rung, source{repo,plan,phase}, toolchain{install,test_hidden}, starter_dir`) — zero missing
fields in any of the three; `rung` values are `1, 2, 2` as expected (one easy, two hard).

## Prerequisites
- [x] Required files exist (created fresh — no phase-1 files existed before this build)
- [x] Dependencies available (bun 1.3.14 confirmed on PATH)
- [x] Corpus accessible (`~/repos/*/.code-foundations/plans/` — 115 plan files, read access confirmed)

## Recommendation
BUILD. Screening confirmed portability for one easy + two hard candidates (theGrid rejected at screening per the plan's own fallback instruction, no invented tasks needed). Proceed to stub → implement → validate for all three task fixtures plus SCHEMA.md.

## Addendum (2026-07-03): calibration-vet fix for 02-cas-refcount-quota

Live calibration (`benchmarks/model-tiers/calibration/decisions.md`, `02-cas-refcount-quota`
entry) rejected this task: `vet_result` FAIL/FAIL on 2 independent judge-pair runs — codex:
"dereferenceVersion nonempty return shape, duplicate-hash sizes, and live_version->site_versions
mapping undefined." A solver could satisfy the visible DW text with materially different behavior
than the hidden suite (`hidden/hidden.test.ts`) actually asserts. Fix scope was `spec.md` only
(per `SCHEMA.md`'s "spec.md ... NEVER hints at the hidden suite's contents or the gold solution");
no hidden test, gold, starter, or manifest file was touched.

### What changed (spec.md, `tasks/02-cas-refcount-quota/spec.md`)

| Ambiguity (vet finding) | Fix |
|---|---|
| `dereferenceVersion` return shape unstated | DW-H1.2 now states the signature (`referenceBlobs` → `void`, `dereferenceVersion` → `Array<{hash, size}>`) and pins the contract: the array lists exactly the hashes whose `refcount` reaches 0 as a *direct* result of the call; a hash decremented but still >0 is excluded; a hash already at 0 before the call (guarded) is excluded too — not reported as newly freed. |
| `live_version` → `site_versions` mapping undefined | New Background paragraph: `sites.live_version` stores a `site_versions.version_number` (not a `site_versions.id`); a site's live version is found by joining on `site_id` + `version_number = sites.live_version`; a site with no matching row has no CAS live version. This is the join DW-H1.4's hybrid quota depends on to decide whether a site's live version is CAS- or prefix-format. |
| Hybrid-quota duplicate-hash / term semantics under-specified | DW-H1.3 gained a bullet pinning that `blobs.size` is set once at a hash's first reference and never overwritten by a later re-reference (content-addressing invariant — same hash, same bytes, same size). DW-H1.4 was rewritten from a narrative description into three explicit, named, non-overlapping terms (CAS term: `SUM(blobs.size)` where `refcount > 0`; prefix term (a): live-site `total_size` for non-CAS-live sites; prefix term (b): archived-version `total_size` for `storage_format = 'prefix'`), with the CAS-free-equals-legacy and transition-fixture claims re-derived against the named terms instead of prose. |

No SQL or code was added to spec.md — only prose contract language (signatures, term names, and
inclusion/exclusion rules), consistent with "specify contracts, not test cases." No fixture number
from the hidden suite (e.g. specific byte sizes) was copied into spec.md.

### Re-validation (re-run from a scratch workspace, not in place)

```
$ bun test hidden.test.ts     # gold/{db.ts,schema.ts} + hidden/hidden.test.ts, scratch dir
23 pass
0 fail
37 expect() calls
Ran 23 tests across 1 file.

$ bun test pristine.test.ts   # untouched starter/{db.ts,schema.ts} + hidden/pristine.test.ts
3 pass
0 fail
5 expect() calls
Ran 3 tests across 1 file.
```

- **DW-1.2** (gold passes hidden suite from clean starter; pristine starter green): re-confirmed —
  identical pass counts to the original authoring-time run (23/23, 3/3) since only `spec.md` prose
  changed, not `gold/`, `starter/`, or `hidden/`.
- **DW-1.3** (dirty tests per DW item; ≥2 modules for a hard task): re-confirmed — `starter/` vs
  `gold/` still differ in exactly 2 files (`db.ts`, `schema.ts`); `hidden.test.ts` still has 7
  `test_offdw_*` cases spanning DW-H1.1 through DW-H1.5, unchanged.
- **spec.md still DW-items-only, no solution hints**: confirmed — the only fenced code blocks in
  `spec.md` are the original two starter-signature stubs (`migrate`, `sumStorageForSpace`); no SQL,
  no new code block, no hidden-suite fixture value was added.

### Files changed
- `benchmarks/model-tiers/tasks/02-cas-refcount-quota/spec.md` (Background + DW-H1.2/H1.3/H1.4
  prose clarified; no other files in the task directory touched).

Next step (outside this fix's scope, per the original vet_result note): 02-cas-refcount-quota
loops back into the Phase 4 calibration vet for re-judgment against the clarified spec — that
re-vet is a Phase 4 activity, not part of this Phase 1 spec fix.
