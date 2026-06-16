# Review: Phase 3 — Headless Build Runner

## Executed Results (Step 0)

| Command | Result |
|---------|--------|
| `.venv/bin/python -m pytest test_phase3.py -q` | **22 passed, 2 skipped** (2 skipped = live tests gated behind `--run-live`, correct) |
| `diff -q agents/build-agent.md arms/build-agent.baseline.md` | **MATCH: byte-identical** |
| Inspect `_live-smoke/01-duration/baseline/sonnet/run-1/meta.json` | `status: "ok"`, `impl_found: true`, `tests_found: true` |
| Inspect `_live-smoke/01-duration/baseline/sonnet/run-1/outputs/` | `duration.py`, `test_duration.py` both present |

---

## Requirement Fulfillment

### DW-3.1
PREMISE: "A single invocation produces a populated `outputs/` (impl + tests) and a `meta.json`. GREENFIELD: verify against the captured live artifacts at `_live-smoke/01-duration/baseline/sonnet/run-1/` (expect `meta.json` status `ok`, `impl_found`/`tests_found` true, `outputs/` containing `duration.py` + `test_duration.py`). MODIFY task: a live modify run is DEFERRED TO PHASE 5 by project decision — verify the modify path is covered by the mocked capture unit test, not a live run."

EVIDENCE (greenfield, live artifact):
- `_live-smoke/01-duration/baseline/sonnet/run-1/meta.json`: `status: "ok"`, `impl_found: true`, `tests_found: true`, `exit: 0`, `turns: 41`, `cost_usd: 1.2838131`
- `_live-smoke/01-duration/baseline/sonnet/run-1/outputs/duration.py` — present (1.0K)
- `_live-smoke/01-duration/baseline/sonnet/run-1/outputs/test_duration.py` — present (2.8K)

EVIDENCE (modify path, mocked):
- `test_phase3.py:295` — `test_DW_3_1_capture_collects_outputs_and_meta_modify` uses `_plant_and_ok_for("03-inventory")` and asserts `inventory.py` + `test_inventory.py` exist in outputs
- `test_phase3.py:313` — `test_DW_3_1_modify_task_seeds_starter` asserts the starter `inventory.py` is copied into the sandbox working tree for kind=`modify`
- Both tests pass in the mocked suite (confirmed in Step 0)

TRACE (greenfield): `run_build.py execute("01-duration", "baseline", "sonnet", run=1)` → `provision_sandbox` copies plugin + sets arm + `git init` → `invoke_build` spawns real `claude` → agent writes `outputs/duration.py` + `outputs/test_duration.py` → `capture` copies to `run_dir/outputs/`, writes `meta.json` with `status: "ok"` → confirmed in captured artifact

TRACE (modify, mocked): `provision_sandbox("03-inventory")` → seeds `work/` from `tasks/03-inventory/starter/` (kind=modify) → `invoke_build` (mocked) plants `work/outputs/inventory.py` + `test_inventory.py` → `capture` copies to `run_dir/outputs/`, writes `meta.json` → test asserts pass

VERDICT: **PASS**

---

### DW-3.2
PREMISE: "Arm selection is honored — the build agent's effective instructions differ between `baseline` and `concise` runs (asserted via the `### Concise Implementation` marker in the variant; the `claude` argv points at the arm's `--plugin-dir` sandbox)."

EVIDENCE:
- `arms/build-agent.concise.md:58` — `### Concise Implementation` present
- `grep` on `build-agent.baseline.md` returns 0 matches for the marker
- `test_phase3.py:92` — `test_DW_3_2_concise_sandbox_carries_marker`: asserts concise sandbox `agent_file` contains `### Concise Implementation` — PASSED
- `test_phase3.py:100` — `test_DW_3_2_baseline_sandbox_lacks_marker`: asserts baseline sandbox `agent_file` does NOT contain marker — PASSED
- `test_phase3.py:108` — `test_DW_3_2_effective_instructions_differ_between_arms`: asserts the two agent files differ in text — PASSED
- `test_phase3.py:121` — `test_DW_3_2_invocation_points_plugin_dir_at_arm_sandbox`: captures argv, asserts `--plugin-dir` is present and points to `sandbox.plugin_dir` which carries the concise marker — PASSED
- `run_build.py:194` — `swap.set_arm(spec.arm, agent_file)` writes arm variant into `plugin_dir/agents/build-agent.md`
- `run_build.py:246` — `"--plugin-dir", str(sandbox.plugin_dir)` included in argv

TRACE: `provision_sandbox(arm="concise")` → `swap.set_arm("concise", plugin_dir/agents/build-agent.md)` atomically writes concise variant → `invoke_build` builds argv with `--plugin-dir plugin_dir` → `claude` picks up the concise-variant agent → instructions differ from baseline's agent file

VERDICT: **PASS**

---

### DW-3.3
PREMISE: "Failure modes (max-turns, timeout, non-zero exit, empty output) yield `status != ok` with partial artifacts retained, never an unhandled crash, and the real `agents/build-agent.md` stays byte-unchanged across every path."

EVIDENCE:
- `test_phase3.py:155` — `test_DW_3_3_max_turns_with_artifacts_is_partial`: status == `"partial"`, both artifacts retained in `outputs/` — PASSED
- `test_phase3.py:174` — `test_DW_3_3_timeout_is_fail_no_crash`: raises `TimeoutExpired`, status == `"fail"`, `terminal_reason == "timeout"`, no exception escapes — PASSED
- `test_phase3.py:184` — `test_DW_3_3_nonzero_exit_is_fail`: returncode=1 → status == `"fail"` — PASSED
- `test_phase3.py:192` — `test_DW_3_3_empty_outputs_is_fail`: clean exit but no artifacts → status == `"fail"`, `impl_found: False`, `tests_found: False` — PASSED
- `test_phase3.py:203` — `test_DW_3_3_real_build_agent_byte_unchanged_across_all_paths`: runs all 4 failure modes for both arms, hashes real agent file before/after, asserts hash unchanged — PASSED
- `diff agents/build-agent.md arms/build-agent.baseline.md` → MATCH (confirmed in Step 0)
- `run_build.py:255-264` — `TimeoutExpired` caught, returns a `CompletedInvocation` with `timed_out=True`; never re-raises
- `run_build.py:277-284` — `JSONDecodeError` caught, `terminal_reason="unparseable-json"`, never re-raises
- `run_build.py:379-383` — `execute()` wraps everything in try/finally; `shutil.rmtree(sandbox.root)` always runs

TRACE: `invoke_build` with timeout → `_run_claude` raises `TimeoutExpired` → caught at `run_build.py:257` → `CompletedInvocation(exit=124, timed_out=True, terminal_reason="timeout")` returned → `_classify(timed_out=True, ...)` returns `"fail"` → `capture` writes `meta.json` with `status: "fail"` → no exception escapes, real agent file untouched

VERDICT: **PASS**

---

### DW-3.4
PREMISE: "Runs are isolated — two concurrent invocations don't collide on sandbox or agent-file state."

EVIDENCE:
- `test_phase3.py:235` — `test_DW_3_4_distinct_sandboxes_per_invocation`: two `provision_sandbox` calls produce distinct `root` and `plugin_dir` paths, each holds correct arm state — PASSED
- `test_phase3.py:249` — `test_DW_3_4_distinct_run_dirs`: `run_dir(s0) != run_dir(s1)` for differing run indices — PASSED
- `test_phase3.py:255` — `test_DW_3_4_concurrent_runs_no_collision`: two threads call `provision_sandbox` for different arms simultaneously; asserts disjoint roots, correct arm state in each, no shared mutable state error — PASSED
- `run_build.py:181` — each `provision_sandbox` call creates an independent `tempfile.mkdtemp(prefix=...)` — no shared temp dir
- `run_build.py:193` — each call copies plugin independently into its own `plugin_dir`
- `run_build.py:194` — `swap.set_arm` writes into the per-run `plugin_dir/agents/build-agent.md`, never the real path
- `arms/swap.py:56-68` — `set_arm` validates arm name and does atomic write to the caller-supplied target path (never touches real agent file)

TRACE: Thread-A calls `provision_sandbox(arm="baseline", run=0)` → `tempfile.mkdtemp` → unique `/tmp/runbuild-01-duration-baseline-XYZ/` → copies plugin to `root/plugin/` → `set_arm("baseline", root/plugin/agents/build-agent.md)`. Thread-B simultaneously: unique `/tmp/runbuild-01-duration-concise-ABC/` → copies plugin → `set_arm("concise", abc_root/plugin/agents/build-agent.md)`. Distinct paths, no shared mutable file, no collision possible.

VERDICT: **PASS**

---

## Test-DW Coverage

| DW Item | Tests | Form |
|---------|-------|------|
| DW-3.1 | `test_DW_3_1_capture_collects_outputs_and_meta_greenfield`, `test_DW_3_1_capture_collects_outputs_and_meta_modify`, `test_DW_3_1_modify_task_seeds_starter` (unit, mocked); greenfield confirmed via captured live artifact inspection | Automated unit + live artifact |
| DW-3.2 | `test_DW_3_2_concise_sandbox_carries_marker`, `test_DW_3_2_baseline_sandbox_lacks_marker`, `test_DW_3_2_effective_instructions_differ_between_arms`, `test_DW_3_2_invocation_points_plugin_dir_at_arm_sandbox` | Automated unit |
| DW-3.3 | `test_DW_3_3_max_turns_with_artifacts_is_partial`, `test_DW_3_3_timeout_is_fail_no_crash`, `test_DW_3_3_nonzero_exit_is_fail`, `test_DW_3_3_empty_outputs_is_fail`, `test_DW_3_3_real_build_agent_byte_unchanged_across_all_paths` | Automated unit |
| DW-3.4 | `test_DW_3_4_distinct_sandboxes_per_invocation`, `test_DW_3_4_distinct_run_dirs`, `test_DW_3_4_concurrent_runs_no_collision` | Automated unit |

- [x] All DW items have corresponding tests that ran in Step 0
- [x] Test coverage matches stated level: 100% of failure/isolation/arm logic via subprocess mocking; integration anchor is the captured live artifact (not re-run)
- [x] Live tests (`@pytest.mark.live`) are properly skipped by default via `conftest.py` `--run-live` gate

---

## Edge Cases

| Edge Case | Test | Status |
|-----------|------|--------|
| max-turns with artifacts → `partial`, artifacts retained | `test_DW_3_3_max_turns_with_artifacts_is_partial` (line 155); `test_offdw_classify_truth_table` (lines 363-367) | PASS |
| max-turns with no artifacts → `fail` | `test_offdw_classify_truth_table` line 367: `_classify(inv(term="max_turns"), False, False) == "fail"` | PASS |
| subprocess timeout → `fail`, no crash | `test_DW_3_3_timeout_is_fail_no_crash` (line 174) | PASS |
| non-zero exit → `fail` | `test_DW_3_3_nonzero_exit_is_fail` (line 184) | PASS |
| empty output dir → `fail` | `test_DW_3_3_empty_outputs_is_fail` (line 192) | PASS |

Note on "grader max-retries": there is no grader component in Phase 3; run_build.py has no retry loop. The edge case as listed in the prompt is fully covered by the max-turns path (turn cap → `partial`). No gap.

---

## Dead Code

None found. All imports are used. No unreachable blocks after early returns. No debug statements or commented-out code blocks.

---

## Correctness Dimensions

| Dimension | Status | Evidence |
|-----------|--------|----------|
| Concurrency | PASS | `test_DW_3_4_concurrent_runs_no_collision` (line 255): two threads provision distinct sandboxes simultaneously with no errors; isolation is by construction (each uses `tempfile.mkdtemp`; `set_arm` writes only to the per-run sandbox path) |
| Error Handling | PASS | `TimeoutExpired` caught at `run_build.py:257`; `JSONDecodeError` caught at `run_build.py:277`; non-zero exit mapped to `is_error=True` at line 286; all failure modes produce recorded `CompletedInvocation` — no exception escapes `invoke_build` or `execute` |
| Resources | PASS | `execute()` (line 379-383) wraps provision/invoke/capture in try/finally; `shutil.rmtree(sandbox.root, ignore_errors=True)` runs on all paths including exceptions — temp dirs always cleaned |
| Boundaries | PASS | `RunSpec.validated()` enforces arm ∈ `valid_arms()`, task ∈ manifest keys, model ∈ `_MODELS`, `run >= 0`; `test_offdw_bogus_coordinates_rejected` (line 434) asserts `ValueError` for bad arm/task/model — all pass |
| Security | PASS | `_run_claude` uses list argv (`argv[0] = "claude"`, no shell=True) per `run_build.py:397-400`; `test_offdw_argv_is_list_no_shell` (line 384) asserts `isinstance(argv, list)` and `argv[0] == "claude"` — SM-3 satisfied; user-supplied task/arm/model validated against allowlists before flowing into paths or subprocess |

---

## CC Skill Observations (non-blocking)

Applied cc-routine-and-class-design and cc-defensive-programming checklists:

- **Cohesion (RP-6):** `provision_sandbox`, `invoke_build`, `capture`, `execute` are functionally cohesive; `execute` is correctly temporal/orchestrating (delegates, does no direct work). PASS.
- **Parameter count (PP-4):** `RunSpec.validated` has 7 parameters (task, arm, model, run, out_root, max_turns, timeout_s) — within the 7-max threshold. PASS.
- **Encapsulation (CQ-3, CQ-4):** `RunSpec` and `Sandbox` are frozen dataclasses with no public mutable state. PASS.
- **Error handling (GC-1, EC-3):** External subprocess output and filesystem state validated at the boundary; no empty catch blocks — all exceptions produce a recorded `CompletedInvocation` or propagate as ValueError. PASS.
- **Shell injection (SM-3):** List argv + `shell=False` (the default) throughout. PASS.
- **RF-11 (function hides failure as neutral value):** `_classify` resolves ambiguous outcomes to `fail`/`partial`, never optimistically to `ok` (line 348 comment confirms intent). PASS.

---

## Notes (non-blocking)

1. `test_phase3.py:277` has a dead-looking assertion: `assert CONCISE_MARKER not in REAL_AGENT_FILE.read_text() or True` — the `or True` makes it a no-op tautology. It appears to be a placeholder note rather than a real assertion. Not a bug (the real coverage is in `test_DW_3_3_real_build_agent_byte_unchanged_across_all_paths`), but the line is misleading.

2. The `run_build.py` module-level `sys.path` mutation at line 51-52 is a common pattern for script imports but is a minor encapsulation note; the sentinel `if str(HERE) not in sys.path` prevents duplicate insertion.

3. The live smoke artifact uses `run=1` (not `run=0`), which is a minor naming curiosity; the live test in `test_phase3.py:325` uses `run=0`. The captured artifact path is `run-1/`, suggesting a prior run exists. Not a defect — run index is just an artifact directory name.

---

**Verdict: PASS**
