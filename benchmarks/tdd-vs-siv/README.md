# TDD vs Stub-Implement-Validate — agent doctrine A/B

A benchmark comparing two build-agent doctrines for AI coding agents:

- **TDD** (`old_skill`): for each Done-When (DW) item, write a failing test first, then minimum code to pass (red-green). Tests scoped to DW items.
- **SIV** (`with_skill`): stub the interface → implement → write tests *after* that validate the DW items **and** important behavior beyond them.

The two doctrines are the same skill (`build-doctrine`) with two bodies (`build-doctrine/` = SIV, `snapshots/tdd/build-doctrine/` = TDD), minimal-diff so the only variables are test *timing* and test *scope*.

## Why

Hypotheses (from the project owner):
- **H1** — dropping test-first costs no code quality.
- **H2** — TDD produces "useless tests" (low fault-detection).
- **H3** — TDD doesn't test the right things: it anchors tests to the enumerated DW items.

Grounding research (see commit history / agent briefs): the controlled-experiment literature finds test-first vs test-after **ordering is near-neutral for code quality** (Fucci et al., IEEE TSE 2017; Karac & Turhan 2018); what drives quality is the *amount* of testing (Erdogmus 2005). **Mutation score** is the metric tied to real fault detection (Just et al., FSE 2014) and is the only one that catches implementation-anchored tests — coverage cannot (Inozemtseva & Holmes 2014). No mainstream agent benchmark measures agent-written test quality.

## Design

- **Harness:** `skill-eval` MCP (`run_eval`) runs each doctrine as an isolated headless session per task; everything written lands in `outputs/`. Ground truth (hidden suites + mutation) is scored offline — never by the agent's own tests.
- **Tasks** (`tasks/`): 2 greenfield (`01-duration`, `02-rpn`), 2 modify-existing (`03-inventory`, `04-password`). Each has a `spec.md` (what the agent sees, DW items only) and `hidden/test_hidden.py` (ground truth, `test_dw_*` + `test_offdw_*` buckets). Modify tasks ship a `starter/`.
- **Runs:** 4 tasks × {SIV, TDD} × 5 runs = 40 sessions, model `sonnet`, iteration 2.
- **Metrics** (`harness/grade.py`, `harness/mutate.py`):
  - `mutation_score` (HEADLINE) — AST-mutant kill-rate of the agent's own tests vs its own code. Gated on the agent's suite being green first.
  - `n_agent_tests` — breadth proxy.
  - `hidden_dw` / `hidden_offdw` — correctness of the agent's *implementation* on DW-derivable / unspecified-edge behavior.

## How to run

```bash
uv venv .venv -p 3.12 && uv pip install --python .venv/bin/python pytest
# (via skill-craft) run_eval per eval id, configurations [with_skill, old_skill], old_skill_path=snapshots/tdd/build-doctrine
.venv/bin/python harness/grade.py --runs-root build-doctrine-workspace/iteration-2 --eval 02-rpn --out results-02-rpn.csv
```

The harness was validated before any LLM runs via synthetic runs under `harness/_smoke/` (a thorough suite scores 1.0, a thin DW-only suite 0.8 on identical code).

## Results (iteration 2, n=5/arm/task)

| Task | Arm | Avg #tests | Mutation | Correctness (hidden DW) |
|---|---|---|---|---|
| 01-duration | SIV | 13.0 | 1.000 | 1.000 |
| 01-duration | TDD | 3.0 | 0.943 | 1.000 |
| 02-rpn | SIV | 15.0 | 1.000 | 1.000 |
| 02-rpn | TDD | 6.2 | 1.000 | 1.000 |
| 03-inventory | SIV | 9.2 | 1.000 | 1.000 |
| 03-inventory | TDD | 3.6 | 0.920 | 1.000 |
| 04-password | SIV | 13.4 | 1.000 | 1.000 |
| 04-password | TDD | 2.8 | 0.500 | 1.000 |
| **Overall** | **SIV** | **12.7** | **1.000** | 1.000 |
| **Overall** | **TDD** | **3.9** | **0.841** | 1.000 |

### Findings

- **H1 confirmed** — correctness is a wash (hidden-DW 1.000 both arms). SIV costs no code quality. Matches the literature: ordering is neutral on correctness.
- **H2 confirmed** — TDD test suites caught fewer seeded faults (mutation 0.841 vs 1.000). `04-password` is the standout: TDD's ~2.8 tests killed only **half** the mutants — the digit/uppercase/length branches go under-tested because the DW examples don't exercise the mutation surface.
- **H3 confirmed, strongly** — SIV wrote **~3.3× more tests** (12.7 vs 3.9), on every task. TDD writes ≈one test per DW item and stops; SIV explores edges the DW list never named. This is the causal chain behind H2: SIV doctrine → more testing → more faults caught (Erdogmus's "amount of testing" mechanism).

### Caveats

- Small: n=5/arm/task, 4 small tasks, `sonnet` only. SIV's mutation **saturated at 1.000** (ceiling) — the benchmark can't distinguish gradations of SIV quality; all discrimination is in TDD's shortfall.
- The A/B bundles two variables (test-first+DW-scoped vs test-after+beyond-DW). A factorial (test-after-but-DW-scoped) would isolate ordering from scope. The literature says ordering is neutral, so the *scope freedom* is doing the work — which is exactly H3.
- `hidden_offdw` (impl robustness on unspecified edges) is noisy for `01-duration` (arbitrary conventions like order-independence) and was de-emphasized; it is ~equal across arms (~0.86) — both impls are about equally robust on unspecified behavior.

## Iteration 3 — isolating ordering from scope (the factorial)

The iteration-2 TDD arm scoped tests to the DW items ("that is the test suite") — a *scope* constraint, not inherent to TDD. So iter-2 confounded **ordering** (first/after) with **scope** (DW-only/beyond). Iteration 3 adds a third arm, **TDD-unscoped** (`snapshots/tdd-unscoped/`): test-first red-green, but explicitly free to test beyond the DW list — same scope freedom as SIV. 4 tasks × 5 runs = 20 runs.

| Arm (ordering, scope) | Avg #tests | Mutation | Correctness |
|---|---|---|---|
| SIV (after, beyond) | 12.7 | 1.000 | 1.000 |
| TDD-scoped (first, DW-only) | 3.9 | 0.841 | 1.000 |
| **TDD-unscoped (first, beyond)** | **13.3** | **0.988** | 1.000 |

**Lifting the DW-only ceiling off TDD closes the entire gap.** TDD-unscoped ≈ SIV on every metric. Ordering (test-first vs test-after) is ~neutral; the lever is the *scope freedom to test beyond the enumerated acceptance items*. Matches the literature (Fucci 2017: ordering neutral; Erdogmus 2005: amount-of-testing drives quality).

Secondary signal: TDD-unscoped was more turn-expensive — 2/20 runs hit the 50-turn cap (red-green per edge case costs turns); SIV had zero turn-exhaustion. A mild efficiency edge for test-after, not a quality one.

### Conclusion

For an AI coding agent, **the quality lever is "test beyond the Done-When items," not the test ordering.** Test-first and test-after produce equal correctness, breadth, and fault-detection *once both are told the DW items are a floor, not a ceiling*. The original "TDD is worse" result was an artifact of a scope constraint wrongly attributed to TDD.

Implication for `code-foundations`: the load-bearing edit is the **"floor, not ceiling"** instruction in the build doctrine (applies under either ordering). The switch to Stub-Implement-Validate is defensible on a minor efficiency margin (fewer turns, no quality cost) but is **not** itself the source of the benefit.
