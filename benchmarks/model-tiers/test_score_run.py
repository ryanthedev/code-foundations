"""Unit/integration tests for score_run.py against synthetic fixtures (Phase 3).

Fixtures live under fixtures/rung{1,2,3,4}/ and fixtures/empty/ — each a
self-contained task dir (manifest.json + hidden/ + starter/ [+ answer-key])
with a gold_run/ and bad_run/ subdirectory standing in for two completed
matrix run dirs. Rung-4's judge calls are exercised through a deterministic
fake judge_fns (keyword matching on defect location strings) rather than
real CLIs — DW-3.5's live-CLI check is judge.py's job, not this scorer's.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from score_run import ROW_FIELDS, load_manifest, score_run

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _fake_review_judge_fns():
    """Deterministic stand-in for the 3-judge panel: scores/verdicts are
    derived from whether the defect's location string appears in the
    artifact text sent to it — no real CLI is ever invoked."""

    def make(name):
        def fn(prompt):
            if "EXTRANEOUS-FINDING-CHECK" in prompt:
                return json.dumps({"verdict": "FAIL"})  # none of our fixtures hallucinate findings
            # graded per-defect detection: the reference answer key (a single
            # defect dict) is rendered into the prompt as JSON: find its location.
            m = re.search(r'"location":\s*"([^"]+)"', prompt)
            location = m.group(1) if m else ""
            found = location and location in prompt.split("Artifact under review:")[1].split("\nReference")[0]
            return json.dumps({"score": 5 if found else 1})
        return fn

    return {name: make(name) for name in ("codex", "agy", "sonnet46")}


# ---------------------------------------------------------------------------
# DW-3.3 — valid ROW_FIELDS row for a fixture run-dir of each rung
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rung_dir", ["rung1", "rung2", "rung3"])
def test_score_run_row_schema_build_and_debug_rungs(rung_dir):
    task_dir = FIXTURES / rung_dir
    manifest = load_manifest(task_dir)
    row = score_run(task_dir / "gold_run", manifest)
    assert set(row.keys()) == set(ROW_FIELDS)


def test_score_run_row_schema_rung4():
    task_dir = FIXTURES / "rung4"
    manifest = load_manifest(task_dir)
    row = score_run(task_dir / "gold_run", manifest, judge_fns=_fake_review_judge_fns())
    assert set(row.keys()) == set(ROW_FIELDS)


# ---------------------------------------------------------------------------
# DW-3.4 — smoke differential: gold outscores planted-bad, every rung
# ---------------------------------------------------------------------------

def test_score_run_rung1_gold_outscores_bad():
    task_dir = FIXTURES / "rung1"
    manifest = load_manifest(task_dir)
    gold = score_run(task_dir / "gold_run", manifest)
    bad = score_run(task_dir / "bad_run", manifest)
    assert gold["correct"] == 1
    assert bad["correct"] == 0
    assert gold["score"] > bad["score"]


def test_score_run_rung2_gold_outscores_bad():
    task_dir = FIXTURES / "rung2"
    manifest = load_manifest(task_dir)
    gold = score_run(task_dir / "gold_run", manifest)
    bad = score_run(task_dir / "bad_run", manifest)
    assert gold["correct"] == 1
    assert bad["correct"] == 0
    assert gold["score"] > bad["score"]


def test_score_run_rung3_gold_outscores_bad_via_diff_scope():
    task_dir = FIXTURES / "rung3"
    manifest = load_manifest(task_dir)
    gold = score_run(task_dir / "gold_run", manifest)
    bad = score_run(task_dir / "bad_run", manifest)
    # both fix the underlying bug (hidden suite passes for both) -- the
    # differential comes entirely from the diff-scope check.
    assert gold["correct"] == 1
    assert bad["correct"] == 0
    assert gold["score"] > bad["score"]


def test_score_run_rung4_gold_outscores_bad():
    task_dir = FIXTURES / "rung4"
    manifest = load_manifest(task_dir)
    fns = _fake_review_judge_fns()
    gold = score_run(task_dir / "gold_run", manifest, judge_fns=fns)
    bad = score_run(task_dir / "bad_run", manifest, judge_fns=fns)
    assert gold["tp"] == 2
    assert gold["fn"] == 0
    assert bad["tp"] == 0
    assert bad["fn"] == 2
    assert gold["score"] > bad["score"]
    assert gold["correct"] == 1
    assert bad["correct"] == 0


# ---------------------------------------------------------------------------
# Boundary: empty outputs/ scores 0, never crashes
# ---------------------------------------------------------------------------

def test_score_run_empty_outputs_scores_zero_no_crash():
    task_dir = FIXTURES / "empty"
    manifest = load_manifest(task_dir)
    row = score_run(task_dir / "empty_run", manifest)
    assert row["correct"] == 0
    assert row["score"] == 0.0
    assert row["tp"] == row["fp"] == row["fn"] == 0
    assert row["judge_fail"] is False
    assert set(row.keys()) == set(ROW_FIELDS)


def test_score_run_missing_outputs_dir_scores_zero_no_crash(tmp_path):
    task_dir = FIXTURES / "rung1"
    manifest = load_manifest(task_dir)
    run_dir = tmp_path / "no_outputs_run"
    run_dir.mkdir()
    row = score_run(run_dir, manifest)
    assert row["correct"] == 0
    assert row["score"] == 0.0


def test_hidden_suite_timeout_is_bounded_not_a_crash(monkeypatch):
    """A hung toolchain command must score as a failure, never propagate an
    uncaught TimeoutExpired that would crash a whole matrix scoring pass."""
    import subprocess as sp
    import score_run as sr

    def fake_run(cmd, **kwargs):
        raise sp.TimeoutExpired(cmd, kwargs.get("timeout", 1))

    monkeypatch.setattr(sr.subprocess, "run", fake_run)
    task_dir = FIXTURES / "rung1"
    manifest = load_manifest(task_dir)
    row = score_run(task_dir / "gold_run", manifest)
    assert row["correct"] == 0
    assert row["score"] == 0.0


# ---------------------------------------------------------------------------
# load_manifest seam
# ---------------------------------------------------------------------------

def test_load_manifest_injects_task_dir():
    task_dir = FIXTURES / "rung1"
    manifest = load_manifest(task_dir)
    assert manifest["_task_dir"] == str(task_dir)
    assert manifest["rung"] == 1
