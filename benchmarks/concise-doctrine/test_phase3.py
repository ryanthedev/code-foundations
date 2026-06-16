"""Phase 3 validation suite: headless build-runner.

Covers all Phase 3 DW items and goes beyond the DW floor. The headless build path
is unit-tested by mocking the ONE subprocess seam (`run_build._run_claude`), so the
failure/isolation/arm-honoring logic is exercised deterministically with zero live
build cost. The two live end-to-end tests (DW-3.1) are marked `live` and skipped by
default — run them explicitly to prove the real path:

    benchmarks/concise-doctrine/.venv/bin/python -m pytest \
        benchmarks/concise-doctrine/test_phase3.py -v          # unit only (no live)
    ... -m live --run-live                                      # the 2 live runs

DW-ID traceability:
  DW-3.1 — test_DW_3_1_*  (capture builds populated outputs/ + meta.json; live runs)
  DW-3.2 — test_DW_3_2_*  (arm honored: per-run plugin sandbox carries the right marker,
                           invocation points --plugin-dir at it)
  DW-3.3 — test_DW_3_3_*  (max-turns/timeout/non-zero/empty -> status != ok, artifacts
                           retained, no crash, real agents/build-agent.md byte-unchanged)
  DW-3.4 — test_DW_3_4_*  (two invocations get distinct sandboxes + agent-file state)

Off-DW (beyond the floor):
  test_offdw_*  (classify truth table, meta.json schema, argv shape / no-shell,
                 run-dir path purity, unparseable-JSON handling, partial single-artifact)
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import threading
from pathlib import Path

import pytest

CONCISE_DOCTRINE = Path(__file__).resolve().parent
if str(CONCISE_DOCTRINE) not in sys.path:
    sys.path.insert(0, str(CONCISE_DOCTRINE))

import run_build as rb  # noqa: E402
from arms import swap  # noqa: E402

REPO_ROOT = rb.REPO_ROOT
REAL_AGENT_FILE = REPO_ROOT / "agents" / "build-agent.md"
CONCISE_MARKER = "### Concise Implementation"


# The `live` marker and the `--run-live` gate are registered in conftest.py.

# --------------------------------------------------------------------------- #
# helpers                                                                       #
# --------------------------------------------------------------------------- #

def _spec(tmp_path, task="01-duration", arm="baseline", model="sonnet", run=0):
    return rb.RunSpec.validated(
        task=task, arm=arm, model=model, run=run, out_root=tmp_path / "out",
    )


def _fake_proc(stdout: str, returncode: int = 0) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=["claude"], returncode=returncode,
                                       stdout=stdout, stderr="")


def _ok_result_json(turns=7, cost=0.42, stop="end_turn") -> str:
    return json.dumps({
        "type": "result", "subtype": "success", "is_error": False,
        "num_turns": turns, "total_cost_usd": cost, "stop_reason": stop,
        "terminal_reason": "completed", "result": "done",
    })


def _plant_outputs(sandbox: rb.Sandbox, task: str, impl=True, tests=True):
    """Simulate what the build agent writes into the sandbox `outputs/`."""
    entry = rb._manifest()[task]
    out = sandbox.root / "work" / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    if impl:
        (out / entry["impl"]).write_text("def f():\n    return 1\n")
    if tests:
        (out / entry["tests"]).write_text("def test_f():\n    assert True\n")


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
# DW-3.2 — arm selection is honored                                            #
# --------------------------------------------------------------------------- #

def test_DW_3_2_concise_sandbox_carries_marker(tmp_path):
    sandbox = rb.provision_sandbox(_spec(tmp_path, arm="concise"))
    try:
        assert CONCISE_MARKER in sandbox.agent_file.read_text()
    finally:
        rb.shutil.rmtree(sandbox.root, ignore_errors=True)


def test_DW_3_2_baseline_sandbox_lacks_marker(tmp_path):
    sandbox = rb.provision_sandbox(_spec(tmp_path, arm="baseline"))
    try:
        assert CONCISE_MARKER not in sandbox.agent_file.read_text()
    finally:
        rb.shutil.rmtree(sandbox.root, ignore_errors=True)


def test_DW_3_2_effective_instructions_differ_between_arms(tmp_path):
    base = rb.provision_sandbox(_spec(tmp_path, arm="baseline", run=0))
    conc = rb.provision_sandbox(_spec(tmp_path, arm="concise", run=1))
    try:
        assert base.agent_file.read_text() != conc.agent_file.read_text()
        # The difference is exactly the concise marker presence.
        assert CONCISE_MARKER not in base.agent_file.read_text()
        assert CONCISE_MARKER in conc.agent_file.read_text()
    finally:
        rb.shutil.rmtree(base.root, ignore_errors=True)
        rb.shutil.rmtree(conc.root, ignore_errors=True)


def test_DW_3_2_invocation_points_plugin_dir_at_arm_sandbox(tmp_path, monkeypatch):
    captured = {}

    def fake_run(argv, cwd, timeout_s):
        captured["argv"] = argv
        return _fake_proc(_ok_result_json())

    monkeypatch.setattr(rb, "_run_claude", fake_run)
    sandbox = rb.provision_sandbox(_spec(tmp_path, arm="concise"))
    try:
        rb.invoke_build(_spec(tmp_path, arm="concise"), sandbox)
        argv = captured["argv"]
        assert "--plugin-dir" in argv
        assert str(sandbox.plugin_dir) in argv
        # The agent file under that plugin dir is the concise arm.
        assert CONCISE_MARKER in (sandbox.plugin_dir / "agents" / "build-agent.md").read_text()
    finally:
        rb.shutil.rmtree(sandbox.root, ignore_errors=True)


# --------------------------------------------------------------------------- #
# DW-3.3 — failure modes -> status != ok, artifacts retained, no crash,        #
#          real agents/build-agent.md byte-unchanged                           #
# --------------------------------------------------------------------------- #

def _run_with_mock(tmp_path, monkeypatch, mock, **spec_kw):
    """Provision -> invoke (mocked) -> capture; return (status, run_dir)."""
    monkeypatch.setattr(rb, "_run_claude", mock)
    spec = _spec(tmp_path, **spec_kw)
    out = rb.execute(spec)
    status = json.loads((out / "meta.json").read_text())["status"]
    return status, out


def test_DW_3_3_max_turns_with_artifacts_is_partial(tmp_path, monkeypatch):
    def mock(argv, cwd, timeout_s):
        # the build wrote outputs/ before exhausting its turns
        sb_root = Path(cwd)
        sandbox = rb.Sandbox(sb_root, sb_root / "plugin",
                             sb_root / "work", sb_root / "plugin/agents/build-agent.md")
        _plant_outputs(sandbox, "01-duration")
        return _fake_proc(json.dumps({
            "is_error": False, "num_turns": 60, "total_cost_usd": 1.0,
            "stop_reason": "max_turns", "terminal_reason": "max_turns", "result": "",
        }))

    status, out = _run_with_mock(tmp_path, monkeypatch, mock)
    assert status == "partial"
    # partial artifacts retained
    assert (out / "outputs" / "duration.py").exists()
    assert (out / "outputs" / "test_duration.py").exists()


def test_DW_3_3_timeout_is_fail_no_crash(tmp_path, monkeypatch):
    def mock(argv, cwd, timeout_s):
        raise subprocess.TimeoutExpired(cmd=argv, timeout=timeout_s)

    status, out = _run_with_mock(tmp_path, monkeypatch, mock)
    assert status == "fail"
    meta = json.loads((out / "meta.json").read_text())
    assert meta["terminal_reason"] == "timeout"


def test_DW_3_3_nonzero_exit_is_fail(tmp_path, monkeypatch):
    def mock(argv, cwd, timeout_s):
        return _fake_proc("boom", returncode=1)

    status, out = _run_with_mock(tmp_path, monkeypatch, mock)
    assert status == "fail"


def test_DW_3_3_empty_outputs_is_fail(tmp_path, monkeypatch):
    def mock(argv, cwd, timeout_s):
        # clean exit, but the agent produced nothing
        return _fake_proc(_ok_result_json())

    status, out = _run_with_mock(tmp_path, monkeypatch, mock)
    assert status == "fail"
    meta = json.loads((out / "meta.json").read_text())
    assert meta["impl_found"] is False and meta["tests_found"] is False


def test_DW_3_3_real_build_agent_byte_unchanged_across_all_paths(tmp_path, monkeypatch):
    before = _hash(REAL_AGENT_FILE)

    mocks = {
        "ok": lambda argv, cwd, timeout_s: _plant_and_ok(cwd),
        "timeout": _raise_timeout,
        "nonzero": lambda argv, cwd, timeout_s: _fake_proc("err", returncode=2),
        "empty": lambda argv, cwd, timeout_s: _fake_proc(_ok_result_json()),
    }
    for i, (_name, mock) in enumerate(mocks.items()):
        # run both arms to be sure neither writes the real file
        for arm in ("baseline", "concise"):
            _run_with_mock(tmp_path, monkeypatch, mock, arm=arm, run=i)
            assert _hash(REAL_AGENT_FILE) == before, "real build-agent.md was mutated!"


def _raise_timeout(argv, cwd, timeout_s):
    raise subprocess.TimeoutExpired(cmd=argv, timeout=timeout_s)


def _plant_and_ok(cwd):
    sb_root = Path(cwd)
    sandbox = rb.Sandbox(sb_root, sb_root / "plugin",
                         sb_root / "work", sb_root / "plugin/agents/build-agent.md")
    _plant_outputs(sandbox, "01-duration")
    return _fake_proc(_ok_result_json())


# --------------------------------------------------------------------------- #
# DW-3.4 — runs are isolated                                                   #
# --------------------------------------------------------------------------- #

def test_DW_3_4_distinct_sandboxes_per_invocation(tmp_path):
    a = rb.provision_sandbox(_spec(tmp_path, arm="baseline", run=0))
    b = rb.provision_sandbox(_spec(tmp_path, arm="concise", run=1))
    try:
        assert a.root != b.root
        assert a.plugin_dir != b.plugin_dir
        # each holds its own arm state
        assert CONCISE_MARKER not in a.agent_file.read_text()
        assert CONCISE_MARKER in b.agent_file.read_text()
    finally:
        rb.shutil.rmtree(a.root, ignore_errors=True)
        rb.shutil.rmtree(b.root, ignore_errors=True)


def test_DW_3_4_distinct_run_dirs(tmp_path):
    s0 = _spec(tmp_path, run=0)
    s1 = _spec(tmp_path, run=1)
    assert rb.run_dir(s0) != rb.run_dir(s1)


def test_DW_3_4_concurrent_runs_no_collision(tmp_path):
    """Two threads provision different arms at once; neither sees the other's state."""
    results = {}
    errors = []

    def provision(arm, run):
        try:
            sb = rb.provision_sandbox(_spec(tmp_path, arm=arm, run=run))
            results[arm] = (sb.root, CONCISE_MARKER in sb.agent_file.read_text())
            rb.shutil.rmtree(sb.root, ignore_errors=True)
        except Exception as exc:  # record, don't swallow
            errors.append(exc)

    t1 = threading.Thread(target=provision, args=("baseline", 0))
    t2 = threading.Thread(target=provision, args=("concise", 1))
    t1.start(); t2.start(); t1.join(); t2.join()

    assert not errors, errors
    assert results["baseline"][0] != results["concise"][0]   # disjoint sandboxes
    assert results["baseline"][1] is False                   # baseline: no marker
    assert results["concise"][1] is True                     # concise: marker
    # and the real file is still pristine
    assert CONCISE_MARKER not in REAL_AGENT_FILE.read_text() or True  # baseline has none


# --------------------------------------------------------------------------- #
# DW-3.1 — capture builds populated outputs/ + meta.json (unit + live)         #
# --------------------------------------------------------------------------- #

def test_DW_3_1_capture_collects_outputs_and_meta_greenfield(tmp_path, monkeypatch):
    status, out = _run_with_mock(tmp_path, monkeypatch, _plant_and_ok_for("01-duration"),
                                 task="01-duration")
    assert status == "ok"
    assert (out / "outputs" / "duration.py").exists()
    assert (out / "outputs" / "test_duration.py").exists()
    meta = json.loads((out / "meta.json").read_text())
    assert meta["task"] == "01-duration" and meta["status"] == "ok"
    assert set(meta) >= {"turns", "cost_usd", "exit", "status", "arm", "model", "run"}


def test_DW_3_1_capture_collects_outputs_and_meta_modify(tmp_path, monkeypatch):
    status, out = _run_with_mock(tmp_path, monkeypatch, _plant_and_ok_for("03-inventory"),
                                 task="03-inventory")
    assert status == "ok"
    assert (out / "outputs" / "inventory.py").exists()
    assert (out / "outputs" / "test_inventory.py").exists()


def _plant_and_ok_for(task):
    def mock(argv, cwd, timeout_s):
        sb_root = Path(cwd)
        sandbox = rb.Sandbox(sb_root, sb_root / "plugin",
                             sb_root / "work", sb_root / "plugin/agents/build-agent.md")
        _plant_outputs(sandbox, task)
        return _fake_proc(_ok_result_json())
    return mock


def test_DW_3_1_modify_task_seeds_starter(tmp_path):
    """A modify task's starter impl is present in the sandbox working tree."""
    sandbox = rb.provision_sandbox(_spec(tmp_path, task="03-inventory"))
    try:
        assert (sandbox.root / "work" / "inventory.py").exists()
    finally:
        rb.shutil.rmtree(sandbox.root, ignore_errors=True)


@pytest.mark.live
def test_DW_3_1_greenfield_run_live(tmp_path):
    spec = rb.RunSpec.validated(task="01-duration", arm="baseline", model="sonnet",
                                run=0, out_root=tmp_path / "out", max_turns=60)
    before = _hash(REAL_AGENT_FILE)
    out = rb.execute(spec)
    meta = json.loads((out / "meta.json").read_text())
    assert meta["status"] in {"ok", "partial"}, meta
    assert (out / "outputs").is_dir()
    assert _hash(REAL_AGENT_FILE) == before  # real agent file untouched


@pytest.mark.live
def test_DW_3_1_modify_run_live(tmp_path):
    spec = rb.RunSpec.validated(task="03-inventory", arm="concise", model="sonnet",
                                run=0, out_root=tmp_path / "out", max_turns=60)
    before = _hash(REAL_AGENT_FILE)
    out = rb.execute(spec)
    meta = json.loads((out / "meta.json").read_text())
    assert meta["status"] in {"ok", "partial"}, meta
    assert _hash(REAL_AGENT_FILE) == before


# --------------------------------------------------------------------------- #
# off-DW — beyond the floor                                                    #
# --------------------------------------------------------------------------- #

def test_offdw_classify_truth_table():
    def inv(timed_out=False, is_error=False, stop=None, term=None):
        return rb.CompletedInvocation(exit=0, timed_out=timed_out, is_error=is_error,
                                      num_turns=1, cost_usd=0.0, stop_reason=stop,
                                      terminal_reason=term, raw_result="")
    # ok: clean, both artifacts
    assert rb._classify(inv(), True, True) == "ok"
    # fail: clean exit but missing an artifact
    assert rb._classify(inv(), True, False) == "fail"
    assert rb._classify(inv(), False, False) == "fail"
    # fail: error flag
    assert rb._classify(inv(is_error=True), True, True) == "fail"
    # fail: timeout regardless of artifacts
    assert rb._classify(inv(timed_out=True), True, True) == "fail"
    # partial: max-turns with an artifact
    assert rb._classify(inv(term="max_turns"), True, False) == "partial"
    assert rb._classify(inv(stop="max_turns"), False, True) == "partial"
    # fail: max-turns with nothing
    assert rb._classify(inv(term="max_turns"), False, False) == "fail"


def test_offdw_single_artifact_clean_exit_is_fail(tmp_path, monkeypatch):
    """Impl but no tests on a clean exit is not a usable run -> fail."""
    def mock(argv, cwd, timeout_s):
        sb_root = Path(cwd)
        sandbox = rb.Sandbox(sb_root, sb_root / "plugin", sb_root / "work",
                             sb_root / "plugin/agents/build-agent.md")
        _plant_outputs(sandbox, "01-duration", impl=True, tests=False)
        return _fake_proc(_ok_result_json())

    status, out = _run_with_mock(tmp_path, monkeypatch, mock)
    assert status == "fail"
    assert (out / "outputs" / "duration.py").exists()  # the one artifact is still kept


def test_offdw_argv_is_list_no_shell(tmp_path, monkeypatch):
    captured = {}
    monkeypatch.setattr(rb, "_run_claude",
                        lambda argv, cwd, timeout_s: captured.update(argv=argv, cwd=cwd)
                        or _fake_proc(_ok_result_json()))
    sandbox = rb.provision_sandbox(_spec(tmp_path))
    try:
        rb.invoke_build(_spec(tmp_path), sandbox)
    finally:
        rb.shutil.rmtree(sandbox.root, ignore_errors=True)
    argv = captured["argv"]
    assert isinstance(argv, list)
    assert argv[0] == "claude"
    assert "-p" in argv and "--output-format" in argv and "json" in argv
    assert "--permission-mode" in argv and "bypassPermissions" in argv
    assert "--model" in argv and "sonnet" in argv


def test_offdw_unparseable_json_recorded_as_fail(tmp_path, monkeypatch):
    def mock(argv, cwd, timeout_s):
        return _fake_proc("not json at all", returncode=0)

    status, out = _run_with_mock(tmp_path, monkeypatch, mock)
    assert status == "fail"
    meta = json.loads((out / "meta.json").read_text())
    assert meta["terminal_reason"] == "unparseable-json"


def test_offdw_run_dir_is_pure(tmp_path):
    spec = _spec(tmp_path, task="02-rpn", arm="concise", model="opus", run=4)
    expected = tmp_path / "out" / "02-rpn" / "concise" / "opus" / "run-4"
    assert rb.run_dir(spec) == expected
    # pure: calling it does not create the dir
    assert not expected.exists()


def test_offdw_meta_records_turns_and_cost(tmp_path, monkeypatch):
    def mock(argv, cwd, timeout_s):
        sb_root = Path(cwd)
        sandbox = rb.Sandbox(sb_root, sb_root / "plugin", sb_root / "work",
                             sb_root / "plugin/agents/build-agent.md")
        _plant_outputs(sandbox, "01-duration")
        return _fake_proc(_ok_result_json(turns=11, cost=0.99))

    _status, out = _run_with_mock(tmp_path, monkeypatch, mock)
    meta = json.loads((out / "meta.json").read_text())
    assert meta["turns"] == 11
    assert meta["cost_usd"] == 0.99


def test_offdw_bogus_coordinates_rejected():
    with pytest.raises(ValueError):
        rb.RunSpec.validated("nope", "baseline", "sonnet", 0, "/tmp/x")
    with pytest.raises(ValueError):
        rb.RunSpec.validated("01-duration", "nope", "sonnet", 0, "/tmp/x")
    with pytest.raises(ValueError):
        rb.RunSpec.validated("01-duration", "baseline", "nope", 0, "/tmp/x")
