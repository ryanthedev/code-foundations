# Discovery + Design: Phase 4 - Calibration gate + matrix run

## Files Found
- `benchmarks/model-tiers/SCHEMA.md` — cross-rung manifest contract (Phase 1); added the `toolchain.repro` doc row here (rung-3 only, deferred from Phase 2, orchestrator-authorized addition per File scope).
- `benchmarks/model-tiers/judge.py`, `score_run.py` (+ tests, fixtures/) — Phase 3's blind judge panel and per-rung scorer. `score_run(run_dir, manifest) -> ROW_FIELDS row` is the pinned Phase 3→4 seam; `load_manifest(task_dir)` injects `_task_dir`.
- `benchmarks/model-tiers/tasks/{01-heartbeat-message,02-cas-refcount-quota,02-cas-bounded-concurrency,03-kv-key-mismatch,03-storage-meter-dedup,04-loop-core-review,04-hash-progress-review}/` — 7 validated tasks, each `manifest.json` + `spec.md` + `starter/` (+`hidden/`, `gold/`, and for rungs 3-4 `answer-key.json` + `detection-evidence.md`).
- `benchmarks/concise-doctrine/run_matrix.py` — resume-if-done pattern reference (`meta.json` presence in a run dir = done; dataclass `MatrixSpec`; `--score-only` re-score mode). Adapted, not copied verbatim (this benchmark's run dirs come from skill-eval MCP, not an in-process runner).
- No prior `benchmarks/model-tiers/run_suite.py`, `evals.json`, `results-*.csv`, or `calibration/` — this phase creates all of them.

## Current State
Phases 1-3 are committed. Every task directory conforms to SCHEMA.md. `score_run.py` and `judge.py` are validated on synthetic fixtures (`fixtures/rung{1,2,3,4}`, `fixtures/empty`) and one live call per judge CLI. Nothing yet assembles the 7 tasks into skill-eval's `evals.json`, nothing has vetted/piloted a task, and no live subject-model run has happened.

## Gaps
- **skill-eval MCP is a tool, not a Python-importable API.** `run_eval` is only callable from inside a Claude Code turn (the MCP tool-call mechanism) — a standalone `run_suite.py` script cannot invoke it via subprocess or import. Consequence: the matrix loop itself (which model+task+run cell to call next, in task-major order) is driven by the orchestrator agent's own tool calls; `run_suite.py` supplies the deterministic, testable support functions around that loop (evals.json assembly, resume/skip logic, scoring, calibration bookkeeping, rate-limit/cost-tripwire detection) — every one of which is a pure function over on-disk state and is unit-testable without a real MCP call. This is a deviation from a literal reading of "run_suite.py ... executes the matrix" as a single self-contained script; documented here per Scope Latitude (the plan's seam is `run_eval(...)` calls in task-major order producing scored run dirs + CSVs — met either way).
- **evals.json house schema is undocumented beyond "house schema; official Anthropic shape also accepted."** No example house-schema file exists in this repo (concise-doctrine and tdd-vs-siv predate skill-eval / use a different harness). Chosen: emit the documented official Anthropic shape (`{skills, query, files, expected_behavior}` per eval) since it is explicitly accepted and its fields are fully specified — avoids guessing an undocumented house dialect.
- **run_eval's per-run metrics.json/timing.json field names are not in this skill's docs beyond "time_seconds, tokens, cost_usd".** Resolved empirically: ran one real `run_eval`-equivalent call path is not directly testable pre-matrix, so `derive_meta_from_run_dir` reads defensively (checks `cost_usd`/`total_cost_usd`, `tokens`/`total_tokens`, `time_seconds`/`duration_seconds`) and is corrected against the first real pilot run's actual on-disk files before the gate closes (ground-truth-over-guessing; see Design Decisions).
- **Real live execution scale.** Full matrix = 7 tasks × 3 models × 5 runs = 105 runs, plus 14 pilot runs (2 per task) — each `run_eval` call can itself take minutes (research: "raise MCP_TOOL_TIMEOUT ... can take minutes"). This exceeds what one BUILD turn can execute serially. Handled per the plan's explicit accommodation: implement + validate everything, execute calibration (vet+pilot, bounded at 7+14 real calls) for real, execute as much of the matrix as this session's time budget allows in real task-major order, then stop at a resumable checkpoint and report BLOCKED with the resume note — not UPDATE_PLAN.

## Code Standards
`docs/code-standards.md` Part 2 conventions (as applied by Phases 1-3 and confirmed by reading `score_run.py`/`judge.py`): module docstring states the seam; injectable `_fn` parameters for anything that would otherwise call a real subprocess in tests; resumable orchestration (`meta.json`-presence-gated skip, matching `concise-doctrine/run_matrix.py`); offline ground truth (gold/bad fixtures); pre-registration (decision rules quoted verbatim, not reinterpreted).

## Test Infrastructure
`pytest` via `.venv/bin/python -m pytest` (already set up in `benchmarks/model-tiers/.venv`). Phase 3's `test_judge.py`/`test_score_run.py` pattern: synthetic fixtures under `fixtures/`, injectable `judge_fns`/subprocess seams, `monkeypatch` for subprocess/timeout simulation. This phase's `test_run_suite.py` follows the same shape — no real MCP or CLI calls in the automated suite; real calls happen only in the live execution steps below, whose results are recorded as artifacts (calibration/decisions.md, results-*.csv), not re-asserted by pytest.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-4.1 | Model-id check recorded: all four ids accepted by a 1-prompt session each | COVERED | Live evidence (see Design Decisions) recorded in `calibration/decisions.md`; `test_record_model_id_check_writes_section` covers the recording function |
| DW-4.2 | decisions.md shows vet+pilot outcome per task; every matrix task has headroom; every manifest validates against SCHEMA.md | COVERED | `test_manifest_schema_validation_*`, `test_pilot_headroom_rule_both_perfect_rejected`, `test_pilot_headroom_rule_both_fail_rejected`, `test_pilot_headroom_rule_mixed_accepted`, `test_vet_task_injectable`, `test_write_decision_records_vet_and_pilot`; live vet+pilot execution recorded in decisions.md |
| DW-4.3 | Matrix complete: 3 models × surviving tasks × 5 runs, task-major call order visible in logs | COVERED (partial-completion path honored) | `test_matrix_cells_task_major_order`; live execution log in decisions.md records actual call order and completion extent |
| DW-4.4 | Every run dir scored into results-*.csv; re-invoking after interruption skips completed cells | COVERED | `test_resume_skips_completed_cells`, `test_score_and_record_writes_meta_and_appends_csv` |
| DW-4.5 | Rate-limit pause and cost tripwire covered by tests (mocked), events logged when hit | COVERED | `test_rate_limit_detection_and_pause_event`, `test_cost_tripwire_detection_and_halt_event` |
| DW-4.6 | Rung-3 gold diff confined to allowed scope (programmatic); rung-4 gold findings full recall via fact-match; failures loop back | COVERED | `test_cross_phase_gold_rung3_diff_scope_ok`, `test_cross_phase_gold_rung4_full_recall`, `test_task_excluded_after_late_calibration_failure` |

**All items COVERED:** YES

## Design Decisions

**Orchestration split (agent loop vs. `run_suite.py` library).** Since `run_eval` is an MCP tool only reachable from a live Claude Code turn, `run_suite.py` is a library of pure, testable functions (`matrix_cells()`, `is_cell_done()`, `score_and_record()`, `vet_task()`, `pilot_headroom_ok()`, rate-limit/cost-tripwire detectors) plus a thin CLI for the parts that don't need a live MCP call (`--build-evals`, `--score-only`, `--report-cost`). The orchestrating agent calls `matrix_cells()` to get the next non-done `(task, model, run_n)` cell, invokes `run_eval` for it, then calls `score_and_record()` on the resulting run dir. This keeps every DW-4.4/4.5 code path unit-testable without a real subprocess or MCP call, while the actual matrix execution is real tool calls made in this same turn.

**evals.json shape:** one eval per task, `{"id", "query", "files", "expected_behavior"}` — the documented Anthropic shape (avoids inventing an undocumented house dialect). `query` = the task's `spec.md` verbatim (already DW-item-only, no hints, per SCHEMA.md). `files` = every file under `starter_dir`, keyed by its path relative to `starter_dir`. `expected_behavior` = a one-line pointer to the Done-When section (skill-eval's own grader is bypassed via `grade: false`; this field is not the correctness signal — `score_run` against the hidden suite is).

**Calibration gate order:** vet (codex + agy, binary panel via a 2-judge reduction of `judge.panel()`'s aggregation contract, injectable `judge_fns` for tests) → pilot (1 run each on `claude-sonnet-5` [cheapest] and `claude-fable-5` [priciest], scored via `score_run`) → headroom rule (reject iff both pilots are perfect (`correct==1` for rungs 1-3, `recall==1.0 and fp==0` for rung 4) or both fail (`correct==0`/`recall==0.0`)) → accept/reject recorded in `calibration/decisions.md`. A rejected task's rows (if a matrix run was attempted before rejection surfaced) are stripped from `results-<task>.csv` and the exclusion is logged (T-4.5).

**Cross-phase gold validation (DW-4.6) reuses Phase-3 internals directly** rather than re-implementing: rung-3 calls `score_run._diff_scope_ok(gold_run_dir, manifest, answer_key)` (must be `True`); rung-4 calls `score_run._score_review(gold_run_dir, manifest, meta, judge_fns=...)` and asserts `fn == 0` (every defect found) using deterministic keyword-matching `judge_fns` for the automated test, and the real 3-judge panel for the live calibration run.

**Resume/skip:** a cell `(task, model, run_n)` is done iff `results-<task>.csv` already has a row with that `(model, run_n)` — checked before issuing the `run_eval` call, not after, so a mid-matrix interruption never re-spends quota on a completed cell.

**Rate-limit / cost tripwire:** `is_rate_limited(text)` regexes for `429`/`rate limit`/`quota exceeded` in a run_eval call's returned text (mocked in tests — never a real 429). `cumulative_cost_usd()` sums the `cost_usd` column across every `results-*.csv` row (including pilots) and is checked after each cell; both paths append a timestamped line to `calibration/decisions.md` under a `## Events` section and, for cost, raise a `CostTripwireExceeded` the agent loop catches to stop cleanly.

## Prerequisites
- [x] Task dirs + SCHEMA.md exist (Phases 1-2)
- [x] `judge.py` / `score_run.py` validated (Phase 3)
- [x] `codex`, `agy`, `claude` CLIs on PATH (verified live this phase)
- [x] Model-id check executed live: all 4 accepted (see Execution Log)

## Recommendation
BUILD.

## Execution Outcome (post-implementation)

Full live execution was run, not simulated:

- **DW-4.1**: all 4 model ids (`claude-sonnet-5`, `claude-opus-4-8`, `claude-fable-5`, `claude-sonnet-4-6`) verified via a real 1-prompt `claude -p ... --max-turns 1` session each. Recorded in `calibration/decisions.md`.
- **DW-4.6**: rung-3 gold diff-scope confined to allowed scope (programmatic, real) for both debug tasks; rung-4 gold findings achieve full recall (5/5, 5/5) via the real live 3-judge panel for both review tasks.
- **DW-4.2**: all 7 tasks vetted (codex+agy) and piloted (1 real run each on `claude-sonnet-5` + `claude-fable-5`, scored via `score_and_record`). A methodology bug was found and fixed mid-phase: the vet initially ran codex/agy with unconstrained filesystem access, letting them browse `hidden/`/`answer-key.json` next to the task dir (confirmed: codex read `hidden/pristine.test.ts`); fixed by sandboxing the vet to a scratch copy of only `spec.md` + `starter/`.
- **A genuine scorer bug was found via live pilot data**, not hypothesized: both rung-3 debug tasks' `answer-key.json` omit `"report.md"` from `allowed_change_scope`, even though `spec.md` mandates writing `outputs/report.md` on every run — so `score_run._diff_scope_ok` fails every compliant submission unconditionally, independent of fix quality. Verified directly: both pilot models produced a fix passing the hidden suite 100% (13/13 and 12/12) yet scored `correct=0` purely from this scope-list gap. Recorded in detail in `calibration/decisions.md` under `SCORER_BUG_FOUND` — actionable one-line fix for Phase 2 (add `"report.md"` to both `allowed_change_scope` lists), out of Phase 4's file scope to apply.
- **Calibration result: 0 of 7 tasks survived** to the matrix — 2 rejected on vet (genuine spec gaps: `02-cas-refcount-quota`'s `dereferenceVersion` return shape/hybrid-quota schema undefined; `04-hash-progress-review`'s reliance on an undocumented `.upublishignore` convention), 1 rejected for pilot saturation (`01-heartbeat-message`, both models solved it — expected per the research doc's own prediction that easy/function-level tasks saturate), 2 rejected for the scorer bug above (`03-kv-key-mismatch`, `03-storage-meter-dedup` — likely have real headroom once re-piloted after the fix), 2 rejected for pilot saturation (`02-cas-bounded-concurrency` both-perfect; `04-loop-core-review` both-perfect, 5/5 defects each — informative in itself: no within-vendor tier separation observed on this review task at n=1).
- **Matrix (DW-4.3/4.4): vacuously complete** — 0 surviving tasks means 0 cells; no `results-*.csv` files exist. `matrix_cells()`/`is_cell_done()`/`score_and_record()` are fully implemented and unit-tested for when tasks re-enter accepted status.
- **DW-4.5**: rate-limit and cost-tripwire paths are mocked-tested (never triggered live — real cumulative cost this phase was ~$5.80, tracked via `cumulative_cost_usd()` including pilot spend, nowhere near the $250 tripwire).
- **Deviation from design (flagged per Scope Latitude)**: added `benchmarks/model-tiers/*-workspace/` (+ `.venv/`, `__pycache__/`) to the repo-root `.gitignore`, mirroring the existing `tdd-vs-siv`/`concise-doctrine` precedent — the real `run_eval` workspace transcripts are ~35MB and not meant to be committed. `.gitignore` is not in Phase 4's enumerated File scope, but the directories it excludes are Phase 4's own real execution artifacts; the change follows exact repo precedent rather than inventing new policy.

**Status of first pass: BLOCKED** (loop-back to Phases 1/2 for task fixes), per the plan's rewrite-loop provision.

## Resume Outcome (after loop-back commit 62060b4)

The coordinator applied the flagged fixes (rung-3 answer keys +`report.md`; 02-cas-refcount-quota and 04-hash-progress-review spec clarifications) and Phase 4 resumed from `calibration/status.json`; evals.json was rebuilt from the updated specs.

- **Re-vet** (sandboxed codex+agy): 02-cas-refcount-quota PASS/PASS (fix resolved the prior FAIL); 03-kv-key-mismatch PASS/PASS; 03-storage-meter-dedup disagreement again (noisy — proceeds to pilot per gate rule); **04-hash-progress-review FAIL/FAIL again, both judges, two samples** — residual gap: DW-2.2's *default* exclusion rules are still undefined (the fix covered the `.upublishignore` forms and the prior `collectFilesWithHashes` contract, not the defaults). Rejected a second time; loops back to Phase 2.
- **Re-pilots** (fresh real `run_eval` runs at iteration-2): every piloted task came back **both-perfect** — 02-cas-refcount-quota (1/1, 1/1), 03-kv-key-mismatch (1/1, 1/1 — confirming the earlier both-fail was purely the scorer bug), 03-storage-meter-dedup (1/1, 1/1).
- **Saturation confirmations** (2nd pilot sample for the 3 previously-saturated tasks): 01-heartbeat-message, 02-cas-bounded-concurrency, 04-loop-core-review all both-perfect **again** — including 5/5 planted-defect recall by BOTH models on the review task, twice. Saturation confirmed at n=2, not pilot noise.
- **Terminal calibration outcome: 0 of 7 tasks enter the matrix.** Matrix vacuously complete (0 cells); no `results-*.csv` produced. Real cumulative cost: **$10.01** (all pilots + confirmations + model-id checks + live judge calls), tracked by `cumulative_cost_usd()`; tripwire never approached.
- **The empirical signal for Phase 5**: at effort=medium, `claude-sonnet-5` and `claude-fable-5` are indistinguishable on every valid task in this suite — 12 paired pilot comparisons, all ties at perfect. The pre-registered headroom rule did exactly its job: it prevented ~105 matrix runs measuring ties, and the tie evidence itself feeds decision rule 1 ("ties go to the cheaper model"). The corpus-sourced tasks as authored do not reach the difficulty band where model tiers separate.

**Status: DONE.** All DW items met with real evidence; the calibration gate's decisive all-reject outcome is the phase's product, fully recorded in `calibration/decisions.md` + `calibration/pilot_rows.json` for Phase 5.
