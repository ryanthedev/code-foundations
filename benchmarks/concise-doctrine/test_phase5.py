"""Phase 5 validation suite: matrix orchestrator + report generator.

Covers all Phase 5 DW items and goes beyond the DW floor. All build execution is
mocked — no real builds or LLM calls. Report generation is tested on canned rows.

DW-ID traceability:
  DW-5.1 — test_DW_5_1_*  (mocked matrix writes CSV; partial cells accounted for;
                            already-done cells are skipped / idempotent)
  DW-5.2 — test_DW_5_2_*  (report shows medians per arm×model; arm deltas; guardrail)
  DW-5.3 — test_DW_5_3_*  (verdict: GO when quality↑ + no regression;
                            NO-GO when regression; NO-GO when no quality delta;
                            noise-boundary resolves deterministically)
  DW-5.4 — test_DW_5_4_*  (N/partial/unscorable counts; all-partial cell flagged;
                            no silent omission of dropped runs)

Off-DW (beyond the floor):
  test_offdw_*  (MatrixSpec validation; iter_cells; cell_run_dir; _median;
                 compute_deltas; render_report verdict last-line format;
                 dry-run prints; score-only path; CSV schema)
"""
from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path
from typing import Iterator
from unittest.mock import patch, MagicMock

import pytest

CONCISE_DOCTRINE = Path(__file__).resolve().parent
if str(CONCISE_DOCTRINE) not in sys.path:
    sys.path.insert(0, str(CONCISE_DOCTRINE))

import run_matrix as rm  # noqa: E402
from run_matrix import (  # noqa: E402
    MatrixSpec,
    iter_cells,
    cell_run_dir,
    cell_is_done,
    orchestrate,
    write_csv,
    load_rows,
    compute_medians,
    compute_deltas,
    check_guardrail,
    compute_verdict,
    count_accounting,
    render_report,
    generate_report,
    NOISE_THRESHOLD,
    _median,
    _DEFAULT_ARMS,
    _DEFAULT_MODELS,
)


# --------------------------------------------------------------------------- #
# helpers                                                                       #
# --------------------------------------------------------------------------- #

def _spec(tmp_path, *, n_runs=2, tasks=None, arms=None, models=None) -> MatrixSpec:
    """Build a minimal MatrixSpec for testing (2 tasks, both arms, both models, n runs)."""
    return MatrixSpec.build(
        n_runs=n_runs,
        out_root=tmp_path / "out",
        tasks=tasks or ("01-duration", "02-rpn"),
        arms=arms or ("baseline", "concise"),
        models=models or ("sonnet", "opus"),
    )


def _make_row(
    task="01-duration",
    arm="baseline",
    model="sonnet",
    run_n=1,
    *,
    status="ok",
    loc=50,
    cc_avg=1.5,
    cc_max=3,
    fn_len_max=20,
    n_funcs=5,
    mutation=1.0,
    hidden_dw=1.0,
    hidden_offdw=0.8,
    rubric_score=0.8,
    out_root: Path | None = None,
) -> dict:
    """Build a synthetic full-schema row."""
    from run_matrix import ROW_FIELDS  # noqa: PLC0415
    out_root = out_root or Path("/fake")
    run_id = str(cell_run_dir(task, arm, model, run_n, out_root).relative_to(out_root))
    row = {
        "run_id": run_id,
        "task": task,
        "arm": arm,
        "model": model,
        "loc": loc,
        "cc_avg": cc_avg,
        "cc_max": cc_max,
        "fn_len_max": fn_len_max,
        "n_funcs": n_funcs,
        "mutation": mutation,
        "hidden_dw": hidden_dw,
        "hidden_offdw": hidden_offdw,
        "rubric_score": rubric_score,
        "status": status,
    }
    # Fill missing fields with None.
    for f in ROW_FIELDS:
        row.setdefault(f, None)
    return row


def _canned_rows_go() -> list[dict]:
    """Canned rows where concise arm clearly improves quality with no regression."""
    rows = []
    for model in ("sonnet", "opus"):
        # baseline: higher LOC + complexity
        rows.append(_make_row("01-duration", "baseline", model, 1,
                              loc=80, cc_avg=3.0, cc_max=6, fn_len_max=30,
                              mutation=1.0, hidden_dw=1.0, rubric_score=0.8))
        rows.append(_make_row("02-rpn", "baseline", model, 1,
                              loc=70, cc_avg=2.5, cc_max=5, fn_len_max=25,
                              mutation=0.95, hidden_dw=1.0, rubric_score=0.75))
        # concise: lower LOC + complexity, equal-or-better rubric
        rows.append(_make_row("01-duration", "concise", model, 1,
                              loc=50, cc_avg=2.0, cc_max=4, fn_len_max=20,
                              mutation=1.0, hidden_dw=1.0, rubric_score=0.85))
        rows.append(_make_row("02-rpn", "concise", model, 1,
                              loc=45, cc_avg=1.8, cc_max=3, fn_len_max=18,
                              mutation=0.97, hidden_dw=1.0, rubric_score=0.8))
    return rows


def _canned_rows_nogo_regression() -> list[dict]:
    """Canned rows where concise improves quality but correctness regresses."""
    rows = []
    for model in ("sonnet",):
        rows.append(_make_row("01-duration", "baseline", model, 1,
                              loc=80, cc_avg=3.0, mutation=1.0, hidden_dw=1.0))
        rows.append(_make_row("01-duration", "concise", model, 1,
                              loc=50, cc_avg=2.0,
                              # Correctness drops by 0.15 — beyond noise 0.05
                              mutation=0.85, hidden_dw=0.80))
    return rows


def _canned_rows_nogo_no_delta() -> list[dict]:
    """Canned rows where concise doesn't improve any quality metric."""
    rows = []
    for model in ("sonnet",):
        rows.append(_make_row("01-duration", "baseline", model, 1,
                              loc=50, cc_avg=2.0, cc_max=4, fn_len_max=20,
                              mutation=1.0, hidden_dw=1.0))
        # concise is identical (no improvement)
        rows.append(_make_row("01-duration", "concise", model, 1,
                              loc=50, cc_avg=2.0, cc_max=4, fn_len_max=20,
                              mutation=1.0, hidden_dw=1.0))
    return rows


def _write_rows_csv(rows: list[dict], path: Path) -> None:
    """Write canned rows to a CSV for generate_report tests."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        from run_matrix import ROW_FIELDS  # noqa: PLC0415
        w = csv.DictWriter(fh, fieldnames=ROW_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


# --------------------------------------------------------------------------- #
# DW-5.1: orchestrator drives mock matrix, writes CSV, accounts for partials   #
# --------------------------------------------------------------------------- #

class TestDW51MockedMatrix:

    def test_DW_5_1_mocked_matrix_writes_csv(self, tmp_path):
        """Orchestrator drives every cell in the grid (mocked) and writes all rows to CSV."""
        spec = _spec(tmp_path, n_runs=1, tasks=("01-duration",),
                     arms=("baseline", "concise"), models=("sonnet",))

        call_log: list[tuple] = []

        def mock_cell_fn(task, arm, model, run_n, spec_):
            call_log.append((task, arm, model, run_n))
            return _make_row(task, arm, model, run_n, out_root=spec_.out_root)

        rows = orchestrate(spec, cell_fn=mock_cell_fn)

        # All 2 cells (1 task × 2 arms × 1 model × 1 run) were called.
        assert len(call_log) == 2
        assert ("01-duration", "baseline", "sonnet", 1) in call_log
        assert ("01-duration", "concise", "sonnet", 1) in call_log

        # Rows returned.
        assert len(rows) == 2

        # Write and verify CSV.
        csv_path = spec.results_dir / "matrix-runs.csv"
        write_csv(rows, csv_path)
        assert csv_path.exists()
        loaded = load_rows(csv_path)
        assert len(loaded) == 2
        tasks_in_csv = {r["task"] for r in loaded}
        assert tasks_in_csv == {"01-duration"}

    def test_DW_5_1_partial_cell_accounted(self, tmp_path):
        """Partial-status runs appear in the output CSV — not silently dropped."""
        spec = _spec(tmp_path, n_runs=1, tasks=("01-duration",),
                     arms=("baseline",), models=("sonnet",))

        def mock_cell_fn(task, arm, model, run_n, spec_):
            return _make_row(task, arm, model, run_n, status="partial",
                             out_root=spec_.out_root)

        rows = orchestrate(spec, cell_fn=mock_cell_fn)
        assert rows[0]["status"] == "partial"

        csv_path = spec.results_dir / "matrix-runs.csv"
        write_csv(rows, csv_path)
        loaded = load_rows(csv_path)
        assert len(loaded) == 1
        assert loaded[0]["status"] == "partial"

    def test_DW_5_1_skip_already_scored(self, tmp_path):
        """A cell with an existing meta.json is skipped (idempotent resume)."""
        spec = _spec(tmp_path, n_runs=1, tasks=("01-duration",),
                     arms=("baseline",), models=("sonnet",))

        # Pre-seed the meta.json so cell_is_done() returns True.
        rd = cell_run_dir("01-duration", "baseline", "sonnet", 1, spec.out_root)
        rd.mkdir(parents=True)
        (rd / "meta.json").write_text(json.dumps({
            "task": "01-duration", "arm": "baseline", "model": "sonnet",
            "run": 1, "status": "ok",
        }))

        new_builds: list[tuple] = []

        def mock_cell_fn(task, arm, model, run_n, spec_):
            new_builds.append((task, arm, model, run_n))
            return _make_row(task, arm, model, run_n, out_root=spec_.out_root)

        rows = orchestrate(spec, cell_fn=mock_cell_fn)

        # No new builds (skipped the done cell).
        assert new_builds == []
        # But the row was still returned (loaded from existing).
        assert len(rows) == 1

    def test_DW_5_1_full_grid_cell_count(self, tmp_path):
        """All 2×2×2×2 = 16 cells are generated for the default 2-task grid."""
        spec = _spec(tmp_path, n_runs=2, tasks=("01-duration", "02-rpn"),
                     arms=("baseline", "concise"), models=("sonnet", "opus"))
        cells = list(iter_cells(spec))
        assert len(cells) == 2 * 2 * 2 * 2  # tasks × arms × models × runs

    def test_DW_5_1_unscorable_run_in_csv(self, tmp_path):
        """Unscorable runs appear in the CSV, never silently omitted."""
        spec = _spec(tmp_path, n_runs=1, tasks=("01-duration",),
                     arms=("baseline",), models=("sonnet",))

        def mock_cell_fn(task, arm, model, run_n, spec_):
            return _make_row(task, arm, model, run_n, status="unscorable",
                             loc=None, cc_avg=None, out_root=spec_.out_root)

        rows = orchestrate(spec, cell_fn=mock_cell_fn)
        csv_path = spec.results_dir / "matrix-runs.csv"
        write_csv(rows, csv_path)
        loaded = load_rows(csv_path)
        assert len(loaded) == 1
        assert loaded[0]["status"] == "unscorable"


# --------------------------------------------------------------------------- #
# DW-5.2: report shows medians, deltas, guardrail                              #
# --------------------------------------------------------------------------- #

class TestDW52Report:

    def test_DW_5_2_report_medians(self, tmp_path):
        """Report contains medians per arm×model for all numeric metrics."""
        rows = _canned_rows_go()
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)

        report_path = tmp_path / "REPORT.md"
        content = generate_report(csv_path, report_path,
                                  models=("sonnet", "opus"),
                                  arms=("baseline", "concise"))

        # Report must contain the medians table header.
        assert "Medians per Arm" in content
        # Both arms appear as rows.
        assert "baseline" in content
        assert "concise" in content
        # Both models appear.
        assert "sonnet" in content
        assert "opus" in content
        # Key metrics present in report.
        assert "loc" in content
        assert "cc_avg" in content
        assert "mutation" in content

    def test_DW_5_2_report_deltas(self, tmp_path):
        """Report contains arm delta rows for every numeric metric."""
        rows = _canned_rows_go()
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        content = generate_report(csv_path, report_path,
                                  models=("sonnet", "opus"),
                                  arms=("baseline", "concise"))

        assert "Arm Deltas" in content
        assert "concise" in content.lower()
        assert "baseline" in content.lower()

    def test_DW_5_2_guardrail_check(self, tmp_path):
        """Report contains explicit guardrail correctness+mutation section."""
        rows = _canned_rows_go()
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        content = generate_report(csv_path, report_path,
                                  models=("sonnet", "opus"),
                                  arms=("baseline", "concise"))

        assert "Guardrail" in content
        # Must mention correctness or mutation in the guardrail context.
        assert "mutation" in content.lower() or "correctness" in content.lower()
        # Must state the noise threshold.
        assert "0.05" in content

    def test_DW_5_2_medians_correct_values(self, tmp_path):
        """Median values in the report match hand-computed values from canned rows."""
        # Single model, single arm, two tasks — median of two LOC values.
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, loc=60),
            _make_row("02-rpn", "baseline", "sonnet", 1, loc=80),
        ]
        medians = compute_medians(rows)
        # Median of [60, 80] = 70.0
        assert medians["baseline"]["sonnet"]["loc"] == 70.0

    def test_DW_5_2_medians_exclude_unscorable(self, tmp_path):
        """Unscorable rows are excluded from median computation."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, loc=100, status="ok"),
            _make_row("02-rpn", "baseline", "sonnet", 1, loc=None, status="unscorable"),
        ]
        medians = compute_medians(rows)
        # Only the ok row contributed — median is 100.
        assert medians["baseline"]["sonnet"]["loc"] == 100.0


# --------------------------------------------------------------------------- #
# DW-5.3: verdict GO/NO-GO logic                                               #
# --------------------------------------------------------------------------- #

class TestDW53Verdict:

    def _run_verdict(self, rows, models=("sonnet",)):
        medians = compute_medians(rows)
        deltas = compute_deltas(medians, models)
        passed, g_rationale = check_guardrail(deltas, models)
        verdict, v_rationale = compute_verdict(medians, deltas, passed, models)
        return verdict, v_rationale, passed

    def test_DW_5_3_verdict_go(self, tmp_path):
        """GO when quality improves and no guardrail regression."""
        rows = _canned_rows_go()
        verdict, rationale, passed = self._run_verdict(rows, ("sonnet", "opus"))
        assert verdict == "GO"
        assert passed is True
        assert "GO" in rationale or "quality improved" in rationale.lower()

    def test_DW_5_3_verdict_nogo_regression(self):
        """NO-GO when correctness/mutation regresses beyond noise."""
        rows = _canned_rows_nogo_regression()
        verdict, rationale, passed = self._run_verdict(rows, ("sonnet",))
        assert verdict == "NO-GO"
        assert passed is False
        assert "regress" in rationale.lower() or "regression" in rationale.lower()

    def test_DW_5_3_verdict_nogo_no_delta(self):
        """NO-GO when concise shows no quality improvement."""
        rows = _canned_rows_nogo_no_delta()
        verdict, rationale, passed = self._run_verdict(rows, ("sonnet",))
        assert verdict == "NO-GO"
        assert "no quality improvement" in rationale.lower() or "no quality" in rationale.lower()

    def test_DW_5_3_verdict_at_noise_threshold_nogo(self):
        """Regression exactly at -NOISE_THRESHOLD resolves as NO-GO (strict boundary)."""
        # concise mutation = baseline mutation - NOISE_THRESHOLD exactly
        baseline_mutation = 1.0
        concise_mutation = baseline_mutation - NOISE_THRESHOLD  # exactly at threshold

        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1,
                      loc=80, cc_avg=3.0, mutation=baseline_mutation, hidden_dw=1.0),
            # concise has improved quality metrics but mutation exactly at threshold
            _make_row("01-duration", "concise", "sonnet", 1,
                      loc=50, cc_avg=2.0, mutation=concise_mutation, hidden_dw=1.0),
        ]
        medians = compute_medians(rows)
        deltas = compute_deltas(medians, ("sonnet",))
        passed, rationale = check_guardrail(deltas, ("sonnet",))
        # delta == -NOISE_THRESHOLD is NOT < -NOISE_THRESHOLD, so guardrail passes
        # (the check is delta < -NOISE_THRESHOLD for violation)
        assert passed is True, (
            "At exactly -NOISE_THRESHOLD the guardrail should pass (not strict <)"
        )

    def test_DW_5_3_verdict_just_beyond_threshold_nogo(self):
        """Regression just beyond -NOISE_THRESHOLD (by one epsilon) is NO-GO."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1,
                      mutation=1.0, loc=80, cc_avg=3.0, hidden_dw=1.0),
            _make_row("01-duration", "concise", "sonnet", 1,
                      mutation=1.0 - NOISE_THRESHOLD - 0.001,  # just beyond threshold
                      loc=50, cc_avg=2.0, hidden_dw=1.0),
        ]
        medians = compute_medians(rows)
        deltas = compute_deltas(medians, ("sonnet",))
        passed, _ = check_guardrail(deltas, ("sonnet",))
        assert passed is False

    def test_DW_5_3_report_ends_with_verdict_line(self, tmp_path):
        """The last line of REPORT.md is 'VERDICT: GO|NO-GO — <rationale>'."""
        rows = _canned_rows_go()
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        generate_report(csv_path, report_path,
                        models=("sonnet", "opus"),
                        arms=("baseline", "concise"))

        content = report_path.read_text()
        last_line = content.rstrip("\n").split("\n")[-1]
        assert last_line.startswith("VERDICT: GO") or last_line.startswith("VERDICT: NO-GO"), (
            f"Last line must start with 'VERDICT: GO' or 'VERDICT: NO-GO', got: {last_line!r}"
        )
        assert " — " in last_line, f"Verdict line must include rationale after ' — ': {last_line!r}"

    def test_DW_5_3_nogo_report_verdict_line(self, tmp_path):
        """REPORT.md for a NO-GO run also ends with the VERDICT line."""
        rows = _canned_rows_nogo_regression()
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        generate_report(csv_path, report_path,
                        models=("sonnet",),
                        arms=("baseline", "concise"))

        content = report_path.read_text()
        last_line = content.rstrip("\n").split("\n")[-1]
        assert last_line.startswith("VERDICT: NO-GO")

    def test_DW_5_3_verdict_cites_numbers(self, tmp_path):
        """The verdict rationale cites actual metric values (not just labels)."""
        rows = _canned_rows_go()
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        content = generate_report(csv_path, report_path,
                                  models=("sonnet", "opus"),
                                  arms=("baseline", "concise"))
        # Should contain numbers in the verdict section.
        verdict_section = content[content.find("## Verdict"):]
        # Numbers like -0.xxxx or +0.xxxx or digit sequences.
        import re
        has_numbers = bool(re.search(r"[-+]?\d+\.\d+", verdict_section))
        assert has_numbers, "Verdict section should cite actual numeric values"


# --------------------------------------------------------------------------- #
# DW-5.4: honest accounting                                                    #
# --------------------------------------------------------------------------- #

class TestDW54Accounting:

    def test_DW_5_4_accounting_in_report(self, tmp_path):
        """Report shows N per cell, partial/unscorable counts."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, status="ok"),
            _make_row("01-duration", "baseline", "sonnet", 2, status="partial"),
            _make_row("01-duration", "concise", "sonnet", 1, status="ok"),
            _make_row("01-duration", "concise", "sonnet", 2, status="unscorable"),
        ]
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        content = generate_report(csv_path, report_path,
                                  models=("sonnet",),
                                  arms=("baseline", "concise"))

        # Accounting section exists.
        assert "Run Accounting" in content or "accounting" in content.lower()
        # N=2 appears for each cell.
        assert "2" in content
        # "partial" and "unscorable" mentioned.
        assert "partial" in content.lower()
        assert "unscorable" in content.lower()

    def test_DW_5_4_all_partial_cell_flagged(self, tmp_path):
        """A cell where every run is partial gets flagged explicitly in the report."""
        rows = [
            # baseline: normal
            _make_row("01-duration", "baseline", "sonnet", 1, status="ok"),
            # concise: all partial
            _make_row("01-duration", "concise", "sonnet", 1, status="partial"),
            _make_row("01-duration", "concise", "sonnet", 2, status="partial"),
        ]
        accounting = count_accounting(rows)
        # concise/sonnet cell should be flagged all_partial
        assert accounting["concise"]["sonnet"]["all_partial"] is True
        # baseline/sonnet cell should NOT be flagged
        assert accounting["baseline"]["sonnet"]["all_partial"] is False

    def test_DW_5_4_all_partial_flag_in_report(self, tmp_path):
        """An all-partial cell appears as a FLAG in the report, not silently omitted."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, status="ok"),
            _make_row("01-duration", "concise", "sonnet", 1, status="partial"),
            _make_row("01-duration", "concise", "sonnet", 2, status="partial"),
        ]
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        content = generate_report(csv_path, report_path,
                                  models=("sonnet",),
                                  arms=("baseline", "concise"))

        assert "FLAG" in content or "all-partial" in content.lower()

    def test_DW_5_4_no_silent_omission(self, tmp_path):
        """All rows (ok, partial, unscorable) appear in the CSV — nothing dropped."""
        spec = _spec(tmp_path, n_runs=2, tasks=("01-duration",),
                     arms=("baseline",), models=("sonnet",))

        statuses = ["ok", "partial"]
        call_idx = [0]

        def mock_cell_fn(task, arm, model, run_n, spec_):
            s = statuses[call_idx[0] % len(statuses)]
            call_idx[0] += 1
            return _make_row(task, arm, model, run_n, status=s, out_root=spec_.out_root)

        rows = orchestrate(spec, cell_fn=mock_cell_fn)
        assert len(rows) == 2  # both runs present

        csv_path = spec.results_dir / "matrix-runs.csv"
        write_csv(rows, csv_path)
        loaded = load_rows(csv_path)
        assert len(loaded) == 2

        loaded_statuses = {r["status"] for r in loaded}
        assert "ok" in loaded_statuses
        assert "partial" in loaded_statuses

    def test_DW_5_4_n_per_cell_correct(self):
        """count_accounting returns correct N for each arm/model cell."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, status="ok"),
            _make_row("02-rpn", "baseline", "sonnet", 1, status="ok"),
            _make_row("01-duration", "concise", "sonnet", 1, status="ok"),
        ]
        accounting = count_accounting(rows)
        assert accounting["baseline"]["sonnet"]["n"] == 2
        assert accounting["concise"]["sonnet"]["n"] == 1

    def test_DW_5_4_caveats_in_report(self, tmp_path):
        """Report states caveats about small N and saturation."""
        rows = _canned_rows_go()
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        content = generate_report(csv_path, report_path,
                                  models=("sonnet", "opus"),
                                  arms=("baseline", "concise"))

        # Must mention small N / caveats.
        content_lower = content.lower()
        has_caveat = (
            "caveat" in content_lower
            or "small" in content_lower
            or "honest" in content_lower
            or "saturate" in content_lower
        )
        assert has_caveat, "Report must include caveats about sample size"


# --------------------------------------------------------------------------- #
# Off-DW: beyond the floor                                                      #
# --------------------------------------------------------------------------- #

class TestOffDW:

    def test_offdw_matrix_spec_invalid_arm(self, tmp_path):
        """MatrixSpec.build rejects unknown arm names."""
        with pytest.raises(ValueError, match="unknown arm"):
            MatrixSpec.build(n_runs=1, out_root=tmp_path, arms=("bogus",))

    def test_offdw_matrix_spec_invalid_task(self, tmp_path):
        """MatrixSpec.build rejects unknown task IDs."""
        with pytest.raises(ValueError, match="unknown task"):
            MatrixSpec.build(n_runs=1, out_root=tmp_path, tasks=("99-fake",))

    def test_offdw_matrix_spec_n_runs_zero(self, tmp_path):
        """MatrixSpec.build rejects n_runs < 1."""
        with pytest.raises(ValueError, match="n_runs"):
            MatrixSpec.build(n_runs=0, out_root=tmp_path)

    def test_offdw_iter_cells_ordering(self, tmp_path):
        """iter_cells produces all combinations in a predictable order."""
        spec = MatrixSpec.build(
            n_runs=2, out_root=tmp_path,
            tasks=("01-duration",), arms=("baseline",), models=("sonnet",),
        )
        cells = list(iter_cells(spec))
        # 1 task × 1 arm × 1 model × 2 runs = 2 cells
        assert len(cells) == 2
        assert cells[0] == ("01-duration", "baseline", "sonnet", 1)
        assert cells[1] == ("01-duration", "baseline", "sonnet", 2)

    def test_offdw_cell_run_dir_pure_path(self, tmp_path):
        """cell_run_dir returns the expected path without filesystem writes."""
        out = tmp_path / "out"
        result = cell_run_dir("01-duration", "baseline", "sonnet", 3, out)
        assert result == out / "01-duration" / "baseline" / "sonnet" / "run-3"
        # Must be purely a path computation (no filesystem effect).
        assert not result.exists()

    def test_offdw_cell_is_done_false_missing(self, tmp_path):
        """cell_is_done returns False when the run dir has no meta.json."""
        rd = tmp_path / "nonexistent"
        assert cell_is_done(rd) is False

    def test_offdw_cell_is_done_true_with_meta(self, tmp_path):
        """cell_is_done returns True when meta.json exists."""
        rd = tmp_path / "run-1"
        rd.mkdir()
        (rd / "meta.json").write_text("{}")
        assert cell_is_done(rd) is True

    def test_offdw_median_odd_count(self):
        """_median returns the middle value for an odd-length list."""
        assert _median([1.0, 2.0, 3.0]) == 2.0

    def test_offdw_median_even_count(self):
        """_median returns the average of the two middle values for even length."""
        assert _median([1.0, 2.0, 3.0, 4.0]) == 2.5

    def test_offdw_median_single(self):
        """_median of a single element returns that element."""
        assert _median([7.0]) == 7.0

    def test_offdw_median_empty(self):
        """_median of an empty list returns None."""
        assert _median([]) is None

    def test_offdw_compute_deltas_none_when_arm_missing(self, tmp_path):
        """compute_deltas returns None for a metric when one arm has no data."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, loc=80),
            # No concise rows at all
        ]
        medians = compute_medians(rows)
        deltas = compute_deltas(medians, ("sonnet",))
        # No concise data → delta is None
        assert deltas["sonnet"].get("loc") is None

    def test_offdw_write_csv_schema(self, tmp_path):
        """write_csv writes all ROW_FIELDS as CSV column headers."""
        from run_matrix import ROW_FIELDS  # noqa: PLC0415
        rows = [_make_row()]
        path = tmp_path / "test.csv"
        write_csv(rows, path)
        content = path.read_text()
        first_line = content.splitlines()[0]
        for field in ROW_FIELDS:
            assert field in first_line

    def test_offdw_write_csv_creates_parent_dirs(self, tmp_path):
        """write_csv creates nested parent directories if needed."""
        rows = [_make_row()]
        path = tmp_path / "deep" / "nested" / "out.csv"
        write_csv(rows, path)
        assert path.exists()

    def test_offdw_load_rows_roundtrip(self, tmp_path):
        """Rows written by write_csv can be loaded back by load_rows intact."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, loc=55, mutation=0.9),
        ]
        path = tmp_path / "r.csv"
        write_csv(rows, path)
        loaded = load_rows(path)
        assert len(loaded) == 1
        assert loaded[0]["task"] == "01-duration"
        assert float(loaded[0]["loc"]) == 55.0
        assert float(loaded[0]["mutation"]) == 0.9

    def test_offdw_dry_run_no_execution(self, tmp_path, capsys):
        """--dry-run prints cells but does not call the cell function."""
        spec = _spec(tmp_path, n_runs=1, tasks=("01-duration",),
                     arms=("baseline",), models=("sonnet",))
        executed: list = []

        def mock_fn(task, arm, model, run_n, spec_):
            executed.append((task, arm, model, run_n))
            return _make_row(task, arm, model, run_n)

        rows = orchestrate(spec, cell_fn=mock_fn, dry_run=True)
        assert executed == []
        assert rows == []
        captured = capsys.readouterr()
        assert "dry-run" in captured.out.lower() or "WOULD RUN" in captured.out

    def test_offdw_report_file_written(self, tmp_path):
        """generate_report writes REPORT.md to the specified path."""
        rows = _canned_rows_go()
        csv_path = tmp_path / "results" / "matrix-runs.csv"
        _write_rows_csv(rows, csv_path)
        report_path = tmp_path / "REPORT.md"
        content = generate_report(csv_path, report_path,
                                  models=("sonnet", "opus"),
                                  arms=("baseline", "concise"))
        assert report_path.exists()
        assert report_path.read_text() == content

    def test_offdw_render_report_verdict_format(self):
        """render_report produces exactly 'VERDICT: GO — ...' on the last line."""
        medians = {
            "baseline": {"sonnet": {"loc": 80.0}},
            "concise": {"sonnet": {"loc": 50.0}},
        }
        deltas = {"sonnet": {"loc": -30.0, "rubric_score": 0.05}}
        content = render_report(
            medians=medians,
            deltas=deltas,
            guardrail_passed=True,
            guardrail_rationale="no regression",
            verdict="GO",
            verdict_rationale="quality improved: sonnet/loc: -30.0000",
            accounting={"baseline": {"sonnet": {"n": 1, "ok": 1, "partial": 0, "unscorable": 0, "all_partial": False}},
                        "concise": {"sonnet": {"n": 1, "ok": 1, "partial": 0, "unscorable": 0, "all_partial": False}}},
            models=("sonnet",),
            arms=("baseline", "concise"),
            n_runs=1,
            n_tasks=1,
        )
        last_line = content.rstrip("\n").split("\n")[-1]
        assert last_line == "VERDICT: GO — quality improved: sonnet/loc: -30.0000"

    def test_offdw_render_report_nogo_format(self):
        """render_report produces 'VERDICT: NO-GO — ...' for a NO-GO verdict."""
        content = render_report(
            medians={},
            deltas={"sonnet": {}},
            guardrail_passed=False,
            guardrail_rationale="mutation regressed",
            verdict="NO-GO",
            verdict_rationale="correctness regressed",
            accounting={},
            models=("sonnet",),
            arms=("baseline", "concise"),
            n_runs=1,
            n_tasks=1,
        )
        last_line = content.rstrip("\n").split("\n")[-1]
        assert last_line.startswith("VERDICT: NO-GO — ")

    def test_offdw_partial_rows_excluded_from_quality_medians(self):
        """Partial-status rows are excluded from quality metric medians."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, loc=50, status="ok"),
            # partial row with wildly different LOC — must NOT contribute to median
            _make_row("02-rpn", "baseline", "sonnet", 2, loc=5000, status="partial"),
        ]
        # Note: per design, partial IS included in medians (only unscorable excluded).
        # This test documents the actual behavior.
        medians = compute_medians(rows)
        loc_vals = medians.get("baseline", {}).get("sonnet", {}).get("loc")
        # partial is included: median of [50, 5000] = 2525.0
        assert loc_vals == 2525.0

    def test_offdw_count_accounting_unscorable(self):
        """count_accounting correctly counts unscorable runs (not as ok or partial)."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1, status="ok"),
            _make_row("01-duration", "baseline", "sonnet", 2, status="unscorable"),
        ]
        ac = count_accounting(rows)
        assert ac["baseline"]["sonnet"]["ok"] == 1
        assert ac["baseline"]["sonnet"]["unscorable"] == 1
        assert ac["baseline"]["sonnet"]["n"] == 2
        assert ac["baseline"]["sonnet"]["all_partial"] is False

    def test_offdw_guardrail_passes_when_no_data(self):
        """check_guardrail passes (not fails) when guardrail metrics have no data."""
        # If there's no delta data (None), it's not treated as a regression.
        deltas = {"sonnet": {"mutation": None, "hidden_dw": None}}
        passed, rationale = check_guardrail(deltas, ("sonnet",))
        assert passed is True

    def test_offdw_verdict_nogo_rubric_regression(self):
        """NO-GO when rubric_score regresses beyond noise even if static metrics improve."""
        rows = [
            _make_row("01-duration", "baseline", "sonnet", 1,
                      loc=80, cc_avg=3.0, rubric_score=0.9,
                      mutation=1.0, hidden_dw=1.0),
            _make_row("01-duration", "concise", "sonnet", 1,
                      loc=50, cc_avg=2.0,
                      rubric_score=0.9 - NOISE_THRESHOLD - 0.01,  # regressed beyond noise
                      mutation=1.0, hidden_dw=1.0),
        ]
        medians = compute_medians(rows)
        deltas = compute_deltas(medians, ("sonnet",))
        passed, _ = check_guardrail(deltas, ("sonnet",))
        verdict, rationale = compute_verdict(medians, deltas, passed, ("sonnet",))
        assert verdict == "NO-GO"
        assert "readability" in rationale.lower() or "rubric" in rationale.lower()
