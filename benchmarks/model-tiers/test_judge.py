"""Unit tests for judge.py's panel() aggregation and CLI adapters (Phase 3).

Fake judge_fns stand in for real CLI subprocesses everywhere except the
explicitly-gated live tests (DW-3.5), which spawn the real codex/agy/claude
CLIs once each and are skipped unless RUN_LIVE_JUDGE=1 is set (mirrors
concise-doctrine/score_rubric.py's --run-live convention).
"""
from __future__ import annotations

import json
import os
import subprocess

import pytest

import judge
from judge import _build_prompt, _codex_subprocess, _agy_subprocess, panel


def _fn(*, verdict=None, score=None):
    """Build a fake judge_fn returning a fixed verdict or score."""
    payload = {"verdict": verdict} if verdict is not None else {"score": score}
    return lambda prompt: json.dumps(payload)


def _malformed_fn(calls: list):
    def fn(prompt):
        calls.append(prompt)
        return "not json at all"
    return fn


# ---------------------------------------------------------------------------
# DW-3.1 — aggregation: majority, median, disagreement, quorum, all-fail
# ---------------------------------------------------------------------------

def test_panel_majority_binary_unanimous():
    fns = {"a": _fn(verdict="PASS"), "b": _fn(verdict="PASS"), "c": _fn(verdict="PASS")}
    result = panel("artifact", None, "rubric", mode="binary", judge_fns=fns)
    assert result["verdict"] == "PASS"
    assert result["quorum"] == "3/3"
    assert result["judge_fail"] is False
    assert result["disagreement"] is False


def test_panel_majority_binary_disagreement():
    fns = {"a": _fn(verdict="PASS"), "b": _fn(verdict="PASS"), "c": _fn(verdict="FAIL")}
    result = panel("artifact", None, "rubric", mode="binary", judge_fns=fns)
    assert result["verdict"] == "PASS"  # 2-1 majority
    assert result["disagreement"] is True
    assert result["quorum"] == "3/3"


def test_panel_median_graded():
    fns = {"a": _fn(score=3), "b": _fn(score=4), "c": _fn(score=5)}
    result = panel("artifact", None, "rubric", mode="graded", judge_fns=fns)
    assert result["score"] == 4
    assert result["judge_fail"] is False


def test_panel_one_judge_failure_quorum():
    fns = {"a": _fn(verdict="PASS"), "b": _fn(verdict="PASS"), "c": _malformed_fn([])}
    result = panel("artifact", None, "rubric", mode="binary", judge_fns=fns)
    assert result["verdict"] == "PASS"
    assert result["judge_fail"] is False
    assert result["quorum"] == "2/3"
    assert result["judges"]["c"]["status"] == "failed"


def test_panel_all_fail():
    calls_a, calls_b, calls_c = [], [], []
    fns = {"a": _malformed_fn(calls_a), "b": _malformed_fn(calls_b), "c": _malformed_fn(calls_c)}
    result = panel("artifact", None, "rubric", mode="binary", judge_fns=fns)
    assert result["verdict"] is None
    assert result["score"] is None
    assert result["judge_fail"] is True
    assert result["quorum"] == "0/3"


# ---------------------------------------------------------------------------
# DW-3.2 — malformed output / nonzero exit -> judge-failure, never a default
# ---------------------------------------------------------------------------

def test_panel_malformed_output_recorded_as_failure_not_default():
    calls = []
    fns = {"a": _fn(verdict="PASS"), "b": _fn(verdict="PASS"), "c": _malformed_fn(calls)}
    result = panel("artifact", None, "rubric", mode="binary", judge_fns=fns)
    assert result["judges"]["c"]["status"] == "failed"
    assert "verdict" not in result["judges"]["c"]
    assert len(calls) == 2  # retried exactly once


def test_panel_one_judge_fn_raises_runtime_error():
    def raiser(prompt):
        raise RuntimeError("subprocess exploded")
    fns = {"a": _fn(verdict="FAIL"), "b": _fn(verdict="FAIL"), "c": raiser}
    result = panel("artifact", None, "rubric", mode="binary", judge_fns=fns)
    assert result["verdict"] == "FAIL"
    assert result["judges"]["c"]["status"] == "failed"
    assert "subprocess exploded" in result["judges"]["c"]["error"]


def test_adapter_nonzero_exit_raises(monkeypatch):
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, returncode=1, stdout="", stderr="boom")
    monkeypatch.setattr(judge.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="failed"):
        _codex_subprocess("hello")


def test_adapter_timeout_raises(monkeypatch):
    def fake_run(cmd, **kwargs):
        raise subprocess.TimeoutExpired(cmd, kwargs.get("timeout", 1))
    monkeypatch.setattr(judge.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="timed out"):
        _agy_subprocess("hello")


def test_adapter_cli_not_found_raises(monkeypatch):
    def fake_run(cmd, **kwargs):
        raise FileNotFoundError()
    monkeypatch.setattr(judge.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="not found"):
        _codex_subprocess("hello")


# ---------------------------------------------------------------------------
# DW-3.6 — blind grading: no model/arm/run identifiers in the judge prompt
# ---------------------------------------------------------------------------

_BANNED_IDENTIFIERS = [
    "sonnet", "opus", "fable", "haiku", "gpt", "claude-", "--model",
    "arm", "run_n", "baseline",
]


def test_blind_prompt_has_no_model_or_arm_identifiers():
    prompt = _build_prompt("some report text about a bug", {"id": "d1"}, "grade this", mode="graded")
    lowered = prompt.lower()
    for banned in _BANNED_IDENTIFIERS:
        assert banned not in lowered, f"prompt leaked identifier: {banned!r}"


def test_panel_never_passes_identifiers_to_judge_fns():
    captured = []

    def spy(prompt):
        captured.append(prompt)
        return json.dumps({"verdict": "PASS"})

    panel("report text", None, "rubric text", mode="binary",
          judge_fns={"a": spy, "b": spy, "c": spy})
    assert len(captured) == 3
    for prompt in captured:
        assert "model" not in prompt.lower()


# ---------------------------------------------------------------------------
# DW-3.5 — one live call per judge CLI parses successfully (gated)
# ---------------------------------------------------------------------------

_LIVE = os.environ.get("RUN_LIVE_JUDGE") == "1"


@pytest.mark.skipif(not _LIVE, reason="set RUN_LIVE_JUDGE=1 to hit real judge CLIs")
def test_live_codex_parses():
    out = judge._codex_subprocess("Reply with ONLY this JSON: {\"verdict\": \"PASS\"}")
    assert judge._extract_json(out)["verdict"] == "PASS"


@pytest.mark.skipif(not _LIVE, reason="set RUN_LIVE_JUDGE=1 to hit real judge CLIs")
def test_live_agy_parses():
    out = judge._agy_subprocess("Reply with ONLY this JSON: {\"verdict\": \"PASS\"}")
    assert judge._extract_json(out)["verdict"] == "PASS"


@pytest.mark.skipif(not _LIVE, reason="set RUN_LIVE_JUDGE=1 to hit real judge CLIs")
def test_live_sonnet46_parses():
    out = judge._sonnet46_subprocess("Reply with ONLY this JSON: {\"verdict\": \"PASS\"}")
    assert judge._extract_json(out)["verdict"] == "PASS"
