"""judge.py — Cross-vendor judge panel (Phase 3).

panel() hides three CLI adapters (codex exec / agy --print / claude -p
--model claude-sonnet-4-6) behind one blind-grading call: judges see only
the rendered prompt (artifacts + rubric [+ answer key]) — never a model
name, arm label, or run identifier, which is what prevents tier bias on
the exact axis this benchmark measures (rung-4 review grading). Aggregation
is majority vote for binary PASS/FAIL verdicts and median for 5-point
graded scores.

A judge whose output is malformed or whose subprocess times out is retried
once, then recorded as a judge-failure — never defaulted to a verdict.
Quorum degrades to 2-of-3 when one judge fails outright; below 2 successful
judges the whole panel is judge_fail with verdict=None.

Seam: _JUDGE_ADAPTERS maps judge name -> a str-in/str-out callable, each
independently overridable via panel()'s judge_fns parameter so unit tests
never spawn real CLI processes (mirrors concise-doctrine/score_rubric.py's
injectable _judge_subprocess pattern).
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path
from typing import Callable, Mapping

JudgeFn = Callable[[str], str]

JUDGE_TIMEOUT_S = 90
QUORUM_MIN = 2  # fewer than this many successful judges -> whole panel judge_fail

_BINARY_RUBRIC_WRAPPER = """\
{rubric}

Reply with ONLY a JSON object with exactly two keys:
  "verdict": "PASS" or "FAIL"
  "rationale": a one-sentence explanation
"""

_GRADED_RUBRIC_WRAPPER = """\
{rubric}

Reply with ONLY a JSON object with exactly two keys:
  "score": an integer 1-5 (1 = not at all, 5 = fully/precisely)
  "rationale": a one-sentence explanation
"""


# ---------------------------------------------------------------------------
# blind prompt construction — no model/arm/run identifiers ever enter this
# ---------------------------------------------------------------------------

def _build_prompt(artifacts: str, answer_key: dict | None, rubric: str, *, mode: str) -> str:
    """Render the blind judge prompt. Never receives or emits model/arm/run identity."""
    wrapper = _BINARY_RUBRIC_WRAPPER if mode == "binary" else _GRADED_RUBRIC_WRAPPER
    parts = [wrapper.format(rubric=rubric), "\nArtifact under review:\n" + artifacts]
    if answer_key is not None:
        parts.append("\nReference answer key:\n" + json.dumps(answer_key, indent=2))
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# subprocess adapters (injectable seam: judge_fns overrides these per-call)
# ---------------------------------------------------------------------------

def _run_cli(cmd: list[str], *, timeout: int = JUDGE_TIMEOUT_S) -> str:
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"{cmd[0]} timed out after {timeout}s") from exc
    except FileNotFoundError as exc:
        raise RuntimeError(f"{cmd[0]} not found — is it on PATH?") from exc
    if r.returncode != 0:
        raise RuntimeError(f"{cmd[0]} failed (exit {r.returncode}): {r.stderr[:200]}")
    return r.stdout


def _codex_subprocess(prompt: str) -> str:
    return _run_cli(["codex", "exec", prompt])


def _agy_subprocess(prompt: str) -> str:
    return _run_cli(["agy", "--print", prompt])


def _sonnet46_subprocess(prompt: str) -> str:
    return _run_cli([
        "claude", "-p", prompt,
        "--model", "claude-sonnet-4-6",
        "--output-format", "text",
        "--max-turns", "1",
        "--permission-mode", "default",
    ])


_JUDGE_ADAPTERS: dict[str, JudgeFn] = {
    "codex": _codex_subprocess,
    "agy": _agy_subprocess,
    "sonnet46": _sonnet46_subprocess,
}


# ---------------------------------------------------------------------------
# output parsing
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[^{}]+\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON object found in judge output: {text[:200]!r}")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in judge output: {exc}") from exc


def _parse_verdict(raw: str, *, mode: str) -> dict:
    """Parse and validate one judge's raw output. Raises ValueError if malformed."""
    result = _extract_json(raw)
    if mode == "binary":
        if "verdict" not in result:
            raise ValueError(f"judge output missing 'verdict': {result}")
        verdict = str(result["verdict"]).strip().upper()
        if verdict not in ("PASS", "FAIL"):
            raise ValueError(f"verdict must be PASS or FAIL, got {verdict!r}")
        return {"verdict": verdict}
    if "score" not in result:
        raise ValueError(f"judge output missing 'score': {result}")
    score = int(result["score"])
    if not (1 <= score <= 5):
        raise ValueError(f"score out of range [1,5]: {score}")
    return {"score": score}


# ---------------------------------------------------------------------------
# per-judge call with retry-once-on-failure
# ---------------------------------------------------------------------------

def _call_one_judge(judge_fn: JudgeFn, prompt: str, *, mode: str) -> dict:
    """Call one judge; malformed output or a raised error retries once, then
    is recorded as a judge-failure — never a default verdict."""
    last_error = None
    for _attempt in range(2):
        try:
            raw = judge_fn(prompt)
            parsed = _parse_verdict(raw, mode=mode)
            return {"status": "ok", **parsed}
        except (RuntimeError, ValueError) as exc:
            last_error = exc
    return {"status": "failed", "error": str(last_error)}


# ---------------------------------------------------------------------------
# aggregation
# ---------------------------------------------------------------------------

def _aggregate(results: Mapping[str, dict], *, mode: str) -> dict:
    ok = {name: r for name, r in results.items() if r["status"] == "ok"}
    quorum = f"{len(ok)}/{len(results)}"

    if len(ok) < QUORUM_MIN:
        return {"verdict": None, "score": None, "judge_fail": True,
                "quorum": quorum, "disagreement": False}

    if mode == "binary":
        verdicts = [r["verdict"] for r in ok.values()]
        pass_n, fail_n = verdicts.count("PASS"), verdicts.count("FAIL")
        disagreement = pass_n > 0 and fail_n > 0
        if pass_n == fail_n:
            verdict = None
        else:
            verdict = "PASS" if pass_n > fail_n else "FAIL"
        return {"verdict": verdict, "score": None, "judge_fail": False,
                "quorum": quorum, "disagreement": disagreement}

    scores = [r["score"] for r in ok.values()]
    median = statistics.median(scores)
    disagreement = (max(scores) - min(scores)) >= 2
    return {"verdict": None, "score": median, "judge_fail": False,
            "quorum": quorum, "disagreement": disagreement}


# ---------------------------------------------------------------------------
# public entry point
# ---------------------------------------------------------------------------

def panel(
    artifacts: str,
    answer_key: dict | None,
    rubric: str,
    *,
    mode: str = "binary",
    judge_fns: Mapping[str, JudgeFn] | None = None,
) -> dict:
    """Blind-grade *artifacts* against *rubric* (and optional *answer_key*)
    with the cross-vendor 3-judge panel.

    mode: "binary" (majority PASS/FAIL) or "graded" (median of a 1-5 score).
    judge_fns: overrides the real CLI adapters — inject fakes for tests.

    Returns:
        {"verdict": "PASS"|"FAIL"|None, "score": float|None, "judge_fail": bool,
         "quorum": "n/3", "disagreement": bool, "judges": {name: {...}}}
    """
    if mode not in ("binary", "graded"):
        raise ValueError(f"mode must be 'binary' or 'graded', got {mode!r}")

    adapters = dict(judge_fns) if judge_fns is not None else _JUDGE_ADAPTERS
    prompt = _build_prompt(artifacts, answer_key, rubric, mode=mode)

    results = {name: _call_one_judge(fn, prompt, mode=mode) for name, fn in adapters.items()}
    aggregate = _aggregate(results, mode=mode)
    return {**aggregate, "judges": results}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Cross-vendor judge panel")
    ap.add_argument("--artifacts-file", required=True)
    ap.add_argument("--rubric-file", required=True)
    ap.add_argument("--answer-key-file")
    ap.add_argument("--mode", choices=["binary", "graded"], default="binary")
    args = ap.parse_args(argv)

    artifacts = Path(args.artifacts_file).read_text()
    rubric = Path(args.rubric_file).read_text()
    answer_key = json.loads(Path(args.answer_key_file).read_text()) if args.answer_key_file else None

    result = panel(artifacts, answer_key, rubric, mode=args.mode)
    print(json.dumps(result, indent=2))
    if result["judge_fail"]:
        sys.exit(1)


if __name__ == "__main__":
    _cli()
