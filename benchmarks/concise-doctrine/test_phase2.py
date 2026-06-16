"""Phase 2 validation suite: candidate doctrine wording + arm-swap mechanism.

Covers all Phase 2 DW items and goes beyond the DW floor.

DW-ID traceability:
  DW-2.1 — test_DW_2_1_*  (concise variant = baseline + exactly the two additions)
  DW-2.2 — test_DW_2_2_*  (paragraph passes code-clarity self-review constraints)
  DW-2.3 — test_DW_2_3_*  (set_arm selects deterministically; failure restores baseline)

Off-DW (beyond the floor):
  test_offdw_* — clean-exit restore, configurable target, atomicity/no-partial-write,
  marker presence for the Phase-3 arm assertion, swap idempotence.

Run from the repo root with the benchmark venv:
  benchmarks/concise-doctrine/.venv/bin/python -m pytest benchmarks/concise-doctrine/test_phase2.py -v
"""
from __future__ import annotations

import difflib
import sys
from pathlib import Path

import pytest

# Make `arms` importable as a package (its parent dir on sys.path).
CONCISE_DOCTRINE = Path(__file__).resolve().parent
if str(CONCISE_DOCTRINE) not in sys.path:
    sys.path.insert(0, str(CONCISE_DOCTRINE))

from arms import swap  # noqa: E402

ARMS_DIR = CONCISE_DOCTRINE / "arms"
BASELINE = ARMS_DIR / "build-agent.baseline.md"
CONCISE = ARMS_DIR / "build-agent.concise.md"

# The two literal additions the concise arm must contribute and nothing else.
SUBSECTION_HEADING = "### Concise Implementation"
PHASE1_CHECK = (
    "When sketching the interface, note where a built-in or existing solution "
    "replaces hand-written code, and prefer the concise expression that stays readable."
)


def _added_lines() -> list[str]:
    """Lines present in concise but not baseline, per a line-level unified diff."""
    base = BASELINE.read_text().splitlines(keepends=True)
    conc = CONCISE.read_text().splitlines(keepends=True)
    return [l[1:] for l in difflib.unified_diff(base, conc, n=0) if l.startswith("+") and not l.startswith("+++")]


def _removed_lines() -> list[str]:
    base = BASELINE.read_text().splitlines(keepends=True)
    conc = CONCISE.read_text().splitlines(keepends=True)
    return [l[1:] for l in difflib.unified_diff(base, conc, n=0) if l.startswith("-") and not l.startswith("---")]


# -------------------------------------------------------------------------
# DW-2.1: concise == baseline + the subsection + the Phase-1 check (additions only)
# -------------------------------------------------------------------------

def test_DW_2_1_arm_files_exist():
    assert BASELINE.is_file(), "baseline arm file missing"
    assert CONCISE.is_file(), "concise arm file missing"


def test_DW_2_1_concise_diff_is_exactly_additions():
    # No baseline line may be removed or changed — the delta is additions only.
    assert _removed_lines() == [], (
        f"concise removed/changed baseline lines: {_removed_lines()!r}"
    )


def test_DW_2_1_concise_is_superset_of_baseline_in_order():
    # Every baseline line still appears, in order, inside concise.
    base = BASELINE.read_text().splitlines()
    conc = CONCISE.read_text().splitlines()
    matcher = difflib.SequenceMatcher(a=base, b=conc, autojunk=False)
    # Sum of matched baseline lines must equal the full baseline length.
    matched = sum(size for _, _, size in matcher.get_matching_blocks())
    assert matched == len(base), (
        f"baseline not fully preserved: matched {matched}/{len(base)} lines"
    )


def test_DW_2_1_additions_are_the_subsection_and_check():
    added = "".join(_added_lines())
    assert SUBSECTION_HEADING in added, "Concise Implementation subsection not added"
    assert PHASE1_CHECK in added, "Phase-1 design-time check not added"


def test_DW_2_1_no_other_headings_added():
    # The only added markdown heading is the Concise Implementation subsection.
    added_headings = [l for l in _added_lines() if l.lstrip().startswith("#")]
    assert added_headings == [SUBSECTION_HEADING + "\n"], (
        f"unexpected added headings: {added_headings!r}"
    )


# -------------------------------------------------------------------------
# DW-2.2: paragraph passes code-clarity self-review constraints
# -------------------------------------------------------------------------

def _concise_subsection_body() -> str:
    """The text of the Concise Implementation subsection (heading to next blank-then-rule)."""
    text = CONCISE.read_text()
    start = text.index(SUBSECTION_HEADING)
    # Subsection runs until the horizontal rule that closes Baseline Discipline.
    end = text.index("\n---", start)
    return text[start:end]


def test_DW_2_2_no_aposd_token():
    # Constraint: the candidate wording must not reference aposd. Check the additions
    # only — the baseline already names the aposd design skill and is preserved verbatim.
    added = "".join(_added_lines()).lower()
    assert "aposd" not in added, "candidate additions must not reference aposd"


def test_DW_2_2_governs_implementation_only():
    body = _concise_subsection_body().lower()
    assert "implementation code only" in body, (
        "paragraph must scope itself to implementation code only"
    )


def test_DW_2_2_no_contradiction_with_validation_coverage():
    # Must not weaken the test-beyond-the-floor rule; it explicitly defers to it.
    body = _concise_subsection_body()
    assert "Validation Coverage" in body, (
        "paragraph must name and preserve the Validation Coverage rule"
    )
    assert "never licenses cutting a test" in body


def test_DW_2_2_no_contradiction_with_scope_latitude():
    body = _concise_subsection_body()
    assert "Scope Latitude" in body, (
        "paragraph must name and preserve the Scope Latitude rule"
    )
    assert "trimming scope" in body


def test_DW_2_2_has_clarity_tiebreaker():
    # "readable and maintainable" must win ties — obvious is the requirement.
    body = _concise_subsection_body().lower()
    assert "clarity wins" in body, "paragraph must resolve concision-vs-clarity in clarity's favor"


def test_DW_2_2_different_words_from_heading():
    # Different-Words test: the body must not merely restate "Concise Implementation".
    body = _concise_subsection_body()
    body_no_heading = body.replace(SUBSECTION_HEADING, "").strip()
    # The body carries substantive content beyond echoing the heading words.
    assert len(body_no_heading.split()) > 30, "subsection body is too thin to be doctrine"
    assert "built-ins" in body_no_heading, "body must give concrete guidance (reuse built-ins)"


def test_DW_2_2_existing_baseline_subsections_unchanged():
    # The four original subsections survive verbatim (no contradiction by edit).
    base = BASELINE.read_text()
    for heading in ("### Scope Latitude", "### Done-When Traceability",
                    "### Validation Coverage", "### Test Anchoring"):
        assert heading in CONCISE.read_text(), f"{heading} lost from concise arm"
        assert heading in base


# -------------------------------------------------------------------------
# DW-2.3: set_arm selects deterministically; injected failure restores baseline
# -------------------------------------------------------------------------

def test_DW_2_3_set_arm_baseline_selects_baseline(tmp_path):
    target = tmp_path / "build-agent.md"
    swap.set_arm("baseline", target)
    assert target.read_text() == BASELINE.read_text()


def test_DW_2_3_set_arm_concise_selects_concise(tmp_path):
    target = tmp_path / "build-agent.md"
    swap.set_arm("concise", target)
    assert target.read_text() == CONCISE.read_text()


def test_DW_2_3_set_arm_returns_target_path(tmp_path):
    target = tmp_path / "build-agent.md"
    returned = swap.set_arm("concise", target)
    assert returned == target


def test_DW_2_3_injected_failure_restores_baseline(tmp_path):
    target = tmp_path / "build-agent.md"

    class InjectedError(RuntimeError):
        pass

    with pytest.raises(InjectedError):
        with swap.arm_session("concise", target):
            # Mid-run the agent file holds concise content...
            assert target.read_text() == CONCISE.read_text()
            raise InjectedError("simulated crash mid-run")

    # ...but after the crash the target is restored to baseline.
    assert target.read_text() == BASELINE.read_text(), (
        "a crashed run must leave the target holding baseline content"
    )


def test_DW_2_3_rejects_unknown_arm(tmp_path):
    target = tmp_path / "build-agent.md"
    with pytest.raises(ValueError):
        swap.set_arm("bogus", target)
    with pytest.raises(ValueError):
        swap.variant_path("bogus")


# -------------------------------------------------------------------------
# Off-DW: beyond the floor
# -------------------------------------------------------------------------

def test_offdw_clean_exit_restores_baseline(tmp_path):
    # Even on a normal exit, arm_session leaves the safe arm in place.
    target = tmp_path / "build-agent.md"
    with swap.arm_session("concise", target):
        assert target.read_text() == CONCISE.read_text()
    assert target.read_text() == BASELINE.read_text()


def test_offdw_arm_session_can_restore_to_concise(tmp_path):
    target = tmp_path / "build-agent.md"
    with swap.arm_session("baseline", target, restore_to="concise"):
        pass
    assert target.read_text() == CONCISE.read_text()


def test_offdw_target_path_is_configurable(tmp_path):
    # The target is caller-supplied; two different targets are independently swapped.
    a = tmp_path / "sandbox-a" / "agent.md"
    b = tmp_path / "sandbox-b" / "agent.md"
    swap.set_arm("baseline", a)
    swap.set_arm("concise", b)
    assert a.read_text() == BASELINE.read_text()
    assert b.read_text() == CONCISE.read_text()


def test_offdw_does_not_touch_production_agent_file():
    # Guard: swap must never write the repo's real agents/build-agent.md.
    production = CONCISE_DOCTRINE.parent.parent / "agents" / "build-agent.md"
    before = production.read_text()
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        swap.set_arm("concise", Path(d) / "agent.md")
    assert production.read_text() == before, "swap mutated the production agent file"


def test_offdw_no_temp_files_left_after_swap(tmp_path):
    target = tmp_path / "build-agent.md"
    swap.set_arm("concise", target)
    leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".arm-")]
    assert leftovers == [], f"atomic write left temp files behind: {leftovers!r}"


def test_offdw_swap_overwrites_prior_content(tmp_path):
    # Swapping arms twice on one target overwrites cleanly (no append/merge).
    target = tmp_path / "build-agent.md"
    swap.set_arm("concise", target)
    swap.set_arm("baseline", target)
    assert target.read_text() == BASELINE.read_text()


def test_offdw_concise_marker_distinguishes_arms():
    # Phase 3 (DW-3.2) asserts arm selection via a marker; confirm the marker is
    # present in concise and absent in baseline.
    assert SUBSECTION_HEADING in CONCISE.read_text()
    assert SUBSECTION_HEADING not in BASELINE.read_text()


def test_offdw_valid_arms_lists_both():
    assert set(swap.valid_arms()) == {"baseline", "concise"}
