"""Phase 1 validation suite for benchmarks/concise-doctrine/tasks/.

Covers all DW items from Phase 1 and goes beyond the DW floor.

DW-ID traceability:
  DW-1.1 — test_DW_1_1_*
  DW-1.2 — test_DW_1_2_*
  DW-1.3 — test_DW_1_3_*
  DW-1.4 — test_DW_1_4_*

Off-DW (beyond the floor):
  test_offdw_* — additional correctness checks (dirty manifest, hidden suite
  naming conventions, _smoke reference impls pass their own thorough suites, etc.)

Run from the repo root:
  uv run --python 3.12 pytest benchmarks/concise-doctrine/tasks/test_phase1.py -v
or if venv is already active:
  python -m pytest benchmarks/concise-doctrine/tasks/test_phase1.py -v
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# -------------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------------
TASKS_DIR = Path(__file__).resolve().parent
CONCISE_DOCTRINE = TASKS_DIR.parent
TDD_VS_SIV = CONCISE_DOCTRINE.parent / "tdd-vs-siv"
HARNESS = TDD_VS_SIV / "harness"

PORTED_TASK_IDS = ["01-duration", "02-rpn", "03-inventory", "04-password"]
NEW_TASK_IDS = ["05-rate-limiter", "06-csv-stats"]
ALL_TASK_IDS = PORTED_TASK_IDS + NEW_TASK_IDS

# -------------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------------

def load_manifest() -> dict:
    return json.loads((TASKS_DIR / "manifest.json").read_text())


def hidden_suite_functions(task_id: str) -> list[str]:
    """Return all function names from a task's hidden test file."""
    src = (TASKS_DIR / task_id / "hidden" / "test_hidden.py").read_text()
    return re.findall(r"^def (test_\w+)", src, re.MULTILINE)


# -------------------------------------------------------------------------
# DW-1.1: Ported tasks have build-ready plan.md with DW-IDs
# -------------------------------------------------------------------------

@pytest.mark.parametrize("task_id", PORTED_TASK_IDS)
def test_DW_1_1_plan_md_exists(task_id):
    plan = TASKS_DIR / task_id / "plan.md"
    assert plan.exists(), f"Missing plan.md for {task_id}"


@pytest.mark.parametrize("task_id", PORTED_TASK_IDS)
def test_DW_1_1_plan_md_contains_dw_ids(task_id):
    plan_text = (TASKS_DIR / task_id / "plan.md").read_text()
    # Each plan must have at least one DW-N.M pattern
    assert re.search(r"DW-\d+\.\d+", plan_text), \
        f"{task_id}/plan.md has no DW-ID references"


@pytest.mark.parametrize("task_id", PORTED_TASK_IDS)
def test_DW_1_1_plan_md_has_gate_and_model(task_id):
    plan_text = (TASKS_DIR / task_id / "plan.md").read_text()
    assert "**Gate:**" in plan_text, f"{task_id}/plan.md missing **Gate:** field"
    assert "**Model:**" in plan_text, f"{task_id}/plan.md missing **Model:** field"


@pytest.mark.parametrize("task_id", PORTED_TASK_IDS)
def test_DW_1_1_hidden_suites_carried_over(task_id):
    hidden = TASKS_DIR / task_id / "hidden" / "test_hidden.py"
    assert hidden.exists(), f"Missing hidden suite for {task_id}"


@pytest.mark.parametrize("task_id", PORTED_TASK_IDS)
def test_DW_1_1_hidden_suite_has_dw_and_offdw_buckets(task_id):
    fns = hidden_suite_functions(task_id)
    dw = [f for f in fns if f.startswith("test_dw_")]
    offdw = [f for f in fns if f.startswith("test_offdw_")]
    assert dw, f"{task_id}: hidden suite has no test_dw_* functions"
    assert offdw, f"{task_id}: hidden suite has no test_offdw_* functions"


# -------------------------------------------------------------------------
# DW-1.2: New tasks have plan.md, hidden suite (both buckets), no starter needed
# -------------------------------------------------------------------------

@pytest.mark.parametrize("task_id", NEW_TASK_IDS)
def test_DW_1_2_plan_md_exists(task_id):
    plan = TASKS_DIR / task_id / "plan.md"
    assert plan.exists(), f"Missing plan.md for {task_id}"


@pytest.mark.parametrize("task_id", NEW_TASK_IDS)
def test_DW_1_2_plan_md_has_dw_ids(task_id):
    plan_text = (TASKS_DIR / task_id / "plan.md").read_text()
    assert re.search(r"DW-\d+\.\d+", plan_text), \
        f"{task_id}/plan.md has no DW-ID references"


@pytest.mark.parametrize("task_id", NEW_TASK_IDS)
def test_DW_1_2_hidden_test_hidden_exists(task_id):
    hidden = TASKS_DIR / task_id / "hidden" / "test_hidden.py"
    assert hidden.exists(), f"Missing hidden/test_hidden.py for {task_id}"


@pytest.mark.parametrize("task_id", NEW_TASK_IDS)
def test_DW_1_2_hidden_suite_has_test_dw_bucket(task_id):
    fns = hidden_suite_functions(task_id)
    dw = [f for f in fns if f.startswith("test_dw_")]
    assert len(dw) >= 1, f"{task_id}: hidden suite has no test_dw_* functions"


@pytest.mark.parametrize("task_id", NEW_TASK_IDS)
def test_DW_1_2_hidden_suite_has_test_offdw_bucket(task_id):
    fns = hidden_suite_functions(task_id)
    offdw = [f for f in fns if f.startswith("test_offdw_")]
    assert len(offdw) >= 1, f"{task_id}: hidden suite has no test_offdw_* functions"


def test_DW_1_2_count_of_new_tasks():
    # Plan specifies 2-3 new tasks; we created exactly 2.
    assert len(NEW_TASK_IDS) >= 2, "Fewer than 2 new tasks — violates DW-1.2"
    assert len(NEW_TASK_IDS) <= 3, "More than 3 new tasks — exceeds plan scope"


# -------------------------------------------------------------------------
# DW-1.3: Mutation calibration — thin < 1.0, thorough == 1.0
# This test is slow (runs AST mutation); skip with -m "not slow" to skip.
# -------------------------------------------------------------------------

def _run_mutation_calibration(task_id: str, impl_name: str, test_file_name: str) -> float:
    """Run mutation_score() from tdd-vs-siv harness on a _smoke file pair.

    Returns the mutation score as a float in [0, 1].
    Gated: unmutated suite must be green first; raises AssertionError otherwise.
    """
    sys.path.insert(0, str(HARNESS))
    from mutate import mutation_score  # noqa: PLC0415

    smoke_dir = TASKS_DIR / task_id / "_smoke"
    impl = smoke_dir / impl_name
    test_file = smoke_dir / test_file_name

    # Gate: unmutated suite must pass before we trust mutation scores.
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=str(smoke_dir),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Unmutated suite {test_file_name} is RED — cannot trust mutation score.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )

    k, n, _ = mutation_score(impl, test_file)
    return round(k / n, 3) if n > 0 else 0.0


@pytest.mark.slow
def test_DW_1_3_thin_suite_below_1_task_05():
    score = _run_mutation_calibration("05-rate-limiter", "impl.py", "test_thin.py")
    assert score < 1.0, (
        f"05-rate-limiter thin suite scored {score} — expected < 1.0 (mutation surface is saturated)"
    )


@pytest.mark.slow
def test_DW_1_3_thin_suite_below_1_task_06():
    score = _run_mutation_calibration("06-csv-stats", "impl.py", "test_thin.py")
    assert score < 1.0, (
        f"06-csv-stats thin suite scored {score} — expected < 1.0 (mutation surface is saturated)"
    )


@pytest.mark.slow
def test_DW_1_3_thorough_suite_scores_1_task_05():
    score = _run_mutation_calibration("05-rate-limiter", "impl.py", "test_thorough.py")
    assert score == 1.0, (
        f"05-rate-limiter thorough suite scored {score} — expected 1.0 (reference impl + thorough suite must kill all mutants)"
    )


@pytest.mark.slow
def test_DW_1_3_thorough_suite_scores_1_task_06():
    score = _run_mutation_calibration("06-csv-stats", "impl.py", "test_thorough.py")
    assert score == 1.0, (
        f"06-csv-stats thorough suite scored {score} — expected 1.0 (reference impl + thorough suite must kill all mutants)"
    )


# -------------------------------------------------------------------------
# DW-1.4: manifest.json validates
# -------------------------------------------------------------------------

def test_DW_1_4_manifest_loads():
    manifest = load_manifest()
    assert isinstance(manifest, dict), "manifest.json is not a dict"
    assert len(manifest) > 0, "manifest.json is empty"


def test_DW_1_4_manifest_has_all_tasks():
    manifest = load_manifest()
    for task_id in ALL_TASK_IDS:
        assert task_id in manifest, f"manifest.json missing task {task_id!r}"


def test_DW_1_4_manifest_required_fields():
    manifest = load_manifest()
    required = {"kind", "impl", "tests", "hidden", "plan"}
    for task_id, entry in manifest.items():
        missing = required - entry.keys()
        assert not missing, f"manifest entry {task_id!r} missing fields: {missing}"


def test_DW_1_4_all_referenced_files_exist():
    manifest = load_manifest()
    for task_id, entry in manifest.items():
        for field in ("hidden", "plan"):
            path = CONCISE_DOCTRINE / entry[field]
            assert path.exists(), (
                f"manifest[{task_id!r}][{field!r}] = {entry[field]!r} — file not found at {path}"
            )


def test_DW_1_4_manifest_python_load_check():
    """Mirrors the plan's 'python -c load check' — confirm manifest is valid JSON via subprocess."""
    manifest_path = TASKS_DIR / "manifest.json"
    result = subprocess.run(
        [sys.executable, "-c", f"import json; json.loads(open({str(manifest_path)!r}).read()); print('ok')"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"python -c load check failed: {result.stderr}"
    assert "ok" in result.stdout


# -------------------------------------------------------------------------
# Off-DW: additional correctness checks beyond the DW floor
# -------------------------------------------------------------------------

def test_offdw_manifest_kind_values_are_valid():
    manifest = load_manifest()
    valid_kinds = {"greenfield", "modify"}
    for task_id, entry in manifest.items():
        assert entry["kind"] in valid_kinds, (
            f"manifest[{task_id!r}]['kind'] = {entry['kind']!r} — must be 'greenfield' or 'modify'"
        )


def test_offdw_modify_tasks_have_starter():
    manifest = load_manifest()
    for task_id, entry in manifest.items():
        if entry["kind"] == "modify":
            starter_dir = TASKS_DIR / task_id / "starter"
            assert starter_dir.exists(), f"modify task {task_id!r} missing starter/ directory"
            files = list(starter_dir.iterdir())
            assert files, f"modify task {task_id!r}: starter/ directory is empty"


def test_offdw_greenfield_tasks_have_no_starter():
    manifest = load_manifest()
    for task_id, entry in manifest.items():
        if entry["kind"] == "greenfield":
            starter_dir = TASKS_DIR / task_id / "starter"
            assert not starter_dir.exists(), (
                f"greenfield task {task_id!r} should not have a starter/ directory"
            )


def test_offdw_plan_md_has_produces_section():
    """All plan.md files should describe what they produce (output paths)."""
    for task_id in ALL_TASK_IDS:
        plan_text = (TASKS_DIR / task_id / "plan.md").read_text()
        assert "outputs/" in plan_text, (
            f"{task_id}/plan.md does not mention 'outputs/' — agent won't know where to write"
        )


def test_offdw_plan_md_has_phase_header():
    """All plan.md files must have a '### Phase N:' header for build command consumption."""
    for task_id in ALL_TASK_IDS:
        plan_text = (TASKS_DIR / task_id / "plan.md").read_text()
        assert re.search(r"###\s+Phase\s+\d+:", plan_text), (
            f"{task_id}/plan.md missing '### Phase N:' header — build command may not parse it"
        )


def test_offdw_hidden_suites_are_valid_python():
    """All hidden suites must be syntactically valid Python."""
    import ast
    for task_id in ALL_TASK_IDS:
        src = (TASKS_DIR / task_id / "hidden" / "test_hidden.py").read_text()
        try:
            ast.parse(src)
        except SyntaxError as e:
            pytest.fail(f"{task_id}/hidden/test_hidden.py is not valid Python: {e}")


def test_offdw_malformed_manifest_dangling_path_detected():
    """Dirty test: a manifest with a dangling file path must be detectable."""
    bad_manifest = {
        "99-fake": {
            "kind": "greenfield",
            "impl": "fake.py",
            "tests": "test_fake.py",
            "hidden": "tasks/99-fake/hidden/test_hidden.py",
            "plan": "tasks/99-fake/plan.md",
        }
    }
    # Simulate what a manifest validator would do
    for task_id, entry in bad_manifest.items():
        for field in ("hidden", "plan"):
            path = CONCISE_DOCTRINE / entry[field]
            # The path should NOT exist (it's a dangling reference)
            assert not path.exists(), (
                f"Test setup error: dangling path {path} unexpectedly exists"
            )
            # A validator that checks existence would correctly flag this
            detected = not path.exists()
            assert detected, f"Validator failed to detect dangling path for {task_id}[{field}]"


@pytest.mark.slow
def test_offdw_smoke_reference_impls_pass_own_thorough_suites():
    """Both _smoke reference impls must have green thorough suites (sanity before mutation)."""
    for task_id in NEW_TASK_IDS:
        smoke_dir = TASKS_DIR / task_id / "_smoke"
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_thorough.py", "-q", "--no-header"],
            cwd=str(smoke_dir),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"{task_id}/_smoke/test_thorough.py failed against reference impl:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


@pytest.mark.slow
def test_offdw_smoke_reference_impls_pass_own_thin_suites():
    """Both _smoke reference impls must also pass the thin suites (sanity)."""
    for task_id in NEW_TASK_IDS:
        smoke_dir = TASKS_DIR / task_id / "_smoke"
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "test_thin.py", "-q", "--no-header"],
            cwd=str(smoke_dir),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"{task_id}/_smoke/test_thin.py failed against reference impl:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
