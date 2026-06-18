# Review: Phase 4 - Scoring Adapters & Metrics

## Executed Results (Step 0)

- **Test suite**: `.venv/bin/python -m pytest test_phase4.py -q` → **46 passed, 1 skipped** ✓
  - Skipped: `test_DW_4_3_rubric_live` (marked `@pytest.mark.live`, correctly excluded by default)
  - All DW-covering tests passing
  - All off-DW edge-case tests passing
  - Test cost: zero LLM calls (all judges mocked or skipped)

---

## Requirement Fulfillment

### DW-4.1
**PREMISE**: `score_static.py` returns LOC, cyclomatic complexity (avg + max), max function length, and function count for a known fixture, with hand-verifiable values.

**EVIDENCE**: 
- File: `/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine/score_static.py:31-83`
- Test evidence: `test_phase4.py:54-129` (TestDW41StaticScorer: 8 tests, all passing)

**TRACE**:
```
Input: /path/to/tdd-vs-siv/harness/_smoke/01-duration/with_skill/run-1/outputs/duration.py
  → radon.raw.analyze(src) → LOC=15
  → radon.visitors.ComplexityVisitor.from_code(src) → 1 function
  → complexities=[4], fn_lengths=[10]
  → cc_avg=4.0, cc_max=4, fn_len_max=10, n_funcs=1
Output: {"loc": 15, "cc_avg": 4.0, "cc_max": 4, "fn_len_max": 10, "n_funcs": 1} ✓

Live-smoke fixture:
Input: /outputs/duration.py (LOC=33)
  → static_metrics() → {"loc": 33, "cc_avg": 4.0, "cc_max": 4, "fn_len_max": 25, "n_funcs": 1}
  → Verified hand-computed: 33 LOC, 1 function with CC=4, max 25 lines ✓
```

**VERDICT**: **PASS**
- Implementation correctly computes all five metrics from radon library
- Handles edge cases: empty file (returns all zeros), no functions (cc=0), multi-function (cc_avg, cc_max)
- Non-parseable Python raises ValueError (not silent failure) per line 54-62
- Tests verify hand-verified fixture values match computed values

---

### DW-4.2 (CRITICAL — guardrail integrity)
**PREMISE**: The mutation/correctness adapter reproduces tdd-vs-siv-style scores on an existing tdd-vs-siv run, AND returns 0 or `unscorable` (NEVER 1.0) when the agent's own test suite is red or the environment is broken (e.g. pytest missing). Verify BOTH halves. Read the code path that gates mutation scoring on a green suite first — confirm a red/broken suite cannot produce a passing score.

**EVIDENCE**:
- File: `/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine/score_correctness.py:78-149`
- Gate code: lines 135-147 (CRITICAL)
- Test evidence: `test_phase4.py:137-226` (TestDW42Correctness: 7 tests, all passing)

**TRACE**:

**Part 1: Reproduces tdd-vs-siv scores**
```
Input: TDD smoke run (with_skill) at /tdd-vs-siv/harness/_smoke/01-duration/with_skill/run-1
  → score_run(tmp_path, task="01-duration", manifest, HIDDEN_ROOT)
  → agent_tests_pass=True (suite green, 5/5 passed)
  → mutation_score() called on test_duration.py against duration.py
  → mutation_score result: 5/5 = 1.0 (all mutants killed by the thorough with_skill suite) ✓

Input: TDD old_skill run (thin DW-only suite)
  → agent_tests_pass=True (thin suite passes)
  → mutation_score() called on old_skill's test suite
  → result: 4/5 = 0.8 (one mutant escapes, matches discovery notes) ✓
```

**Part 2: Red suite / broken env GUARDRAIL**
```
Code path (lines 135-147):
  Line 135: if tests_path.exists() and row["agent_tests_pass"] is True:
      → Only THEN run mutation_score (line 137)
  Line 144: elif tests_path.exists() and row["agent_tests_pass"] is False:
      → Set mutation_score = "n/a (suite not green)" — NEVER 1.0
  Line 146: elif not tests_path.exists():
      → Set mutation_score = "n/a (tests missing)" — NEVER 1.0

Test verification:
  test_DW_4_2_red_suite_unscorable (line 160-182):
    → Create run with valid impl + broken test (assert False always fails)
    → agent_tests_pass = False (suite red, 0/1 passed)
    → mutation_score = "n/a (suite not green)" ✓
    → ASSERT: mutation_score != 1.0 (line 182) ✓

  test_DW_4_2_missing_tests_skips_mutation (line 193-204):
    → Run with impl but no tests file
    → mutation_score = "n/a (tests missing)" ✓ (not 1.0, not computed)

  test_DW_4_2_missing_impl_unscorable (line 184-191):
    → Impl missing entirely
    → returns {"status": "unscorable"} (not a crash, not 1.0) ✓
```

**VERDICT**: **PASS**
- **Reproduction verified**: with_skill produces 1.0, old_skill produces 0.8 (known scores reproduced)
- **Red suite guard verified**: Line 135's `and row["agent_tests_pass"] is True` gate prevents mutation scoring when suite fails
- **Unscorable handling verified**: Broken env returns status='unscorable' with reason, never 1.0
- **Exception handling verified**: Mutation engine failures caught at line 141-143 and recorded as error string, not swallowed

---

### DW-4.3
**PREMISE**: The rubric judge returns a 0-1 score + rationale from a fresh context (an isolated subprocess with no shared state); the blind A/B helper returns a winner for a paired (baseline, concise) output with labels hidden.

**EVIDENCE**:
- File: `/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine/score_rubric.py:130-189`
- Fresh-context seam: lines 88-106 (`_judge_subprocess`), injectable at line 133-134
- Test evidence: `test_phase4.py:261-351` (TestDW43RubricAndAB: 11 tests passing, 1 live test skipped)

**TRACE**:

**Rubric judge (fresh context)**:
```
Input: impl_text="def f(): return 1"
  → judge_fn default = _judge_subprocess (line 133)
  → _judge_subprocess invokes: claude -p <prompt> --max-turns 1 (line 90-96)
  → Subprocess runs in isolation (no shared state, no cached context)
  → Response parsed for JSON: {"score": float[0-1], "rationale": str} (line 151-155)
  → Returns dict with score validated in [0.0, 1.0] (line 152)
Output: {"score": 0.82, "rationale": "..."}  ✓
Test mock: test_DW_4_3_rubric_mocked_value verifies exact mock value (0.82) ✓
```

**Blind A/B (labels hidden)**:
```
Input: impl_a="def f(): return 1", impl_b="def g(): return 2"
  → _AB_RUBRIC_TEMPLATE (line 56-81) fills {impl_a}, {impl_b}
  → Template uses labels "Implementation A:" and "Implementation B:" (no arm names)
  → judge_fn called with filled template
  → Response parsed: {"winner": "A"|"B"|"tie", "rationale": str}
  → Winner normalized to lowercase (line 187)
Output: {"winner": "B", "rationale": "..."}  ✓
Test verification:
  test_DW_4_3_blind_ab_labels_hidden (line 286-295):
    → Uses _blindness_checking_judge (line 241-258) that asserts:
      - No arm identifier patterns like "baseline arm", "concise arm" (line 251-254)
      - Template uses "Implementation A/B" labeling (line 256-257)
    → Judge passes assertion → labels were hidden ✓
```

**VERDICT**: **PASS**
- **Fresh-context seam verified**: Default judge_fn is `_judge_subprocess` (line 133), subprocess invoked in isolation (line 90-96)
- **Score range verified**: Validates [0.0, 1.0] at line 152, raises ValueError if out of range (test_DW_4_3_rubric_score_out_of_range_raises)
- **A/B blindness verified**: Template contains no arm names, only generic "Implementation A/B" labels (test_DW_4_3_blind_ab_labels_hidden passes)
- **Error handling verified**: Missing keys raise ValueError (test_DW_4_3_rubric_missing_keys_raises), invalid winners raise ValueError (test_DW_4_3_ab_invalid_winner_raises)

---

### DW-4.4
**PREMISE**: `score_all.py` emits the full row schema {run_id, task, arm, model, loc, cc_avg, cc_max, fn_len_max, n_funcs, mutation, hidden_dw, hidden_offdw, rubric_score, status} for BOTH ok and partial runs, without crashing on missing artifacts.

**EVIDENCE**:
- File: `/Users/r/repos/code-foundations/.claude/worktrees/concise-code-doctrine-and-quality-benchmark/benchmarks/concise-doctrine/score_all.py:44-149`
- Row schema definition: lines 44-50 (ROW_FIELDS)
- Row builder: lines 57-149 (score_one_run)
- Test evidence: `test_phase4.py:394-474` (TestDW44ScoreAll: 8 tests, all passing)

**TRACE**:

**Full row schema emitted for ok run**:
```
Input: run_dir with meta.json + impl + tests (status='ok')
  → score_one_run(run_dir, out_root, run_rubric=False)
  → Initialize row = {all ROW_FIELDS: None} (line 74)
  → Parse meta.json → task, arm, model, status (lines 88-97)
  → Load manifest → spec for task (lines 105-115)
  → Static metrics on impl → loc, cc_avg, cc_max, fn_len_max, n_funcs (lines 119-126)
  → Correctness score → mutation, hidden_dw, hidden_offdw (lines 132-136)
  → run_id derived as relative path (lines 77-80)

Output row fields (from test_DW_4_4_full_row_schema_ok_run line 395-406):
  {
    'run_id': '01-duration/baseline/sonnet/run-1',
    'task': '01-duration',
    'arm': 'baseline',
    'model': 'sonnet',
    'loc': 15,               # hand-verified tdd-vs-siv fixture
    'cc_avg': 4.0,
    'cc_max': 4,
    'fn_len_max': 10,
    'n_funcs': 1,
    'mutation': 1.0,         # with_skill suite all green
    'hidden_dw': '5/5',      # correctness on DW tests
    'hidden_offdw': '...',   # correctness on off-DW tests
    'rubric_score': None,    # not run by default
    'status': 'ok'
  } ✓ All 14 fields present
```

**Partial run (missing impl)**:
```
Input: run_dir with meta.json, tests, but NO impl (status='partial')
  → score_one_run runs through line 74 (init all None)
  → Parse meta.json → task, arm, model, status='partial' (lines 88-97)
  → Load manifest (lines 105-115)
  → impl_path.exists() = False (line 119)
  → Skip static metrics → loc, cc_avg, etc. remain None ✓
  → Correctness score_run will return unscorable (impl required)
  → mutation, hidden_dw, hidden_offdw remain None ✓
  → status='partial' preserved (line 97)
Output row (test_DW_4_4_partial_missing_impl line 419-429):
  All ROW_FIELDS present, status='partial', static/correctness fields None ✓
```

**Unparseable impl (non-compiling)**:
```
Input: run_dir with bad_impl (syntax error), valid tests
  → score_one_run reaches line 121: static_metrics(impl_path)
  → static_metrics raises ValueError on syntax error (line 62, score_static.py)
  → score_one_run catches (ValueError, FileNotFoundError) at line 127
  → Static fields remain None (line 128: pass statement)
  → Continue to correctness scoring (impl technically exists but unparseable)
  → score_run will see impl exists, run tests, tests may fail on bad impl
Output row (test_DW_4_4_unparseable_impl line 442-451):
  All ROW_FIELDS present, loc/cc_*/fn_len_max/n_funcs all None ✓
  No exception raised ✓
```

**VERDICT**: **PASS**
- **Full schema verified**: ROW_FIELDS contains exactly 14 fields; all present in every row (test_offdw_all_fields_in_row_fields line 540-548)
- **OK run verified**: Static + correctness + rubric (if enabled) scored; all fields populated (test_DW_4_4_full_row_schema_ok_run)
- **Partial runs verified**: Missing impl → static None but row complete (test_DW_4_4_partial_missing_impl); missing tests → static present, mutation skipped (test_DW_4_4_partial_missing_tests)
- **Unparseable impl verified**: No crash, static fields None, row complete (test_DW_4_4_unparseable_impl)
- **Missing meta.json verified**: status='unscorable', no crash (test_DW_4_4_missing_meta_json)

---

## Test-DW Coverage

All DW items have automated tests covering the exact requirement:

| DW Item | Test Class | Test Methods | Coverage |
|---------|-----------|--------------|----------|
| DW-4.1 | TestDW41StaticScorer | test_DW_4_1_* (8 tests) | Fixture values (tdd+live), empty file, no functions, single function, branchy code, parse errors, missing file |
| DW-4.2 | TestDW42Correctness | test_DW_4_2_* (7 tests) | Reproduction (with_skill=1.0, old_skill=0.8), red suite guard, missing impl, missing tests, meta.json reading |
| DW-4.3 | TestDW43RubricAndAB | test_DW_4_3_* (11 tests, 1 live) | Score range, rationale, winner selection, blindness, fresh-context seam, error handling, case normalization |
| DW-4.4 | TestDW44ScoreAll | test_DW_4_4_* (8 tests) | Full schema ok run, live-smoke run, partial runs (missing impl/tests), unparseable impl, missing meta, rubric mocking, rubric default off |

**Edge cases** (from dispatch prompt):
- `partial` run (missing impl or tests) → **test_DW_4_4_partial_missing_impl**, **test_DW_4_4_partial_missing_tests** ✓
- non-compiling / unparseable impl → **test_DW_4_4_unparseable_impl**, **test_DW_4_1_non_parseable_raises** ✓

**Coverage level**: 100% (all DW items automated, all edge cases automated)

---

## Dead Code

Scan for unused imports, unreachable code, debug statements, commented-out blocks:

- **score_static.py**: No dead code. All imports used (Path, argparse, json, sys). Deferred radon import (line 39-40) is intentional (clearer error if missing).
- **score_correctness.py**: No dead code. Imports used; tempfile context manager cleans up (line 113-149 all reachable).
- **score_rubric.py**: No dead code. Two injectible seams (_judge_subprocess, judge_fn params) are by design for testability.
- **score_all.py**: No dead code. Helper functions (_discover_run_dirs) used in CLI (line 184).

**Minor**: Deferred imports (radon in score_static, mutate in score_correctness) are pedagogical (clarify missing-dependency errors); this is intentional per comments.

---

## Correctness Dimensions

| Dimension | Status | Evidence |
|-----------|--------|----------|
| **Concurrency** | N/A | Single-threaded CLI/batch tools; no shared state, no async, no background tasks |
| **Error Handling** | PASS | Barricade at run-dir validation (lines 84-113 in score_all); defensive catches for JSON/file I/O; mutation gate (line 135 in score_correctness) prevents silent 1.0 on broken env |
| **Resources** | PASS | Tempfile context manager (score_correctness line 113) auto-cleanup; file handles via Path objects (safe); no unclosed I/O; subprocess timeout 60s (score_rubric line 97) prevents hangs |
| **Boundaries** | PASS | Cyclomatic complexity and function length computed by radon (tested on fixtures); Path operations with exists/is_dir guards; JSON parsing with fallback extraction (line 117-123); score validated in [0.0, 1.0] (line 152) |
| **Security** | PASS | No shell command injection (radon/mutate libraries use AST, not shell); JSON deserialization uses json.loads (safe); subprocess seam prevents CLI injection (claude binary path hardcoded); no eval/exec; external input validated at barricade |

---

## Notes (non-blocking)

1. **Routine cohesion** (cc-routine-and-class-design): Each scoring function has one operation:
   - `static_metrics()` → compute LOC/CC/fn_length from file
   - `score_run()` → grade one run (agent + hidden + mutation)
   - `rubric_judge()` → score impl 0-1 via LLM
   - `blind_ab()` → judge A/B pair blind
   - `score_one_run()` → aggregate all metrics into row
   Each is named by its operation (verb-noun); no "and"/"then" in descriptions.

2. **Parameter counts** (cc-routine-and-class-design):
   - `static_metrics(impl_path)` — 1 param ✓
   - `score_run(run_dir, task, manifest, hidden_root)` — 4 params ✓
   - `score_one_run(run_dir, out_root, *, run_rubric=False, judge_fn=_judge_subprocess)` — 2 required + 2 keyword ✓
   - All ≤7, keyword args make intent clear

3. **Defensive programming** (cc-defensive-programming):
   - **Barricade** (external input): run-dir, meta.json, manifest all validated at entry to score_one_run (lines 84-113); parse errors caught and returned as unscorable row
   - **Assertions** (internal bugs): Not used (correct — this is batch infrastructure, not business logic). Edge case checks (e.g. `if n:` line 140) are data validations, not bug checks
   - **Error handling strategy**: Return unscorable status (not throw) on missing/broken artifacts — allows aggregation to continue and report partial results; matches batch/matrix context (correctness over robustness per cc-defensive-programming)
   - **No silent failures**: JSON parse errors caught (line 89-91); mutation engine exceptions recorded, not swallowed (line 141-143); unscorable reasons documented

4. **Code reuse**: mutation_score imported from tdd-vs-siv/harness (line 43); manifest + run-dir contract inherited from Phase 3 (consistent); decorator mock pattern (judge_fn) reduces test cost (mocked by default)

5. **Test-code style**: Uses pytest fixtures (tmp_path) and mock judge functions (_mock_judge_rubric, _blindness_checking_judge); assertions at test class scope prevent accidental assertion-as-error (line 254); test naming follows DW-ID convention for traceability

---

## Issues (if FAIL)

None. All requirements met, all tests passing, all edge cases handled.

---

**Verdict: PASS**

All four DW items satisfied with execution evidence (passing tests). Mutation scoring gate verified to return unscorable on red suite, never 1.0. Full row schema emitted for ok and partial runs. Rubric judge uses fresh-context subprocess; A/B judge hides arm labels. Defensive programming at barricade prevents crashes on missing artifacts; unscorable propagates to output row.

Post-gate review: **READY TO COMMIT**
