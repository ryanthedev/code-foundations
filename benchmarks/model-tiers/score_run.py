"""score_run.py — Turns a run dir into one ROW_FIELDS CSV row (Phase 3).

Covers all four rungs via manifest["rung"], per SCHEMA.md:
  1-2 (build)  -> execute toolchain.test_hidden against outputs/ merged over
                  hidden/ (SCHEMA.md's Execution contract groups both rungs
                  under one contract, so one helper serves both); score is
                  the fraction of hidden tests passed.
  3   (debug)  -> the same hidden-suite execution (the repro test) PLUS a
                  diff-scope check: outputs/ may only differ from starter/
                  in files named by answer_key["allowed_change_scope"].
  4   (review) -> no hidden suite; judge.panel() fact-matches outputs/report.md
                  against answer_key["defects"] one defect at a time (a 1-5
                  graded "how clearly is this identified" score, median across
                  the 3-judge panel, >=3 counts as found) plus one coarse
                  binary check for an extraneous (spurious) finding, yielding
                  tp/fp/fn and a recall score. This is a documented
                  simplification of full SWR-Bench-style fact-matching — see
                  the phase-3 discovery doc's Design Decisions.

Seam: manifest dicts passed here must carry an injected "_task_dir" key
(str) pointing at the task directory that owns hidden/, starter/, and any
answer-key file — load_manifest() attaches it. SCHEMA.md's on-disk
manifest.json never has this field; only the in-memory dict score_run()
receives does. This keeps score_run(run_dir, manifest) at exactly the two
positional args pinned as the Phase 4/5 seam.

Empty outputs/ (agent produced nothing) short-circuits to a zeroed row
before any subprocess or judge call — never crashes, never invokes the
hidden suite or a judge on nothing.
"""
from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Mapping

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
from judge import JudgeFn, panel  # noqa: E402

ROW_FIELDS = [
    "task", "rung", "model", "run_n", "correct", "score",
    "tp", "fp", "fn", "judge_fail", "time_seconds", "tokens", "cost_usd",
]

HIDDEN_SUITE_TIMEOUT_S = 120
FOUND_THRESHOLD = 3  # 1-5 graded detection score >= this counts as found (TP)

_DETECTION_RUBRIC = (
    "Rate 1-5 how clearly the report below identifies the specific defect "
    "described in the reference answer key (its location and kind). "
    "1 = not mentioned at all; 5 = precisely and unambiguously identified."
)
_EXTRANEOUS_FINDING_RUBRIC = (
    "EXTRANEOUS-FINDING-CHECK: does the report below claim any additional "
    "finding that is NOT among the defects listed in the reference answer "
    "key? Reply PASS if yes (at least one extraneous/spurious finding is "
    "present); reply FAIL if every finding in the report matches a known "
    "defect (or the report has no findings at all)."
)


# ---------------------------------------------------------------------------
# manifest loading (injects the private _task_dir seam)
# ---------------------------------------------------------------------------

def load_manifest(task_dir: Path) -> dict:
    """Load manifest.json from *task_dir* and attach where it lives, so
    score_run can find sibling hidden/, starter/, and answer-key files."""
    manifest = json.loads((task_dir / "manifest.json").read_text())
    manifest["_task_dir"] = str(task_dir)
    return manifest


# ---------------------------------------------------------------------------
# row assembly helpers
# ---------------------------------------------------------------------------

def _load_meta(run_dir: Path) -> dict:
    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def _base_row(manifest: dict, meta: dict) -> dict:
    return {
        "task": meta.get("task", manifest.get("id")),
        "rung": manifest["rung"],
        "model": meta.get("model", ""),
        "run_n": meta.get("run_n", ""),
        "time_seconds": meta.get("time_seconds", ""),
        "tokens": meta.get("tokens", ""),
        "cost_usd": meta.get("cost_usd", ""),
    }


def _zero_row(manifest: dict, meta: dict) -> dict:
    row = _base_row(manifest, meta)
    row.update({"correct": 0, "score": 0.0, "tp": 0, "fp": 0, "fn": 0, "judge_fail": False})
    return row


# ---------------------------------------------------------------------------
# build/debug rungs — hidden-suite execution (SCHEMA.md Execution contract)
# ---------------------------------------------------------------------------

def _parse_bun_summary(output: str) -> tuple[int, int]:
    passed = sum(int(m) for m in re.findall(r"(\d+)\s+pass\b", output))
    failed = sum(int(m) for m in re.findall(r"(\d+)\s+fail\b", output))
    return passed, failed


def _run_hidden_suite(run_dir: Path, manifest: dict) -> tuple[int, int]:
    """Merge outputs/ over a copy of hidden/, run toolchain.install then
    toolchain.test_hidden there, and return (passed, failed) test counts.

    A hung or over-long toolchain command is a bounded failure (0 passed,
    0 failed -> scores as incorrect), never an uncaught exception that would
    crash the whole scoring pass over a matrix of many runs."""
    task_dir = Path(manifest["_task_dir"])
    scratch = run_dir / ".scratch_hidden"
    if scratch.exists():
        shutil.rmtree(scratch)
    shutil.copytree(task_dir / "hidden", scratch)
    for f in (run_dir / "outputs").iterdir():
        if f.is_file():
            shutil.copy(f, scratch / f.name)
    try:
        subprocess.run(shlex.split(manifest["toolchain"]["install"]), cwd=scratch,
                        capture_output=True, timeout=HIDDEN_SUITE_TIMEOUT_S)
        r = subprocess.run(shlex.split(manifest["toolchain"]["test_hidden"]), cwd=scratch,
                            capture_output=True, text=True, timeout=HIDDEN_SUITE_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        return 0, 0
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    return _parse_bun_summary(r.stdout + r.stderr)


def _score_build(run_dir: Path, manifest: dict, meta: dict) -> dict:
    passed, failed = _run_hidden_suite(run_dir, manifest)
    total = passed + failed
    score = passed / total if total else 0.0
    correct = 1 if total and failed == 0 else 0
    row = _base_row(manifest, meta)
    row.update({"correct": correct, "score": round(score, 3), "tp": 0, "fp": 0, "fn": 0,
                "judge_fail": False})
    return row


def _diff_scope_ok(run_dir: Path, manifest: dict, answer_key: dict) -> bool:
    task_dir = Path(manifest["_task_dir"])
    starter_dir = task_dir / manifest["starter_dir"]
    starter_files = {f.name: f.read_bytes() for f in starter_dir.iterdir() if f.is_file()}
    changed = set()
    for f in (run_dir / "outputs").iterdir():
        if not f.is_file():
            continue
        if f.name not in starter_files or f.read_bytes() != starter_files[f.name]:
            changed.add(f.name)
    return changed <= set(answer_key["allowed_change_scope"])


def _score_debug(run_dir: Path, manifest: dict, meta: dict) -> dict:
    task_dir = Path(manifest["_task_dir"])
    answer_key = json.loads((task_dir / manifest["answer_key"]).read_text())
    passed, failed = _run_hidden_suite(run_dir, manifest)
    repro_passes = failed == 0 and passed > 0
    scope_ok = _diff_scope_ok(run_dir, manifest, answer_key)
    correct = 1 if repro_passes and scope_ok else 0
    row = _base_row(manifest, meta)
    row.update({"correct": correct, "score": float(correct), "tp": 0, "fp": 0, "fn": 0,
                "judge_fail": False})
    return row


# ---------------------------------------------------------------------------
# review rung — panel fact-match against planted defects
# ---------------------------------------------------------------------------

def _score_review(
    run_dir: Path, manifest: dict, meta: dict, *, judge_fns: Mapping[str, JudgeFn] | None = None,
) -> dict:
    task_dir = Path(manifest["_task_dir"])
    answer_key = json.loads((task_dir / manifest["answer_key"]).read_text())
    report_path = run_dir / "outputs" / manifest["report_file"]
    report_text = report_path.read_text() if report_path.exists() else ""

    tp = fn = 0
    any_judge_fail = False
    for defect in answer_key["defects"]:
        result = panel(report_text, defect, _DETECTION_RUBRIC, mode="graded", judge_fns=judge_fns)
        if result["judge_fail"]:
            any_judge_fail = True
            continue
        if (result["score"] or 0) >= FOUND_THRESHOLD:
            tp += 1
        else:
            fn += 1

    fp_result = panel(
        report_text, {"defects": answer_key["defects"]}, _EXTRANEOUS_FINDING_RUBRIC,
        mode="binary", judge_fns=judge_fns,
    )
    if fp_result["judge_fail"]:
        any_judge_fail = True
        fp = 0
    else:
        fp = 1 if fp_result["verdict"] == "PASS" else 0

    recall = tp / (tp + fn) if (tp + fn) else 0.0
    correct = 1 if fp == 0 and fn == 0 else 0
    row = _base_row(manifest, meta)
    row.update({"correct": correct, "score": round(recall, 3), "tp": tp, "fp": fp, "fn": fn,
                "judge_fail": any_judge_fail})
    return row


# ---------------------------------------------------------------------------
# public entry point
# ---------------------------------------------------------------------------

def score_run(
    run_dir: Path, manifest: dict, *, judge_fns: Mapping[str, JudgeFn] | None = None,
) -> dict:
    """Score *run_dir* against *manifest* (from load_manifest()) into a
    ROW_FIELDS-shaped dict. Dispatches on manifest["rung"]; empty or missing
    outputs/ short-circuits to a zeroed row without running anything."""
    meta = _load_meta(run_dir)
    outputs = run_dir / "outputs"
    if not outputs.is_dir() or not any(outputs.iterdir()):
        return _zero_row(manifest, meta)

    rung = manifest["rung"]
    if rung in (1, 2):
        return _score_build(run_dir, manifest, meta)
    if rung == 3:
        return _score_debug(run_dir, manifest, meta)
    if rung == 4:
        return _score_review(run_dir, manifest, meta, judge_fns=judge_fns)
    raise ValueError(f"unknown rung: {rung}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Score one run dir into a ROW_FIELDS row")
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--task-dir", required=True)
    args = ap.parse_args(argv)

    manifest = load_manifest(Path(args.task_dir))
    row = score_run(Path(args.run_dir), manifest)
    print(json.dumps(row, indent=2))


if __name__ == "__main__":
    _cli()
