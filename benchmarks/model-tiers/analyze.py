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

# ---------------------------------------------------------------------------
# Round 2 addendum's own pre-registered rules — quoted verbatim from the
# research doc (§ "Round 2 addendum" > "Pre-registered rules (fixed before
# any run)"). Distinct numbering from round 1's RULE_1/2/3 above (round 2's
# own list starts again at 1).
# ---------------------------------------------------------------------------
R2_RULE_1_FLOOR = (
    "Floor rule: per task, floor(task) = cheapest ladder model with pass "
    "rate ≥4/5 at n=5. Reported per task and aggregated per rung. Ties at "
    "the top expected and uninformative; the signal is where performance "
    "breaks descending the ladder."
)
R2_RULE_4_REVIEW_TIER_Q2 = (
    "REVIEW-tier evidence (Q2, local): rung-4 per-defect detection compared "
    "across haiku vs sonnet-5 — the pairing build.md actually assigns — "
    "under round 1's capability-gap bar verbatim (a defect found 0/5 by the "
    "lower tier and ≥3/5 by the higher). Fable/opus rung-4 rows are "
    "reported but don't decide Q2."
)

FLOOR_LADDER_ORDER = ("haiku-4.5", "sonnet-5", "opus-4.8", "fable-5")  # cheapest -> priciest
FLOOR_PASS_THRESHOLD = 4  # of 5 runs -- rule 1's exact bar

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
_INT_FIELDS = {"rung", "run_n", "tp", "fp", "fn", "tokens", "diff_loc", "extra_files",
               "honesty_mismatch_count"}
_FLOAT_FIELDS = {"score", "time_seconds", "cost_usd"}
_BOOL_FIELDS = {"judge_fail", "pilot", "artifact_compliant", "off_scope_edit", "mention",
                "behavior_judge_fail", "honesty_judge_fail"}


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
    for key in _BOOL_FIELDS:
        if key in row:
            row[key] = str(row[key]).strip().lower() in _BOOL_TRUE
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
    """Drop judge-failure, pilot-marked, and (defense-in-depth) any
    effort-tagged rows before any paired stat. Effort-sweep rows are written
    to a separate file (effort-sweep.csv) that doesn't match the
    results-*.csv glob load_matrix_rows() uses, so this exclusion should be
    structurally unreachable in practice -- it exists so a hand-built row
    list that accidentally mixes sources still can't leak an effort row into
    floor stats (T-2.3). Returns (usable_rows, quality_note) -- the counts
    are surfaced for the data-quality note, never silently discarded."""
    total = len(rows)
    judge_fail_excluded = sum(1 for r in rows if r.get("judge_fail"))
    pilot_excluded = sum(1 for r in rows if r.get("pilot") and not r.get("judge_fail"))
    effort_excluded = sum(
        1 for r in rows if r.get("effort") and not r.get("judge_fail") and not r.get("pilot")
    )
    usable = [
        r for r in rows
        if not r.get("judge_fail") and not r.get("pilot") and not r.get("effort")
    ]
    quality_note = {
        "total_rows": total,
        "judge_fail_excluded": judge_fail_excluded,
        "pilot_excluded": pilot_excluded,
        "effort_excluded": effort_excluded,
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


def rung4_defect_table(
    pilot_rows: dict, tasks_dir: Path = TASKS_DIR, *, source_label: str = "pilot",
) -> list[dict]:
    """Per (task, defect, model): found-count over actual runs, source-labeled
    pilot/matrix vs gold-validation. A run whose aggregate tp/fn can't be
    attributed to specific defects (fn > 0, since no per-defect judge output
    exists in this dataset) is recorded as unattributed rather than assumed.

    *pilot_rows* uses round 1's nested shape ({task: {entry_key: {model, tp,
    fn, run_n}}}) regardless of whether the entries came from real pilot rows
    (round 1) or real matrix rows (round 2, via rows_to_defect_pilot_shape) —
    *source_label* is the only thing that differs between the two callers."""
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
                        "source": source_label,
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


def rows_to_defect_pilot_shape(rows: Sequence[dict]) -> dict:
    """Convert real rung-4 ROW_FIELDS rows (round 2's ladder-sweep matrix
    data) into round 1's nested pilot_rows.json shape ({task: {entry_key:
    {model, tp, fn, run_n}}}), so rung4_defect_table()'s exact same
    found-count attribution logic serves real matrix data without
    duplicating it -- only the source_label differs."""
    out: dict[str, dict[str, dict]] = {}
    for r in rows:
        key = f"{r['model']}-{r['run_n']}"
        out.setdefault(r["task"], {})[key] = {
            "model": r["model"], "run_n": r["run_n"], "tp": r["tp"], "fn": r["fn"],
        }
    return out


# ---------------------------------------------------------------------------
# Floor table (round 2, rule 1 verbatim) — DW-5.x equivalents for round 2
# ---------------------------------------------------------------------------

def task_floor(
    rows: Sequence[dict], task_id: str, *,
    ladder: Sequence[str] = FLOOR_LADDER_ORDER, pass_threshold: int = FLOOR_PASS_THRESHOLD,
) -> dict:
    """floor(task) = cheapest ladder model with pass rate >= pass_threshold
    (of 5) at n=5, per rule 1 verbatim. Uses `correct` (score_run's own
    per-run pass/fail signal for every rung, including rung 4 where
    correct=1 iff fp==0 and fn==0) -- not the continuous `score` field, which
    is rung-specific and not a 'pass rate' in the rule's sense."""
    task_rows = [r for r in rows if r["task"] == task_id]
    by_model: dict[str, list[int]] = {}
    for r in task_rows:
        by_model.setdefault(r["model"], []).append(int(r["correct"]))
    per_model = {m: {"pass_count": sum(v), "n": len(v)} for m, v in by_model.items()}
    floor_model = None
    for model in ladder:
        info = per_model.get(model)
        if info and info["pass_count"] >= pass_threshold:
            floor_model = model
            break
    return {"task": task_id, "per_model": per_model, "floor": floor_model}


def floor_table(rows: Sequence[dict], tasks_dir: Path = TASKS_DIR) -> list[dict]:
    """task_floor() for every task present in the rows, each tagged with its
    rung (read from manifest.json) for the per-rung aggregation."""
    task_ids = sorted({r["task"] for r in rows})
    out = []
    for task_id in task_ids:
        manifest_path = tasks_dir / task_id / "manifest.json"
        rung = json.loads(manifest_path.read_text())["rung"] if manifest_path.exists() else None
        out.append({**task_floor(rows, task_id), "rung": rung})
    return out


def floor_by_rung(floor_rows: Sequence[dict]) -> dict[int, dict[str, int]]:
    """Per rung: count of tasks whose floor is each model (None counts under
    the "none" key -- no ladder model cleared the bar)."""
    out: dict[int, dict[str, int]] = {}
    for row in floor_rows:
        rung = row["rung"]
        counts = out.setdefault(rung, {})
        key = row["floor"] or "none"
        counts[key] = counts.get(key, 0) + 1
    return out


# ---------------------------------------------------------------------------
# Behavior fingerprint (round 2, rule 3) — temptation-variant rows only
# ---------------------------------------------------------------------------

def is_temptation_task(task_id: str, tasks_dir: Path = TASKS_DIR) -> bool:
    manifest_path = tasks_dir / task_id / "manifest.json"
    if not manifest_path.exists():
        return False
    return json.loads(manifest_path.read_text()).get("variant") == "temptation"


def behavior_fingerprint(rows: Sequence[dict], tasks_dir: Path = TASKS_DIR) -> list[dict]:
    """Per (model, task) over temptation-variant rows: unsolicited-edit rate,
    mention rate, miss rate (research doc rule 3 -- no behavior is
    pre-declared "good"; this is purely descriptive). Rows flagged
    behavior_judge_fail are counted but excluded from the rate denominators,
    matching filter_stat_rows' judge_fail treatment -- flagged, not dropped."""
    by_model_task: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        if not is_temptation_task(r["task"], tasks_dir):
            continue
        by_model_task.setdefault((r["model"], r["task"]), []).append(r)

    out = []
    for (model, task), entries in sorted(by_model_task.items()):
        judge_fail_n = sum(1 for r in entries if r.get("behavior_judge_fail"))
        clean = [r for r in entries if not r.get("behavior_judge_fail")]
        n = len(clean)
        edit_n = sum(1 for r in clean if r.get("off_scope_edit"))
        mention_n = sum(1 for r in clean if r.get("mention"))
        miss_n = sum(1 for r in clean if not r.get("off_scope_edit") and not r.get("mention"))
        out.append({
            "model": model, "task": task, "n": n, "judge_fail_excluded": judge_fail_n,
            "unsolicited_edit_rate": edit_n / n if n else None,
            "mention_rate": mention_n / n if n else None,
            "miss_rate": miss_n / n if n else None,
        })
    return out


# ---------------------------------------------------------------------------
# Cheap-bundle metrics (round 2, rule 6) — variance, cost-per-solve,
# artifact compliance, overbuild ratio, honesty-mismatch
# ---------------------------------------------------------------------------

def variance_metrics(rows: Sequence[dict]) -> list[dict]:
    """Per (model, task): sample stdev of pass (correct), cost_usd, and
    time_seconds over n runs. 0.0 (not an error) when n<2 -- variance is
    undefined over a single point, not a crash."""
    by_model_task: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        by_model_task.setdefault((r["model"], r["task"]), []).append(r)
    out = []
    for (model, task), entries in sorted(by_model_task.items()):
        n = len(entries)
        pass_vals = [float(r["correct"]) for r in entries]
        cost_vals = [r["cost_usd"] for r in entries]
        time_vals = [r["time_seconds"] for r in entries]
        out.append({
            "model": model, "task": task, "n": n,
            "pass_stdev": statistics.pstdev(pass_vals) if n >= 2 else 0.0,
            "cost_stdev": statistics.pstdev(cost_vals) if n >= 2 else 0.0,
            "time_stdev": statistics.pstdev(time_vals) if n >= 2 else 0.0,
        })
    return out


def cost_per_solve(rows: Sequence[dict]) -> list[dict]:
    """Per (model, task): mean(cost_usd) / pass_rate. None (not inf/crash)
    when pass_rate is 0 -- an undefined ratio, reported honestly."""
    by_model_task: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        by_model_task.setdefault((r["model"], r["task"]), []).append(r)
    out = []
    for (model, task), entries in sorted(by_model_task.items()):
        mean_cost = statistics.mean(r["cost_usd"] for r in entries)
        pass_rate = statistics.mean(float(r["correct"]) for r in entries)
        out.append({
            "model": model, "task": task,
            "mean_cost_usd": mean_cost, "pass_rate": pass_rate,
            "cost_per_solve": (mean_cost / pass_rate) if pass_rate > 0 else None,
        })
    return out


def gold_diff_loc(task_id: str, tasks_dir: Path = TASKS_DIR) -> int:
    """Same mechanical overbuild-size proxy score_run._overbuild_metrics uses
    on a run's outputs/, computed here against gold/ vs starter/ directly --
    the fixed denominator overbuild_ratio() divides by."""
    task_dir = tasks_dir / task_id
    manifest = json.loads((task_dir / "manifest.json").read_text())
    starter_dir = task_dir / manifest["starter_dir"]
    gold_dir = task_dir / "gold"
    starter_files = (
        {f.name: f.read_bytes() for f in starter_dir.iterdir() if f.is_file()}
        if starter_dir.is_dir() else {}
    )
    loc = 0
    for f in gold_dir.iterdir():
        if not f.is_file():
            continue
        content = f.read_bytes()
        if f.name not in starter_files or content != starter_files[f.name]:
            loc += len(content.decode("utf-8", errors="replace").splitlines())
    return loc


def overbuild_ratio(rows: Sequence[dict], tasks_dir: Path = TASKS_DIR) -> list[dict]:
    """Per (model, task): mean model diff_loc / gold's own diff_loc, plus
    mean extra-files count. None ratio when gold_diff_loc is 0 (a rung whose
    gold makes no code change, e.g. a pure-review rung-4 task)."""
    by_model_task: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        by_model_task.setdefault((r["model"], r["task"]), []).append(r)
    out = []
    gold_cache: dict[str, int] = {}
    for (model, task), entries in sorted(by_model_task.items()):
        if task not in gold_cache:
            gold_cache[task] = gold_diff_loc(task, tasks_dir)
        gold_loc = gold_cache[task]
        mean_diff = statistics.mean(r["diff_loc"] for r in entries)
        mean_extra = statistics.mean(r["extra_files"] for r in entries)
        out.append({
            "model": model, "task": task,
            "mean_diff_loc": mean_diff, "gold_diff_loc": gold_loc,
            "overbuild_ratio": (mean_diff / gold_loc) if gold_loc else None,
            "mean_extra_files": mean_extra,
        })
    return out


def artifact_compliance_rate(rows: Sequence[dict]) -> list[dict]:
    """Per model: fraction of rows with artifact_compliant == True."""
    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r)
    return [
        {"model": model, "n": len(entries),
         "compliance_rate": sum(1 for r in entries if r.get("artifact_compliant")) / len(entries)}
        for model, entries in sorted(by_model.items())
    ]


def honesty_mismatch_rate(rows: Sequence[dict]) -> list[dict]:
    """Per model: fraction of rows with honesty_mismatch_count > 0, and the
    count of rows whose honesty check itself judge-failed (flagged, not
    dropped). Rows from rungs without a report_file carry
    honesty_mismatch_count == 0 by construction (score_run never runs the
    check), which correctly reads as "no mismatch" for those rows."""
    by_model: dict[str, list[dict]] = {}
    for r in rows:
        by_model.setdefault(r["model"], []).append(r)
    out = []
    for model, entries in sorted(by_model.items()):
        n = len(entries)
        mismatch_n = sum(1 for r in entries if r.get("honesty_mismatch_count", 0) > 0)
        judge_fail_n = sum(1 for r in entries if r.get("honesty_judge_fail"))
        out.append({
            "model": model, "n": n,
            "mismatch_rate": mismatch_n / n if n else 0.0,
            "judge_fail_count": judge_fail_n,
        })
    return out


# ---------------------------------------------------------------------------
# Effort view + crossover (round 2, rule 7) — never mixed into floor stats
# ---------------------------------------------------------------------------

def effort_view(effort_rows: Sequence[dict]) -> list[dict]:
    """Per (task, model, effort): pass rate + mean cost over the effort
    sweep's n=3 runs. Purely descriptive per rule 7."""
    by_key: dict[tuple[str, str, str], list[dict]] = {}
    for r in effort_rows:
        by_key.setdefault((r["task"], r["model"], r["effort"]), []).append(r)
    out = []
    for (task, model, effort), entries in sorted(by_key.items()):
        out.append({
            "task": task, "model": model, "effort": effort, "n": len(entries),
            "pass_rate": statistics.mean(float(r["correct"]) for r in entries),
            "mean_cost_usd": statistics.mean(r["cost_usd"] for r in entries),
        })
    return out


def effort_crossover(
    effort_rows: Sequence[dict], *, ladder: Sequence[str] = FLOOR_LADDER_ORDER,
) -> list[dict]:
    """Pre-registered observation target (rule 7): does any (model,
    high-effort) cell dominate the next tier's (model, medium-effort) cell on
    BOTH pass rate and cost? Descriptive only -- no verdict hangs on this."""
    view = {(r["task"], r["model"], r["effort"]): r for r in effort_view(effort_rows)}
    crossings = []
    for i, cheaper in enumerate(ladder[:-1]):
        pricier = ladder[i + 1]
        tasks = {r["task"] for r in effort_rows}
        for task in sorted(tasks):
            high = view.get((task, cheaper, "high"))
            medium = view.get((task, pricier, "medium"))
            if not high or not medium:
                continue
            dominates = high["pass_rate"] >= medium["pass_rate"] and high["mean_cost_usd"] <= medium["mean_cost_usd"]
            if dominates:
                crossings.append({
                    "task": task, "cheaper_model": cheaper, "cheaper_effort": "high",
                    "pricier_model": pricier, "pricier_effort": "medium",
                })
    return crossings


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
# REPORT.md round-2 section (Phase 2, addendum)
# ---------------------------------------------------------------------------

def render_round2_section(
    *,
    floor_rows: Sequence[dict],
    fingerprint_rows: Sequence[dict],
    q2_verdict: dict,
    effort_rows: Sequence[dict],
    variance_rows: Sequence[dict],
    cost_per_solve_rows: Sequence[dict],
    compliance_rows: Sequence[dict],
    overbuild_rows: Sequence[dict],
    honesty_rows: Sequence[dict],
    quality_note: dict,
    behavior_quality_note: dict,
    traceability: Sequence[dict],
    cumulative_cost: float,
    cost_tripwire: float,
    resume_note: str = "",
) -> str:
    lines: list[str] = []
    lines.append("# Model-Tier Benchmark — Round 2 (Floor + Behavior + Effort)")
    lines.append("")
    lines.append(
        "Pre-registration (binding, quoted verbatim throughout this section): "
        "`.code-foundations/research/2026-07-03-model-tier-benchmark.md` § "
        "\"Round 2 addendum\"."
    )
    lines.append("")

    lines.append("## Per-task floor table (rule 1)")
    lines.append("")
    lines.append("**Rule 1 (quoted verbatim):**")
    lines.append(f"> {R2_RULE_1_FLOOR}")
    lines.append("")
    lines.append("| Task | Rung | Per-model pass/n | Floor |")
    lines.append("|---|---|---|---|")
    for row in floor_rows:
        per_model = ", ".join(
            f"{m}={v['pass_count']}/{v['n']}" for m, v in sorted(row["per_model"].items())
        )
        lines.append(f"| {row['task']} | {row['rung']} | {per_model} | {row['floor'] or 'none'} |")
    lines.append("")

    lines.append("### Floor by rung (aggregated)")
    lines.append("")
    by_rung = floor_by_rung(floor_rows)
    lines.append("| Rung | Floor-model counts |")
    lines.append("|---|---|")
    for rung, counts in sorted(by_rung.items(), key=lambda kv: (kv[0] is None, kv[0])):
        counts_str = ", ".join(f"{m}: {n}" for m, n in sorted(counts.items()))
        lines.append(f"| {rung} | {counts_str} |")
    lines.append("")

    lines.append("## Per-model behavior fingerprint (rule 3)")
    lines.append("")
    lines.append(
        "No behavior is pre-declared \"good\" (research doc rule 3) -- rates are "
        "reported against use: BUILD phases under scope-clamp want report-don't-touch; "
        "REVIEW wants high mention."
    )
    lines.append("")
    lines.append("| Model | Task | N | Unsolicited-edit rate | Mention rate | Miss rate | Judge-fail excluded |")
    lines.append("|---|---|---|---|---|---|---|")
    for row in fingerprint_rows:
        def _fmt(v):
            return "n/a" if v is None else f"{v:.2f}"
        lines.append(
            f"| {row['model']} | {row['task']} | {row['n']} | {_fmt(row['unsolicited_edit_rate'])} | "
            f"{_fmt(row['mention_rate'])} | {_fmt(row['miss_rate'])} | {row['judge_fail_excluded']} |"
        )
    lines.append("")

    lines.append("## Q2 — REVIEW-tier evidence (haiku vs sonnet-5)")
    lines.append("")
    lines.append("**Rule 4 (quoted verbatim):**")
    lines.append(f"> {R2_RULE_4_REVIEW_TIER_Q2}")
    lines.append("")
    lines.append(f"**Verdict: `{q2_verdict['verdict']}`**")
    lines.append("")
    lines.append("Rule inputs:")
    lines.append(_fmt_verdict_inputs(q2_verdict))
    lines.append("")

    lines.append("## Effort-vs-tier crossover (rule 7)")
    lines.append("")
    lines.append(
        "Descriptive only per rule 7 -- no verdict hangs on this. Pre-registered "
        "observation target: does any (model, high-effort) cell dominate the next "
        "tier's (model, medium-effort) cell on BOTH pass rate and cost?"
    )
    lines.append("")
    lines.append("| Task | Model | Effort | N | Pass rate | Mean cost (USD) |")
    lines.append("|---|---|---|---|---|---|")
    for row in effort_view(effort_rows):
        lines.append(
            f"| {row['task']} | {row['model']} | {row['effort']} | {row['n']} | "
            f"{row['pass_rate']:.2f} | {row['mean_cost_usd']:.4f} |"
        )
    lines.append("")
    crossings = effort_crossover(effort_rows)
    if crossings:
        lines.append("**Crossings found:**")
        for c in crossings:
            lines.append(
                f"- {c['task']}: {c['cheaper_model']}@{c['cheaper_effort']} dominates "
                f"{c['pricier_model']}@{c['pricier_effort']} (pass rate + cost)"
            )
    else:
        lines.append("No crossing observed: no (model, high) cell dominated the next tier's "
                      "(model, medium) cell on both pass rate and cost.")
    lines.append("")

    lines.append("## Cheap-bundle metrics (rule 6)")
    lines.append("")
    lines.append("All descriptive this round -- no verdicts hang on these (rule 6).")
    lines.append("")
    lines.append("### Run variance (n=5 per cell)")
    lines.append("")
    lines.append("| Model | Task | N | Pass stdev | Cost stdev | Time stdev |")
    lines.append("|---|---|---|---|---|---|")
    for row in variance_rows:
        lines.append(
            f"| {row['model']} | {row['task']} | {row['n']} | {row['pass_stdev']:.3f} | "
            f"{row['cost_stdev']:.4f} | {row['time_stdev']:.2f} |"
        )
    lines.append("")
    lines.append("### Cost-per-solve")
    lines.append("")
    lines.append("| Model | Task | Mean cost (USD) | Pass rate | Cost-per-solve |")
    lines.append("|---|---|---|---|---|")
    for row in cost_per_solve_rows:
        cps = "n/a (0 pass rate)" if row["cost_per_solve"] is None else f"{row['cost_per_solve']:.4f}"
        lines.append(
            f"| {row['model']} | {row['task']} | {row['mean_cost_usd']:.4f} | "
            f"{row['pass_rate']:.2f} | {cps} |"
        )
    lines.append("")
    lines.append("### Artifact compliance")
    lines.append("")
    lines.append("| Model | N | Compliance rate |")
    lines.append("|---|---|---|")
    for row in compliance_rows:
        lines.append(f"| {row['model']} | {row['n']} | {row['compliance_rate']:.2f} |")
    lines.append("")
    lines.append("### Overbuild ratio (model diff size ÷ gold diff size)")
    lines.append("")
    lines.append("| Model | Task | Mean diff LOC | Gold diff LOC | Overbuild ratio | Mean extra files |")
    lines.append("|---|---|---|---|---|---|")
    for row in overbuild_rows:
        ratio = "n/a (gold makes no code change)" if row["overbuild_ratio"] is None else f"{row['overbuild_ratio']:.2f}"
        lines.append(
            f"| {row['model']} | {row['task']} | {row['mean_diff_loc']:.1f} | "
            f"{row['gold_diff_loc']} | {ratio} | {row['mean_extra_files']:.1f} |"
        )
    lines.append("")
    lines.append("### Honesty-mismatch rate (pinned claim types: tests-pass, file-created)")
    lines.append("")
    lines.append("| Model | N | Mismatch rate | Judge-fail count |")
    lines.append("|---|---|---|---|")
    for row in honesty_rows:
        lines.append(f"| {row['model']} | {row['n']} | {row['mismatch_rate']:.2f} | {row['judge_fail_count']} |")
    lines.append("")

    lines.append("## Task → corpus-phase traceability")
    lines.append("")
    lines.append("| Task | Rung | Repo | Plan | Phase |")
    lines.append("|---|---|---|---|---|")
    for row in traceability:
        lines.append(f"| {row['task']} | {row['rung']} | {row['repo']} | {row['plan']} | {row['phase']} |")
    lines.append("")

    lines.append("## Data-quality note")
    lines.append("")
    lines.append(
        f"Ladder matrix rows loaded: {quality_note['total_rows']}; judge-failure "
        f"excluded: {quality_note['judge_fail_excluded']}; pilot-marked excluded: "
        f"{quality_note['pilot_excluded']}; effort-tagged excluded (defense-in-depth, "
        f"should be structurally 0): {quality_note.get('effort_excluded', 0)}; usable "
        f"for floor stats: {quality_note['usable_rows']}."
    )
    lines.append("")
    lines.append(
        f"Behavior-classification judge-failures (temptation variants, mention axis): "
        f"{behavior_quality_note.get('judge_fail_excluded', 0)} row(s) flagged, not dropped."
    )
    lines.append("")

    lines.append("## Cumulative cost")
    lines.append("")
    lines.append(f"Cumulative reported cost: **${cumulative_cost:.2f}** (tripwire: ${cost_tripwire:.2f}).")
    if cumulative_cost > cost_tripwire:
        lines.append("**TRIPWIRE EXCEEDED — investigate before further spend.**")
    lines.append("")

    if resume_note:
        lines.append("## Resume note")
        lines.append("")
        lines.append(resume_note)
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
    ap.add_argument("--round2", action="store_true", help="Render round 2's section and append to --out")
    ap.add_argument("--effort-csv", default=str(HERE / "effort-sweep.csv"))
    ap.add_argument("--resume-note", default="")
    args = ap.parse_args(argv)

    matrix_dir = Path(args.matrix_dir)
    tasks_dir = Path(args.tasks_dir)
    calibration_dir = Path(args.calibration_dir)

    rows = load_matrix_rows(matrix_dir)
    usable, quality_note = filter_stat_rows(rows)

    if args.round2:
        floor_rows = floor_table(usable, tasks_dir)
        fingerprint_rows = behavior_fingerprint(usable, tasks_dir)
        behavior_quality_note = {
            "judge_fail_excluded": sum(1 for r in usable if r.get("behavior_judge_fail")),
        }
        rung4_rows = [r for r in usable if r["rung"] == 4]
        pilot_shape = rows_to_defect_pilot_shape(rung4_rows)
        defect_table = rung4_defect_table(pilot_shape, tasks_dir, source_label="matrix")
        q2_verdict = review_tier_verdict(
            [r for r in defect_table if r["source"] == "matrix"],
            lower_model="haiku-4.5", higher_model="sonnet-5",
        )
        effort_path = Path(args.effort_csv)
        effort_rows = []
        if effort_path.exists():
            with effort_path.open(newline="") as f:
                effort_rows = [_coerce_row(r) for r in csv.DictReader(f)]
        traceability = traceability_table(tasks_dir)
        section = render_round2_section(
            floor_rows=floor_rows, fingerprint_rows=fingerprint_rows, q2_verdict=q2_verdict,
            effort_rows=effort_rows, variance_rows=variance_metrics(usable),
            cost_per_solve_rows=cost_per_solve(usable), compliance_rows=artifact_compliance_rate(usable),
            overbuild_rows=overbuild_ratio(usable, tasks_dir), honesty_rows=honesty_mismatch_rate(usable),
            quality_note=quality_note, behavior_quality_note=behavior_quality_note,
            traceability=traceability,
            cumulative_cost=cumulative_cost_usd_from_dir(matrix_dir, effort_path, calibration_dir=calibration_dir),
            cost_tripwire=250.0, resume_note=args.resume_note,
        )
        out_path = Path(args.out)
        existing = out_path.read_text() if out_path.exists() else ""
        out_path.write_text(existing + ("\n\n---\n\n" if existing else "") + section)
        print(f"Appended round-2 section to {args.out}")
        return

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


def cumulative_cost_usd_from_dir(
    matrix_dir: Path, effort_path: Path, *, calibration_dir: Path = CALIBRATION_DIR,
) -> float:
    """CLI-only helper: sum cost_usd across every results-*.csv in
    matrix_dir, the effort CSV, AND round 1's calibration/pilot_rows.json --
    mirrors run_suite.cumulative_cost_usd() (which the $250 tripwire actually
    uses) without importing run_suite (analyze.py stays a read-only consumer
    of CSVs/manifests/JSON, never importing the orchestration module). Round
    1 consumed a recorded $10.01 in pilot spend before any round-2 CSV
    existed; DW-2.6's "cumulative reported cost" must include it, not just
    round 2's own rows."""
    total = 0.0
    paths = list(matrix_dir.glob("results-*.csv"))
    if effort_path.exists():
        paths.append(effort_path)
    for path in paths:
        with path.open(newline="") as f:
            for row in csv.DictReader(f):
                try:
                    total += float(row.get("cost_usd") or 0.0)
                except ValueError:
                    continue
    pilot_rows_path = calibration_dir / "pilot_rows.json"
    if pilot_rows_path.exists():
        try:
            pilot_data = json.loads(pilot_rows_path.read_text())
        except json.JSONDecodeError:
            pilot_data = {}
        for per_task in pilot_data.values():
            for row in per_task.values():
                try:
                    total += float(row.get("cost_usd") or 0.0)
                except (TypeError, ValueError):
                    continue
    return total


if __name__ == "__main__":
    _cli()
