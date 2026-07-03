"""Unit tests for run_suite.py (Phase 4).

Every test here is offline: no real MCP `run_eval` call, no real codex/agy/
claude subprocess. Live-CLI/live-model verification happens in the actual
calibration + matrix execution (recorded in calibration/decisions.md), not in
this suite — mirroring test_judge.py's split between injectable-adapter unit
tests and its one live-call-per-CLI smoke test.

Tests that write calibration/decisions.md, status.json, or results-*.csv
monkeypatch run_suite's module-level path constants to a tmp_path so they
never touch this benchmark's real, in-progress artifacts.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import run_suite as rs

REAL_TASKS_DIR = rs.TASKS_DIR


@pytest.fixture(autouse=True)
def _isolated_calibration_dir(tmp_path, monkeypatch):
    """Redirect every write-target constant to a scratch dir so tests never
    touch the real calibration/decisions.md, status.json, or results-*.csv
    this phase is actually producing."""
    monkeypatch.setattr(rs, "HERE", tmp_path)
    monkeypatch.setattr(rs, "CALIBRATION_DIR", tmp_path / "calibration")
    monkeypatch.setattr(rs, "DECISIONS_MD", tmp_path / "calibration" / "decisions.md")
    monkeypatch.setattr(rs, "STATUS_JSON", tmp_path / "calibration" / "status.json")
    monkeypatch.setattr(rs, "EVALS_JSON", tmp_path / "evals.json")
    yield tmp_path


# ---------------------------------------------------------------------------
# manifest schema validation (DW-4.2's "every manifest validates against SCHEMA.md")
# ---------------------------------------------------------------------------

def test_validate_all_manifests_real_tasks_are_valid():
    errors = rs.validate_all_manifests()
    assert errors, "expected at least one task dir"
    bad = {k: v for k, v in errors.items() if v}
    assert bad == {}, f"schema violations: {bad}"


def test_DW_4_2_validate_manifest_schema_catches_missing_field():
    manifest = {"id": "x", "rung": 1, "source": {"repo": "r", "plan": "p", "phase": "ph"},
                "toolchain": {"install": "true"}, "starter_dir": "starter",
                "report_file": None, "answer_key": None}
    errors = rs.validate_manifest_schema(manifest, task_dir_name="x")
    assert any("test_hidden" in e for e in errors)


def test_validate_manifest_schema_rung3_requires_repro_and_answer_key():
    manifest = {"id": "x", "rung": 3, "source": {"repo": "r", "plan": "p", "phase": "ph"},
                "toolchain": {"install": "true", "test_hidden": "bun test"}, "starter_dir": "starter",
                "report_file": "report.md", "answer_key": None}
    errors = rs.validate_manifest_schema(manifest, task_dir_name="x")
    assert any("answer_key" in e for e in errors)
    assert any("repro" in e for e in errors)


def test_validate_manifest_schema_id_mismatch_flagged():
    manifest = {"id": "wrong-id", "rung": 1, "source": {"repo": "r", "plan": "p", "phase": "ph"},
                "toolchain": {"install": "true", "test_hidden": "bun test"}, "starter_dir": "starter",
                "report_file": None, "answer_key": None}
    errors = rs.validate_manifest_schema(manifest, task_dir_name="01-heartbeat-message")
    assert any("!=" in e for e in errors)


# ---------------------------------------------------------------------------
# evals.json assembly
# ---------------------------------------------------------------------------

def test_DW_4_2_build_evals_json_covers_every_task():
    monkeypatch_tasks_dir = REAL_TASKS_DIR
    doc = rs.build_evals_json()
    ids = {e["id"] for e in doc["evals"]}
    assert ids == set(rs.all_task_ids())
    assert rs.EVALS_JSON.exists()


def test_build_eval_entry_prompt_is_spec_and_files_are_starter_contents():
    entry = rs.build_eval_entry("01-heartbeat-message")
    assert "DW-E1.1" in entry["prompt"]
    assert all(isinstance(p, str) for p in entry["files"])
    assert any(p.endswith("heartbeat.ts") for p in entry["files"])
    # spec.md must not be leaked as a starter file (it's the prompt, not context the agent reads as a file)
    assert not any(p.endswith("spec.md") for p in entry["files"])


# ---------------------------------------------------------------------------
# pilot headroom rule (DW-4.2 boundary: both-perfect / both-fail rejected)
# ---------------------------------------------------------------------------

def test_DW_4_2_pilot_headroom_both_perfect_rejected():
    cheap = {"correct": 1, "score": 1.0}
    expensive = {"correct": 1, "score": 1.0}
    assert rs.pilot_headroom_ok(cheap, expensive, rung=1) is False


def test_DW_4_2_pilot_headroom_both_fail_rejected():
    cheap = {"correct": 0, "score": 0.0}
    expensive = {"correct": 0, "score": 0.0}
    assert rs.pilot_headroom_ok(cheap, expensive, rung=1) is False


def test_pilot_headroom_mixed_result_accepted():
    cheap = {"correct": 0, "score": 0.0}
    expensive = {"correct": 1, "score": 1.0}
    assert rs.pilot_headroom_ok(cheap, expensive, rung=1) is True


def test_pilot_headroom_rung4_uses_recall_shape():
    both_perfect = {"tp": 3, "fp": 0, "fn": 0}
    assert rs.pilot_headroom_ok(both_perfect, both_perfect, rung=4) is False
    both_fail = {"tp": 0, "fp": 0, "fn": 3}
    assert rs.pilot_headroom_ok(both_fail, both_fail, rung=4) is False
    mixed = {"tp": 1, "fp": 0, "fn": 2}
    assert rs.pilot_headroom_ok(both_fail, mixed, rung=4) is True


# ---------------------------------------------------------------------------
# vet (injectable, no real subprocess)
# ---------------------------------------------------------------------------

def test_vet_task_injectable_no_real_subprocess():
    calls = []

    def fake_codex(prompt):
        calls.append("codex")
        return json.dumps({"verdict": "PASS", "rationale": "solvable"})

    def fake_agy(prompt):
        calls.append("agy")
        return json.dumps({"verdict": "PASS", "rationale": "solvable"})

    result = rs.vet_task("01-heartbeat-message", vet_fns={"codex": fake_codex, "agy": fake_agy})
    assert calls == ["codex", "agy"]
    assert result["verdict"] == "PASS"
    assert result["judge_fail"] is False


def test_vet_task_disagreement_yields_no_verdict():
    def fake_pass(prompt):
        return json.dumps({"verdict": "PASS"})

    def fake_fail(prompt):
        return json.dumps({"verdict": "FAIL"})

    result = rs.vet_task("01-heartbeat-message", vet_fns={"codex": fake_pass, "agy": fake_fail})
    assert result["verdict"] is None
    assert result["disagreement"] is True


# ---------------------------------------------------------------------------
# calibration_gate + decisions.md / status.json recording
# ---------------------------------------------------------------------------

def _pilot_rows(cheap_correct, expensive_correct):
    return {
        rs.CHEAPEST_MODEL: {"correct": cheap_correct, "score": float(cheap_correct), "tp": 0, "fp": 0, "fn": 0},
        rs.PRICIEST_MODEL: {"correct": expensive_correct, "score": float(expensive_correct), "tp": 0, "fp": 0, "fn": 0},
    }


def test_DW_4_2_calibration_gate_accepts_with_headroom_and_records_decision():
    vet = {"verdict": "PASS", "judge_fail": False, "quorum": "2/2"}
    accepted = rs.calibration_gate("01-heartbeat-message", vet_result=vet, pilot_rows=_pilot_rows(0, 1))
    assert accepted is True
    assert rs.load_status()["01-heartbeat-message"] == "accepted"
    text = rs.DECISIONS_MD.read_text()
    assert "01-heartbeat-message" in text
    assert "ACCEPT" in text


def test_calibration_gate_rejects_on_no_headroom():
    vet = {"verdict": "PASS", "judge_fail": False, "quorum": "2/2"}
    accepted = rs.calibration_gate("01-heartbeat-message", vet_result=vet, pilot_rows=_pilot_rows(1, 1))
    assert accepted is False
    assert rs.load_status()["01-heartbeat-message"] == "rejected"
    assert "REJECT" in rs.DECISIONS_MD.read_text()


def test_calibration_gate_rejects_on_vet_failure_regardless_of_pilot():
    vet = {"verdict": "FAIL", "judge_fail": False, "quorum": "2/2"}
    accepted = rs.calibration_gate("01-heartbeat-message", vet_result=vet, pilot_rows=_pilot_rows(0, 1))
    assert accepted is False
    assert rs.load_status()["01-heartbeat-message"] == "rejected"


def test_record_model_id_check_writes_all_four_ids():
    rs.record_model_id_check({"sonnet-5": True, "opus-4.8": True, "fable-5": True, "sonnet-4.6": True})
    text = rs.DECISIONS_MD.read_text()
    for k in ("sonnet-5", "opus-4.8", "fable-5", "sonnet-4.6"):
        assert k in text
    assert "REJECTED" not in text


# ---------------------------------------------------------------------------
# resume-if-done + task-major matrix cell ordering (DW-4.3, DW-4.4)
# ---------------------------------------------------------------------------

def test_DW_4_3_matrix_cells_task_major_order():
    cells = list(rs.matrix_cells(["taskA", "taskB"], models=("m1", "m2"), runs=2))
    assert cells == [
        ("taskA", "m1", 1), ("taskA", "m1", 2), ("taskA", "m2", 1), ("taskA", "m2", 2),
        ("taskB", "m1", 1), ("taskB", "m1", 2), ("taskB", "m2", 1), ("taskB", "m2", 2),
    ]


def test_DW_4_4_resume_skips_completed_cells(tmp_path):
    rs.append_row("taskA", {"task": "taskA", "rung": 1, "model": "m1", "run_n": 1, "correct": 1,
                             "score": 1.0, "tp": 0, "fp": 0, "fn": 0, "judge_fail": False,
                             "time_seconds": 1, "tokens": 1, "cost_usd": 0.1, "pilot": False})
    assert rs.is_cell_done("taskA", "m1", 1) is True
    assert rs.is_cell_done("taskA", "m1", 2) is False
    cells = list(rs.matrix_cells(["taskA"], models=("m1",), runs=2))
    assert cells == [("taskA", "m1", 2)]


def test_DW_4_4_append_row_creates_header_once():
    row = {k: "" for k in rs.CSV_FIELDS}
    row.update({"task": "t", "model": "m", "run_n": 1})
    rs.append_row("t", row)
    rs.append_row("t", {**row, "run_n": 2})
    lines = rs.results_csv_path("t").read_text().splitlines()
    assert lines[0].startswith("task,")
    assert len(lines) == 3  # header + 2 rows


def test_task_excluded_after_late_calibration_failure_removes_csv_and_logs():
    rs.append_row("taskA", {**{k: "" for k in rs.CSV_FIELDS}, "task": "taskA", "model": "m1", "run_n": 1})
    assert rs.results_csv_path("taskA").exists()
    rs.exclude_task_from_csvs("taskA", reason="failed calibration late")
    assert not rs.results_csv_path("taskA").exists()
    assert "excluded" in rs.DECISIONS_MD.read_text()


# ---------------------------------------------------------------------------
# meta.json derivation + score_and_record
# ---------------------------------------------------------------------------

def test_derive_meta_from_run_dir_reads_metrics_and_timing(tmp_path):
    # Real field names, confirmed against an actual run_eval output dir during this phase.
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    (run_dir / "metrics.json").write_text(json.dumps(
        {"total_cost_usd": 0.42, "total_tool_calls": 3, "num_turns": 4, "terminal": "success"}))
    (run_dir / "timing.json").write_text(json.dumps(
        {"total_tokens": 1234, "duration_ms": 12500, "total_duration_seconds": 12.5}))
    meta = rs.derive_meta_from_run_dir(run_dir, task_id="t", model_key="sonnet-5", run_n=3)
    assert meta == {"task": "t", "model": "sonnet-5", "run_n": 3, "time_seconds": 12.5,
                     "tokens": 1234, "cost_usd": 0.42, "pilot": False}


def test_derive_meta_from_run_dir_missing_files_defaults_to_zero(tmp_path):
    run_dir = tmp_path / "run-1"
    run_dir.mkdir()
    meta = rs.derive_meta_from_run_dir(run_dir, task_id="t", model_key="m", run_n=1)
    assert meta["cost_usd"] == 0.0
    assert meta["tokens"] == 0
    assert meta["time_seconds"] == 0.0


def test_score_and_record_writes_meta_and_appends_csv(tmp_path, monkeypatch):
    # build a minimal rung-1 run dir against the real 01-heartbeat-message task
    task_dir = REAL_TASKS_DIR / "01-heartbeat-message"
    gold_ts = (task_dir / "gold" / "heartbeat.ts").read_text()
    run_dir = tmp_path / "run-1"
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (outputs / "heartbeat.ts").write_text(gold_ts)
    (run_dir / "metrics.json").write_text(json.dumps({"cost_usd": 0.05, "tokens": 500}))
    (run_dir / "timing.json").write_text(json.dumps({"time_seconds": 8.0}))

    monkeypatch.setattr(rs, "TASKS_DIR", REAL_TASKS_DIR)
    row = rs.score_and_record(run_dir, "01-heartbeat-message", "sonnet-5", 1)

    assert (run_dir / "meta.json").exists()
    assert row["correct"] == 1
    csv_text = rs.results_csv_path("01-heartbeat-message").read_text()
    assert "sonnet-5" in csv_text and "0.05" in csv_text


def test_score_and_record_pilot_run_not_appended_to_csv(tmp_path, monkeypatch):
    task_dir = REAL_TASKS_DIR / "01-heartbeat-message"
    gold_ts = (task_dir / "gold" / "heartbeat.ts").read_text()
    run_dir = tmp_path / "run-1"
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)
    (outputs / "heartbeat.ts").write_text(gold_ts)

    monkeypatch.setattr(rs, "TASKS_DIR", REAL_TASKS_DIR)
    rs.score_and_record(run_dir, "01-heartbeat-message", "sonnet-5", 1, pilot=True)
    assert not rs.results_csv_path("01-heartbeat-message").exists()


# ---------------------------------------------------------------------------
# rate-limit pause + cost tripwire (DW-4.5, mocked — never a real 429)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "Error: 429 Too Many Requests", "rate limit exceeded, please retry",
    "quota exceeded for this billing period", "RateLimited: backoff required",
])
def test_DW_4_5_is_rate_limited_detects_signal(text):
    assert rs.is_rate_limited(text) is True


def test_is_rate_limited_false_on_normal_output():
    assert rs.is_rate_limited("run completed successfully, 5/5 tests passed") is False


def test_DW_4_5_handle_run_eval_output_logs_pause_event_no_data_loss(tmp_path):
    rs.append_row("taskA", {**{k: "" for k in rs.CSV_FIELDS}, "task": "taskA", "model": "m1", "run_n": 1})
    before = rs.results_csv_path("taskA").read_text()

    paused = rs.handle_run_eval_output("429 rate limit hit", context="taskA/m2/run3")

    assert paused is True
    assert "rate_limit_pause" in rs.DECISIONS_MD.read_text()
    assert rs.results_csv_path("taskA").read_text() == before  # no data loss


def test_handle_run_eval_output_no_event_on_success():
    handled = rs.handle_run_eval_output("all good", context="x")
    assert handled is False
    assert not rs.DECISIONS_MD.exists()


def test_cumulative_cost_usd_includes_pilot_rows_not_just_csvs():
    rs.append_row("t1", {**{k: "" for k in rs.CSV_FIELDS}, "task": "t1", "cost_usd": 1.0})
    rs.ensure_calibration_dir()
    (rs.CALIBRATION_DIR / "pilot_rows.json").write_text(json.dumps(
        {"taskA": {"sonnet-5": {"cost_usd": 2.0}, "fable-5": {"cost_usd": 3.0}}}))
    assert rs.cumulative_cost_usd() == pytest.approx(6.0)  # 1.0 matrix + 2.0 + 3.0 pilot


def test_DW_4_5_cumulative_cost_usd_sums_across_csvs():
    rs.append_row("t1", {**{k: "" for k in rs.CSV_FIELDS}, "task": "t1", "cost_usd": 1.5})
    rs.append_row("t1", {**{k: "" for k in rs.CSV_FIELDS}, "task": "t1", "cost_usd": 2.5})
    rs.append_row("t2", {**{k: "" for k in rs.CSV_FIELDS}, "task": "t2", "cost_usd": 3.0})
    assert rs.cumulative_cost_usd() == pytest.approx(7.0)


def test_DW_4_5_cost_tripwire_halts_and_logs():
    rs.append_row("t1", {**{k: "" for k in rs.CSV_FIELDS}, "task": "t1", "cost_usd": 300})
    with pytest.raises(rs.CostTripwireExceeded):
        rs.check_cost_tripwire(threshold=250.0)
    assert "cost_tripwire" in rs.DECISIONS_MD.read_text()


def test_cost_tripwire_does_not_trigger_under_threshold():
    rs.append_row("t1", {**{k: "" for k in rs.CSV_FIELDS}, "task": "t1", "cost_usd": 10})
    rs.check_cost_tripwire(threshold=250.0)  # must not raise
    assert not rs.DECISIONS_MD.exists()


# ---------------------------------------------------------------------------
# cross-phase gold validation (DW-4.6)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("task_id", ["03-kv-key-mismatch", "03-storage-meter-dedup"])
def test_DW_4_6_rung3_gold_diff_confined_to_allowed_scope(task_id, monkeypatch):
    monkeypatch.setattr(rs, "TASKS_DIR", REAL_TASKS_DIR)
    assert rs.validate_rung3_gold_diff_scope(task_id) is True


def test_rung3_gold_diff_scope_detects_out_of_scope_change(tmp_path, monkeypatch):
    task_dir = tmp_path / "fake-rung3"
    (task_dir / "starter").mkdir(parents=True)
    (task_dir / "gold").mkdir()
    (task_dir / "starter" / "a.ts").write_text("original")
    (task_dir / "gold" / "a.ts").write_text("original")
    (task_dir / "gold" / "pinned.ts").write_text("changed but not allowed")
    (task_dir / "answer-key.json").write_text(json.dumps({"allowed_change_scope": ["a.ts"]}))
    monkeypatch.setattr(rs, "TASKS_DIR", tmp_path)
    manifest = {"starter_dir": "starter", "answer_key": "answer-key.json"}
    (tmp_path / "fake-rung3" / "manifest.json").write_text(json.dumps({**manifest, "id": "fake-rung3"}))
    assert rs.validate_rung3_gold_diff_scope("fake-rung3") is False


@pytest.mark.parametrize("task_id", ["04-loop-core-review", "04-hash-progress-review"])
def test_DW_4_6_rung4_gold_full_recall_all_defects_found(task_id, monkeypatch):
    monkeypatch.setattr(rs, "TASKS_DIR", REAL_TASKS_DIR)

    def fake_always_found(prompt):
        return json.dumps({"score": 5, "rationale": "found"})

    judge_fns = {"codex": fake_always_found, "agy": fake_always_found, "sonnet46": fake_always_found}
    assert rs.validate_rung4_gold_full_recall(task_id, judge_fns=judge_fns) is True


def test_rung4_gold_full_recall_detects_a_missed_defect(monkeypatch):
    monkeypatch.setattr(rs, "TASKS_DIR", REAL_TASKS_DIR)
    # All three judges agree defect LC-4 (the bun:sqlite infra import) was
    # missed; every other defect is unanimously found. Median-of-3 must stay
    # low for LC-4 specifically, so all three (not just one) judge calls for
    # that defect return a low score.
    missed_marker = "ports.ts:9"

    def fake_one_missed(prompt):
        if missed_marker in prompt:
            return json.dumps({"score": 1, "rationale": "not mentioned"})
        return json.dumps({"score": 5, "rationale": "found"})

    judge_fns = {"codex": fake_one_missed, "agy": fake_one_missed, "sonnet46": fake_one_missed}
    assert rs.validate_rung4_gold_full_recall("04-loop-core-review", judge_fns=judge_fns) is False
