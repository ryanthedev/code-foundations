# Single-Skill Adherence — with-skill vs without-skill

**Question:** when a skill is loaded, how well does the produced code follow that skill's
checklist — and does loading the skill measurably change the code vs not loading it?

**Design:** 3 skills, each on a best-fit task, **with-skill vs without-skill** (Minimal gate,
build agent only, sonnet, n=5/condition = 30 runs, all `ok`). Two instruments:
- **Adherence rubric** — a fresh-context judge scores each *applicable* checklist item
  satisfied/partial/violated → adherence fraction. Applied to BOTH conditions (the without
  condition graded against the same skill's checklist = baseline the model reaches anyway).
- **Objective backstop** per skill: defensive→adversarial hidden inputs; control-flow→static
  cyclomatic complexity + function length; clarity→readability rubric + LOC.

## Results

| Skill (task) | Adherence with | without | Δ | Objective signal (with → without) |
|---|---|---|---|---|
| cc-defensive-programming (password) | 0.90 | 0.89 | **+0.01** | hidden adversarial inputs **5/5 both** (saturated) |
| cc-control-flow-quality (rpn) | 0.97 | 0.98 | **−0.02** | cc_avg **3.7 ← 5.8**, fn_len_max **14.2 ← 32.4** |
| code-clarity-and-docs (rate-limiter) | 0.96 | 0.93 | **+0.03** | LOC +8.8 (docs), readability 0.93 vs 0.94 |

## Findings

1. **By the adherence rubric, loading a skill barely moves the needle (Δ ≈ ±0.02).** The reason is
   not that skills fail — it's that **baseline adherence is already 0.89–0.98 without the skill.**
   These are mainstream CC/APOSD principles (validate inputs, short functions, clear names) that
   sonnet already applies by default. There is little ceiling left for the skill to add *on this
   rubric*.

2. **But the objective ruler tells a different, more reliable story for control-flow.** Loading
   cc-control-flow-quality **cut average cyclomatic complexity ~36% and max function length ~56%**
   (32→14 lines), with clean run-level separation (with fn_len ∈ [8,18]; without ∈ [21,41] — no
   overlap). The skill demonstrably changed the code toward shorter, simpler routines — an effect
   the holistic adherence rubric (which rated both ~0.97) was **too lenient to capture.** It even
   scored the with-skill arm marginally *lower*, confirming the rubric is noisy near ceiling.

3. **A concrete item that is NOT followed even when the skill is loaded:** cc-defensive-programming's
   GC-2 ("document pre/postconditions with assertions") was the top cited gap in **all 10 runs** —
   with and without. The agent consistently substitutes `raise`/type-checks/docstrings for
   `assert`. The one place the skill *did* help: the lone without-skill run that omitted a None/type
   guard (GC-1) had no counterpart in the with-skill arm (0/5 with vs 1/5 without missed it).

4. **LLM-judge metrics saturate; objective metrics discriminate.** This is the third metric in this
   benchmark family to hit a ceiling (after mutation and the readability rubric). The adherence
   rubric is a weak instrument when the model is already near-compliant — the static/behavioral
   metric is what reveals the skill's real effect.

## Verdict per skill

- **cc-control-flow-quality — FOLLOWED, with a large measurable effect.** Best demonstration that a
  skill changes the produced code. Use the objective metric, not the rubric, to see it.
- **cc-defensive-programming — mostly already-known; marginal effect.** Skill closes the occasional
  input-guard miss but does not enforce its assertion item (GC-2) even when loaded.
- **code-clarity-and-docs — mostly already-known; small positive.** Adds documentation (LOC↑) at
  near-flat readability; adherence +0.03 within noise.

## Caveats

1. **n=5** — control-flow's static separation is robust at this N; defensive/clarity deltas are
   within noise.
2. **Adherence rubric is near-ceiling and lenient** (see finding 4). Treat it as a floor check, not
   a fine discriminator. The objective per-skill metric is the spine.
3. **Defensive's adversarial backstop saturated** (5/5 both) — the existing off-DW hidden bucket is
   too easy. A harder hostile-input suite (None, non-str, unicode, huge inputs) would discriminate.
4. **Single task per skill.** The effect could be task-specific; control-flow's result should
   replicate on a second branchy task before being treated as general.

## Follow-up done (2026-06-19)

**The "GC-2 gap" was a judge error, not a skill or agent failure.** GC-2 ("document
pre/postconditions with assertions") was cited as violated on boundary-validation code —
but the skill's OWN GC-3/RF-9 forbid assertions for expected/external input (use `raise`).
The with-skill impls correctly `raise TypeError` at the boundary and return `False` for
invalid passwords; adding `assert` would VIOLATE the skill. No skill change made (forcing
assertions would be wrong); the defect was the LLM judge over-applying an internal-invariant
item. Recorded honestly rather than "fixed."

**Objective adversarial probe (`probe_defense.py`) — replaces the saturated rubric for
defensive.** Feeds 12 hostile inputs (None, non-str, bytes, unicode, null-byte, huge, …) to
each password impl and scores graceful-handling vs crash — deterministic, no LLM:

| condition | robustness (mean) | per-run | crashes |
|---|---|---|---|
| with cc-defensive-programming | **1.000** | [1,1,1,1,1] | none |
| without (control) | 0.983 | [1, 0.917, 1, 1, 1] | 1 run crashed on `bytes` |

**Δ = +0.017.** Small, because the no-skill baseline is already very robust (sonnet guards
inputs by default) — but unlike the rubric (which saturated ~0.9 both and mis-scored GC-2),
this metric *discriminates*: the skill made the GC-1 input-type guard universal (5/5 vs 4/5),
and the one unguarded run crashed on `bytes` (`int.isdigit` AttributeError). This is the real,
observable effect of the skill, measured without an LLM.

**Doc-drift fixed** (separate from the benchmark): `agents/build-agent.md`,
`agents/post-gate-agent.md`, and the `dispatch-templates.md` BUILD→REVIEW propagation note all
said "execute every `Read()` line" / "checklist Read() lines" while the dispatch emits
`Skill()` lines — reworded to match the Skill-tool mechanism.

## If pursued

- Replace the adherence rubric's holistic scoring with **per-item objective probes** where possible
  (e.g. AST checks: does an `assert` exist? max nesting depth? function count?) — kills the ceiling.
- Add a genuinely hard adversarial suite for the defensive task.
- The GC-2 finding is actionable for the skill itself: if assertions matter, the checklist wording
  isn't changing behavior — worth a skill-craft pass.
