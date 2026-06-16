"""Phase 4 validation suite: scoring extensions.

Covers all Phase 4 DW items and goes beyond the DW floor. The rubric judge and
any live LLM calls are unit-tested via an injectable judge_fn seam, so the
default suite costs nothing and is fully deterministic. One live rubric smoke
test is marked `live` and skipped unless --run-live is passed.

DW-ID traceability:
  DW-4.1 — test_DW_4_1_* (static scorer returns hand-verified metrics for known fixtures)
  DW-4.2 — test_DW_4_2_* (mutation/correctness adapter + red-suite / broken-env guard)
  DW-4.3 — test_DW_4_3_* (rubric judge 0-1+rationale; blind A/B; fresh-context seam)
  DW-4.4 — test_DW_4_4_* (score_all.py full row schema for ok and partial runs)

Off-DW (beyond the floor):
  test_offdw_* (empty file, no-functions file, multi-function CC, run_id derivation,
               discover_run_dirs, unscorable propagation, rubric parse fallback, etc.)
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

CONCISE_DOCTRINE = Path(__file__).resolve().parent
if str(CONCISE_DOCTRINE) not in sys.path:
    sys.path.insert(0, str(CONCISE_DOCTRINE))

from score_static import static_metrics, score_run_static  # noqa: E402
from score_correctness import score_run, grade_run_dir, MANIFEST_PATH, HIDDEN_ROOT  # noqa: E402
from score_rubric import rubric_judge, blind_ab, score_run_rubric, _extract_json  # noqa: E402
from score_all import score_one_run, _discover_run_dirs, ROW_FIELDS  # noqa: E402

# Paths to known fixtures.
TDD_HARNESS = CONCISE_DOCTRINE.parent / "tdd-vs-siv" / "harness"
TDD_SMOKE = TDD_HARNESS / "_smoke" / "01-duration"
LIVE_SMOKE = CONCISE_DOCTRINE / "_live-smoke" / "01-duration" / "baseline" / "sonnet" / "run-1"

# Hand-verified values (computed in discovery).
#   tdd-vs-siv smoke / with_skill / duration.py
#     LOC=15, cc_avg=4.0, cc_max=4, fn_len_max=10, n_funcs=1
#   live-smoke / duration.py
#     LOC=33, cc_avg=4.0, cc_max=4, fn_len_max=25, n_funcs=1


# ============================================================================
# DW-4.1: Static scorer returns hand-verified metrics for known fixtures
# ============================================================================

class TestDW41StaticScorer:
    def test_DW_4_1_known_fixture_tdd_smoke(self):
        """tdd-vs-siv with_skill duration.py: hand-verified LOC=15, cc=4, fn_len=10."""
        impl = TDD_SMOKE / "with_skill" / "run-1" / "outputs" / "duration.py"
        m = static_metrics(impl)
        assert m["loc"] == 15
        assert m["cc_avg"] == 4.0
        assert m["cc_max"] == 4
        assert m["fn_len_max"] == 10
        assert m["n_funcs"] == 1

    def test_DW_4_1_known_fixture_live_smoke(self):
        """live-smoke duration.py: hand-verified LOC=33, cc=4, fn_len=25."""
        impl = LIVE_SMOKE / "outputs" / "duration.py"
        m = static_metrics(impl)
        assert m["loc"] == 33
        assert m["cc_avg"] == 4.0
        assert m["cc_max"] == 4
        assert m["fn_len_max"] == 25
        assert m["n_funcs"] == 1

    def test_DW_4_1_boundary_empty_file(self, tmp_path):
        """Empty file returns all-zero metrics, not an error."""
        f = tmp_path / "empty.py"
        f.write_text("")
        m = static_metrics(f)
        assert m == {"loc": 0, "cc_avg": 0.0, "cc_max": 0, "fn_len_max": 0, "n_funcs": 0}

    def test_DW_4_1_boundary_no_functions(self, tmp_path):
        """Module with only module-level constants: n_funcs=0."""
        f = tmp_path / "consts.py"
        f.write_text("X = 1\nY = 2\n")
        m = static_metrics(f)
        assert m["n_funcs"] == 0
        assert m["cc_avg"] == 0.0
        assert m["cc_max"] == 0
        assert m["fn_len_max"] == 0
        assert m["loc"] > 0

    def test_DW_4_1_boundary_single_fn(self, tmp_path):
        """Single trivial function: cc=1."""
        f = tmp_path / "single.py"
        f.write_text("def hello():\n    return 42\n")
        m = static_metrics(f)
        assert m["n_funcs"] == 1
        assert m["cc_max"] == 1
        assert m["fn_len_max"] == 2

    def test_DW_4_1_boundary_deeply_nested_cc(self, tmp_path):
        """Branchy function has cc_max > 1."""
        src = (
            "def branchy(x):\n"
            "    if x > 0:\n"
            "        if x > 10:\n"
            "            return 'big'\n"
            "        return 'small'\n"
            "    elif x == 0:\n"
            "        return 'zero'\n"
            "    return 'neg'\n"
        )
        f = tmp_path / "branchy.py"
        f.write_text(src)
        m = static_metrics(f)
        assert m["n_funcs"] == 1
        assert m["cc_max"] >= 4  # base 1 + 3 branches

    def test_DW_4_1_non_parseable_raises(self, tmp_path):
        """Unparseable Python raises ValueError (caller records unscorable)."""
        f = tmp_path / "bad.py"
        f.write_text("def broken(\n    return 1\n")
        with pytest.raises(ValueError):
            static_metrics(f)

    def test_DW_4_1_missing_file_raises(self, tmp_path):
        """Missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            static_metrics(tmp_path / "nonexistent.py")


# ============================================================================
# DW-4.2: Mutation/correctness adapter + red-suite / broken-env guard
# ============================================================================

class TestDW42Correctness:
    def test_DW_4_2_reproduces_tdd_smoke_with_skill(self, tmp_path):
        """Adapter reproduces known tdd-vs-siv score: with_skill mutation=1.0."""
        smoke_run = TDD_SMOKE / "with_skill" / "run-1"
        # score_run uses concise-doctrine manifest; create a synthetic meta + run dir
        # pointing at tdd-vs-siv fixture files.
        manifest = json.loads(MANIFEST_PATH.read_text())
        task = "01-duration"
        result = score_run(smoke_run, task, manifest, HIDDEN_ROOT)
        # Agent suite must be green (both tdd fixtures pass their own tests).
        assert result["agent_tests_pass"] is True
        # Mutation score on the thorough with_skill suite: 5/5 = 1.0 (verified in discovery).
        assert result["mutation_score"] == 1.0

    def test_DW_4_2_reproduces_tdd_smoke_old_skill(self, tmp_path):
        """old_skill (thin DW-only suite) produces mutation_score < 1.0."""
        smoke_run = TDD_SMOKE / "old_skill" / "run-1"
        manifest = json.loads(MANIFEST_PATH.read_text())
        task = "01-duration"
        result = score_run(smoke_run, task, manifest, HIDDEN_ROOT)
        assert result["agent_tests_pass"] is True
        # old_skill thin suite misses mutant #2: 4/5 = 0.8 (verified in discovery).
        assert result["mutation_score"] == 0.8

    def test_DW_4_2_red_suite_unscorable(self, tmp_path):
        """Red agent suite → mutation_score is 'n/a (suite not green)', never 1.0."""
        # Build a minimal run dir with a broken test (always fails).
        manifest = json.loads(MANIFEST_PATH.read_text())
        task = "01-duration"
        spec = manifest[task]
        outputs = tmp_path / "outputs"
        outputs.mkdir()

        # Valid impl that the broken suite will fail against.
        src = TDD_SMOKE / "with_skill" / "run-1" / "outputs" / "duration.py"
        shutil.copy(src, outputs / spec["impl"])

        # Red test suite: assertion that always fails.
        (outputs / spec["tests"]).write_text(
            "def test_always_fail():\n    assert False\n"
        )

        result = score_run(tmp_path, task, manifest, HIDDEN_ROOT)
        assert result["agent_tests_pass"] is False
        assert result["mutation_score"] == "n/a (suite not green)"
        # Guard: must NOT be 1.0.
        assert result["mutation_score"] != 1.0

    def test_DW_4_2_missing_impl_unscorable(self, tmp_path):
        """Missing impl → unscorable (not a crash, not 1.0)."""
        manifest = json.loads(MANIFEST_PATH.read_text())
        task = "01-duration"
        # outputs dir exists but impl is absent.
        (tmp_path / "outputs").mkdir()
        result = score_run(tmp_path, task, manifest, HIDDEN_ROOT)
        assert result.get("status") == "unscorable"

    def test_DW_4_2_missing_tests_skips_mutation(self, tmp_path):
        """Missing tests file → mutation_score is 'n/a (tests missing)', not 1.0."""
        manifest = json.loads(MANIFEST_PATH.read_text())
        task = "01-duration"
        spec = manifest[task]
        outputs = tmp_path / "outputs"
        outputs.mkdir()
        src = TDD_SMOKE / "with_skill" / "run-1" / "outputs" / "duration.py"
        shutil.copy(src, outputs / spec["impl"])
        # No tests file.
        result = score_run(tmp_path, task, manifest, HIDDEN_ROOT)
        assert result["mutation_score"] == "n/a (tests missing)"

    def test_DW_4_2_grade_run_dir_reads_meta(self, tmp_path):
        """grade_run_dir resolves task from meta.json automatically."""
        manifest = json.loads(MANIFEST_PATH.read_text())
        task = "01-duration"
        spec = manifest[task]
        outputs = tmp_path / "outputs"
        outputs.mkdir()
        src = TDD_SMOKE / "with_skill" / "run-1" / "outputs" / "duration.py"
        shutil.copy(src, outputs / spec["impl"])
        (tmp_path / "meta.json").write_text(json.dumps({"task": task, "status": "ok"}))
        result = grade_run_dir(tmp_path)
        # Should not be unscorable (impl present).
        assert result.get("status") != "unscorable" or "missing" not in result.get("reason", "")
        assert result.get("task") == task

    def test_DW_4_2_missing_meta_unscorable(self, tmp_path):
        """grade_run_dir with missing meta.json → unscorable."""
        result = grade_run_dir(tmp_path)
        assert result["status"] == "unscorable"
        assert "meta.json" in result["reason"]


# ============================================================================
# DW-4.3: Rubric judge 0-1+rationale; blind A/B with labels hidden
# ============================================================================

# A mock judge_fn that returns canned JSON responses.
def _mock_judge_rubric(prompt: str) -> str:
    return '{"score": 0.82, "rationale": "Clear variable names and concise logic."}'


def _mock_judge_ab(prompt: str) -> str:
    return '{"winner": "B", "rationale": "B uses a dict lookup instead of a chain."}'


def _blindness_checking_judge(prompt: str) -> str:
    """Judge that asserts ARM IDENTIFIERS are absent from the prompt.

    The A/B prompt uses generic labels 'A' and 'B'. It must not expose the
    arm-identifier strings that would let the judge infer which variant is which
    (e.g., 'baseline arm', 'concise arm', or bare 'baseline'/'concise' as labels).
    Note: 'concise' may appear as a readability criterion word — that is fine.
    """
    # The prompt must not label the implementations by arm name.
    # Check for the combination patterns that would reveal identity.
    arm_label_patterns = ["baseline arm", "concise arm", "arm a", "arm b"]
    prompt_lower = prompt.lower()
    for pattern in arm_label_patterns:
        assert pattern not in prompt_lower, f"arm label pattern {pattern!r} in prompt"
    # The implementations must be labeled "Implementation A" and "Implementation B", not by arm.
    assert "implementation a:" in prompt_lower or "implementation a\n" in prompt_lower, \
        "A/B prompt should label impls as A and B"
    return '{"winner": "A", "rationale": "Template contained no arm labels."}'


class TestDW43RubricAndAB:
    def test_DW_4_3_rubric_returns_score_and_rationale(self):
        """Rubric judge returns dict with float score in [0,1] and rationale string."""
        result = rubric_judge("def f(): return 1", judge_fn=_mock_judge_rubric)
        assert "score" in result
        assert "rationale" in result
        assert isinstance(result["score"], float)
        assert 0.0 <= result["score"] <= 1.0
        assert isinstance(result["rationale"], str)
        assert len(result["rationale"]) > 0

    def test_DW_4_3_rubric_mocked_value(self):
        """Mocked judge returns the exact canned score."""
        result = rubric_judge("def f(): return 1", judge_fn=_mock_judge_rubric)
        assert result["score"] == 0.82
        assert "Clear" in result["rationale"]

    def test_DW_4_3_blind_ab_returns_winner(self):
        """Blind A/B returns dict with winner in {A, B, tie} and rationale."""
        result = blind_ab("def f(): return 1", "def g(): return 2", judge_fn=_mock_judge_ab)
        assert "winner" in result
        assert "rationale" in result
        assert result["winner"] in ("A", "B", "tie")
        assert isinstance(result["rationale"], str)

    def test_DW_4_3_blind_ab_labels_hidden(self):
        """A/B prompt template must not expose arm names like 'baseline' or 'concise'."""
        # The blindness-checking judge validates the template prefix (before code blocks).
        result = blind_ab(
            "def f(): return 1",
            "def g(): return 2",
            judge_fn=_blindness_checking_judge,
        )
        # If we get here without AssertionError, the template was label-free.
        assert result["winner"] in ("A", "B", "tie")

    def test_DW_4_3_rubric_fresh_context_seam(self):
        """judge_fn is injectable — default is _judge_subprocess (fresh-context guarantee)."""
        import score_rubric as sr
        # Verify the default seam is the subprocess function, not a warm-context call.
        import inspect
        sig = inspect.signature(sr.rubric_judge)
        default = sig.parameters["judge_fn"].default
        assert default is sr._judge_subprocess

    def test_DW_4_3_rubric_score_out_of_range_raises(self):
        """Score outside [0,1] raises ValueError (bad model output caught at boundary)."""
        def bad_judge(prompt: str) -> str:
            return '{"score": 1.5, "rationale": "too high"}'
        with pytest.raises(ValueError, match="out of range"):
            rubric_judge("def f(): pass", judge_fn=bad_judge)

    def test_DW_4_3_rubric_missing_keys_raises(self):
        """Response missing required keys raises ValueError."""
        def missing_judge(prompt: str) -> str:
            return '{"only_key": "oops"}'
        with pytest.raises(ValueError, match="missing required keys"):
            rubric_judge("def f(): pass", judge_fn=missing_judge)

    def test_DW_4_3_ab_tie_normalized(self):
        """'tie' winner (case-insensitive) is accepted and lowercased."""
        def tie_judge(prompt: str) -> str:
            return '{"winner": "tie", "rationale": "identical quality"}'
        result = blind_ab("def a(): pass", "def b(): pass", judge_fn=tie_judge)
        assert result["winner"] == "tie"

    def test_DW_4_3_ab_invalid_winner_raises(self):
        """Winner not in {A, B, tie} raises ValueError."""
        def bad_judge(prompt: str) -> str:
            return '{"winner": "C", "rationale": "not possible"}'
        with pytest.raises(ValueError, match="winner must be"):
            blind_ab("def a(): pass", "def b(): pass", judge_fn=bad_judge)

    def test_DW_4_3_score_run_rubric_ok_run(self):
        """score_run_rubric on live-smoke run returns score in [0,1]."""
        result = score_run_rubric(LIVE_SMOKE, judge_fn=_mock_judge_rubric)
        assert "rubric_score" in result
        assert result["rubric_score"] == 0.82

    def test_DW_4_3_score_run_rubric_missing_run_dir(self, tmp_path):
        """Missing run_dir → unscorable."""
        result = score_run_rubric(tmp_path / "nonexistent", judge_fn=_mock_judge_rubric)
        assert result["status"] == "unscorable"

    @pytest.mark.live
    def test_DW_4_3_rubric_live(self):
        """Live rubric judge on the smoke impl returns 0-1 score from a real LLM call."""
        impl = LIVE_SMOKE / "outputs" / "duration.py"
        result = rubric_judge(impl.read_text())
        assert 0.0 <= result["score"] <= 1.0
        assert len(result["rationale"]) > 10


# ============================================================================
# DW-4.4: score_all emits full row schema for ok and partial runs
# ============================================================================

def _make_run_dir(
    tmp_path: Path,
    *,
    task: str = "01-duration",
    arm: str = "baseline",
    model: str = "sonnet",
    run: int = 1,
    status: str = "ok",
    write_impl: bool = True,
    write_tests: bool = True,
    bad_impl: bool = False,
) -> Path:
    """Create a synthetic run dir conforming to the Phase-3 run-dir contract."""
    manifest = json.loads(MANIFEST_PATH.read_text())
    spec = manifest[task]
    run_dir = tmp_path / task / arm / model / f"run-{run}"
    outputs = run_dir / "outputs"
    outputs.mkdir(parents=True)

    meta = {"task": task, "arm": arm, "model": model, "run": run, "status": status}
    (run_dir / "meta.json").write_text(json.dumps(meta))

    if write_impl:
        if bad_impl:
            (outputs / spec["impl"]).write_text("def broken(\n    oops\n")
        else:
            src = TDD_SMOKE / "with_skill" / "run-1" / "outputs" / "duration.py"
            shutil.copy(src, outputs / spec["impl"])

    if write_tests:
        src_t = TDD_SMOKE / "with_skill" / "run-1" / "outputs" / "test_duration.py"
        shutil.copy(src_t, outputs / spec["tests"])

    return run_dir


class TestDW44ScoreAll:
    def test_DW_4_4_full_row_schema_ok_run(self, tmp_path):
        """Full row schema emitted for an ok run; no crashing."""
        run_dir = _make_run_dir(tmp_path)
        row = score_one_run(run_dir, tmp_path, run_rubric=False)
        for field in ROW_FIELDS:
            assert field in row, f"missing field: {field}"
        assert row["task"] == "01-duration"
        assert row["arm"] == "baseline"
        assert row["model"] == "sonnet"
        assert row["loc"] == 15       # hand-verified fixture
        assert row["n_funcs"] == 1
        assert row["status"] == "ok"

    def test_DW_4_4_full_row_schema_uses_live_smoke(self):
        """Live-smoke run dir emits correct schema using real meta.json."""
        row = score_one_run(LIVE_SMOKE, LIVE_SMOKE.parent, run_rubric=False)
        for field in ROW_FIELDS:
            assert field in row, f"missing field: {field}"
        assert row["task"] == "01-duration"
        assert row["arm"] == "baseline"
        assert row["model"] == "sonnet"
        assert row["loc"] == 33       # hand-verified live-smoke impl
        assert row["status"] == "ok"

    def test_DW_4_4_partial_missing_impl(self, tmp_path):
        """Partial run (no impl) → static+correctness null, status preserved, no crash."""
        run_dir = _make_run_dir(tmp_path, status="partial", write_impl=False)
        row = score_one_run(run_dir, tmp_path, run_rubric=False)
        for field in ROW_FIELDS:
            assert field in row, f"missing field: {field}"
        # Static metrics must be None (no impl to analyze).
        assert row["loc"] is None
        assert row["n_funcs"] is None
        # Status reflects the partial status from meta.json.
        assert row["status"] == "partial"

    def test_DW_4_4_partial_missing_tests(self, tmp_path):
        """Partial run (no tests) → static metrics present, mutation skipped, no crash."""
        run_dir = _make_run_dir(tmp_path, status="partial", write_tests=False)
        row = score_one_run(run_dir, tmp_path, run_rubric=False)
        for field in ROW_FIELDS:
            assert field in row, f"missing field: {field}"
        # Impl exists, so static metrics should be populated.
        assert row["loc"] == 15
        # Mutation skipped (no tests) → "n/a (tests missing)" or None.
        assert row["mutation"] in ("n/a (tests missing)", None)

    def test_DW_4_4_unparseable_impl(self, tmp_path):
        """Unparseable Python impl → static fields None, no exception raised."""
        run_dir = _make_run_dir(tmp_path, bad_impl=True)
        row = score_one_run(run_dir, tmp_path, run_rubric=False)
        for field in ROW_FIELDS:
            assert field in row, f"missing field: {field}"
        # Static fields should be None (parse error).
        assert row["loc"] is None
        assert row["cc_max"] is None
        # Must not raise.

    def test_DW_4_4_missing_meta_json(self, tmp_path):
        """No meta.json → status=unscorable, no crash."""
        run_dir = tmp_path / "run-1"
        run_dir.mkdir()
        row = score_one_run(run_dir, tmp_path, run_rubric=False)
        for field in ROW_FIELDS:
            assert field in row, f"missing field: {field}"
        assert row["status"] == "unscorable"

    def test_DW_4_4_rubric_mocked_in_score_all(self, tmp_path):
        """score_all with run_rubric=True uses injected judge_fn (no LLM cost)."""
        run_dir = _make_run_dir(tmp_path)
        row = score_one_run(
            run_dir, tmp_path, run_rubric=True, judge_fn=_mock_judge_rubric
        )
        assert row["rubric_score"] == 0.82

    def test_DW_4_4_rubric_off_by_default(self, tmp_path):
        """run_rubric=False (default) leaves rubric_score None."""
        run_dir = _make_run_dir(tmp_path)
        row = score_one_run(run_dir, tmp_path, run_rubric=False)
        assert row["rubric_score"] is None


# ============================================================================
# Off-DW: edge cases and integration seams
# ============================================================================

class TestOffDW:
    def test_offdw_extract_json_pure(self):
        """_extract_json parses embedded JSON from prose text."""
        text = 'The model says: {"score": 0.75, "rationale": "ok"} and that is it.'
        result = _extract_json(text)
        assert result["score"] == 0.75

    def test_offdw_extract_json_no_json_raises(self):
        """_extract_json raises ValueError on plain text with no JSON."""
        with pytest.raises(ValueError, match="no JSON object found"):
            _extract_json("just some prose without any braces")

    def test_offdw_static_multi_function(self, tmp_path):
        """Multiple functions: cc_avg is mean, cc_max is the maximum."""
        src = (
            "def simple():\n    return 1\n\n"
            "def branchy(x):\n"
            "    if x > 0:\n        return 'pos'\n"
            "    elif x < 0:\n        return 'neg'\n"
            "    return 'zero'\n"
        )
        f = tmp_path / "multi.py"
        f.write_text(src)
        m = static_metrics(f)
        assert m["n_funcs"] == 2
        assert m["cc_max"] >= 3    # branchy has cc ≥ 3
        assert m["cc_avg"] < m["cc_max"]  # avg must be less than max

    def test_offdw_run_id_relative_to_root(self, tmp_path):
        """run_id is relative to out_root (not an absolute path)."""
        run_dir = _make_run_dir(tmp_path)
        row = score_one_run(run_dir, tmp_path, run_rubric=False)
        run_id = row["run_id"]
        assert not run_id.startswith("/"), "run_id must be relative"
        assert "01-duration" in run_id

    def test_offdw_discover_run_dirs(self, tmp_path):
        """_discover_run_dirs finds all dirs containing meta.json."""
        _make_run_dir(tmp_path, run=1)
        _make_run_dir(tmp_path, run=2)
        dirs = _discover_run_dirs(tmp_path)
        assert len(dirs) == 2

    def test_offdw_discover_run_dirs_empty_root(self, tmp_path):
        """Empty root returns empty list (no crash)."""
        dirs = _discover_run_dirs(tmp_path)
        assert dirs == []

    def test_offdw_score_run_static_via_run_dir(self):
        """score_run_static on live-smoke run dir returns populated metrics."""
        result = score_run_static(LIVE_SMOKE)
        assert result["loc"] == 33
        assert result["n_funcs"] == 1

    def test_offdw_score_run_static_missing_run_dir(self, tmp_path):
        """score_run_static with nonexistent run dir returns unscorable."""
        result = score_run_static(tmp_path / "nonexistent")
        assert result["status"] == "unscorable"

    def test_offdw_all_fields_in_row_fields(self):
        """ROW_FIELDS contains exactly the fields from the plan contract."""
        expected = {
            "run_id", "task", "arm", "model",
            "loc", "cc_avg", "cc_max", "fn_len_max", "n_funcs",
            "mutation", "hidden_dw", "hidden_offdw",
            "rubric_score", "status",
        }
        assert set(ROW_FIELDS) == expected

    def test_offdw_correctness_hidden_dw_format(self, tmp_path):
        """hidden_dw is reported as 'P/T' fraction string."""
        manifest = json.loads(MANIFEST_PATH.read_text())
        task = "01-duration"
        spec = manifest[task]
        outputs = tmp_path / "outputs"
        outputs.mkdir()
        src = TDD_SMOKE / "with_skill" / "run-1" / "outputs" / "duration.py"
        shutil.copy(src, outputs / spec["impl"])
        result = score_run(tmp_path, task, manifest, HIDDEN_ROOT)
        if result.get("hidden_dw") is not None:
            # Format must be "N/M" fraction.
            dw = result["hidden_dw"]
            assert "/" in dw, f"hidden_dw should be P/T fraction, got {dw!r}"

    def test_offdw_rubric_json_embedded_in_prose(self):
        """Rubric judge tolerates prose wrapping the JSON response."""
        def prose_judge(prompt: str) -> str:
            return 'I think this code is pretty good. {"score": 0.9, "rationale": "Concise."}'
        result = rubric_judge("def f(): pass", judge_fn=prose_judge)
        assert result["score"] == 0.9

    def test_offdw_score_all_nonexistent_run_dir(self, tmp_path):
        """score_one_run on a nonexistent dir returns unscorable row with all fields."""
        fake = tmp_path / "nonexistent_run"
        row = score_one_run(fake, tmp_path, run_rubric=False)
        for field in ROW_FIELDS:
            assert field in row
        assert row["status"] == "unscorable"
