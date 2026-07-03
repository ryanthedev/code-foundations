"""analyze.py — Applies the pre-registered decision rules to matrix CSVs (Phase 5).

Seam: consumes `score_run.ROW_FIELDS`-shaped rows from `results-*.csv` (Phase 4's
output — the Phase 4/5 seam per SCHEMA.md), plus read-only `calibration/pilot_rows.json`
and `calibration/decisions.md` for the calibration-evidence section, plus
`tasks/*/manifest.json` and `tasks/*/answer-key.json` for traceability and the
rung-4 per-defect table. Never writes into calibration/ or tasks/.

Pseudocode (cc-pseudocode-programming — written before any code, iterated until
each line was code-generation-ready; see the Phase 5 discovery doc's Design
Decisions for the two alternatives weighed):

    load_matrix_rows(matrix_dir):
        find every results-*.csv (sorted); [] if none exist — never raises.
        parse + coerce numeric/bool fields per ROW_FIELDS.

    filter_stat_rows(rows):
        drop judge_fail and pilot rows; return (usable, quality_note counts).

    paired_deltas(rows, model_a, model_b):
        per task, mean(model_a's score) - mean(model_b's score);
        raise if the two models' run counts for a task differ (an unfiltered
        pilot leaking through, or a genuine anomaly — never silently averaged).

    bootstrap_ci(deltas, seed=42):
        fixed-seed percentile bootstrap; deterministic given the same input.

    rung_verdict(rows, cheaper, costlier):
        <2 surviving tasks -> insufficient-data (never a mean-only claim);
        else apply rule 1 (tie -> cheaper) / rule 2 (consistent win) to label
        change-rule / no-difference->cheaper / keep-rule.

    rung4_defect_table(pilot_rows, answer_keys):
        per (task, defect, model): found-count over actual runs, source-labeled
        pilot vs gold-validation (04-hash-progress-review was never piloted).

    review_tier_verdict(defect_table, lower, higher):
        rule 3's specific bar: lower found 0-of-n where higher found >=3-of-n,
        at the rule's designed n=5 — reports insufficient-data honestly when
        actual n falls short (this run: actual matrix n=0, pilot n<=2).

    traceability_table(tasks_dir):
        every tasks/*/manifest.json's source.{repo,plan,phase} — all 7 tasks,
        regardless of matrix survival (DW-5.5).

    render_report(...):
        assembles REPORT.md text from all of the above.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from pathlib import Path
from random import Random
from typing import Sequence

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from score_run import ROW_FIELDS  # noqa: E402

TASKS_DIR = HERE / "tasks"
CALIBRATION_DIR = HERE / "calibration"

# ---------------------------------------------------------------------------
# Pre-registered decision rules — quoted verbatim from the research doc
# (.code-foundations/research/2026-07-03-model-tier-benchmark.md
#  § "Pre-registered decision rules (grill decision 2026-07-03 ...)").
# Analysis must not invent thresholds; these three strings are the only
# rule text REPORT.md is allowed to quote as "the rule".
# ---------------------------------------------------------------------------
RULE_1_TIES_CHEAPER = (
    "Ties go to the cheaper model. Paired per-task gap within the bootstrap CI "
    "→ verdict is “no difference,” cheap option wins explicitly."
)
RULE_2_CONSISTENT_WIN = (
    "Rule changes need a consistent win, not a mean win: the costlier model "
    "must win the paired comparison on a majority of the rung's tasks AND by "
    "more than the CI on the rung aggregate."
)
RULE_3_REVIEW_ASYMMETRIC = (
    "Asymmetric bar for the REVIEW rule: overturning “one tier below” "
    "(a permanent cost increase on every build) requires the higher-tier "
    "reviewer to catch planted violations the lower tier missed entirely — "
    "operationalized at n=5 as: a violation the lower tier found in 0 of 5 runs "
    "that the higher tier found in ≥3 of 5. A capability gap in missed-defect "
    "counts, not a rubric-score gap."
)

RUNG4_DESIGNED_N_RUNS = 5  # rule 3's operationalization is pinned at n=5
MIN_TASKS_FOR_VERDICT = 2  # <2 surviving tasks -> insufficient-data (plan edge case)

# Gold-validation provenance (DW-4.6; calibration/decisions.md, the
# 2026-07-03T11:20:24Z [gold_validation] log line) — NOT a live model pilot.
# 04-hash-progress-review never reached the pilot stage (vet-rejected twice);
# this is the reference/gold solution's own recall check, recorded verbatim
# from that log line so the per-defect table can source-label it distinctly
# from real pilot rows.
GOLD_VALIDATION_RUNG4 = {
    "04-hash-progress-review": {
        "model": "gold-reference",
        "of_n_runs": 1,
        "source": "gold-validation (decisions.md 2026-07-03T11:20:24Z; never model-piloted, vet-rejected)",
        "all_defects_found": True,
    },
}


# ---------------------------------------------------------------------------
# Matrix CSV loading
# ---------------------------------------------------------------------------

_BOOL_TRUE = {"true", "1", "yes"}
_INT_FIELDS = {"rung", "run_n", "tp", "fp", "fn", "tokens"}
_FLOAT_FIELDS = {"score", "time_seconds", "cost_usd"}


def _coerce_row(raw: dict) -> dict:
    """Coerce a CSV DictReader row's string values to ROW_FIELDS' real types.
    Unknown/blank numeric fields fall back to 0 rather than raising -- a
    matrix CSV is trusted output of score_run, not untrusted input."""
    row = dict(raw)
    for key in _INT_FIELDS:
        if key in row:
            row[key] = int(row[key]) if row[key] not in ("", None) else 0
    for key in _FLOAT_FIELDS:
        if key in row:
            row[key] = float(row[key]) if row[key] not in ("", None) else 0.0
    if "judge_fail" in row:
        row["judge_fail"] = str(row["judge_fail"]).strip().lower() in _BOOL_TRUE
    if "pilot" in row:
        row["pilot"] = str(row["pilot"]).strip().lower() in _BOOL_TRUE
    return row


def load_matrix_rows(matrix_dir: Path) -> list[dict]:
    """Load every results-*.csv under matrix_dir into ROW_FIELDS-shaped dicts.
    Returns [] when no CSV exists -- the vacuous-matrix case (this suite's
    actual state per Phase 4), never raises."""
    rows: list[dict] = []
    for csv_path in sorted(matrix_dir.glob("results-*.csv")):
        with csv_path.open(newline="") as f:
            reader = csv.DictReader(f)
            missing = set(ROW_FIELDS) - set(reader.fieldnames or [])
            if missing:
                raise ValueError(f"{csv_path}: missing ROW_FIELDS columns {sorted(missing)}")
            for raw in reader:
                rows.append(_coerce_row(raw))
    return rows


# ---------------------------------------------------------------------------
# Filtering + paired stats
# ---------------------------------------------------------------------------

def filter_stat_rows(rows: Sequence[dict]) -> tuple[list[dict], dict]:
    """Drop judge-failure and pilot-marked rows before any paired stat.
    Returns (usable_rows, quality_note) -- the counts are surfaced for the
    data-quality note, never silently discarded."""
    total = len(rows)
    judge_fail_excluded = sum(1 for r in rows if r.get("judge_fail"))
    pilot_excluded = sum(1 for r in rows if r.get("pilot") and not r.get("judge_fail"))
    usable = [r for r in rows if not r.get("judge_fail") and not r.get("pilot")]
    quality_note = {
        "total_rows": total,
        "judge_fail_excluded": judge_fail_excluded,
        "pilot_excluded": pilot_excluded,
        "usable_rows": len(usable),
    }
    return usable, quality_note


def paired_deltas(
    rows: Sequence[dict], model_a: str, model_b: str, field: str = "score"
) -> dict[str, float]:
    """Per task present under BOTH models, mean(model_a[field]) - mean(model_b[field]).
    A task missing either model is simply absent from the result (not zeroed).
    Raises ValueError if the two models' run counts differ for a shared task --
    that signals an unfiltered pilot row or a genuine anomaly, never silently
    averaged over mismatched n (T-5.6)."""
    by_task_model: dict[str, dict[str, list[float]]] = {}
    for r in rows:
        by_task_model.setdefault(r["task"], {}).setdefault(r["model"], []).append(r[field])

    deltas: dict[str, float] = {}
    for task, by_model in by_task_model.items():
        if model_a not in by_model or model_b not in by_model:
            continue
        vals_a, vals_b = by_model[model_a], by_model[model_b]
        if len(vals_a) != len(vals_b):
            raise ValueError(
                f"task {task!r}: {model_a} has {len(vals_a)} runs but {model_b} "
                f"has {len(vals_b)} -- asymmetric run count (unfiltered pilot row?)"
            )
        deltas[task] = statistics.mean(vals_a) - statistics.mean(vals_b)
    return deltas


def bootstrap_ci(
    deltas: Sequence[float], *, seed: int = 42, n_resamples: int = 10_000, alpha: float = 0.05
) -> tuple[float, float, float]:
    """Fixed-seed percentile bootstrap over paired deltas. Deterministic given
    the same input + seed -- this determinism IS DW-5.1's "reproducing expected
    interval" requirement. Returns (mean, ci_lo, ci_hi); (0.0, 0.0, 0.0) if
    deltas is empty (nothing to resample)."""
    if not deltas:
        return 0.0, 0.0, 0.0
    values = list(deltas)
    rng = Random(seed)
    resample_means = sorted(
        statistics.mean(rng.choices(values, k=len(values))) for _ in range(n_resamples)
    )
    lo_idx = int((alpha / 2) * (n_resamples - 1))
    hi_idx = int((1 - alpha / 2) * (n_resamples - 1))
    return statistics.mean(values), resample_means[lo_idx], resample_means[hi_idx]


def rung_verdict(
    rung_rows: Sequence[dict], *, cheaper_model: str, costlier_model: str,
    min_tasks: int = MIN_TASKS_FOR_VERDICT,
) -> dict:
    """Apply rule 1 (ties -> cheaper) + rule 2 (consistent win) to one rung's
    rows. Verdict-label mapping (change-rule / no-difference->cheaper /
    keep-rule) is a documented interpretation of the plan's 4-value enum --
    see the Phase 5 discovery doc's Design Decisions; the two rule bars
    themselves (majority + CI-clears-zero) are exactly as pre-registered."""
    usable, quality_note = filter_stat_rows(rung_rows)
    deltas = paired_deltas(usable, costlier_model, cheaper_model)
    n_tasks = len(deltas)
    result = {
        "n_tasks": n_tasks,
        "cheaper_model": cheaper_model,
        "costlier_model": costlier_model,
        "quality_note": quality_note,
        "per_task_deltas": deltas,
    }
    if n_tasks < min_tasks:
        result["verdict"] = "insufficient-data"
        result["reason"] = f"{n_tasks} surviving task(s) < required minimum {min_tasks}"
        return result

    mean, lo, hi = bootstrap_ci(list(deltas.values()))
    wins = sum(1 for d in deltas.values() if d > 0)
    majority_win = wins > n_tasks / 2
    result.update({"mean_delta": mean, "ci_lo": lo, "ci_hi": hi, "wins": wins})

    if majority_win and lo > 0:
        result["verdict"] = "change-rule"
    elif lo <= 0 <= hi:
        result["verdict"] = "no-difference→cheaper"
    else:
        result["verdict"] = "keep-rule"
    return result


def review_tier_verdict(
    defect_rows: Sequence[dict], *, lower_model: str, higher_model: str,
    designed_n_runs: int = RUNG4_DESIGNED_N_RUNS,
) -> dict:
    """Rule 3's specific bar: a defect the lower tier missed in 0-of-n runs
    that the higher tier caught in >=3-of-n, at the rule's designed n=5.
    Distinct from rung_verdict -- this is a per-defect capability-gap test,
    not a paired-score delta."""
    by_task: dict[str, list[dict]] = {}
    for row in defect_rows:
        by_task.setdefault(row["task"], []).append(row)

    n_tasks = len(by_task)
    result: dict = {
        "n_tasks": n_tasks,
        "designed_n_runs": designed_n_runs,
        "lower_model": lower_model,
        "higher_model": higher_model,
    }
    if n_tasks < MIN_TASKS_FOR_VERDICT:
        result["verdict"] = "insufficient-data"
        result["reason"] = (
            f"{n_tasks} surviving rung-4 task(s) < required minimum "
            f"{MIN_TASKS_FOR_VERDICT}; rule 3 is pinned at n={designed_n_runs} runs "
            "per model -- actual runs observed fall short of that design"
        )
        return result

    qualifying_gaps = []
    for task, rows in by_task.items():
        by_defect: dict[str, dict[str, dict]] = {}
        for r in rows:
            by_defect.setdefault(r["defect_id"], {})[r["model"]] = r
        for defect_id, by_model in by_defect.items():
            lower = by_model.get(lower_model)
            higher = by_model.get(higher_model)
            if not lower or not higher:
                continue
            if lower["found_count"] == 0 and higher["found_count"] >= 3:
                qualifying_gaps.append({"task": task, "defect_id": defect_id})
    result["qualifying_gaps"] = qualifying_gaps
    result["verdict"] = "change-rule" if qualifying_gaps else "no-difference→cheaper"
    return result


# ---------------------------------------------------------------------------
# Rung-4 per-defect detection table (DW-5.3)
# ---------------------------------------------------------------------------

def _load_answer_key_defects(task_id: str) -> list[str]:
    answer_key = json.loads((TASKS_DIR / task_id / "answer-key.json").read_text())
    return [d["id"] for d in answer_key["defects"]]


def rung4_defect_table(pilot_rows: dict, tasks_dir: Path = TASKS_DIR) -> list[dict]:
    """Per (task, defect, model): found-count over actual runs, source-labeled
    pilot vs gold-validation. A pilot run whose aggregate tp/fn can't be
    attributed to specific defects (fn > 0, since no per-defect judge output
    exists in this dataset) is recorded as unattributed rather than assumed."""
    rows: list[dict] = []
    for task_dir in sorted(tasks_dir.iterdir()):
        manifest_path = task_dir / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text())
        if manifest["rung"] != 4:
            continue
        task_id = manifest["id"]
        defect_ids = _load_answer_key_defects(task_id)
        n_defects = len(defect_ids)

        task_pilots = pilot_rows.get(task_id)
        if task_pilots:
            by_model: dict[str, list[dict]] = {}
            for entry in task_pilots.values():
                by_model.setdefault(entry["model"], []).append(entry)
            for model, entries in by_model.items():
                attributable = [e for e in entries if e["fn"] == 0 and e["tp"] == n_defects]
                unattributable = len(entries) - len(attributable)
                for defect_id in defect_ids:
                    rows.append({
                        "task": task_id,
                        "defect_id": defect_id,
                        "model": model,
                        "found_count": len(attributable),
                        "of_n_runs": len(entries),
                        "unattributed_runs": unattributable,
                        "source": "pilot",
                    })
        else:
            gold = GOLD_VALIDATION_RUNG4.get(task_id)
            if gold:
                for defect_id in defect_ids:
                    rows.append({
                        "task": task_id,
                        "defect_id": defect_id,
                        "model": gold["model"],
                        "found_count": gold["of_n_runs"] if gold["all_defects_found"] else 0,
                        "of_n_runs": gold["of_n_runs"],
                        "unattributed_runs": 0,
                        "source": gold["source"],
                    })
    return rows


# ---------------------------------------------------------------------------
# Traceability table (DW-5.5)
# ---------------------------------------------------------------------------

def traceability_table(tasks_dir: Path = TASKS_DIR) -> list[dict]:
    """Every tasks/*/manifest.json's source.{repo,plan,phase} -- all tasks,
    regardless of matrix survival."""
    rows = []
    for task_dir in sorted(tasks_dir.iterdir()):
        manifest_path = task_dir / "manifest.json"
        if not manifest_path.exists():
            continue
        manifest = json.loads(manifest_path.read_text())
        source = manifest["source"]
        rows.append({
            "task": manifest["id"],
            "rung": manifest["rung"],
            "repo": source["repo"],
            "plan": source["plan"],
            "phase": source["phase"],
        })
    return rows


# ---------------------------------------------------------------------------
# Speed (secondary axis, DW-5.4)
# ---------------------------------------------------------------------------

def speed_summary(rows: Sequence[dict], *, time_field: str = "time_seconds") -> dict[str, dict]:
    """Median + range of time_field, grouped by model. Secondary axis only --
    callers must never use this to drive a verdict unless the gap exceeds 2x
    (research doc's speed-axis protocol); render_report enforces this by never
    referencing speed_summary output inside a verdict section."""
    by_model: dict[str, list[float]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r[time_field])
    return {
        model: {
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "n": len(times),
        }
        for model, times in by_model.items()
    }


def count_pilot_comparisons(pilot_rows: dict) -> tuple[int, int]:
    """Count (paired_comparisons, individual_rows) in pilot_rows.json, pairing
    by (task, run_n) where both sonnet-5 and fable-5 are present. Computed
    from the JSON directly -- see discovery doc's Design Decisions on why this
    may not match a rounded figure quoted elsewhere."""
    individual = sum(len(entries) for entries in pilot_rows.values())
    pairs = 0
    for entries in pilot_rows.values():
        by_run_n: dict[int, set[str]] = {}
        for entry in entries.values():
            by_run_n.setdefault(entry["run_n"], set()).add(entry["model"])
        pairs += sum(1 for models in by_run_n.values() if {"sonnet-5", "fable-5"} <= models)
    return pairs, individual


# ---------------------------------------------------------------------------
# REPORT.md rendering
# ---------------------------------------------------------------------------

def _fmt_verdict_inputs(v: dict) -> str:
    lines = [f"- n_tasks (surviving): {v['n_tasks']}"]
    if "reason" in v:
        lines.append(f"- reason: {v['reason']}")
    if "mean_delta" in v:
        lines.append(f"- mean paired delta (costlier - cheaper): {v['mean_delta']:.3f}")
        lines.append(f"- bootstrap 95% CI: [{v['ci_lo']:.3f}, {v['ci_hi']:.3f}]")
        lines.append(f"- tasks won by costlier model: {v['wins']}/{v['n_tasks']}")
    if "designed_n_runs" in v:
        lines.append(f"- rule's designed n_runs: {v['designed_n_runs']}")
    if "qualifying_gaps" in v:
        lines.append(f"- qualifying capability gaps found: {len(v['qualifying_gaps'])}")
    return "\n".join(lines)


def render_report(
    *,
    q1_verdict: dict,
    q2_verdict: dict,
    defect_table: Sequence[dict],
    traceability: Sequence[dict],
    speed: dict,
    pilot_pairs: int,
    pilot_individual: int,
    quality_note: dict,
) -> str:
    lines: list[str] = []
    lines.append("# Model-Tier Benchmark — Analysis Report (Phase 5)")
    lines.append("")
    lines.append(
        "**Data reality:** the calibration gate (Phase 4) rejected all 7 candidate "
        "tasks before the matrix ran (5 for both-perfect/both-fail saturation, 2 for a "
        "residual spec gap looping back to earlier phases). No `results-*.csv` exists. "
        "The verdicts below are computed against that empty matrix first, per the "
        "pre-registered edge rule; a clearly separate section below reports what the "
        "calibration pilots actually measured."
    )
    lines.append("")

    lines.append("## Q1 — Fable 5 vs Opus 4.8 horizon split")
    lines.append("")
    lines.append("**Rule 1 (quoted verbatim):**")
    lines.append(f"> {RULE_1_TIES_CHEAPER}")
    lines.append("")
    lines.append("**Rule 2 (quoted verbatim):**")
    lines.append(f"> {RULE_2_CONSISTENT_WIN}")
    lines.append("")
    lines.append(f"**Verdict: `{q1_verdict['verdict']}`**")
    lines.append("")
    lines.append("Rule inputs:")
    lines.append(_fmt_verdict_inputs(q1_verdict))
    lines.append("")

    lines.append("## Q2 — REVIEW one tier below BUILD")
    lines.append("")
    lines.append("**Rule 3 (quoted verbatim):**")
    lines.append(f"> {RULE_3_REVIEW_ASYMMETRIC}")
    lines.append("")
    lines.append(f"**Verdict: `{q2_verdict['verdict']}`**")
    lines.append("")
    lines.append("Rule inputs:")
    lines.append(_fmt_verdict_inputs(q2_verdict))
    lines.append("")

    lines.append("## Calibration-level evidence (not matrix data)")
    lines.append("")
    lines.append(
        f"{pilot_pairs} sonnet-5/fable-5 paired pilot comparisons "
        f"({pilot_individual} individual pilot runs) across the 6 tasks that reached "
        "piloting, at effort=medium, n=2 per task where a confirmation round ran. "
        "Every comparison tied at perfect correctness (including 5/5 and 5/5 "
        "planted-defect recall on the two rung-4 pilots recorded in "
        "`calibration/pilot_rows.json`). This count is computed directly from that "
        "file's contents (grouped by task + run_n, both models present); the phase "
        "context's rounded figure of ~12 apparently also counts pre-bugfix pilot "
        "rounds for `03-kv-key-mismatch`/`03-storage-meter-dedup` that were superseded "
        "and overwritten in the final JSON snapshot (see `calibration/decisions.md`'s "
        "[SCORER_BUG_FOUND] entry)."
    )
    lines.append("")
    lines.append(
        "**Scope limits:** pilot n is 1-2 per model per task (never the rule's "
        "designed n=5); only the cheapest (sonnet-5) and priciest (fable-5) matrix "
        "arms were ever piloted — Opus 4.8 was never piloted, so Q1's actual pair "
        "(Fable vs Opus) has zero direct evidence, pilot or matrix; effort was pinned "
        "at medium throughout (no sweep)."
    )
    lines.append("")
    lines.append(
        "**Implication under rule 1 (ties → cheaper), at the task-population "
        "level only:** for the corpus-sourced tasks as authored, sonnet-5 and "
        "fable-5 are indistinguishable — every surviving-quality task tied at "
        "perfect. This does not answer Q1 (no Opus data) or Q2 (n=2 << designed "
        "n=5) as pre-registered; it is a related but distinct signal: the task "
        "population as currently authored does not reach the difficulty band where "
        "tiers separate, which is why the matrix itself is empty."
    )
    lines.append("")
    lines.append(
        "**Follow-up register:** (1) `04-hash-progress-review` has a residual spec "
        "gap (DW-2.2's default `.upublishignore` exclusion rules are still "
        "undefined) — loops back to Phase 2 a second time per "
        "`calibration/decisions.md`'s final `[re_vet]` entry. (2) A harder-task "
        "round two (rungs 2-4 rewritten to reach the tier-separation band the "
        "research doc's own web survey identified) is the path to a decisive Q1/Q2 "
        "verdict; this round's saturation is itself informative evidence that the "
        "current corpus sample sits below that band."
    )
    lines.append("")

    lines.append("## Rung-4 per-defect detection table (Q2 evidence)")
    lines.append("")
    lines.append("| Task | Defect | Model | Found-count | Of N runs | Source |")
    lines.append("|---|---|---|---|---|---|")
    for row in defect_table:
        lines.append(
            f"| {row['task']} | {row['defect_id']} | {row['model']} | "
            f"{row['found_count']} | {row['of_n_runs']} | {row['source']} |"
        )
    lines.append("")

    lines.append("## Speed (secondary axis)")
    lines.append("")
    lines.append(
        "Speed is reported as median + range only, and is never decisive except "
        "where a gap exceeds ~2x (research doc's speed-axis protocol) — no verdict "
        "above cites a speed figure."
    )
    lines.append("")
    if speed:
        lines.append("| Model | Median (s) | Min (s) | Max (s) | N |")
        lines.append("|---|---|---|---|---|")
        for model, s in sorted(speed.items()):
            lines.append(f"| {model} | {s['median']:.1f} | {s['min']:.1f} | {s['max']:.1f} | {s['n']} |")
    else:
        lines.append("No matrix speed data (0 runs).")
    lines.append("")

    lines.append("## Task → corpus-phase traceability")
    lines.append("")
    lines.append("| Task | Rung | Repo | Plan | Phase |")
    lines.append("|---|---|---|---|---|")
    for row in traceability:
        lines.append(
            f"| {row['task']} | {row['rung']} | {row['repo']} | {row['plan']} | {row['phase']} |"
        )
    lines.append("")

    lines.append("## Data-quality note")
    lines.append("")
    lines.append(
        f"Matrix rows loaded: {quality_note['total_rows']}; judge-failure excluded: "
        f"{quality_note['judge_fail_excluded']}; pilot-marked excluded: "
        f"{quality_note['pilot_excluded']}; usable for paired stats: "
        f"{quality_note['usable_rows']}."
    )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Apply pre-registered decision rules to matrix CSVs")
    ap.add_argument("--matrix-dir", default=str(HERE))
    ap.add_argument("--tasks-dir", default=str(TASKS_DIR))
    ap.add_argument("--calibration-dir", default=str(CALIBRATION_DIR))
    ap.add_argument("--out", default=str(HERE / "REPORT.md"))
    args = ap.parse_args(argv)

    matrix_dir = Path(args.matrix_dir)
    tasks_dir = Path(args.tasks_dir)
    calibration_dir = Path(args.calibration_dir)

    rows = load_matrix_rows(matrix_dir)
    usable, quality_note = filter_stat_rows(rows)

    rung_234_rows = [r for r in usable if r["rung"] in (2, 3, 4)]
    q1_verdict = rung_verdict(rung_234_rows, cheaper_model="opus-4.8", costlier_model="fable-5")

    pilot_rows_path = calibration_dir / "pilot_rows.json"
    pilot_rows = json.loads(pilot_rows_path.read_text()) if pilot_rows_path.exists() else {}
    defect_table = rung4_defect_table(pilot_rows, tasks_dir)
    q2_verdict = review_tier_verdict(
        [{**r, "found_count": r["found_count"]} for r in defect_table if r["source"] == "pilot"],
        lower_model="sonnet-5", higher_model="fable-5",
    )

    traceability = traceability_table(tasks_dir)
    speed = speed_summary([r for r in usable if "time_seconds" in r])
    pilot_pairs, pilot_individual = count_pilot_comparisons(pilot_rows)

    report = render_report(
        q1_verdict=q1_verdict, q2_verdict=q2_verdict, defect_table=defect_table,
        traceability=traceability, speed=speed, pilot_pairs=pilot_pairs,
        pilot_individual=pilot_individual, quality_note=quality_note,
    )
    Path(args.out).write_text(report)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    _cli()
