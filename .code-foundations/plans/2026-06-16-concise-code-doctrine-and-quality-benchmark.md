# Plan: Concise-Code Doctrine + Quality Benchmark (full-build A/B)

**Created:** 2026-06-16
**Status:** in-progress
**Started:** 2026-06-16
**Current Phase:** 1
**Complexity:** complex

---

## Context

code-foundations has no way to measure whether its build agent produces *quality* (concise-but-readable) code, and wants to adopt a "prefer concise over verbose code, while keeping it readable and maintainable" first principle in the build agent — but only land it if it's proven to help.

The benchmark mirrors ponytail's *form* (tasks × arms × runs, medians, BRAG-style report) but scores what code-foundations is *for*: correctness + fault detection as a guardrail, plus quality (static metrics, blind A/B, rubric judge). The arm variable is `agents/build-agent.md` itself, run through the real gated `/build` pipeline (full-fidelity A/B). The candidate doctrine paragraph is the benchmark's *input* (the "concise" arm); committing it to production `build-agent.md` is **gated** on a GO verdict.

## Constraints

- The doctrine governs **implementation/production code only** — never tests, never scope. The "test beyond the Done-When floor" and scope-clamp rules stay intact.
- **Do not reference aposd** in the doctrine wording.
- Principle wording target: *prefer concise code over verbose code, while keeping it readable and maintainable; reach for built-ins and existing solutions before hand-rolling.*
- Reuse the existing `benchmarks/` + `skill-eval` harness pattern (Python tasks, pytest, offline AST mutation, hidden suites scored offline — never the agent's own tests as ground truth).
- **Correctness + mutation must not regress** between arms — terseness that breaks tests or lowers fault detection is a FAIL, not a win.
- The production edit to `agents/build-agent.md` (Phase 6) is **conditional** on Phase 5's verdict = GO.
- Plan must stay pipeline-compatible: deterministic runner, no interactive prompts mid-run.

---

## Chosen Approach

**B — Full-build-pipeline A/B.** Run the real gated `/build` per task with two `build-agent.md` variants (baseline vs +concise paragraph), across sonnet + opus. Chosen for production fidelity: it measures the doctrine where it will actually live rather than in a proxy skill snapshot. **Fallback:** if the headless build-runner (Phase 3) proves intractable or too noisy, fall back to the tdd-vs-siv snapshot-skill A/B (run the doctrine as an isolated `skill-eval` skill body) — lower fidelity but proven wiring.

## Rejected Approaches

- **A — Snapshot-skill A/B:** lower production fidelity (tests a proxy skill body, not the real build-agent). Kept as the Phase-3 fallback, not the primary path.

---

## Implementation Phases

### Phase 1: Tasks-as-plans + hidden ground truth
**Model:** sonnet
**Skills:** code-foundations:cc-quality-practices
**Gate:** Standard

**Goal:** Assemble the benchmark task suite — the existing 4 tdd-vs-siv Python tasks plus 2-3 new ones — each expressed as a one-phase **plan file** the `/build` command can consume, with an offline hidden suite and a mutation surface.

**Scope:**
- IN: a `benchmarks/concise-doctrine/tasks/<id>/` dir per task with `plan.md` (one phase, DW-IDs), `spec.md`-equivalent inside the plan, `starter/` for modify tasks, `hidden/test_hidden.py` (`test_dw_*` + `test_offdw_*` buckets); a `manifest.json`; 2-3 NEW tasks (e.g. rate-limiter, debounce-equivalent, csv-sum) authored fresh.
- OUT: the runner, scorers, doctrine wording.

**Constraints:** New tasks must have a real mutation surface (multiple branches/boundaries) so fault detection is discriminating — `04-password`-style, not saturated. Hidden suites are ground truth; never shown to the build agent.

**Edge cases:** boundary inputs (empty, max, off-by-one), error paths (bad type, out-of-range) live in `test_offdw_*`; each new task carries ≥1 dirty test in the hidden suite.

**File hints:** `benchmarks/tdd-vs-siv/tasks/` — copy structure/manifest; `benchmarks/tdd-vs-siv/tasks/04-password/` — exemplar with a rich mutation surface.

**Depends on:** nothing — entry phase | **Unlocks:** Phase 3
**Produces:** `benchmarks/concise-doctrine/tasks/` with, per task: `plan.md` (one-phase plan, DW-`{n}.{i}` IDs the build command reads), optional `starter/`, `hidden/test_hidden.py`; and `tasks/manifest.json` = `{ "<id>": {kind: greenfield|modify, impl, tests, hidden, plan} }`.

**Done when:**
- [ ] DW-1.1: Existing 4 tasks are represented in the new suite as build-ready `plan.md` files (DW-IDs present) with their hidden suites carried over.
- [ ] DW-1.2: 2-3 new tasks authored, each with `plan.md`, `hidden/test_hidden.py` (`test_dw_*` + `test_offdw_*`), and (modify tasks) a `starter/`.
- [ ] DW-1.3: Each new task's hidden suite has a non-saturated mutation surface — verified by a thin DW-only suite scoring < 1.0 and a thorough suite scoring 1.0 on a reference impl (mirrors `harness/_smoke`).
- [ ] DW-1.4: `manifest.json` validates — every referenced file exists; `python -c` load check passes.

**Difficulty:** MEDIUM
**Uncertainty:** Whether one-phase plan files drive `/build` cleanly without orchestrator-level scaffolding — resolved early in Phase 3 integration.

---

### Phase 2: Candidate doctrine wording + arm-swap mechanism
**Model:** opus
**Skills:** code-foundations:code-clarity-and-docs
**Gate:** Full

**Goal:** Author the candidate concise-code paragraph as a `build-agent.md` variant, and build a deterministic mechanism to swap the agent file between `baseline` and `concise` arms for a run.

**Scope:**
- IN: the candidate paragraph (a new `Baseline Discipline` subsection + a one-line Phase-1 design-time check); a `concise`-arm copy of `build-agent.md`; a `set_arm(arm)` swap that points the runner at the chosen variant.
- OUT: editing the real `agents/build-agent.md` in place (that's Phase 6, gated).

**Constraints:** Wording governs implementation only; must not contradict "test beyond the DW floor" or the scope clamp. No aposd reference. Apply the "Different Words" test and precision/consistency naming rules — the paragraph must read as obvious doctrine, not aspiration.

**Edge cases:** the swap must be atomic and reversible (restore baseline on exit/failure) so a crashed run never leaves a mutated agent file behind.

**Approach notes:** candidate wording is benchmark *input*, not a production change — production landing is Phase 6, gated on GO.
**File hints:** `agents/build-agent.md` — the `Baseline Discipline (always on)` section (insert subsection) and `Phase 1: Discovery + Design` (design-time check).
**Depends on:** nothing — entry phase | **Unlocks:** Phase 3, Phase 6
**Produces:** `benchmarks/concise-doctrine/arms/build-agent.baseline.md` (verbatim current agent) + `…/build-agent.concise.md` (baseline + paragraph); a swap fn `set_arm(arm: "baseline"|"concise") -> path` that the runner consumes, with guaranteed baseline-restore.

**Done when:**
- [ ] DW-2.1: `build-agent.concise.md` = baseline + the new subsection + the Phase-1 check, diffable to exactly those additions (no other deltas).
- [ ] DW-2.2: The paragraph passes a self-review against code-clarity rules (Different-Words test; no contradiction with existing Baseline Discipline) — recorded in the discovery notes.
- [ ] DW-2.3: `set_arm("baseline")` and `set_arm("concise")` deterministically select the right variant; an injected failure mid-run restores baseline.

**Difficulty:** MEDIUM
**Uncertainty:** Exact wording may shift after Phase 5 evidence; Phase 6 lands the *validated* form.

---

### Phase 3: Headless build-runner
**Model:** opus
**Skills:** code-foundations:cc-routine-and-class-design, code-foundations:cc-defensive-programming
**Gate:** Full

**Goal:** Build a runner that drives the real gated `/build` flow for one (task, arm, model, run) into an isolated sandbox and captures the produced implementation + tests.

**Scope:**
- IN: a CLI that sets the arm (Phase 2 swap), provisions a sandbox from the task's `starter/` (or empty for greenfield), invokes `/build` headlessly on the task `plan.md` with the model pinned, and writes outputs to a stable run dir; capture of turns/cost/status.
- OUT: scoring (Phase 4), matrix orchestration (Phase 5).

**Constraints:** External boundary = the headless agent subprocess and filesystem — validate exit status, missing output files, and turn/cost exhaustion (no empty catch; surface failures as a recorded run status, never silent). Sandbox per run must be isolated (no cross-run bleed, no mutation of the repo's real `agents/build-agent.md` outside the swap). Routines functionally cohesive (provision / run / capture as separate routines), ≤7 params (use a config object).

**Edge cases:** agent hits max-turns or grader max-retries (tdd-vs-siv saw ~3/60) → mark run `partial`, keep whatever impl+tests landed; subprocess timeout; non-zero exit; empty output dir.

**Approach notes:** full gated build includes REVIEW + per-phase commit; runner must tolerate that (or pin a deterministic gate per task plan) — decide and document during discovery.
**File hints:** `benchmarks/tdd-vs-siv/README.md` (run conventions, `.venv` setup); `commands/build.md` (how `/build` consumes a plan); reference docs for headless invocation.
**Depends on:** Phase 1, Phase 2 | **Unlocks:** Phase 5
**Produces:** `run_build.py --task <id> --arm <baseline|concise> --model <sonnet|opus> --run <n> --out <root>` → writes `<root>/<task>/<arm>/<model>/run-<n>/outputs/` (produced `impl` + `tests`) and `…/run-<n>/meta.json` `{turns, cost_usd, status: ok|partial|fail, exit}`.

**Done when:**
- [ ] DW-3.1: A single invocation produces a populated `outputs/` (impl + tests) and a `meta.json` for a greenfield and a modify task.
- [ ] DW-3.2: Arm selection is honored — the build agent's effective instructions differ between `baseline` and `concise` runs (asserted via a marker in the variant).
- [ ] DW-3.3: Failure modes (max-turns, timeout, empty output) yield `status != ok` with the partial artifacts retained, never an unhandled crash and never a mutated real `agents/build-agent.md`.
- [ ] DW-3.4: Runs are isolated — two concurrent invocations don't collide on sandbox or agent-file state.

**Difficulty:** HIGH
**Uncertainty:** Headless execution of the full multi-agent gated build is the riskiest piece; the Phase-2 fallback (snapshot-skill A/B) exists if fidelity/noise makes it impractical.

---

### Phase 4: Scoring extensions
**Model:** sonnet
**Skills:** code-foundations:cc-routine-and-class-design, code-foundations:cc-defensive-programming
**Gate:** Full

**Goal:** Score each captured run on quality (static metrics + LLM rubric judge + blind A/B) while reusing the existing correctness + mutation scorers as the non-regression guardrail.

**Scope:**
- IN: a static-metrics scorer (LOC, cyclomatic complexity, max function length, function count — via `radon`), a fresh-context rubric judge (readability/maintainability rubric → 0-1 + rationale), blind A/B wiring over `skill-eval compare_outputs`, and a thin adapter so existing `harness/grade.py` + `harness/mutate.py` run against the new run-dir layout.
- OUT: executing the matrix (Phase 5).

**Constraints:** Mutation/grade scorer MUST gate on the agent's own suite being green first (a broken env otherwise fakes a perfect score — known gotcha). Validate run-dir inputs at entry (missing files, unparseable Python → recorded `unscorable`, not a crash; no empty catch). Rubric judge is fresh-context (separate from any model under test); blind A/B presents arms unlabeled. Scorers are pure-ish, functionally cohesive routines.

**Edge cases:** `partial` runs (missing tests or impl) → score what's present, flag the rest; non-compiling impl → static + correctness recorded as fail, not exception.

**Approach notes:** prefer the `radon` library over a hand-rolled AST walker — reusing a built-in is the doctrine we're testing, applied to ourselves. Fresh-context rubric judge = an isolated subprocess with no shared state; a warm-context call is a bug, not a variation.
**File hints:** `benchmarks/tdd-vs-siv/harness/grade.py`, `…/mutate.py`, `…/harness/_smoke/` (synthetic validation pattern).
**Depends on:** nothing — builds to the run-dir/row contract pinned in Phase 3's Produces; unit-tested against synthetic fixtures and existing `tdd-vs-siv` runs. Live integration against real Phase-3 output is exercised in Phase 5. | **Unlocks:** Phase 5
**Produces:** `score_static.py --run-dir <d>`, `score_rubric.py --run-dir <d>`, a blind-A/B helper, and a `score_all.py` emitting one row per run: `{run_id, task, arm, model, loc, cc_avg, cc_max, fn_len_max, n_funcs, mutation, hidden_dw, hidden_offdw, rubric_score, status}`.

**Done when:**
- [ ] DW-4.1: Static scorer returns LOC, cyclomatic (avg+max), max fn length, fn count for a known fixture with hand-verified values.
- [ ] DW-4.2: Mutation/correctness adapter reproduces tdd-vs-siv-style scores on an existing `tdd-vs-siv` run, and returns 0/`unscorable` (not 1.0) when the suite is red or the env is broken.
- [ ] DW-4.3: Rubric judge returns a 0-1 score + rationale from a fresh context; blind A/B returns a winner for a paired (baseline, concise) output with labels hidden.
- [ ] DW-4.4: `score_all.py` emits the full row schema for ok and partial runs without crashing on missing artifacts.

**Difficulty:** MEDIUM
**Uncertainty:** Rubric stability across runs — mitigated by reporting it alongside, not instead of, the objective static + mutation signals.

---

### Phase 5: Run the matrix + analyze + report
**Model:** sonnet
**Skills:** code-foundations:cc-quality-practices, code-foundations:code-clarity-and-docs
**Gate:** Standard

**Goal:** Execute the full A/B matrix, aggregate the scores, and produce a BRAG-style report with an explicit GO/NO-GO verdict on the doctrine.

**Scope:**
- IN: orchestrate `arms{baseline,concise} × tasks × models{sonnet,opus} × N runs` via the Phase-3 runner; score via Phase-4 `score_all.py`; aggregate to medians per cell; compute arm deltas; check the guardrail; write `REPORT.md` + results CSVs; state the verdict.
- OUT: editing `build-agent.md` (Phase 6).

**Constraints:** Report medians (not means) per ponytail/tdd-vs-siv convention; state N and caveats honestly (small-N, model set, saturation). The verdict rule is explicit and pre-registered here: **GO** iff concise arm shows a quality improvement (lower LOC/complexity at equal-or-better readability via rubric + blind A/B) **AND** correctness + mutation do not regress beyond noise; otherwise **NO-GO**.

**Edge cases:** dropped/`partial`/`unscorable` runs must be reported, not silently excluded (no silent truncation); if a cell is all-partial, flag it rather than imputing.

**File hints:** `benchmarks/tdd-vs-siv/README.md` (Results table format), `benchmarks/tdd-vs-siv/results-*.csv`.
**Depends on:** Phase 3, Phase 4 | **Unlocks:** Phase 6
**Produces:** `benchmarks/concise-doctrine/results/*.csv` (per-run rows) + `benchmarks/concise-doctrine/REPORT.md` (median table per arm×model, deltas, guardrail check, caveats) ending in a line `VERDICT: GO | NO-GO — <rationale>`.

**Done when:**
- [ ] DW-5.1: The full matrix is executed (or every missing/partial cell is explicitly accounted for) and per-run rows are written to CSV.
- [ ] DW-5.2: `REPORT.md` shows medians per arm×model, arm deltas for every metric, and an explicit guardrail (correctness+mutation non-regression) check.
- [ ] DW-5.3: The report ends with a `VERDICT: GO|NO-GO` line whose rationale cites the pre-registered rule and the actual numbers.
- [ ] DW-5.4: Run accounting is honest — N per cell, partial/unscorable counts, and caveats are stated.

**Difficulty:** MEDIUM
**Uncertainty:** Effect may be small at this N; report states confidence rather than overclaiming.

---

### Phase 6: Conditional integration into build-agent.md
**Model:** sonnet
**Skills:** code-foundations:code-clarity-and-docs
**Gate:** Full

**Goal:** If and only if Phase 5's verdict is GO, land the validated concise-code paragraph into the real `agents/build-agent.md`.

**Scope:**
- IN: insert the validated `Baseline Discipline` subsection + the Phase-1 design-time check into `agents/build-agent.md`; sync any wording refinements the evidence motivated; note the result in the plan's execution log.
- OUT: any change if verdict = NO-GO (record why and stop).

**Constraints:** Precondition — read the verdict from the **last line of `benchmarks/concise-doctrine/REPORT.md`** (`VERDICT: GO | NO-GO — …`); treat **anything other than `VERDICT: GO`** as NO-GO (safe default — matches the test plan's dirty case). If NO-GO, this phase is a documented no-op (record the negative result — that is itself a valid outcome). The landed text must match the validated `concise` arm, governing implementation only; preserve all existing Baseline Discipline rules verbatim.

**Edge cases:** verdict = NO-GO or missing/malformed → write the negative finding to the artifacts below, leave `build-agent.md` untouched; verdict = GO-with-caveats → land but annotate the caveat.

**Approach notes:** human gate — build may pause here for owner confirmation given the conditional nature; the verdict is the evidence.
**File hints:** `agents/build-agent.md`; `benchmarks/concise-doctrine/REPORT.md` (the verdict + final wording source); `benchmarks/concise-doctrine/arms/build-agent.baseline.md` (rollback source).
**Depends on:** Phase 2, Phase 5 | **Unlocks:** —
**Produces:** On **GO** — edited `agents/build-agent.md` (new subsection under `Baseline Discipline (always on)` + one-line check in `Phase 1: Discovery + Design`). On **NO-GO** — no file change; a dated NO-GO entry appended to this plan's `## Execution Log` and a `## Outcome` note at the foot of `benchmarks/concise-doctrine/REPORT.md` recording the negative result + the numbers behind it.
**Rollback:** restore `agents/build-agent.md` from `benchmarks/concise-doctrine/arms/build-agent.baseline.md` (the verbatim Phase-2 snapshot), or `git checkout agents/build-agent.md` — a bad edit silently regresses every future `/build`, so the restore path must be one command.

**Done when:**
- [ ] DW-6.1: On GO, `agents/build-agent.md` contains the validated subsection + Phase-1 check, and a diff shows only those additions.
- [ ] DW-6.2: On NO-GO, `agents/build-agent.md` is unchanged and the negative result is recorded in the execution log.
- [ ] DW-6.3: The landed wording (if any) is byte-aligned with the `concise` arm's paragraph (plus evidence-motivated refinements noted in the log).

**Difficulty:** LOW
**Uncertainty:** None — purely conditional on the verdict.

---

## Test Coverage
**Level:** 100% everywhere. The runner's headless-build path is unit-tested via **subprocess mocking** (deterministic); at least one live end-to-end smoke run per task-kind serves as the integration anchor.

## Test Plan

**Phase 1 — tasks**
- [ ] Unit: each of the 4 ported tasks has a `plan.md` carrying DW-IDs and a `hidden/test_hidden.py` (carried from source, DW-ID scheme aligned), both referenced by `manifest.json` [DW-1.1]
- [ ] Unit: `manifest.json` loads and every referenced path (`plan`, `hidden`, `starter`) exists [DW-1.4]
- [ ] Calibration: per new task, thin DW-only hidden suite scores < 1.0 AND thorough suite = 1.0 on a reference impl [DW-1.3]
- [ ] Unit: each new task's plan carries DW-IDs; hidden suite has both `test_dw_*` and ≥1 `test_offdw_*` [DW-1.2]
- [ ] Dirty: malformed manifest (missing key / dangling file path) → validator fails loudly, not silently

**Phase 2 — doctrine + swap**
- [ ] Unit: `diff(build-agent.concise.md, build-agent.baseline.md)` == exactly the new subsection + Phase-1 check [DW-2.1]
- [ ] Unit: concise paragraph contains no `aposd` token and passes the Different-Words self-check [DW-2.2]
- [ ] Unit: `set_arm("baseline"|"concise")` resolves the correct variant path [DW-2.3]
- [ ] Dirty: injected failure mid-swap restores baseline; `set_arm("bogus")` is rejected [DW-2.3]

**Phase 3 — runner** (subprocess mocked unless noted)
- [ ] Integration (live): one greenfield + one modify task each produce populated `outputs/` + `meta.json` [DW-3.1]
- [ ] Unit: arm marker present in the build differs between `baseline` and `concise` runs [DW-3.2]
- [ ] Dirty: max-turns → `status=partial`, partial artifacts retained [DW-3.3]
- [ ] Dirty: subprocess timeout / non-zero exit / empty output dir → `status=fail`, no unhandled crash [DW-3.3]
- [ ] Dirty: after any run (incl. crash) the real `agents/build-agent.md` is byte-unchanged [DW-3.3]
- [ ] Unit: two concurrent invocations use distinct sandbox + agent-file state [DW-3.4]

**Phase 4 — scorers**
- [ ] Unit: static scorer on a known fixture returns hand-verified LOC / cc-avg / cc-max / fn-len-max / fn-count [DW-4.1]
- [ ] Boundary: empty file, single-function file, deeply-nested function (cc-max) scored correctly [DW-4.1]
- [ ] Unit: mutation/correctness adapter reproduces a known tdd-vs-siv score on an existing run [DW-4.2]
- [ ] Dirty: red suite → `unscorable`/0 (never 1.0); broken env (no pytest) → `unscorable` (never 1.0) [DW-4.2]
- [ ] Unit: rubric judge returns 0-1 + rationale from fresh context; blind A/B picks a winner with labels hidden [DW-4.3]
- [ ] Dirty: partial run (missing impl or tests) → score present pieces + flag rest; unparseable Python → `unscorable`, not an exception [DW-4.4]
- [ ] Unit: `score_all.py` emits the full row schema for both `ok` and `partial` runs [DW-4.4]

**Phase 5 — run + report**
- [ ] Unit (canned rows): median per arm×model and arm deltas computed correctly [DW-5.2]
- [ ] Unit: verdict rule — GO when quality↑ & no regression; NO-GO when correctness/mutation regress; NO-GO when no quality delta [DW-5.3]
- [ ] Boundary: regression exactly at the noise threshold resolves deterministically [DW-5.3]
- [ ] Unit: report states N, partial/unscorable counts; dropped/all-partial cells are flagged, never silently omitted [DW-5.1, DW-5.4]

**Phase 6 — integration**
- [ ] Unit: on GO, `agents/build-agent.md` diff == only the additions; landed text byte-aligned with the concise arm [DW-6.1, DW-6.3]
- [ ] Unit: on NO-GO, `agents/build-agent.md` unchanged + negative result written to execution log [DW-6.2]
- [ ] Dirty: missing/malformed verdict → treated as NO-GO (safe default), no edit applied

---

## Assumptions

| Assumption | Confidence | Verify Before Phase | Fallback If Wrong |
|---|---|---|---|
| The full gated `/build` can be driven headlessly per task | MED | Phase 3 | Fall back to snapshot-skill A/B (Approach A) |
| One-phase `plan.md` files drive `/build` without extra scaffolding | MED | Phase 3 | Add a minimal orchestrator shim or pre-seed the plan |
| `radon` gives the static metrics we want for Python tasks | HIGH | Phase 4 | Custom AST walker (last resort) |
| New tasks expose a non-saturated mutation surface | MED | Phase 1 | Tune task difficulty until thin-suite < 1.0 |
| The doctrine produces a *measurable* quality delta at this N | LOW | Phase 5 | Report honestly as inconclusive; NO-GO |

## Decision Log

| Decision | Alternatives Considered | Rationale | Phase |
|---|---|---|---|
| Full-build A/B (arm = build-agent.md) | Snapshot-skill A/B | Production fidelity; measure the doctrine where it lives | All |
| Reuse + add 2-3 new tasks | Reuse 4 only; port ponytail's 5 | Wider coverage without the cost of porting JS tasks to the Python harness | 1 |
| Sonnet + Opus | Sonnet only | Show the doctrine generalizes across tiers | 5 |
| Static + blind A/B + rubric judge | Static + blind A/B only | User wants the rubric signal now; objective metrics remain the spine | 4 |
| Production edit gated on GO verdict | Edit first, benchmark after | Evidence-before-commit; clean before/after | 6 |
| Fold doctrine into build-agent (no new skill, no aposd) | New standalone skill | User decision; keeps the 19-skill surface | 2, 6 |

---

## Notes

- Known harness gotchas (from tdd-vs-siv, carried forward): system python 3.14 has no pytest — use `uv venv -p 3.12` + `uv pip install pytest`; the mutation tester MUST gate on the unmutated suite being green first or a broken env fakes a 1.0; skill-eval grader occasionally throws max-retries/max-turns (~3/60) — offline grading is robust to partials.
- The `concise` arm's mutation score may saturate at 1.0 (as SIV did), limiting upper-end discrimination; the discriminating signal is expected in static metrics + rubric + any correctness regression.
- Phase 6 is genuinely conditional; build may pause for owner confirmation before landing the production edit.

---

## Execution Log

### Phase 1: Tasks-as-plans + hidden ground truth (Gate: Standard)
- [x] BUILD: Discovery + design + implementation complete
- [x] REVIEW: SKIPPED — tests are gate (Standard)
- [x] Committed
Commit: add154d
Summary: Built `benchmarks/concise-doctrine/tasks/` — 6 build-ready tasks (4 tdd-vs-siv ported to one-phase `plan.md` + hidden suites; 2 new greenfield: `05-rate-limiter`, `06-csv-stats`) with a validated `manifest.json` (adds a `plan` field). New tasks carry non-saturated mutation surfaces (thin DW-only 0.8/0.75 vs thorough 1.0). 49/49 phase-1 validation tests pass. The suite is ready for the runner (Phase 3) to drive `/build` against; each task's hidden suite is offline ground truth.

### Phase 2: Candidate doctrine wording + arm-swap mechanism (Gate: Full)
- [x] BUILD: Discovery + design + implementation complete
- [x] REVIEW: PASS (sonnet) — 25/25, diff is exactly the additions, baseline verbatim, swap atomic + exception-safe
- [x] Committed
Commit: eeee961
Summary: Authored the benchmark's two arms under `benchmarks/concise-doctrine/arms/`: `build-agent.baseline.md` (byte-verbatim copy of the production agent) and `build-agent.concise.md` (baseline + a `### Concise Implementation` subsection + a one-line Phase-1 built-in/concise check — the only deltas, 0 removed lines). Wording governs implementation only, no aposd, explicitly non-contradicting Validation Coverage / Scope Latitude. `arms/swap.py` exposes `set_arm(arm, target)` + `arm_session()` with entry validation, atomic `os.replace`, and try/finally baseline-restore. The `### Concise Implementation` heading is the arm marker Phase 3 (DW-3.2) asserts on. Runner (Phase 3) consumes `set_arm`/the two variants.

### Phase 3: Headless build-runner (Gate: Full)
- [x] BUILD: Discovery + design + implementation complete
- [x] REVIEW: PASS (sonnet, re-dispatched once after a transient API socket drop) — all 4 DW verified
- [x] Committed
Commit: 062dba8
Summary: Built `run_build.py` — drives the REAL gated `/build` headlessly via `claude -p` with the arm's `build-agent` variant injected through a per-run `--plugin-dir` sandbox (feasibility live-probed; snapshot-skill fallback NOT needed). `RunSpec` config object; provision/invoke/capture cohesive routines behind one mockable subprocess seam; status ok|partial|fail with partial artifacts retained; real `agents/build-agent.md` byte-unchanged on every path. 22 mocked unit tests (arm/failure/isolation). **Live cost datum: one greenfield build = 41 turns, $1.28, ~status ok** → full matrix (120 builds) ≈ $150+/24-30h, hence Phase 5 runs DETACHED/OFFLINE. DW-3.1 greenfield proven live (`_live-smoke/`); modify-task live run folded into Phase 5. Follow-up: dead `or True` assert at `test_phase3.py:277` (no coverage gap).

### Phase 4: Scoring extensions (Gate: Full)
- [x] BUILD: Discovery + design + implementation complete
- [x] REVIEW: PASS (haiku) — all 4 DW; guardrail integrity confirmed (red suite → "n/a (suite not green)", never 1.0)
- [x] Committed
Commit: 5a274a0
Summary: Added the quality scorers under `benchmarks/concise-doctrine/`: `score_static.py` (radon LOC/cyclomatic/fn-len/count), `score_correctness.py` (adapts tdd-vs-siv mutation+hidden-suite logic to this manifest; gates mutation on a green suite first), `score_rubric.py` (fresh-context isolated-subprocess rubric judge + blind A/B with arm labels hidden), and `score_all.py` (full per-run row schema for ok+partial runs). **New dependency: `radon`** (installed in `.venv`; record in any offline-run setup). 46 tests pass (1 live rubric gated off), 93 total no regressions. Phase 5 consumes `score_all.py` over the matrix.

### Phase 5: Run the matrix + analyze + report (Gate: Standard)
- [x] BUILD: Discovery + design + implementation complete
- [x] REVIEW: SKIPPED — tests are gate (Standard)
- [x] Committed
Commit: 66a5f99
Summary: Built `run_matrix.py` — detached-safe, idempotent orchestrator for the full-build A/B. Iterates arms×tasks×models×N, calls the runner then `score_all.py`, aggregates medians per arm×model cell, computes deltas, runs the correctness+mutation guardrail, and renders `REPORT.md` ending in `VERDICT: GO|NO-GO` per the pre-registered rule. Honest accounting (partial/unscorable/all-partial flagged). CLI `--dry-run`/`--score-only`/`--report-only`. 47 tests (canned-row aggregation/verdict + mocked-runner full-grid); 140 total, no regressions. `--dry-run` confirms the full matrix = 120 cells. **The live 120-build matrix is a DETACHED follow-up — not executed in-session.** Phase 6 is gated on the verdict it produces.
