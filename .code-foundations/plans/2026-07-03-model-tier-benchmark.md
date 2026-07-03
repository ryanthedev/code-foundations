# Plan: Model-Tier Benchmark Suite (benchmarks/model-tiers)
**Created:** 2026-07-03
**Status:** in-progress
**Started:** 2026-07-03 21:00
**Current Phase:** 1
**Complexity:** medium
---
## Context

The plugin's model-routing rules (fable for judgment-heavy phases, REVIEW one tier below BUILD) were set on priors when Fable 5 / Sonnet 5 entered the ladder — never measured. Two money-bearing questions are open: (1) does Fable 5 earn its ~2x price over Opus 4.8 outside long-horizon work, and (2) does the REVIEW-one-tier-below rule survive measurement? Build `benchmarks/model-tiers/`: a 4-rung suite (easy-build, hard agentic build, debug, review) sampling real phases from the 113-plan/802-phase corpus in `~/repos/*/.code-foundations/plans/`, run over Sonnet 5 / Opus 4.8 / Fable 5 at n=5, graded on correctness (primary), cost (reported `cost_usd`), and speed (secondary).

Research doc (confirmed, binding): `.code-foundations/research/2026-07-03-model-tier-benchmark.md`

## Constraints

- Pre-registered decision rules (research doc) applied verbatim; ties → cheaper model; REVIEW-rule overturn needs the 0/5-vs-≥3/5 capability gap
- Cross-vendor 3-judge panel: codex CLI + agy CLI + Sonnet 4.6; majority (binary) / median (graded); skill-eval `grade: false`
- n=5 runs/cell — never trimmed; effort pinned `medium` on every arm; task-major interleave
- Tasks sourced from the real plan corpus (or grug-documented bugs); native-toolchain hidden suites (corpus ≈80% TS → bun/vitest); every gold solution validated; every planted defect trips a check
- Judges grade written artifacts (report files), never transcripts
- Runs bill subscription quota (verified: no API key; SDK inherits login); rate-limit hit = pause at window boundary; ~$250 reported-cost = runaway tripwire only
- Scope ends at REPORT.md verdicts — no routing-rule edits, no dispatch-template effort fix in this plan
- House benchmark conventions per `docs/code-standards.md` Part 2 (resumable orchestration, module docstrings with seams, offline ground truth, pre-registration)

---
## Chosen Approach
**A — skill-eval MCP drives runs** — session isolation, budget caps, `effort` param, and cost/time metrics are battle-tested across two prior benchmarks; novelty budget goes to tasks + judging, where the research says small benchmarks die. Task-major interleave falls out of `run_eval` call ordering. **Fallback:** custom Agent SDK orchestrator (run_matrix.py descendant) if skill-eval can't express a needed control.

## Rejected Approaches
- **B — custom Agent SDK orchestrator:** rebuilds isolation/budget/cost accounting that skill-eval already validated; more untested harness code is the top contamination risk for verdicts.

---
## Implementation Phases

### Phase 1: Build-rung tasks from corpus
**Model:** sonnet
**Skills:** cc-quality-practices
**Gate:** Full

**Goal:** Port one easy-build and **two** hard-build phases from the real plan corpus into isolated benchmark tasks with hidden native-toolchain suites and validated gold solutions — two on the decision-bearing hard rung so decision rule 2 (majority of the rung's tasks) can fire.

**Scope:**
- IN: corpus phase selection (easy: a sonnet/haiku Minimal-or-Standard phase; hard ×2: opus/Full multi-seam phases, genuinely multi-step); starter fixture extraction into a self-contained workspace; spec.md (DW items only, no solution hints); hidden test suite per task; gold solution; manifest.json; the shared manifest schema all rungs use
- OUT: debug/review tasks (Phase 2); evals.json assembly and any live model runs (Phase 4)

**Edge cases:** hidden suites need dirty tests (error paths, bad data) per DW, not just happy paths — a DW-echo-only suite can't separate models; starter must build/test green before the task change is attempted; TS tasks must not depend on repo-global config outside the extracted fixture.

**Depends on:** none | **Unlocks:** Phase 4
**File scope:** `benchmarks/model-tiers/tasks/01-*/**, benchmarks/model-tiers/tasks/02-*/**, benchmarks/model-tiers/SCHEMA.md`
**Produces:** task dirs + `SCHEMA.md` defining the cross-rung manifest contract (pinned): `manifest.json = {id, rung, source{repo,plan,phase}, toolchain{install,test_hidden}, starter_dir, report_file?, answer_key?}`; hidden suites runnable offline via `toolchain.test_hidden` against `outputs/`.

**Approach notes:** hard-build candidates to screen first: theGrid concurrency fixes, upublish cas-dedup-resume (portability decides); corpus is the population — do not invent tasks.
**File hints:** `~/repos/*/.code-foundations/plans/` — source corpus; `benchmarks/tdd-vs-siv/tasks/` — layout exemplar.

**Done when:**
- [ ] DW-1.1: All three task dirs (1 easy, 2 hard) exist with spec.md, starter/, hidden/, manifest.json conforming to SCHEMA.md
- [ ] DW-1.2: Each gold solution passes its hidden suite from a clean starter copy (command output recorded); each pristine starter is green before the task change
- [ ] DW-1.3: Each hidden suite contains ≥1 dirty test per DW item; each hard task touches ≥2 modules/seams
- [ ] DW-1.4: Each manifest records its source corpus phase (repo, plan file, phase number)

**Difficulty:** MEDIUM
**Uncertainty:** which corpus phases port cleanly — screening may swap candidates

### Phase 2: Debug + review tasks
**Model:** fable
**Skills:** cc-quality-practices, cc-debugging
**Gate:** Standard

**Goal:** Construct **two** rung-3 debug tasks (real documented bugs, deterministically reproduced) and **two** rung-4 review tasks (real phases' implementations with planted DW violations) — every decision-bearing rung (2-4) carries ≥2 tasks so decision rule 2 can fire — each with a machine-checkable answer key.

**Scope:**
- IN: rung 3 ×2 — bug reconstruction of both grug-documented candidates (theGrid stale-write cascade; upublish KV key format), starter workspace with failing repro, `answer-key.json` (root-cause location, allowed-change scope) each; rung 4 ×2 — real corpus phases' committed code + their actual DW lists, ≥3 planted violations each (mix of subtly-unmet DW items and defects hiding behind green tests), answer keys with locations + 5-point detection anchors; a REVIEW-shaped dispatch prompt (execute-first, per-DW evidence, no intent framing) stored as each task's spec
- OUT: judge implementation (Phase 3); pilots/runs (Phase 4)

**Edge cases:** repro must be deterministic — an intermittent bug can't grade n=5 fairly (STABILIZE before porting); planted violations must not be findable from diff shape alone (stratify per SWR-Bench); rung-3 grading needs a diff-scope check so a rewrite-everything "fix" fails.

**Depends on:** none | **Unlocks:** Phase 4
**File scope:** `benchmarks/model-tiers/tasks/03-*/**, benchmarks/model-tiers/tasks/04-*/**`
**Produces:** task dirs conforming to the Phase-1 manifest contract with `report_file` + `answer_key` set; `answer-key.json = {defects:[{id, kind: dw-unmet|hidden-defect|root-cause, location, severity, anchors[5], detectable_via}]}`.

**Approach notes:** all four tasks (both rungs) require `outputs/report.md` — judges grade files, never transcripts (research constraint 5); review-task reviewer sees code + DW list, never the answer key.
**File hints:** grug `thegrid/`, `upublish/` bug memos; `commands/build.md` REVIEW dispatch — the rung-4 shape to mirror.

**Done when:**
- [ ] DW-2.1: Both rung-3 tasks: failing repro command recorded in manifest and reproduces 5/5 times on clean starter
- [ ] DW-2.2: Both rung-4 tasks: ≥3 planted violations each, with location, severity, 5-point anchors in answer-key.json
- [ ] DW-2.3: Every planted violation has recorded evidence it is detectable from task artifacts alone
- [ ] DW-2.4: Self-verifiable gold validation: both rung-3 gold fixes applied to clean starters pass their hidden suites (command outputs recorded); rung-4 gold findings lists enumerate every answer-key defect 1:1 by inspection (cross-phase fact-match and diff-scope checks run in Phase 4 calibration — DW-4.6)
- [ ] DW-2.5: Both rung-4 specs mirror build's REVIEW dispatch (suite-first, per-DW verdict + evidence, PASS/FAIL) with zero plan/intent context

**Difficulty:** HIGH
**Uncertainty:** bug candidates may not port cleanly (env-dependent repro) — grug lists fallbacks (upublish storage-meter double-count, thegrid ghost-windows); a swap keeps the rung at 2 tasks

### Phase 3: Judge panel + scorers
**Model:** sonnet
**Skills:** aposd-designing-deep-modules, cc-defensive-programming
**Gate:** Standard

**Goal:** Build the cross-vendor judge panel and the per-rung scorers that turn a run dir into one CSV row, validated on synthetic fixtures before any live run.

**Scope:**
- IN: `judge.py` — single `panel(artifacts, answer_key, rubric)` entry hiding the three CLI adapters (codex exec / agy --print / Sonnet 4.6 headless) and aggregation (majority binary, median 5-point); `score_run(run_dir, manifest) → row` covering all four rungs (hidden-suite execution; rung-3 diff-scope check; rung-4 fact-match TP/FP/FN vs answer key); ROW_FIELDS CSV schema; synthetic fixture run-dirs + smoke validation
- OUT: task content (Phases 1-2); live matrix orchestration (Phase 4); stats (Phase 5)

**Edge cases:** judge output malformed/timeout → retry once → recorded judge-failure, never a defaulted verdict; 2-of-3 panel quorum when one judge fails, run flagged; empty `outputs/` (agent produced nothing) scores 0, doesn't crash; hidden-suite subprocess timeout bounded.

**Depends on:** none | **Unlocks:** Phase 4, Phase 5
**File scope:** `benchmarks/model-tiers/judge.py, benchmarks/model-tiers/score_run.py, benchmarks/model-tiers/test_judge.py, benchmarks/model-tiers/test_score_run.py, benchmarks/model-tiers/fixtures/**`
**Produces:** `panel()` + `score_run(run_dir, manifest) → dict` conforming to `ROW_FIELDS = [task, rung, model, run_n, correct, score, tp, fp, fn, judge_fail, time_seconds, tokens, cost_usd]` — the Phase 4/5 seam.

**Approach notes:** judge prompts receive artifacts + answer key only, no run metadata (blind to which model produced the artifact — prevents tier bias); reuse `concise-doctrine/score_rubric._judge_subprocess` pattern and `tdd-vs-siv` smoke methodology.
**File hints:** `benchmarks/concise-doctrine/score_rubric.py`, `benchmarks/tdd-vs-siv/harness/grade.py` — patterns to adapt.

**Done when:**
- [ ] DW-3.1: `panel()` unit tests cover majority/median aggregation, disagreement, one-judge-failure quorum, all-fail
- [ ] DW-3.2: Malformed judge output test: verdict recorded as judge-failure, exit nonzero path covered, no default verdict
- [ ] DW-3.3: `score_run` produces a valid ROW_FIELDS row for a fixture run-dir of each rung
- [ ] DW-3.4: Smoke differential: gold fixture outscores planted-bad fixture on every rung's scorer
- [ ] DW-3.5: One live call per judge CLI parses successfully (cheap, single prompt each)
- [ ] DW-3.6: Judge prompt contains no model/arm identifiers (blind grading, asserted by test)

**Difficulty:** MEDIUM
**Uncertainty:** Sonnet 4.6 headless invocation route (claude CLI `--model` vs SDK) — build agent verifies id serveability first (research open item)

### Phase 4: Calibration gate + matrix run
**Model:** sonnet
**Skills:** cc-defensive-programming
**Gate:** Standard

**Goal:** Gate every task through calibration (vet + pilot), then execute the full matrix task-major over Sonnet 5 / Opus 4.8 / Fable 5 at n=5, producing scored CSV rows resumable across rate-limit windows.

**Scope:**
- IN: evals.json assembly from task manifests; model-id serveability check (3 subjects + Sonnet 4.6 judge) before anything else; calibration gate per task (codex/agy adversarial vet → 1 pilot run each on cheapest + priciest model → headroom rule; fail → rewrite loops back to owning phase); matrix via `run_eval(model, effort:"medium", grade:false, runs:5)` in task-major order; `score_run` over every run dir → `results-<task>.csv`; resume-if-done; rate-limit pause; $250 cumulative-cost tripwire
- OUT: task content changes (Phases 1-2 own rewrites); stats/verdicts (Phase 5)

**Edge cases:** run_eval timeout on hard rungs (raise `per_run_timeout_s`, MCP_TOOL_TIMEOUT); mid-matrix rate-limit → pause + resume skips completed cells; a task failing calibration late must not orphan its partial runs (exclude from CSVs); judge-failure rows flagged, not dropped silently.

**Depends on:** Phase 1, Phase 2, Phase 3 | **Unlocks:** Phase 5
**File scope:** `benchmarks/model-tiers/run_suite.py, benchmarks/model-tiers/evals.json, benchmarks/model-tiers/results-*.csv, benchmarks/model-tiers/calibration/**`
**Produces:** completed workspace run dirs + `results-*.csv` (ROW_FIELDS) + `calibration/decisions.md` (per-task vet verdicts, pilot outcomes, accept/reject) — Phase 5 consumes the CSVs only.

**Approach notes:** pilots use the same `run_eval` path as the matrix (no separate code path — pilot rows are real data, marked `pilot`); subscription quota is the binding resource (research: billing verified), so the orchestrator pauses at window boundaries rather than trimming n.
**Rollback:** partial matrix is resumable (skip-if-done); rejected-task rows excluded from CSVs; no state to unwind — quota spent on rejected pilots is the accepted cost of the gate.
**File hints:** `benchmarks/concise-doctrine/run_matrix.py` — resume-if-done pattern; skill-eval MCP docs — house evals.json schema.

**Done when:**
- [ ] DW-4.1: Model-id check recorded: all four ids accepted by a 1-prompt session each
- [ ] DW-4.2: calibration/decisions.md shows vet + pilot outcome per task; every matrix task has headroom (not both-perfect, not both-fail); every task manifest (all rungs) validates against SCHEMA.md
- [ ] DW-4.3: Matrix complete: 3 models × surviving tasks × 5 runs, task-major call order visible in logs
- [ ] DW-4.4: Every run dir scored into results-*.csv; re-invoking the orchestrator after an interruption skips completed cells (demonstrated once)
- [ ] DW-4.5: Rate-limit pause and cost tripwire code paths covered by tests (mocked), events logged when hit
- [ ] DW-4.6: Cross-phase gold validation in calibration: rung-3 gold diff confined to answer-key allowed scope (programmatic); rung-4 gold findings achieve full recall through the Phase-3 fact-match; failures loop the task back to its owning phase

**Difficulty:** MEDIUM
**Uncertainty:** how many tasks survive calibration — matrix size flexes; rate-limit window timing unknowable

### Phase 5: Analysis + REPORT
**Model:** sonnet
**Skills:** cc-pseudocode-programming
**Gate:** Standard

**Goal:** Apply the pre-registered decision rules verbatim to the matrix CSVs and deliver REPORT.md with verdicts on the two open questions.

**Scope:**
- IN: `analyze.py` (pseudocode-first, known-answer tested): paired per-task deltas, fixed-seed bootstrap CIs, per-defect rung-4 detection counts (model × defect × found/5); REPORT.md — verdict per question with the rule text quoted and its inputs shown; speed as median+range (secondary); task→corpus-phase traceability table
- OUT: any routing-rule edits to plan.md/build.md (explicitly downstream, out of plan scope); new runs (Phase 4 owns re-runs)

**Edge cases:** judge-failure rows excluded from correctness stats but counted in a data-quality note; pilot-marked rows excluded from paired stats (pilots exist only for 2 of 3 arms — including them skews n); a rung with <2 surviving tasks can't satisfy the consistent-win rule — verdict degrades to "insufficient data," never a mean-only claim; bootstrap on n=5 pairs reported as intervals, not p-values.

**Depends on:** Phase 3, Phase 4 | **Unlocks:** none — terminal
**File scope:** `benchmarks/model-tiers/analyze.py, benchmarks/model-tiers/test_analyze.py, benchmarks/model-tiers/REPORT.md`
**Produces:** REPORT.md — verdicts for Q1 (Fable-vs-Opus horizon split) and Q2 (REVIEW-one-tier-below), each `change-rule | keep-rule | no-difference→cheaper | insufficient-data`, with rule inputs tabulated.

**Approach notes:** decision rules are quoted from the research doc verbatim — analysis must not invent thresholds; "no measurable difference" is a decisive verdict (buy cheaper), not a failure.
**File hints:** `.code-foundations/research/2026-07-03-model-tier-benchmark.md` § Pre-registered decision rules — the verbatim source.

**Done when:**
- [ ] DW-5.1: analyze.py known-answer tests pass: hand-computable paired-delta case + fixed-seed bootstrap reproducing expected interval on synthetic data
- [ ] DW-5.2: REPORT.md contains one verdict per pre-registered question, rule text quoted, rule inputs shown
- [ ] DW-5.3: Rung-4 per-defect detection table present (model × planted defect × found-count/5) — the Q2 evidence
- [ ] DW-5.4: Speed appears only as median+range labeled secondary; no verdict cites a sub-2x speed gap
- [ ] DW-5.5: Every task row traces to its source corpus phase (repo, plan, phase)

**Difficulty:** MEDIUM
**Uncertainty:** None — inputs and rules are fixed upstream

---
## Test Coverage
**Level:** 100%

## Test Plan
Per-DW (each DW item has a verifying test/command), plus boundary + dirty:
- [ ] T-1.1: Validation script runs each gold solution against its hidden suite from clean starter (DW-1.2) — Integration
- [ ] T-1.2: Manifest schema check: every manifest.json validates against SCHEMA.md (DW-1.1, DW-1.4) — Unit
- [ ] T-1.3: **Dirty:** deliberately broken gold (one-line sabotage) fails its hidden suite — proves suites detect, not echo (DW-1.3)
- [ ] T-2.1: Rung-3 repro loop per task: failing command 5/5 on clean starter (DW-2.1) — Integration
- [ ] T-2.2: Rung-3 gold fixes applied to clean starters pass hidden suites (DW-2.4, self-verifiable half) — Integration
- [ ] T-2.3: Per-violation detection-evidence file exists and is complete for every answer-key defect (DW-2.3) — Unit/inspection
- [ ] T-2.4: answer-key.json schema check: every defect entry carries location, severity, 5-point anchors (DW-2.2) — Unit
- [ ] T-2.5: Rung-4 specs contain the suite-first/per-DW/PASS-FAIL structure and zero plan-context strings (grep assertions) (DW-2.5) — Unit
- [ ] T-3.1: panel() aggregation unit tests: majority, median, split-decision, 1-judge-fail quorum, all-fail (DW-3.1) — Unit
- [ ] T-3.2: **Dirty:** malformed JSON / timeout from a judge CLI → judge-failure recorded, never default verdict (DW-3.2) — Unit
- [ ] T-3.3: Smoke differential per rung: gold fixture > planted-bad fixture (DW-3.4) — Integration
- [ ] T-3.4: Blind-grading assertion: judge prompt string contains no model/arm identifier (DW-3.6) — Unit
- [ ] T-3.5: Live 1-prompt call per judge CLI parses (DW-3.5) — Manual/Integration
- [ ] T-3.6: score_run emits a schema-valid ROW_FIELDS row for a fixture run-dir of each rung (DW-3.3) — Unit
- [ ] T-3.7: **Dirty:** empty review report / empty outputs/ scores 0, doesn't crash (DW-3.3 boundary) — Unit
- [ ] T-4.1: Resume-if-done: kill orchestrator mid-matrix (mocked), re-invoke, completed cells skipped (DW-4.4) — Integration
- [ ] T-4.2: **Dirty:** rate-limit error (mocked 429) → pause + logged event, no data loss (DW-4.5) — Unit
- [ ] T-4.3: **Dirty:** cumulative cost > tripwire (mocked) → halt + logged (DW-4.5) — Unit
- [ ] T-4.4: Boundary: calibration headroom rule at exactly both-perfect and both-fail pilots → task rejected (DW-4.2) — Unit
- [ ] T-4.5: **Dirty:** task failing calibration after partial runs → its rows excluded from results CSVs, exclusion logged (DW-4.6 / Phase-4 edge) — Unit
- [ ] T-4.6: Cross-phase gold validation: rung-4 gold findings full recall via fact-match; rung-3 gold diff within allowed scope (DW-4.6) — Integration
- [ ] T-5.1: Known-answer: hand-computed paired delta + fixed-seed bootstrap interval on synthetic rows (DW-5.1) — Unit
- [ ] T-5.2: **Dirty:** judge-failure rows in input CSV → excluded from correctness, counted in data-quality note (DW-5.2 edge) — Unit
- [ ] T-5.3: **Dirty:** rung with 1 surviving task → verdict "insufficient data," not a mean claim (DW-5.2 edge) — Unit
- [ ] T-5.4: Manual: REPORT.md verdicts cross-checked against rule text by CHECK-style read (DW-5.2)
- [ ] T-5.5: REPORT content checks (programmatic): per-defect detection table present (DW-5.3); speed only median+range/secondary (DW-5.4); task→corpus traceability rows for every task (DW-5.5) — Unit
- [ ] T-5.6: **Dirty:** pilot-marked rows excluded from paired stats; asymmetric-n input raises if a pilot row leaks in (DW-5.1 edge) — Unit
- [ ] T-1.4: Hard-task breadth check: each rung-2 gold diff touches ≥2 modules (programmatic) (DW-1.3) — Unit

---
## Assumptions
| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|---|---|---|---|
| skill-eval accepts the three subject model ids | Medium | Phase 4 (DW-4.1, first action) | Approach B fallback (custom Agent SDK driver) |
| Sonnet 4.6 still API-serveable (judge role) | Medium | Phase 3 (DW-3.5) | 2-judge cross-vendor panel (codex+agy), tie → flagged for human |
| codex + agy work headless non-interactively | High (installed, flags verified) | Phase 3 (DW-3.5) | Same 2-judge/1-judge degradation as above |
| Selected corpus phases port into isolated workspaces | Medium | Phases 1-2 (screening step) | Swap candidates from 802-phase corpus; inventing a task is last resort and flagged in REPORT |
| Subscription quota absorbs ~120 subject sessions (105 matrix + 14 pilots) plus judge calls across windows | Medium | Phase 4 (observed) | User-provided API key (offered) |
| Fable 5 serving stable post-suspension | Medium | Phase 4 pilots | Delay matrix or note capacity caveat on speed axis |

## Decision Log
| Decision | Alternatives Considered | Rationale | Phase |
|---|---|---|---|
| Approach A: skill-eval drives runs | B: custom Agent SDK orchestrator | Validated isolation/metrics; novelty budget goes to tasks+judging | 4 |
| Cross-vendor 3-judge panel | Pinned Sonnet 4.6 single grader | Kills Anthropic-grading-Anthropic self-preference (user decision) | 3 |
| Tasks sampled from real plan corpus | Invented/adapted public tasks | Ecological validity + zero contamination; corpus IS the routed population | 1, 2 |
| Rung 4 mirrors real REVIEW gate | Generic planted-defect PR review | Generic review can't license changing build.md:93-96 (grill Q1) | 2 |
| Pre-registered rules, calibration gate, speed secondary | Post-hoc analysis | Grill decisions 2026-07-03; small-n literature | 4, 5 |
| Sonnet 4.6 = judge, not matrix arm | 4th matrix arm (~25 more runs) | Sonnet 5 strictly dominant per priors; 4.6 has a job as judge | 3 |

---
## Notes
- Model rationale: Phase 2 gets **fable** despite no keyword match — adversarial defect construction is the suite's validity linchpin (HIGH difficulty, judgment-heavy); Phase 1 gate is **Full** because it materializes SCHEMA.md, the cross-phase contract every downstream phase consumes
- The manifest/answer-key/ROW_FIELDS seams are **pinned in phase Produces** so Phases 1-3 build independently — build derives a {1,2,3} wave modulo gate constraints
- Judge prompts are blind: artifacts + answer key only, never model/arm identity
- Pilot rows are real matrix data marked `pilot` — no separate code path
- Task rewrite after calibration failure loops back to the owning phase (1 or 2), then re-pilots
- Scope boundary (research doc): REPORT verdicts end this plan; routing-rule edits and the dispatch-template effort fix are separate downstream changes
- Untrusted-input note: `score_run` executes subject-model-generated code via `toolchain.test_hidden` in a bounded subprocess — same exposure class as skill-eval's own isolated sessions and the two prior benchmarks; accepted with timeout + cwd confinement, not marked Security-sensitive
- Matrix arithmetic (after CHECK rounds 1-2): 7 tasks (1 easy, 2 hard, 2 debug, 2 review — every decision-bearing rung ≥2) × 3 models × 5 runs = 105 runs + 14 pilot runs
- Constraint 8's "module docstrings with seams" is ambient code-standards enforcement applied by every BUILD agent (docs/code-standards.md Part 2), not a per-phase DW
---
## Execution Log
_To be filled during /code-foundations:build_
