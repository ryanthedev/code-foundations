# Discovery + Design: Phase 2 - Candidate doctrine wording + arm-swap mechanism

## Files Found
- `agents/build-agent.md` (worktree copy) — the agent template that is the A/B arm variable. Has a `## Baseline Discipline (always on)` section with four subsections (Scope Latitude, Done-When Traceability, Validation Coverage, Test Anchoring) and a `## Phase 1: Discovery + Design` section with a `### Design Decisions` subsection.
- `benchmarks/concise-doctrine/tasks/` — Phase 1 output (6 tasks, manifest, `test_phase1.py`, `conftest.py`).
- `benchmarks/concise-doctrine/.venv/` — Python 3.12 venv with pytest (system python is 3.14, no pytest — must use this venv).
- `benchmarks/tdd-vs-siv/` — prior harness conventions: Python, `uv venv -p 3.12`, pytest, offline scoring, `harness/` for grade/mutate.
- `docs/code-standards.md` — authoring standards (frontmatter quoting, braced plugin-root refs, voice rules). Present.

## Current State
- No `benchmarks/concise-doctrine/arms/` directory exists yet — must be created.
- The `agents/build-agent.md` in this worktree is the source of the verbatim `baseline` arm.
- Phase 1 established the test conventions this phase mirrors: pytest, `test_DW_<n>_<i>_*` naming for DW traceability, `test_offdw_*` for beyond-floor, `pathlib`-based path resolution, `from __future__ import annotations`.

## Gaps
- None blocking. The plan's `**Produces:**` contract is fully buildable from the current worktree state. The swap fn's target path is parameterized (runner supplies a sandbox path), so no production file is touched.

## Code Standards
`docs/code-standards.md` is about authoring *skill/command/agent markdown* (frontmatter quoting, braced `${CLAUDE_PLUGIN_ROOT}` refs, voice rules: no STOP/NEVER shouting, state a rule once neutrally, checkable assertions). These apply to the **concise paragraph** I add to `build-agent.concise.md`:
- State the rule once, neutrally — no shouting block, no "Red Flags — STOP".
- Phrase as a checkable rule, consistent with the existing four subsections' voice.
- The swap mechanism is Python (not plugin markdown); standards there default to the benchmark's existing Python conventions (Phase 1 / tdd-vs-siv): pytest, `pathlib`, type hints, functionally cohesive routines, validate-at-boundary.

## Test Infrastructure
- Framework: pytest, run via `benchmarks/concise-doctrine/.venv/bin/python -m pytest`.
- Conventions (from Phase 1 `test_phase1.py`): `test_DW_<n>_<i>_*` for DW-traceable tests, `test_offdw_*` for beyond-floor, module docstring with DW-ID traceability map, `pathlib.Path(__file__).resolve()` anchoring, `tempfile` for dirty/isolation cases.
- New tests for this phase go in `benchmarks/concise-doctrine/tasks/test_phase2.py` (alongside `test_phase1.py`, same venv/conftest), or a sibling under `arms/`. Decision: place at `benchmarks/concise-doctrine/test_phase2.py` so it can import `arms/swap.py` and diff the two arm files without reaching into `tasks/`.

## DW Verification

| DW-ID | Done-When Item | Status | Test Cases |
|-------|---------------|--------|------------|
| DW-2.1 | `build-agent.concise.md` = baseline + the new subsection + the Phase-1 check, diffable to exactly those additions (no other deltas). | COVERED | `test_DW_2_1_concise_diff_is_exactly_additions` (unified diff of baseline→concise contains only added lines, zero removed/changed lines), `test_DW_2_1_concise_is_superset_of_baseline` (every baseline line still present in order), `test_DW_2_1_additions_are_the_subsection_and_check` (added lines = the concise subsection block + the one-line Phase-1 check) |
| DW-2.2 | The paragraph passes a self-review against code-clarity rules (Different-Words test; no contradiction with existing Baseline Discipline) — recorded in the discovery notes. | COVERED | Self-review recorded below (this file). Tests: `test_DW_2_2_no_aposd_token` (case-insensitive `aposd` absent), `test_DW_2_2_no_contradiction_markers` (paragraph does not weaken scope/test-floor — asserts coexistence of governing-implementation-only language), `test_DW_2_2_different_words_from_heading` (subsection body does not merely restate its own heading) |
| DW-2.3 | `set_arm("baseline")` and `set_arm("concise")` deterministically select the right variant; an injected failure mid-run restores baseline. | COVERED | `test_DW_2_3_set_arm_baseline_selects_baseline`, `test_DW_2_3_set_arm_concise_selects_concise` (target file content matches the chosen variant), `test_DW_2_3_injected_failure_restores_baseline` (exception raised inside the context manager body leaves target == baseline), `test_DW_2_3_rejects_unknown_arm` (ValueError on bogus arm), plus off-DW: `test_offdw_clean_exit_restores_baseline`, `test_offdw_target_path_is_configurable`, `test_offdw_no_partial_write_on_crash` |

**All items COVERED:** YES (3 DW-IDs in prompt = 3 DW-IDs in table)

## Code-Clarity Self-Review of the Candidate Paragraph (DW-2.2 record)

Candidate subsection (added under `## Baseline Discipline (always on)`, after `### Test Anchoring`):

> ### Concise Implementation
>
> Inside this phase's implementation code, prefer concise code over verbose code, while keeping it readable and maintainable. Reach for built-ins and existing solutions before hand-rolling your own. This governs implementation code only — it never licenses cutting a test, narrowing test coverage below the floor in Validation Coverage, or trimming scope under Scope Latitude. When concision and clarity conflict, clarity wins: shorter is the goal, but obvious is the requirement.

Candidate one-line Phase-1 check (added in `### Design Decisions` of `## Phase 1: Discovery + Design`):

> - When sketching the interface, note where a built-in or existing solution replaces hand-written code, and prefer the concise expression that stays readable.

Self-review against `code-clarity-and-docs`:

| Rule | Check | Result |
|------|-------|--------|
| Different-Words test (CQ-3, RF-1) | Does the body restate its heading "Concise Implementation"? | PASS — the body explains *what* concise means here (prefer concise over verbose; reuse built-ins), *the boundary* (implementation only), and *the tie-breaker* (clarity wins). It does not say "be concise" and stop. |
| Naming precision (NP-1, NP-4) | Heading guessable in isolation, matches scope? | PASS — "Concise Implementation" reads as "rules about writing concise implementation code"; scope-matches because the body confines it to implementation code. Not "Concise Code" (which could be read to include tests). |
| Naming consistency (NK-2) | Heading reused for another purpose? | PASS — no other subsection uses "Concise". |
| No contradiction with Validation Coverage | Does it weaken "test beyond the DW floor / no ceiling"? | PASS — explicitly states it "never licenses cutting a test, narrowing test coverage below the floor in Validation Coverage". Names the existing rule by its exact heading. |
| No contradiction with Scope Latitude | Does it license trimming scope? | PASS — explicitly states it never licenses "trimming scope under Scope Latitude". Names the existing rule by its exact heading. |
| No `aposd` reference (constraint) | Token present? | PASS — absent. |
| Voice (code-standards: state once, neutral, no shouting) | Shouting block / STOP / NEVER-caps? | PASS — declarative sentences, matches the tone of the existing four subsections. |
| Tie-breaker present (constraint: readable + maintainable) | Does it resolve concision-vs-clarity? | PASS — "When concision and clarity conflict, clarity wins." |

Conclusion: the candidate passes the self-review. It is obvious doctrine (a rule with a boundary and a tie-breaker), not aspiration ("try to be concise").

## Design Decisions

### Arm files
- `arms/build-agent.baseline.md` = byte-for-byte copy of the worktree's current `agents/build-agent.md`. Built via file copy so the diff to `concise` is provably "additions only".
- `arms/build-agent.concise.md` = baseline content with exactly two insertions: the `### Concise Implementation` subsection (appended after `### Test Anchoring`, before the `---` that closes the Baseline Discipline section) and the one-line Phase-1 check (appended to `### Design Decisions`). No other bytes change → unified diff shows only added lines (DW-2.1).
- Marker for Phase 3 DW-3.2: the literal heading `### Concise Implementation` is present in `concise` and absent in `baseline`, giving the runner a deterministic marker to assert arm selection.

### Swap mechanism (`arms/swap.py`)
Design guidance applied: validate-at-boundary, context-manager for guaranteed restore, no empty catch, configurable target path, functionally cohesive routines.

- `ARMS = {"baseline": <baseline path>, "concise": <concise path>}` — the only valid arm names; anything else is rejected at entry with `ValueError`.
- `variant_path(arm) -> Path` — pure resolver: validates `arm` membership, returns the variant file path. Single responsibility (input → path), satisfies the `set_arm(arm) -> path` Produces contract's "select the right variant" half.
- `set_arm(arm, target) -> Path` — the runner-facing fn. Validates `arm`, copies the chosen variant onto `target` (the sandbox agent-file path the runner supplies — NOT the production `agents/build-agent.md`), returns `target`. Crossing-the-filesystem-boundary write is the deliberate side effect.
- `arm_session(target, restore_to="baseline")` — context manager: snapshots the prior target bytes (if any) on enter, yields, and on ANY exit (normal or exception) restores baseline content to `target`. This is the "guaranteed baseline-restore" / "injected failure mid-run restores baseline" mechanism. Uses `try/finally`; the `finally` block always runs the restore. No bare `except`.
  - Atomicity: the variant is written to a temp file in the target's directory then `os.replace()`d onto the target (atomic rename on POSIX) so a crash mid-write never leaves a truncated agent file.
  - Restore-to-baseline on exit means a crashed run leaves the target holding baseline content, never the mutated concise content — matching the edge case "a crashed run never leaves a mutated agent file behind."

Why a context manager AND a bare `set_arm`: the runner (Phase 3) may want either the explicit fn (returns path, for logging/asserting) or the scoped guarantee. `arm_session` composes `set_arm` internally, so there is one canonical write path.

### Test file location
`benchmarks/concise-doctrine/test_phase2.py` — sibling of `tasks/`, imports `arms.swap`, diffs the two arm files. Reuses the Phase 1 venv + pytest. A local `conftest.py` is not needed (no custom markers); the mutation `slow` marker is tasks-scoped.

## Prerequisites
- [x] `agents/build-agent.md` exists in the worktree (baseline source)
- [x] Python 3.12 venv with pytest available at `benchmarks/concise-doctrine/.venv`
- [x] No production file is touched (target path is parameterized)

## Recommendation
BUILD — author the two arm files, the `arms/swap.py` module (with `__init__.py` so it's importable), and `test_phase2.py`; validate all 3 DW items pass.
