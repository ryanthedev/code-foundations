"""Rubric judge + blind A/B scorer for the concise-doctrine benchmark (Phase 4).

rubric_judge: Invokes a fresh-context subprocess (isolated claude -p call) to
  score an implementation 0-1 on readability/maintainability. Fresh-context =
  no injected skills, no shared conversation state, no model-under-test context.
  A warm-context call is a bug, not a variation (the rubric must be independent).

blind_ab: Presents two implementations unlabeled (A/B, not arm names) and asks
  a fresh-context judge to pick the more readable one. Labels are hidden — the
  judge sees only "Implementation A" and "Implementation B".

Subprocess seam (_judge_subprocess) is injectable for mocking in unit tests.
One real live invocation is acceptable per cost constraints (live test skipped
by default, requires --run-live).

CLI:
  score_rubric.py --run-dir <d>
  score_rubric.py --impl <path>      # score a single impl file directly
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

MANIFEST_PATH = HERE / "tasks" / "manifest.json"

# The rubric used by both rubric_judge and blind_ab.
_READABILITY_RUBRIC = """\
Rate the following Python implementation on readability and maintainability
on a scale from 0.0 (unreadable) to 1.0 (exemplary).

Criteria:
- Naming: variables, functions, and parameters have clear, descriptive names.
- Conciseness: no unnecessary verbosity; uses built-ins and standard patterns
  instead of hand-rolling equivalent logic.
- Readability: control flow is easy to follow; functions do one thing.
- Maintainability: easy to modify; no hidden complexity; error handling is
  explicit (not silent).

Reply with ONLY a JSON object with exactly two keys:
  "score": a float between 0.0 and 1.0 (two decimal places)
  "rationale": a one-sentence explanation

Example: {"score": 0.85, "rationale": "Clear naming and concise logic; ..."}
"""

_AB_RUBRIC_TEMPLATE = """\
Compare two Python implementations of the same function for readability and
maintainability. Labels are A and B — do not guess which arm they come from.

Criteria:
- Naming clarity
- Conciseness (uses built-ins, avoids unnecessary boilerplate)
- Readability of control flow
- Maintainability

Implementation A:
```python
{impl_a}
```

Implementation B:
```python
{impl_b}
```

Reply with ONLY a JSON object with exactly two keys:
  "winner": "A", "B", or "tie"
  "rationale": a one-sentence explanation

Example: {{"winner": "A", "rationale": "A uses a dict lookup instead of a long if-chain."}}
"""


# ---------------------------------------------------------------------------
# subprocess seam (injectable for mocking)
# ---------------------------------------------------------------------------

def _judge_subprocess(prompt: str) -> str:
    """Invoke a fresh-context claude subprocess with *prompt*. Returns stdout."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--max-turns", "1",
        "--permission-mode", "default",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("rubric judge subprocess timed out") from exc
    except FileNotFoundError as exc:
        raise RuntimeError("claude CLI not found — is it on PATH?") from exc
    if r.returncode != 0:
        raise RuntimeError(
            f"claude subprocess failed (exit {r.returncode}): {r.stderr[:200]}"
        )
    return r.stdout


def _extract_json(text: str) -> dict:
    """Extract the first JSON object from *text*. Raises ValueError if not found."""
    # Try a direct parse first (model may respond with pure JSON).
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    # Fall back to extracting a {...} block.
    m = re.search(r"\{[^{}]+\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON object found in rubric judge output: {text[:200]!r}")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in rubric judge output: {exc}") from exc


# ---------------------------------------------------------------------------
# core scorers — one operation each
# ---------------------------------------------------------------------------

def rubric_judge(
    impl_text: str,
    *,
    judge_fn: Callable[[str], str] = _judge_subprocess,
) -> dict:
    """Score *impl_text* 0-1 on readability/maintainability from a fresh context.

    Returns:
        {"score": float 0-1, "rationale": str}

    Raises:
        RuntimeError: if the subprocess fails or times out.
        ValueError: if the output cannot be parsed.
    """
    prompt = _READABILITY_RUBRIC + "\n\nCode to evaluate:\n```python\n" + impl_text + "\n```"
    raw = judge_fn(prompt)
    result = _extract_json(raw)

    # Validate shape.
    if "score" not in result or "rationale" not in result:
        raise ValueError(f"rubric judge output missing required keys: {result}")
    score = float(result["score"])
    if not (0.0 <= score <= 1.0):
        raise ValueError(f"rubric judge score out of range [0,1]: {score}")

    return {"score": score, "rationale": str(result["rationale"])}


def blind_ab(
    impl_a: str,
    impl_b: str,
    *,
    judge_fn: Callable[[str], str] = _judge_subprocess,
) -> dict:
    """Blind A/B judge: present two implementations unlabeled, return the winner.

    Arms are passed as raw text (not run dirs) so the caller controls what
    goes to A vs B. Labels "A" and "B" are assigned here — the judge never
    sees arm names ("baseline", "concise").

    Returns:
        {"winner": "A" | "B" | "tie", "rationale": str}

    Raises:
        RuntimeError: if the subprocess fails.
        ValueError: if the output cannot be parsed.
    """
    prompt = _AB_RUBRIC_TEMPLATE.format(impl_a=impl_a, impl_b=impl_b)
    raw = judge_fn(prompt)
    result = _extract_json(raw)

    if "winner" not in result or "rationale" not in result:
        raise ValueError(f"blind_ab output missing required keys: {result}")
    winner = str(result["winner"]).strip().upper()
    if winner not in ("A", "B", "TIE"):
        raise ValueError(f"blind_ab winner must be 'A', 'B', or 'tie'; got {winner!r}")
    # Normalise "TIE" back to lowercase to match expected sentinel.
    winner = "tie" if winner == "TIE" else winner

    return {"winner": winner, "rationale": str(result["rationale"])}


def score_run_rubric(
    run_dir: Path,
    *,
    judge_fn: Callable[[str], str] = _judge_subprocess,
) -> dict:
    """Score the impl in *run_dir* with the rubric judge.

    Returns metrics dict or {'status': 'unscorable', 'reason': str}.
    """
    def _unscorable(reason: str) -> dict:
        return {"rubric_score": None, "rubric_rationale": None,
                "status": "unscorable", "reason": reason}

    if not run_dir.is_dir():
        return _unscorable(f"run_dir does not exist: {run_dir}")

    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        return _unscorable("meta.json missing")

    try:
        meta = json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return _unscorable(f"meta.json unreadable: {exc}")

    task = meta.get("task")
    if not task:
        return _unscorable("meta.json missing 'task' field")

    try:
        manifest = json.loads(MANIFEST_PATH.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return _unscorable(f"manifest unreadable: {exc}")

    if task not in manifest:
        return _unscorable(f"task {task!r} not in manifest")

    impl_path = run_dir / "outputs" / manifest[task]["impl"]
    if not impl_path.exists():
        return _unscorable(f"impl file missing: {manifest[task]['impl']}")

    try:
        impl_text = impl_path.read_text(encoding="utf-8")
    except OSError as exc:
        return _unscorable(f"cannot read impl: {exc}")

    try:
        scored = rubric_judge(impl_text, judge_fn=judge_fn)
    except (RuntimeError, ValueError) as exc:
        return _unscorable(f"rubric judge failed: {exc}")

    return {
        "rubric_score": scored["score"],
        "rubric_rationale": scored["rationale"],
        "status": meta.get("status", "unknown"),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Rubric judge scorer")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir", help="run dir containing outputs/ and meta.json")
    group.add_argument("--impl", help="score a single impl file directly")
    ap.add_argument("--ab-compare", help="second impl for blind A/B (use with --impl)")
    args = ap.parse_args(argv)

    if args.impl and args.ab_compare:
        impl_a = Path(args.impl).read_text()
        impl_b = Path(args.ab_compare).read_text()
        try:
            result = blind_ab(impl_a, impl_b)
        except (RuntimeError, ValueError) as exc:
            print(json.dumps({"status": "unscorable", "reason": str(exc)}))
            sys.exit(1)
    elif args.impl:
        try:
            result = rubric_judge(Path(args.impl).read_text())
        except (RuntimeError, ValueError) as exc:
            print(json.dumps({"status": "unscorable", "reason": str(exc)}))
            sys.exit(1)
    else:
        result = score_run_rubric(Path(args.run_dir))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
