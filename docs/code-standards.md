<!-- base-commit: e9e01d0 -->
<!-- generated: 2026-07-03 -->
# code-foundations authoring standards

This repo is a Claude Code plugin plus its benchmark harnesses: the "code" is skill/command/agent markdown (Part 1) and Python eval/scoring code under `benchmarks/` (Part 2). These are the conventions LLM-written edits must follow. Derived from the 2026-06 full audit, grug decision memos, oberskills:skill-craft doctrine, and the two shipped benchmark harnesses.

---

# Part 1 — Plugin markdown (skills/, commands/, agents/, references/)

## Frontmatter

- Quote every `description:` value with double quotes. Unquoted descriptions containing `:` (e.g. `Triggers on:`) are invalid YAML and break spec-compliant hosts and the eval harness.
  ```yaml
  # Good (skills/gof-design-patterns/SKILL.md)
  description: "Use when applying or selecting a Gang of Four design pattern. Triggers on: design pattern, ..."
  # Bad (broke performance-optimization)
  description: Use when code is too slow. Triggers on: profiler hot spots, ...
  ```
- `name` must match the directory name; lowercase alphanumeric + hyphens.
- Description formula: `[capability]. Use when [triggers/contexts]. Not for: [near-miss exclusions].` Third person, key use case first, concrete trigger nouns, **never workflow steps**.

## File references (grug: plugin-root-must-be-braced)

- Inside SKILL.md bodies → `${CLAUDE_SKILL_DIR}/checklists.md` (or `${CLAUDE_PLUGIN_ROOT}/skills/<name>/...`).
- Inside commands/, agents/, hooks → `${CLAUDE_PLUGIN_ROOT}/references/...`.
- NEVER: bare relative paths (resolve against user CWD), unbraced `$CLAUDE_PLUGIN_ROOT` (passed literally to Read), invented vars (`$SKILL_DIR`).
- Cross-skill handoffs name the fully qualified skill: `Skill(code-foundations:welc-legacy-code)` — bare names are not invocable.

## Structure

- SKILL.md body < 500 lines hard, ~200-line core preferred. Every bundled file (checklists.md, references/*) must be linked from SKILL.md or deleted — orphans never load and drift.
- One canonical home per fact. Before "deduplicating" commands/build.md, read grug `build-command-progressive-disclosure`: Gate Policy, Model Resolution, Skill Resolution, Execution Loop are **deliberately inline**; the REVIEW debias rule is **deliberately duplicated** (build.md + dispatch-templates § REVIEW); commit recipe lives only in references/commit-format.md.
- References > 100 lines need a Contents/ToC heading.
- No stated item counts ("Total items: N") — they drift; 6 of 7 were wrong at audit.

## Voice and constructs

- No banned constructs: anti-rationalization tables (`| Myth | Reality |`, `| Pattern | Reality |`), self-assessed compliance checklists ("Did I follow the workflow?"), self-directed "Red Flags — STOP" sections. Replace with checkable gates ("proceed only when X", artifact/output-shape requirements) — welc-legacy-code is the house model.
- No CRISIS/STOP/NEVER-SKIP shouting blocks, no scripted user-pushback lines, no emergency-bypass ceremony, no human-time bounds ("takes 1-2 hours"). State a rule once, neutrally.
- Write to Claude, not about the domain: cut textbook definitions Claude already knows; keep the project-opinionated rules and decision tables.
- Checklist items must be externally checkable assertions about artifacts, phrased so checked = satisfied.

## Commands and agents

- Title commands `# Command: <name>` (not `# Skill:`).
- Command descriptions are trigger-bearing and concrete (model: research.md), with `argument-hint` when the command takes input.
- Dispatch templates and agent files share seam contracts: a placeholder in a template must name its source rule; paths written by parallel-dispatched agents must be parameterized per sample.

## Verification gates for any skill/command edit

1. `validate_skill` on every touched skill dir — zero errors required.
2. Description changed → re-run `test_triggers` (existing query sets: `.skill-audit/trigger-workspaces/<skill>-workspace/trigger-queries.json`).
3. Workflow semantics changed → re-run the skill's behavioral eval (`.skill-audit/<skill>/evals.json`).

---

# Part 2 — Benchmark harnesses (benchmarks/)

Two shipped exemplars set the conventions: `benchmarks/tdd-vs-siv/` (skill-eval-driven A/B) and `benchmarks/concise-doctrine/` (custom orchestrator). New suites follow them.

## File Organization

```
benchmarks/<suite>/
├── README.md            # design, hypotheses, how-to-run, results table
├── evals.json           # skill-eval house schema (when skill-eval drives runs)
├── tasks/<nn-name>/     # numbered task dirs
│   ├── spec.md          # what the agent sees — DW items only
│   ├── hidden/          # ground truth the agent NEVER sees (test_hidden.py)
│   └── starter/         # provided files for modify-existing tasks
├── harness/ or *.py     # graders/orchestrator at suite root
└── results-*.csv        # per-task CSV rows, committed
```

- Task ids are `NN-slug` (`01-duration`, `13-sqli`); DW items are `DW-N.M` and hidden tests bucket as `test_dw_*` / `test_offdw_*` (tdd-vs-siv `tasks/*/hidden/`).
- Workspaces (`*-workspace/`, `results-*/` run dirs) are generated artifacts — never hand-edit.

## Ground truth vs agent view

Hidden suites and mutation scoring run offline, never inside the agent session; the agent sees `spec.md` only.

```python
# From benchmarks/tdd-vs-siv README — the load-bearing gate:
# mutation_score is gated on the agent's own suite being green FIRST —
# a broken env otherwise fakes a perfect mutation score.
```

Validate the harness on synthetic runs before any LLM runs (tdd-vs-siv `harness/_smoke/`: a thorough suite must score 1.0, a thin DW-only suite measurably less, on identical code).

## Python conventions

- Python 3.12 via `uv venv .venv -p 3.12`; deps installed with `uv pip install --python .venv/bin/python pytest ...`. Each suite owns its `.venv` — no shared environment, no requirements.txt observed; the README's setup block is the record.
- Every module opens with a docstring stating its phase/role and its seams (what it adapts, what it depends on):
  ```python
  """score_correctness.py — Correctness + mutation adapter (Phase 4).

  Key difference from tdd-vs-siv grade.py: that file hard-codes ROOT to its
  own parent directory. This adapter accepts the manifest and hidden_root
  explicitly (no global path coupling).   # <- WHY, not just what
  """
  ```
- `from __future__ import annotations`, `pathlib.Path` (never `os.path`), dataclasses for specs, `argparse` CLIs on every runnable module.
- sys.path setup before local imports gets `# noqa: E402` (run_matrix.py, score_correctness.py).

## Orchestrator requirements (run_matrix.py is the exemplar)

- **Resumable/idempotent**: a cell whose run dir already contains `meta.json` is skipped — re-running after partial failure picks up where it left off.
- **Detached-safe**: no interactive prompts; errors to stderr; exit code reflects completion.
- Run-dir layout is the contract between runner and scorers: `<root>/<task>/<arm>/<model>/run-<n>/outputs/` + `meta.json`. Scorers take roots explicitly as arguments — never hard-code a parent-relative ROOT (called out as a fixed defect in score_correctness.py's docstring).
- Results append to flat CSVs with a shared `ROW_FIELDS` schema; reports are `REPORT*.md` beside them.

## Pre-registration

Verdict/decision rules are written into the README or research doc **before** runs, and the orchestrator help text names them (run_matrix.py: "The pre-registered verdict rule requires the readability dimension... Without --rubric... the verdict rule cannot be evaluated."). Post-hoc metric selection is the forbidden pattern.

## Exemplar Files

**`benchmarks/tdd-vs-siv/README.md`** — hypotheses, grounding citations, task/metric design, results table: the template for a new suite's README.
**`benchmarks/concise-doctrine/run_matrix.py`** — resumable detached orchestrator: cell iteration, skip-if-done, CSV writing.
**`benchmarks/concise-doctrine/score_correctness.py`** — scorer with explicit seams (manifest + roots as args), green-suite gating before mutation.
**`skills/welc-legacy-code/SKILL.md`** — house model for checkable-gate skill authoring.
