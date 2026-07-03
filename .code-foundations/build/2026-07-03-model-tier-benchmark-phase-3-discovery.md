# Discovery + Design: Phase 3 - Judge panel + scorers

## Files Found
- `benchmarks/model-tiers/SCHEMA.md` — pinned manifest contract from Phase 1 (fields: id, rung, source, toolchain, starter_dir, report_file, answer_key; Execution contract for build rungs; hidden-suite naming `test_dw_*`/`test_offdw_*`).
- `benchmarks/model-tiers/tasks/{01-heartbeat-message,02-cas-bounded-concurrency,02-cas-refcount-quota}/` — Phase 1's validated rung-1/2 tasks (manifest.json shape confirmed: `{"toolchain":{"install":"true","test_hidden":"bun test hidden.test.ts"}}`).
- `benchmarks/concise-doctrine/score_rubric.py` — `_judge_subprocess` pattern (injectable subprocess seam, `_extract_json` fallback parser, `RuntimeError`/`ValueError` split between transport and parse failures).
- `benchmarks/tdd-vs-siv/harness/grade.py` + `mutate.py` — hidden-suite subprocess execution pattern, pytest-output-count regex, `MANIFEST` loaded from a fixed relative path (noted in code-standards as the anti-pattern to avoid — this phase's `score_run` takes both `run_dir` and `manifest` explicitly).
- No `tasks/03-*` or `04-*` (debug/review) dirs exist yet — Phase 2 not built. Per approach notes, fixtures are self-contained and do not depend on them.
- `docs/code-standards.md` Part 2 — Python conventions (uv venv, `pathlib.Path`, `from __future__ import annotations`, module docstrings stating phase/role/seams, argparse CLI per runnable module).

## Current State
`benchmarks/model-tiers/` has SCHEMA.md and three task dirs only. No `judge.py`, `score_run.py`, tests, or fixtures exist — this phase creates all of them from scratch. No `.venv` yet under `benchmarks/model-tiers/`.

## Gaps
- SCHEMA.md pins the rung-1/2 manifest and Execution contract but does not pin a rung-3/4 manifest shape (report_file/answer_key are typed `rung 3/4 only` but their *content* schema is a Phase-2 decision). Since Phase 2 hasn't run, this phase's fixtures/answer-key shapes for rungs 3-4 are designed here, grounded in the plan's own Produces line for Phase 2 (`answer-key.json = {defects:[{id, kind, location, severity, anchors[5], detectable_via}]}`) and Phase 2's rung-3 approach note (`root-cause location, allowed-change scope`).
- `score_run(run_dir, manifest)` is pinned to exactly two positional args (Produces seam) but manifest.json on disk has no field pointing at the sibling `hidden/`/`starter/`/answer-key files. Resolved by a `load_manifest(task_dir)` helper that injects a private `_task_dir` key into the in-memory dict before calling `score_run` — this does not change the on-disk manifest.json schema, only the runtime dict `score_run` receives.

## Code Standards
Applied: Part 2 (Python 3.12 via `uv venv .venv -p 3.12`; `from __future__ import annotations`; `pathlib.Path` never `os.path`; module docstring stating phase/role + seams; argparse CLI per runnable module; injectable subprocess seams per the two existing benchmark harnesses).

## Test Infrastructure
No existing pytest suite in `benchmarks/model-tiers/`. Following `tdd-vs-siv`/`concise-doctrine` house convention: `pytest` in a dedicated `.venv`, hidden suites executed via `subprocess.run` with a bounded timeout, judge CLIs mocked via an injectable `judge_fns` mapping (mirrors `score_rubric.py`'s `judge_fn` parameter) so unit tests never spawn real processes except one explicitly-gated live test per DW-3.5.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-3.1 | `panel()` unit tests cover majority/median aggregation, disagreement, one-judge-failure quorum, all-fail | COVERED | `test_panel_majority_binary_unanimous`, `test_panel_majority_binary_disagreement`, `test_panel_median_graded`, `test_panel_one_judge_failure_quorum`, `test_panel_all_fail` |
| DW-3.2 | Malformed judge output test: verdict recorded as judge-failure, exit nonzero path covered, no default verdict | COVERED | `test_panel_malformed_output_recorded_as_failure`, `test_adapter_nonzero_exit_raises`, `test_adapter_timeout_raises` |
| DW-3.3 | `score_run` produces a valid ROW_FIELDS row for a fixture run-dir of each rung | COVERED | `test_score_run_row_schema_rung{1,2,3,4}` |
| DW-3.4 | Smoke differential: gold fixture outscores planted-bad fixture on every rung's scorer | COVERED | `test_score_run_rung{1,2,3,4}_gold_outscores_bad` |
| DW-3.5 | One live call per judge CLI parses successfully (cheap, single prompt each) | COVERED | `test_live_codex_parses`, `test_live_agy_parses`, `test_live_sonnet46_parses` (gated behind `RUN_LIVE_JUDGE=1`; manually verified live during discovery — see Prerequisites) |
| DW-3.6 | Judge prompt contains no model/arm identifiers (blind grading, asserted by test) | COVERED | `test_blind_prompt_has_no_model_or_arm_identifiers` |

**All items COVERED:** YES

## Design Decisions

### Design: judge.py's panel()

**Approaches considered:**
1. **One `panel()` with a `mode` switch (binary/graded)** — single entry point, aggregation logic branches internally on mode; judge adapters are pure `str -> str` subprocess wrappers, independently swappable via an injectable `judge_fns` mapping.
2. **Separate `panel_binary()` / `panel_graded()` functions** — mirrors `score_rubric.py`'s `rubric_judge`/`blind_ab` split (one function per grading shape).
3. **A `Judge` class hierarchy** (one subclass per CLI vendor) with a `Panel` orchestrator object.

**Comparison:**
| Criterion | A (one panel, mode arg) | B (two panel fns) | C (class hierarchy) |
|---|---|---|---|
| Interface simplicity | One call site, one mental model | Two call sites, caller must pick the right one | Most ceremony — instantiate 3 judges + a panel object for one call |
| Information hiding | Aggregation strategy (majority vs median) is an internal branch, not exposed API surface | Caller must know which grading shape maps to which function name | Adapter classes leak vendor detail into the call site |
| Matches plan's pinned seam | `panel(artifacts, answer_key, rubric)` — exactly this shape | Would require the plan's Produces line to name two functions (it names one) | Same mismatch |
| Extensibility (new grading mode later) | Add a mode value + one aggregation branch | Add a new function | Add a new class |

**Choice: A.** The plan's Produces line pins a single `panel(artifacts, answer_key, rubric)` entry — a mode-switch keeps that literal signature (mode defaults to `"binary"` as an addition, not a change, since the plan's Produces text doesn't enumerate the modes). Options B/C both required inventing an interface the plan didn't ask for.

**Depth check:**
- Interface methods: 1 public (`panel`), 3 private adapters, 1 private aggregator, 1 private JSON extractor.
- Hidden details: which CLI is invoked and how (codex vs agy vs claude flags), retry-once policy, quorum arithmetic, majority-vs-median branch, blind-prompt template.
- Common case complexity: simple — `panel(report_text, answer_key, rubric_text)` returns a dict; caller never touches subprocess or CLI flags.

### Design: score_run.py's rung dispatch

**Approaches considered:**
1. **One `score_run()` with an if/elif on `manifest["rung"]`**, delegating to four small `_score_build`/`_score_debug`/`_score_review` helpers (build rungs 1-2 share one helper per SCHEMA.md's own "Execution contract (build rungs 1-2)" section).
2. **A registry dict `{1: _score_build, 2: _score_build, 3: _score_debug, 4: _score_review}`** dispatched by lookup instead of branching.
3. **Per-rung modules** (`score_rung1.py`, etc.) imported lazily.

**Comparison:**
| Criterion | A (if/elif + 3 helpers) | B (dispatch dict) | C (per-rung modules) |
|---|---|---|---|
| Interface simplicity | One file, one entry point | Same call site, marginally more indirection for 4 known rungs | Import-time complexity for no benefit at this scale |
| Information hiding | Callers never see the split; unknown rung raises `ValueError` | Same, plus an extra layer to read | Splits one cohesive concept (SCHEMA's rung table) across files |
| Matches SCHEMA.md's own grouping | Mirrors "Execution contract (build rungs 1-2)" directly | Also fine, just more mechanism | Fights the schema's own build-rungs-share-logic framing |

**Choice: A.** Four rungs is not enough branches to justify a registry, and SCHEMA.md itself already groups rungs 1-2 under one execution contract — an if/elif with 3 helpers is the direct translation of that document into code.

**Depth check:**
- Interface methods: 1 public (`score_run`), 1 public loader (`load_manifest`), 3 private per-shape scorers, 2 small private utilities (hidden-suite runner, diff-scope check).
- Hidden details: bun-output parsing regex, the outputs-merged-over-hidden copy step (SCHEMA.md's Execution contract step 4), the fact-match-via-panel loop for rung 4, empty-outputs short-circuit.
- Common case complexity: simple — `score_run(run_dir, load_manifest(task_dir))` returns one ROW_FIELDS-shaped dict for any rung.

### Rung-4 fact-match scope (documented simplification)

Full SWR-Bench-style fact-matching (extracting every claimed finding from a free-form report and matching each to ground truth) is out of scope for this phase's scorer skeleton. Implemented instead: **per-defect graded detection** (panel() in `"graded"` mode, one call per `answer_key["defects"]` entry, median 1-5 score, `>=3` counts as found → TP/FN) plus **one coarse binary "any extraneous finding?" check** for FP. This is a documented, testable approximation — Phase 4's calibration gate (DW-4.6, "rung-4 gold findings achieve full recall through the Phase-3 fact-match") is the checkpoint that would force a revision if this proves too coarse against real Phase-2 tasks; nothing in Phase 3's scope requires more.

## Prerequisites
- [x] Required files exist (or will be created): `judge.py`, `score_run.py`, `test_judge.py`, `test_score_run.py`, `fixtures/**`
- [x] Dependencies available: `codex` 0.142.5, `agy` 1.0.16, `claude` 2.1.199 (all on PATH); `bun` 1.3.14; `python3.14`/`uv` 0.11.21 (code-standards asks for 3.12 via `uv venv .venv -p 3.12` — verified `uv` can provision 3.12 even though the system python is 3.14)
- [x] Live judge-CLI serveability verified manually before design (DW-3.5 / Assumption Verification): `claude -p "Reply with exactly: OK" --model claude-sonnet-4-6 --output-format text --max-turns 1` → `OK`; `codex exec "Reply with exactly: OK"` → `OK` (note: codex prints "Reading additional input from stdin..." to stderr when stdin is a TTY/pipe — adapters pass `stdin=subprocess.DEVNULL` to avoid any hang); `agy --print "Reply with exactly: OK"` → `OK`. All three judges are serveable — **no 2-judge degradation needed**, full 3-judge panel proceeds as designed.

## Recommendation
BUILD. No UPDATE_PLAN needed — the one open assumption (Sonnet 4.6 serveability) resolved positively during discovery, and the rung-3/4 schema gaps are filled by designing self-contained shapes grounded in the plan's own Phase-2 Produces text, per the approach notes' explicit instruction to do so.
