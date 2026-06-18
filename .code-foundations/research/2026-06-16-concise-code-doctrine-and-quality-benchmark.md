# Concise-Code Doctrine + Quality Benchmark

**Summary:** Fold a "prefer concise-but-readable code" first principle into the build agent, and build a ponytail-style benchmark that proves it raises code quality without regressing correctness.

- **Date:** 2026-06-16
- **Status:** Draft (confirmed direction — ready for `/plan`)
- **Still open:** exact wording of the principle; whether to add a rubric-judge metric later; task suite (reuse `tdd-vs-siv` tasks vs new set)

---

## Origin

Triggered by [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) — a "lazy senior developer" ruleset ("the best code is the code you never wrote") with a benchmark we want to learn from. We are **not** adopting ponytail's metrics wholesale, because it measures terseness/cost/speed and code-foundations optimizes for correctness + design quality. We take its **form** and its **doctrine**, scored on what code-foundations is for.

### What ponytail's benchmark does (reference)

| Aspect | Ponytail |
|---|---|
| Tasks | 5 everyday (email validator, debounce, CSV sum, countdown timer, rate limiter) |
| Design | 3 models × 3 arms (no-skill / caveman / ponytail), 10 runs/cell, median |
| Harness | PromptFoo (`npx promptfoo eval -c benchmarks/promptfooconfig.yaml`) |
| Metrics | code reduction (80–94% less), cost (47–77% less), speed (3–6× faster) |

### What we already have

`benchmarks/tdd-vs-siv/` — a skill-eval harness that ran 4 Python tasks × arms × 5 runs, scoring **correctness + mutation (fault detection)** via hidden suite + offline AST mutation (never the agent's own tests as ground truth). This is the correct-shaped base to extend.

---

## Decisions

| Piece | Decision |
|---|---|
| **Doctrine home** | Folded into existing skills — specifically the **build-agent `Baseline Discipline (always on)`** as a first principle. No new standalone skill. **Do not reference aposd.** |
| **The principle** | *Prefer concise code over verbose code, while keeping it readable and maintainable. Reach for built-ins and existing solutions before hand-rolling.* |
| **Scope of the principle** | Governs **implementation / production code only**. Never trims tests (still test beyond the DW floor) and never trims scope (still cannot drop a DW item). |
| **Benchmark form** | ponytail-style: tasks × arms × runs, medians, published BRAG-style results. Extends `benchmarks/tdd-vs-siv/`. |
| **Arms** | code-foundations build **with vs without** the doctrine (A/B on the build agent). |
| **Quality metrics** | **Static** (LOC, cyclomatic complexity, function length, the CC metrics already cited: params ≤7, inheritance depth <3) + **blind A/B** (skill-eval `compare_outputs`, no ground truth needed). Rubric-judge optional, later. |
| **Guardrail** | Correctness + mutation score must **not regress**. Terseness that breaks tests is a fail, not a win. |

---

## The load-bearing tension (resolved)

The build agent's Baseline Discipline already pulls two ways the doctrine touches:

- "Test beyond the DW floor (no ceiling)" → pushes toward **more** test code.
- "Don't gold-plate past what DW requires" + scope clamp → already a partial YAGNI.

Resolution: the concise-code principle applies to **implementation only**. Tests stay thorough; scope stays fixed. The readability/maintainability clause is the explicit counterweight so the principle does not collapse into code-golf. This keeps it non-contradictory with the existing "test beyond DW" and "don't drop scope" rules.

---

## Integration point

`agents/build-agent.md` → **`Baseline Discipline (always on)`** (currently: Scope Latitude, Done-When Traceability, Validation Coverage, Test Anchoring). Add a new subsection for the concise-code principle, plus a design-time check in **Phase 1: Discovery + Design** (look for the built-in / existing seam before designing custom code).

---

## Benchmark design (for `/plan` to detail)

1. **Tasks** — reuse `tdd-vs-siv` Python tasks and/or add a few; consider ponytail's everyday tasks for comparability.
2. **Arms** — `with_doctrine` vs `without_doctrine` build-agent snapshots (skill-eval `old_skill`/`with_skill` pattern; A/B already proven workable here).
3. **Scoring**
   - Correctness + mutation (existing, as guardrail — must not regress).
   - Static: LOC, cyclomatic complexity, function length, CC metric adherence.
   - Blind A/B: `compare_outputs` on paired runs → "which is higher quality."
4. **Report** — medians per arm, BRAG-style, like ponytail.

### Known gotchas (from `tdd-vs-siv`, grug memory)

- System python 3.14 has NO pytest. Use `uv venv -p 3.12` + `uv pip install pytest`.
- Mutation tester MUST gate on the unmutated suite passing first, else a broken env fakes a 1.0 score.
- skill-eval `old_skill` snapshot dir MUST be named after the skill, or `validate_skill` errors. Use a separate `iteration` per extra arm.
- skill-eval grader occasionally throws max-retries / max-turns (~3/60 runs); offline grading is robust to partial runs.

---

## Open questions for `/plan`

1. Final wording of the principle subsection.
2. Task suite: reuse `tdd-vs-siv` set, adopt ponytail's 5, or a blend?
3. Models: sonnet only (cheap) vs add opus for a published claim?
4. Add a rubric-judge metric now or defer?
