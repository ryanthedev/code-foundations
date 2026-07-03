"""Unit tests for analyze.py (Phase 5).

Known-answer tests (DW-5.1) use hand-computable synthetic rows so the paired
delta and bootstrap CI are checkable by arithmetic, not just "code ran".
Structural tests for DW-5.3/DW-5.5 read this benchmark's real, already-produced
Phase 1-4 artifacts (tasks/*/manifest.json, tasks/*/answer-key.json,
calibration/pilot_rows.json) read-only -- never modified here.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

import analyze as an

REAL_TASKS_DIR = Path(__file__).resolve().parent / "tasks"
REAL_CALIBRATION_DIR = Path(__file__).resolve().parent / "calibration"


def _row(task, model, run_n, score, **extra):
    base = {
        "task": task, "rung": 2, "model": model, "run_n": run_n,
        "correct": 1 if score == 1.0 else 0, "score": score,
        "tp": 0, "fp": 0, "fn": 0, "judge_fail": False,
        "time_seconds": 10.0, "tokens": 100, "cost_usd": 0.1,
    }
    base.update(extra)
    return base


# ---------------------------------------------------------------------------
# DW-5.1: known-answer paired delta + fixed-seed bootstrap
# ---------------------------------------------------------------------------

def test_paired_deltas_hand_computable_case():
    # task-a: fable=0.8, sonnet=0.6 -> delta 0.2; task-b: fable=0.9, sonnet=0.7 -> delta 0.2
    rows = [
        _row("task-a", "fable-5", 1, 0.8), _row("task-a", "sonnet-5", 1, 0.6),
        _row("task-b", "fable-5", 1, 0.9), _row("task-b", "sonnet-5", 1, 0.7),
    ]
    deltas = an.paired_deltas(rows, "fable-5", "sonnet-5")
    assert deltas == {"task-a": pytest.approx(0.2), "task-b": pytest.approx(0.2)}


def test_paired_deltas_averages_multiple_runs_per_model():
    # fable runs: 0.8, 1.0 -> mean 0.9; sonnet runs: 0.4, 0.6 -> mean 0.5; delta 0.4
    rows = [
        _row("task-a", "fable-5", 1, 0.8), _row("task-a", "fable-5", 2, 1.0),
        _row("task-a", "sonnet-5", 1, 0.4), _row("task-a", "sonnet-5", 2, 0.6),
    ]
    deltas = an.paired_deltas(rows, "fable-5", "sonnet-5")
    assert deltas == {"task-a": pytest.approx(0.4)}


def test_paired_deltas_task_missing_one_model_is_excluded():
    rows = [_row("task-a", "fable-5", 1, 0.8)]  # sonnet-5 never ran task-a
    assert an.paired_deltas(rows, "fable-5", "sonnet-5") == {}


def test_paired_deltas_asymmetric_run_count_raises():
    # T-5.6: a pilot row leaking in unfiltered creates asymmetric n for one model
    rows = [
        _row("task-a", "fable-5", 1, 0.8), _row("task-a", "fable-5", 2, 0.9, pilot=True),
        _row("task-a", "sonnet-5", 1, 0.6),
    ]
    with pytest.raises(ValueError, match="asymmetric run count"):
        an.paired_deltas(rows, "fable-5", "sonnet-5")


def test_bootstrap_ci_fixed_seed_is_deterministic():
    deltas = [0.2, 0.1, 0.3, -0.1, 0.15]
    result_1 = an.bootstrap_ci(deltas, seed=42)
    result_2 = an.bootstrap_ci(deltas, seed=42)
    assert result_1 == result_2


def test_bootstrap_ci_hand_computable_interval_collapses_on_identical_deltas():
    # every resample mean of a constant list is that same constant -> CI is a point
    mean, lo, hi = an.bootstrap_ci([0.25, 0.25, 0.25, 0.25], seed=42)
    assert mean == pytest.approx(0.25)
    assert lo == pytest.approx(0.25)
    assert hi == pytest.approx(0.25)


def test_bootstrap_ci_empty_deltas_returns_zeros():
    assert an.bootstrap_ci([]) == (0.0, 0.0, 0.0)


def test_bootstrap_ci_mean_matches_arithmetic_mean():
    deltas = [1.0, 2.0, 3.0, 4.0]
    mean, lo, hi = an.bootstrap_ci(deltas, seed=7)
    assert mean == pytest.approx(2.5)
    assert lo <= mean <= hi


# ---------------------------------------------------------------------------
# DW-5.2 (+ edges T-5.2, T-5.3): rung_verdict
# ---------------------------------------------------------------------------

def test_rung_verdict_judge_fail_rows_excluded_but_counted():
    rows = [
        _row("task-a", "fable-5", 1, 0.9), _row("task-a", "sonnet-5", 1, 0.5),
        _row("task-b", "fable-5", 1, 0.9), _row("task-b", "sonnet-5", 1, 0.5),
        _row("task-c", "fable-5", 1, 1.0, judge_fail=True),
        _row("task-c", "sonnet-5", 1, 0.0, judge_fail=True),
    ]
    verdict = an.rung_verdict(rows, cheaper_model="sonnet-5", costlier_model="fable-5")
    assert verdict["n_tasks"] == 2  # task-c excluded from the paired stats
    assert verdict["quality_note"]["judge_fail_excluded"] == 2
    assert "task-c" not in verdict["per_task_deltas"]


def test_rung_verdict_pilot_rows_excluded_from_paired_stats():
    rows = [
        _row("task-a", "fable-5", 1, 0.9), _row("task-a", "sonnet-5", 1, 0.5),
        _row("task-b", "fable-5", 1, 0.9), _row("task-b", "sonnet-5", 1, 0.5),
        _row("task-c", "fable-5", 1, 1.0, pilot=True),
        _row("task-c", "sonnet-5", 1, 1.0, pilot=True),
    ]
    verdict = an.rung_verdict(rows, cheaper_model="sonnet-5", costlier_model="fable-5")
    assert verdict["n_tasks"] == 2
    assert verdict["quality_note"]["pilot_excluded"] == 2


def test_rung_verdict_single_surviving_task_is_insufficient_data():
    rows = [_row("task-a", "fable-5", 1, 0.9), _row("task-a", "sonnet-5", 1, 0.5)]
    verdict = an.rung_verdict(rows, cheaper_model="sonnet-5", costlier_model="fable-5")
    assert verdict["verdict"] == "insufficient-data"
    assert verdict["n_tasks"] == 1
    assert "mean_delta" not in verdict  # never a mean-only claim


def test_rung_verdict_zero_tasks_is_insufficient_data():
    verdict = an.rung_verdict([], cheaper_model="sonnet-5", costlier_model="fable-5")
    assert verdict["verdict"] == "insufficient-data"
    assert verdict["n_tasks"] == 0


def test_rung_verdict_consistent_win_changes_rule():
    # costlier wins every task, by a wide and consistent margin -> CI clears zero
    rows = []
    for i, (a, b) in enumerate([(0.95, 0.5), (0.9, 0.45), (0.98, 0.4)]):
        rows.append(_row(f"task-{i}", "fable-5", 1, a))
        rows.append(_row(f"task-{i}", "sonnet-5", 1, b))
    verdict = an.rung_verdict(rows, cheaper_model="sonnet-5", costlier_model="fable-5")
    assert verdict["verdict"] == "change-rule"
    assert verdict["ci_lo"] > 0


def test_rung_verdict_tie_within_ci_goes_to_cheaper():
    # both models identical on every task -> CI straddles zero
    rows = []
    for i in range(3):
        rows.append(_row(f"task-{i}", "fable-5", 1, 0.8))
        rows.append(_row(f"task-{i}", "sonnet-5", 1, 0.8))
    verdict = an.rung_verdict(rows, cheaper_model="sonnet-5", costlier_model="fable-5")
    assert verdict["verdict"] == "no-difference→cheaper"


# ---------------------------------------------------------------------------
# Q2 / review_tier_verdict
# ---------------------------------------------------------------------------

def _defect_row(task, defect_id, model, found_count):
    return {"task": task, "defect_id": defect_id, "model": model, "found_count": found_count}


def test_review_tier_verdict_insufficient_data_below_min_tasks():
    rows = [_defect_row("task-a", "D1", "sonnet-5", 0), _defect_row("task-a", "D1", "fable-5", 5)]
    verdict = an.review_tier_verdict(rows, lower_model="sonnet-5", higher_model="fable-5")
    assert verdict["verdict"] == "insufficient-data"
    assert verdict["n_tasks"] == 1


def test_review_tier_verdict_qualifying_gap_changes_rule():
    rows = []
    for task in ("task-a", "task-b"):
        rows.append(_defect_row(task, "D1", "sonnet-5", 0))
        rows.append(_defect_row(task, "D1", "fable-5", 3))
    verdict = an.review_tier_verdict(rows, lower_model="sonnet-5", higher_model="fable-5")
    assert verdict["verdict"] == "change-rule"
    assert len(verdict["qualifying_gaps"]) == 2


def test_review_tier_verdict_no_gap_is_no_difference():
    rows = []
    for task in ("task-a", "task-b"):
        rows.append(_defect_row(task, "D1", "sonnet-5", 5))
        rows.append(_defect_row(task, "D1", "fable-5", 5))
    verdict = an.review_tier_verdict(rows, lower_model="sonnet-5", higher_model="fable-5")
    assert verdict["verdict"] == "no-difference→cheaper"
    assert verdict["qualifying_gaps"] == []


# ---------------------------------------------------------------------------
# load_matrix_rows / filter_stat_rows
# ---------------------------------------------------------------------------

def test_load_matrix_rows_empty_dir_returns_empty_list(tmp_path):
    assert an.load_matrix_rows(tmp_path) == []


def test_load_matrix_rows_parses_and_coerces_types(tmp_path):
    csv_path = tmp_path / "results-01-heartbeat-message.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=an.ROW_FIELDS)
        writer.writeheader()
        writer.writerow({
            "task": "01-heartbeat-message", "rung": 1, "model": "sonnet-5", "run_n": 1,
            "correct": 1, "score": 1.0, "tp": 0, "fp": 0, "fn": 0, "judge_fail": "False",
            "time_seconds": 12.5, "tokens": 100, "cost_usd": 0.05,
        })
    rows = an.load_matrix_rows(tmp_path)
    assert len(rows) == 1
    row = rows[0]
    assert row["rung"] == 1 and isinstance(row["rung"], int)
    assert row["score"] == pytest.approx(1.0) and isinstance(row["score"], float)
    assert row["judge_fail"] is False


def test_load_matrix_rows_missing_column_raises(tmp_path):
    csv_path = tmp_path / "results-broken.csv"
    csv_path.write_text("task,rung\nfoo,1\n")
    with pytest.raises(ValueError, match="missing ROW_FIELDS"):
        an.load_matrix_rows(tmp_path)


def test_filter_stat_rows_counts_and_excludes():
    rows = [
        _row("a", "fable-5", 1, 1.0),
        _row("a", "sonnet-5", 1, 1.0, judge_fail=True),
        _row("b", "fable-5", 1, 1.0, pilot=True),
    ]
    usable, quality_note = an.filter_stat_rows(rows)
    assert len(usable) == 1
    assert quality_note == {
        "total_rows": 3, "judge_fail_excluded": 1, "pilot_excluded": 1, "usable_rows": 1,
    }


# ---------------------------------------------------------------------------
# DW-5.3: rung-4 per-defect detection table (real calibration data)
# ---------------------------------------------------------------------------

@pytest.fixture
def real_pilot_rows():
    return json.loads((REAL_CALIBRATION_DIR / "pilot_rows.json").read_text())


def test_rung4_defect_table_structure_and_counts(real_pilot_rows):
    table = an.rung4_defect_table(real_pilot_rows, REAL_TASKS_DIR)
    loop_core = [r for r in table if r["task"] == "04-loop-core-review"]
    # 5 defects x 2 models (sonnet-5, fable-5) = 10 rows
    assert len(loop_core) == 10
    for r in loop_core:
        assert r["source"] == "pilot"
        assert r["of_n_runs"] == 2
        assert r["found_count"] == 2  # tp==5,fn==0 on both pilot runs for both models


def test_rung4_defect_table_source_labels_gold_validation(real_pilot_rows):
    table = an.rung4_defect_table(real_pilot_rows, REAL_TASKS_DIR)
    hash_progress = [r for r in table if r["task"] == "04-hash-progress-review"]
    # 4 defects (HP-1..HP-4), one gold-validation row each -- never model-piloted
    assert len(hash_progress) == 4
    for r in hash_progress:
        assert r["model"] == "gold-reference"
        assert "gold-validation" in r["source"]
        assert r["of_n_runs"] == 1
        assert r["found_count"] == 1


def test_rung4_defect_table_only_includes_rung4_tasks(real_pilot_rows):
    table = an.rung4_defect_table(real_pilot_rows, REAL_TASKS_DIR)
    assert {r["task"] for r in table} == {"04-loop-core-review", "04-hash-progress-review"}


def test_rung4_defect_table_unattributed_run_not_assumed_found():
    fake_pilot_rows = {
        "04-loop-core-review": {
            "fable-5": {"model": "fable-5", "tp": 3, "fn": 2, "run_n": 1},
        }
    }
    table = an.rung4_defect_table(fake_pilot_rows, REAL_TASKS_DIR)
    fable_rows = [r for r in table if r["model"] == "fable-5"]
    assert all(r["found_count"] == 0 for r in fable_rows)
    assert all(r["unattributed_runs"] == 1 for r in fable_rows)


# ---------------------------------------------------------------------------
# DW-5.5: traceability table (real task manifests)
# ---------------------------------------------------------------------------

def test_traceability_table_reads_every_task_manifest():
    rows = an.traceability_table(REAL_TASKS_DIR)
    task_dirs = {p.name for p in REAL_TASKS_DIR.iterdir() if (p / "manifest.json").exists()}
    assert {r["task"] for r in rows} == task_dirs
    for r in rows:
        assert r["repo"] and r["plan"] and r["phase"]


# ---------------------------------------------------------------------------
# DW-5.4: speed summary
# ---------------------------------------------------------------------------

def test_speed_summary_median_and_range():
    rows = [
        _row("a", "fable-5", 1, 1.0, time_seconds=10.0),
        _row("a", "fable-5", 2, 1.0, time_seconds=30.0),
        _row("a", "fable-5", 3, 1.0, time_seconds=20.0),
    ]
    summary = an.speed_summary(rows)
    assert summary["fable-5"]["median"] == pytest.approx(20.0)
    assert summary["fable-5"]["min"] == pytest.approx(10.0)
    assert summary["fable-5"]["max"] == pytest.approx(30.0)
    assert summary["fable-5"]["n"] == 3


# ---------------------------------------------------------------------------
# count_pilot_comparisons (real calibration data)
# ---------------------------------------------------------------------------

def test_count_pilot_comparisons_matches_real_pilot_rows_json(real_pilot_rows):
    pairs, individual = an.count_pilot_comparisons(real_pilot_rows)
    assert individual == 18
    assert pairs == 9


# ---------------------------------------------------------------------------
# render_report / REPORT.md content checks (DW-5.2, DW-5.3, DW-5.4, DW-5.5)
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_report(real_pilot_rows):
    q1 = an.rung_verdict([], cheaper_model="opus-4.8", costlier_model="fable-5")
    q2 = an.review_tier_verdict([], lower_model="sonnet-5", higher_model="fable-5")
    defect_table = an.rung4_defect_table(real_pilot_rows, REAL_TASKS_DIR)
    traceability = an.traceability_table(REAL_TASKS_DIR)
    pairs, individual = an.count_pilot_comparisons(real_pilot_rows)
    return an.render_report(
        q1_verdict=q1, q2_verdict=q2, defect_table=defect_table,
        traceability=traceability, speed={}, pilot_pairs=pairs,
        pilot_individual=individual,
        quality_note={"total_rows": 0, "judge_fail_excluded": 0, "pilot_excluded": 0, "usable_rows": 0},
    )


def test_report_contains_q1_and_q2_verdicts(sample_report):
    assert "Q1" in sample_report and "Q2" in sample_report
    assert "insufficient-data" in sample_report


def test_report_quotes_rule_text_verbatim(sample_report):
    assert an.RULE_1_TIES_CHEAPER in sample_report
    assert an.RULE_2_CONSISTENT_WIN in sample_report
    assert an.RULE_3_REVIEW_ASYMMETRIC in sample_report


def test_report_shows_rule_inputs(sample_report):
    assert "n_tasks (surviving): 0" in sample_report


def test_report_contains_defect_table(sample_report):
    assert "LC-1-conditional-default-cap" in sample_report
    assert "HP-1-missing-opening-zero-report" in sample_report
    assert "gold-validation" in sample_report
    assert "pilot" in sample_report


def test_report_contains_traceability_table_for_all_tasks(sample_report):
    for task_dir in REAL_TASKS_DIR.iterdir():
        if (task_dir / "manifest.json").exists():
            assert task_dir.name in sample_report


def test_report_speed_section_labeled_secondary(sample_report):
    assert "secondary" in sample_report.lower()


def test_report_verdict_sections_never_mention_speed(sample_report):
    q1_section = sample_report.split("## Q1")[1].split("## Q2")[0]
    q2_section = sample_report.split("## Q2")[1].split("## Calibration")[0]
    for section in (q1_section, q2_section):
        assert "median" not in section.lower()
        assert "time_seconds" not in section.lower()


def test_report_no_verdict_cites_a_subtwox_speed_gap(sample_report):
    # No verdict section should contain an explicit speed multiplier claim
    for marker in ("## Q1", "## Q2"):
        section = sample_report.split(marker)[1].split("## ")[0]
        assert "x faster" not in section.lower()
        assert "x slower" not in section.lower()
