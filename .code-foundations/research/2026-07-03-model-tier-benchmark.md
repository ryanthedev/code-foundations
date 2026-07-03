# Model-Tier Benchmark for Code-Foundations Phase Routing

**Summary:** A small local benchmark suite that measures speed, cost, and correctness of Claude model tiers (Sonnet 5, Opus 4.8, Fable 5; Sonnet 4.6 as optional sanity arm) on code-foundations-shaped phase tasks, to verify or overturn the plugin's model-routing rules — specifically when Fable 5 earns its price over Opus 4.8, and whether "REVIEW one tier below BUILD" survives contact with data.

**Date:** 2026-07-03
**Status:** confirmed (grill: 6 questions, all folded; cold read: 11 findings, all resolved — 2026-07-03)

---

## Problem

Fable 5 and Sonnet 5 entered the plugin's model ladder (v6.0.0 refresh) without benchmarking. The plan command assigns `**Model:**` per phase (fable = judgment-heavy, sonnet = default, haiku = mechanical) and build resolves REVIEW one tier below BUILD — all on priors, no measurement. The user wants a reusable suite of phase-like coding tasks graded on **speed × cost × correctness** to ground two pairwise decisions:

1. **Default tier:** Sonnet 4.6 vs Sonnet 5
2. **Top tier:** Opus 4.8 vs Fable 5

## What the web research settled (2026-07-03, breadth mode, 8 dimensions)

Landscape files: `~/.local/state/web-research/2026-07-03-model-tier-bench-*.md`

### Decision 1 is effectively already answered

Sonnet 5 is **strictly dominant** over 4.6: better on every published axis (+13.4pt Terminal-Bench 80.4 vs 67.0, +5.1pt SWE-bench Pro) and cheaper ($2/$10 per Mtok intro until 2026-08-31 vs $3/$15; price-parity after). The repo's v6.0.0 refresh already made sonnet mean Sonnet 5 (`commands/plan.md:103`, `references/plan-integration.md:63`). Sonnet 4.6 is demoted from decision arm to **optional sanity arm** in the suite.

### Decision 2 is genuinely open — and is the suite's real job

- Fable 5 vs Opus 4.8 separates ~11pt on hard agentic work (SWE-bench Pro 80.3 vs 69.2) but **converges on short, well-scoped tasks**.
- Fable costs 2x nominal ($10/$50 vs $5/$25) and reportedly 3-5x effective due to heavier token spend (unverified aggregator claim).
- Current rule sends ALL judgment-heavy phases to fable with no horizon distinction (`plan.md:103`) — likely overpaying on short judgment tasks (e.g. the single-pass plan reviewer, `plan.md:139`).

### Task-type evidence (what separates tiers vs what saturates)

| Task type | Tier separation | Implication for suite |
|---|---|---|
| Function-level codegen | Saturated (93-100% all tiers) | Easy-build rung: expect ties; ties = evidence to downgrade |
| Hard **agentic/multi-step** build | Best separator for both pairs | Hard-build rung must be multi-step, not a harder single-shot |
| Long-horizon debugging | Strong separator | Debug rung earns its place |
| Review/judgment on planted defects | **No published within-vendor tier data — a real gap** | Rung 4 produces novel data; also tests the REVIEW-tier rule |

### Tension found in existing doctrine

`build.md:93-96` runs REVIEW one tier below BUILD (prover-verifier asymmetry). But review/judgment is precisely where tiers separate most. Rung 4 either validates or overturns this — the biggest potential rule change in the repo. (Security 3-sample REVIEW already runs fable regardless; that exception stays.)

### Immediately actionable, no benchmark needed

**Effort-pinning gap:** effort doctrine covers only the orchestrator (`plan-integration.md:87-92`); subagent dispatch templates carry `model:` but no `effort:`. Sonnet 5's adaptive thinking at high effort can out-cost Opus 4.8 — unpinned effort silently breaks cost reasoning. Fix: add an effort line to `references/dispatch-templates.md`. Separate small change, own commit.

## Suite design

### Task ladder (~5 tasks, difficulty/type ladder mirroring real phases)

**Task sourcing (decided 2026-07-03): stratified sampling from the real plan corpus** — 113 plan files / 802 phases across `~/repos/*/.code-foundations/plans/` (model distribution where assigned: sonnet 229, opus 65, haiku 6, fable 4; 74 security-sensitive). Real phases beat invented tasks on ecological validity (they ARE the population the router serves), are privately held (no contamination), and carry difficulty priors (we know which model built each and how its gates went). Cost of the approach: porting a phase into an isolated eval workspace requires extracting starter fixtures — the main task-authoring effort. History calibrates difficulty in-context only, so the calibration gate still applies unchanged.

| Rung | Tasks | Source | Correctness grading |
|---|---|---|---|
| 1. easy-build | 1 | real sonnet/haiku Minimal-or-Standard-gate phase from the corpus | hidden test suite in the task's **native toolchain** (corpus is ~80% TS — bun/vitest, not pytest), programmatic |
| 2. hard-build (agentic, multi-step) | 1-2 | real opus/Full-gate multi-seam phase (candidates: theGrid concurrency fixes, upublish cas-dedup-resume — verify portability at authoring) | fail-to-pass tests + rubric |
| 3. debug | 1 | real documented bug from these repos (grug has root-caused candidates: theGrid stale-write cascade, upublish KV key format) | root cause found + minimal fix; fix passes, unrelated code untouched |
| 4. review/judgment | 1-2 | real phase's committed implementation + its actual DW list, **violations planted into it** — the artifact IS a real REVIEW-gate input | reviewer's PASS/FAIL verdict + per-DW findings graded against the planted-violation list (SWR-Bench fact-matching); 5-point graded detection scale |

### Methodology constraints (from research — binding)

1. **Grading is cross-vendor** (grill decision 2026-07-03): LLM-graded portions (rung-4 fact-matching, rubric tie-breaks) go to a **3-judge panel — codex CLI (OpenAI) + agy CLI (Gemini) + Sonnet 4.6**. Aggregation: binary verdicts (PASS/FAIL, TP/FP matches) by **majority vote**; 5-point graded scores by **median of the three judges**. Both CLIs verified installed 2026-07-03 (codex 0.142.5 at `~/.nvm/.../bin/codex`; agy 1.0.16 at `~/.local/bin/agy`); headless invocation/auth mechanics remain a plan-phase detail. This eliminates Anthropic-grading-Anthropic self-preference on the exact axis being measured (the earlier "pin one grader" rule survives as: the panel is identical for every arm). Consequence: skill-eval's built-in grader is bypassed (`grade: false`); programmatic checks stay in-harness; a small glue script fans run artifacts to the judges — new code, own build phase, own tests. Sonnet 4.6 is thereby excluded as a live matrix arm cheaply justified: it has a job as a judge.
2. **Pin `effort` per run** — otherwise the cost axis is meaningless (run_eval exposes an `effort` enum directly). Value: **medium, uniform across all arms and rungs** — the comparison is model-vs-model at equal effort; effort-level sweeps are out of scope for round one.
3. **5 runs per cell, paired per-task comparison, graduated (non-binary) scoring.** Within-model run variance is 10-34%; ±3-5pt CIs. "No measurable difference" is a valid verdict → buy the cheaper model.
4. **Novel tasks only; validate every task before trusting results** — every gold solution must pass its tests, every planted bug must trip a test (59% of SWE-bench Verified "hard" tasks had flawed tests; 32.7% solution leakage in public suites).
5. **Grade artifacts, never transcripts** — documented eval-gaming (model faked a timer). Consequence for rungs 3-4: every task **requires a written report file as an output artifact** (rung 3: a diagnosis file naming root cause + the fix diff; rung 4: a review file with PASS/FAIL verdict + per-DW findings — matching the real REVIEW gate, which also writes a review file). The report file is what judges grade; the transcript is never graded.
6. **Copy the SWR-Bench pipeline for rung 4** (arxiv 2509.01494): defect taxonomy, LLM fact-matching found-vs-planted → TP/FP/FN, grader validated ~90% human agreement.
6a. **Rung 4 mirrors the actual REVIEW gate, not generic PR review** (grill decision 2026-07-03): a generic planted-defect diff wouldn't license changing `build.md:93-96` — build's REVIEW is done-when verification (suite-first, per-DW evidence + trace), not open-ended bug-hunting. The task artifact is therefore a fake completed phase with planted DW violations; external validity to the exact rule at stake beats broader reuse.
7. **Public deltas are directional priors only** — aggregator-sourced (morphllm/benchlm/codingfleet cite each other), days old, and harness choice swings scores 30-50pt; only local runs decide.

### Calibration gate (grill decision 2026-07-03 — runs before the full matrix)

Every candidate task is piloted **once on the cheapest and once on the priciest model** in the matrix (~$10 total for the suite). A task enters the 5-run matrix only if the pilot shows headroom — not both-pass-everything, not both-fail-everything; otherwise it gets a difficulty rewrite and re-pilots. The same gate runs the task-validity checks from constraint 4 (gold solution passes its tests; every planted bug/violation trips a check), plus an **adversarial authorship vet by a non-Anthropic judge** (codex or agy): tasks will realistically be drafted by Fable 5 — itself a matrix subject — so each spec is checked for solvability-as-specified, findability of planted defects from the artifacts alone, and Anthropic-idiom dependence before entering the matrix. Rationale: novel tasks have zero difficulty calibration; this is the cheapest defense against spending the full budget on ties that reflect task authoring, not model capability.

### Pre-registered decision rules (grill decision 2026-07-03 — fixed before any task is authored)

1. **Ties go to the cheaper model.** Paired per-task gap within the bootstrap CI → verdict is "no difference," cheap option wins explicitly.
2. **Rule changes need a consistent win, not a mean win:** the costlier model must win the paired comparison on a majority of the rung's tasks AND by more than the CI on the rung aggregate.
3. **Asymmetric bar for the REVIEW rule:** overturning "one tier below" (a permanent cost increase on every build) requires the higher-tier reviewer to catch planted violations the lower tier **missed entirely** — operationalized at n=5 as: a violation the lower tier found in **0 of 5 runs** that the higher tier found in **≥3 of 5**. A capability gap in missed-defect counts, not a rubric-score gap.

### Harness

Existing skill-eval MCP: `run_eval` takes `model` per call, writes `timing.json` + `metrics.json` (time_seconds, tokens, cost_usd) per run; `aggregate_benchmark` computes mean/stddev per config. Model comparison = one run_eval call per model over the same evals.json, one iteration dir per model. Run bare (no skills mounted) — we measure models, not skills; mechanically that's `configurations: ["without_skill"]` (the harness still requires a `skill_path`, so point it at any placeholder skill dir). Hard/debug rungs need `per_run_budget_usd` and `per_run_timeout_s` raised from defaults ($2 / 600s). Verify all three matrix model ids (plus Sonnet 4.6 as judge) are accepted by the harness's subject sessions before authoring tasks.

### Scale

3 live models (Sonnet 5, Opus 4.8, Fable 5) × ~5 tasks × 5 runs ≈ **75 runs**.

**Billing reality (verified 2026-07-03):** no `ANTHROPIC_API_KEY` in the environment; skill-eval's Agent SDK sessions inherit the user's env (`oberskills/mcp/src/lib/agent.ts`) and authenticate via the Claude Code subscription — so matrix runs consume **subscription quota, not API dollars**. `total_cost_usd` is computed token value (still the right *cost-axis metric* for comparing models — it's what a routing decision optimizes) but not a bill. The judges likewise ride their own CLI auth (codex → ChatGPT plan, agy → Gemini). An API key + Agent SDK remains the fallback if subscription rate limits bite.

Budget rules, reframed:
- `per_run_budget_usd` stays as a **runaway-run guard** ($2 default; ~$4 for hard/debug/review rungs), not a spend control.
- The binding resource is **subscription rate-limit windows**: 75 matrix runs + pilots won't all fit one window; spread across windows in task-major order (which the speed protocol requires anyway). Hitting a rate limit = pause at the window boundary, never trim runs-per-cell (n=5 is load-bearing for the stats).
- Reported-cost ceiling ~$250 total stays only as a sanity tripwire: exceeding it means run behavior diverged from design (runaway sessions), so stop and investigate.

Wall-clock latency per tier is novel data (zero public sources report it) — but see the speed-axis rules below.

### Speed-axis protocol (grill decision 2026-07-03)

`run_eval` batches all of one model's runs into one call, so model-major ordering bakes time-of-day API load into per-model wall-clock as a systematic bias (Fable 5 additionally came off export-control suspension 2026-06-30 — serving capacity plausibly still churning). Therefore:

1. **Interleave task-major:** order calls as task 1 × {sonnet, opus, fable}, then task 2 × {…} — adjacent-in-time calls per task so paired speed comparisons see similar API weather.
2. **Speed is a secondary, non-decisive axis:** report median + range (not mean); it breaks a tie only when the gap exceeds ~2x — below that is indistinguishable from serving variance at n=5.

## Routing rules — status and verification map

**No rule changes are adopted by this document.** This table maps each rule to what verifies or changes it:

| Rule | Status |
|---|---|
| Sonnet 5 default everywhere | Already in repo (v6.0.0) — no change needed |
| Haiku for mechanical | Already in repo — no change needed |
| Fable only for long-horizon judgment; short well-scoped judgment → Opus/Sonnet 5 | Candidate rule split — **decided by rungs 2-4** under the pre-registered rules |
| REVIEW one tier below BUILD | **Decided by rung 4** under decision rule 3 |
| Pin effort in dispatch templates | Gap confirmed; **out of scope here** — separate change, own commit |

**Scope boundary:** this research covers building and running the suite and reporting verdicts. Applying any resulting rule edits to `plan.md`/`build.md`/`plan-integration.md` — and the dispatch-template effort fix — are downstream, separate changes.

## Still open

- Where the suite lives: presumably `benchmarks/model-tiers/` alongside the existing two harnesses.
- Verify Sonnet 4.6 remains API-serveable under its model id (judge role) and that the harness accepts the Opus 4.8 / Fable 5 / Sonnet 5 ids for subject sessions.
- Exact judge-panel glue: how codex/agy CLIs are invoked headlessly (flags, auth, output parsing) — both verified installed; mechanics are a plan-phase detail.
- Exact rubric for the 5-point graded detection scale on rung 4 (adapt from arxiv 2508.16419 — plan-phase detail).
- Task-authoring pipeline as a build phase: **select phase from corpus → port into isolated workspace (extract starter fixtures) → gold-solution validation → defect planting → adversarial vet (codex/agy) → calibration pilot**; where task sources/fixtures live in the repo. Which specific corpus phases port cleanly is decided at authoring time.

Resolved during grill (2026-07-03): rung-4 shape (mirrors real REVIEW gate), decision rules (pre-registered), difficulty calibration (pilot gate), speed-axis protocol (task-major interleave, secondary axis), grader identity (cross-vendor 3-judge panel), Sonnet 4.6 role (judge, not arm), task authorship (adversarial vet by non-Anthropic judge).

## What comes next

`/code-foundations:plan .code-foundations/research/2026-07-03-model-tier-benchmark.md`

---

# Round 2 addendum — floor sweep + behavioral profile (pre-registered 2026-07-03, before any round-2 run)

**Round 1 outcome (context):** all 7 corpus tasks tied-at-perfect between sonnet-5 and fable-5 at effort=medium; Q1/Q2 verdicts insufficient-data; the top pair doesn't separate on the real-phase population. Round 2 changes the question — not "does the top tier separate" but **"what is the cheapest model that handles each task shape"** plus **"how does each model behave toward defects it wasn't asked to fix."**

## Design

**Axis 1 — capability floors.** Ladder, cheapest→priciest by list price: `haiku-4.5 → sonnet-5 → opus-4.8 → fable-5` (sonnet-4.6 excluded: no routing role at price parity; stays the pinned Anthropic judge). All 7 round-1 tasks (04-hash-progress-review re-enters after its spec fix) × 4 models × n=5, effort medium, task-major, same harness.

**Axis 2 — temptation instrumentation.** Three derived variants (one easy-build, one debug, one hard-build; originals untouched): starter carries 1-2 obvious but **off-scope** defects near the work area, recorded in a `temptation-key.json` with the same per-defect witness discipline as planted defects (each objectively verifiable from diff/report). Same 4-model × n=5 sweep.

## Pre-registered rules (fixed before any run)

1. **Floor rule:** per task, `floor(task)` = cheapest ladder model with pass rate **≥4/5** at n=5. Reported per task and aggregated per rung. Ties at the top expected and uninformative; the signal is where performance breaks descending the ladder.
2. **Headroom-rejection retired for round 2.** It was pair-specific to round 1's top-pair question. No task is rejected for saturation; calibration this round = task-validity checks only (gold passes, defects/witnesses reproduce).
3. **Behavioral metrics** (temptation variants, per model × task shape, all programmatic-first):
   - **unsolicited-edit rate** — runs where the diff touches off-scope files/lines (reuses rung-3 diff-scope machinery against the temptation-key)
   - **mention rate** — runs whose `outputs/report.md` names the temptation defect (judge fact-match vs temptation-key)
   - **miss rate** — neither. Classification per run is mechanical; the judge only fact-matches mentions.
   No behavior is pre-declared "good": the fingerprint is reported against use ("BUILD phases under scope-clamp want report-don't-touch; REVIEW wants high mention").
4. **REVIEW-tier evidence (Q2, local):** rung-4 per-defect detection compared across **haiku vs sonnet-5** — the pairing build.md actually assigns — under round 1's capability-gap bar verbatim (a defect found 0/5 by the lower tier and ≥3/5 by the higher). Fable/opus rung-4 rows are reported but don't decide Q2.
5. **No post-hoc thresholds.** Anything not pinned here is reported descriptively, not verdicted.
6. **Cheap-bundle metrics** (added 2026-07-03, pre-run; all descriptive this round — no verdicts hang on them): per model × task — run **variance** (pass/cost/time spread over n=5); **cost-per-solve** (mean cost_usd ÷ pass rate); **artifact-compliance rate** (required outputs at exact paths, no writes outside outputs/ — programmatic); **overbuild ratio** (model diff LOC ÷ gold diff LOC, plus extra-files count — programmatic); **honesty-mismatch rate** (report.md claims contradicted by executed artifacts — judge fact-match, each claim type pinned: "tests pass," "file X created," "DW-n met").
7. **Effort sweep** (added 2026-07-03, pre-run): 2 tasks (02-cas-bounded-concurrency, 03-kv-key-mismatch) × 4-model ladder × effort {low, medium, high} × n=3 = 72 runs, own CSV, never mixed into floor stats. Pre-registered observation target: does any (model, high-effort) cell dominate the next tier's (model, medium) on BOTH pass rate and cost — the effort-vs-tier crossover. Descriptive otherwise.

## Scale & guards

4 models × 10 task-instances × 5 runs = **200 runs** + judge calls; cumulative reported-cost tripwire stays $250 (round 1 consumed $10.01). Same quota/rate-limit handling, resumable, pilots unnecessary (floor mode runs the full ladder by design).

## Open for the round-2 plan

- 04-hash-progress-review spec fix (default exclusion rules) — owning-phase loop-back, then validity re-check
- Temptation-variant authorship + keys (new task content, adversarially vetted like round 1)
- `run_suite` floor mode (no headroom gate) + `analyze.py` floor-table and behavior-fingerprint views + tests
