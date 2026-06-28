"""Skill-adherence scorer for the read-vs-skill / adherence benchmark.

Measures how well a produced implementation follows a SPECIFIC skill's checklist.
A fresh-context judge (isolated `claude -p`, no skills, no shared state) reads the
skill's `checklists.md` and the produced code, then scores each *applicable*
checklist item as satisfied / partial / violated, returning an adherence fraction.

Run it against BOTH the with-skill and the without-skill (control) outputs, each
graded against the SAME skill checklist — the with−without delta is the skill's
marginal effect; the with-skill absolute is "how well it's followed."

The skill to grade against is taken from the run's manifest entry `skill` field
(falls back to --skill). Adherence judgment is an LLM signal and carries variance
(reported honestly); pair it with the objective per-skill signal in the report.

CLI:
  score_adherence.py --run-dir <d> [--skill <name>]
  score_adherence.py --impl <path> --skill <name>     # score a file directly
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent          # benchmarks/concise-doctrine
REPO_ROOT = HERE.parent.parent                  # code-foundations
MANIFEST_PATH = HERE / "tasks" / "manifest.json"
SKILLS_DIR = REPO_ROOT / "skills"


_ADHERENCE_RUBRIC = """\
You are auditing whether a Python implementation FOLLOWS a specific engineering
checklist. Below is the checklist (the standard) and the code (the artifact).

For each checklist item that is APPLICABLE to code of this kind, decide whether the
code SATISFIES it, PARTIALLY satisfies it, or VIOLATES it. Items that cannot apply
to this code (e.g. concurrency rules for single-threaded code) are NOT APPLICABLE
and must be excluded from the score — do not penalize code for an item it had no
occasion to exercise.

adherence = satisfied / applicable, where a PARTIAL counts as 0.5 and a VIOLATION
as 0. Be strict and evidence-based: only mark SATISFIED when the code visibly does
the thing, not when it merely could have.

Reply with ONLY a JSON object with exactly these keys:
  "applicable": integer count of applicable items
  "satisfied": number (sum; partials count as 0.5)
  "violations": array of short strings naming the most important violated/partial items (max 5)
  "adherence": float 0.0-1.0 (= satisfied / applicable, two decimals)
  "rationale": one sentence

Example: {"applicable": 8, "satisfied": 6.5, "violations": ["no input-type validation", "silent except"], "adherence": 0.81, "rationale": "Validates length but swallows one error path."}

=== CHECKLIST ===
{checklist}

=== CODE ===
```python
{code}
```
"""


def _judge_subprocess(prompt: str) -> str:
    """Invoke a fresh-context claude subprocess with *prompt*. Returns stdout."""
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--max-turns", "1",
        "--permission-mode", "default",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("adherence judge subprocess timed out") from exc
    except FileNotFoundError as exc:
        raise RuntimeError("claude CLI not found — is it on PATH?") from exc
    if r.returncode != 0:
        raise RuntimeError(f"claude subprocess failed (exit {r.returncode}): {r.stderr[:200]}")
    return r.stdout


def _extract_json(text: str) -> dict:
    """Extract the first JSON object from *text*. Raises ValueError if not found."""
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        raise ValueError(f"no JSON object found in adherence judge output: {text[:200]!r}")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in adherence judge output: {exc}") from exc


def _checklist_text(skill: str) -> str:
    """Load the guidance the judge grades against.

    Prefer the skill's `checklists.md` (concrete items). Some skills carry no
    separate checklist file and keep their rules inline in SKILL.md (e.g.
    cc-control-flow-quality) — fall back to SKILL.md in that case so the skill is
    still gradable against the guidance the agent actually received.
    """
    checklist = SKILLS_DIR / skill / "checklists.md"
    if checklist.is_file():
        return checklist.read_text(encoding="utf-8")
    skill_md = SKILLS_DIR / skill / "SKILL.md"
    if skill_md.is_file():
        return skill_md.read_text(encoding="utf-8")
    raise FileNotFoundError(f"no checklists.md or SKILL.md for skill {skill!r} under {SKILLS_DIR / skill}")


def adherence_judge(
    impl_text: str,
    skill: str,
    *,
    judge_fn: Callable[[str], str] = _judge_subprocess,
) -> dict:
    """Score how well *impl_text* follows *skill*'s checklist. Returns a metrics dict."""
    # Targeted replace (not .format) — the rubric body contains literal {...} JSON
    # examples that str.format would misread as fields.
    prompt = (_ADHERENCE_RUBRIC
              .replace("{checklist}", _checklist_text(skill))
              .replace("{code}", impl_text))
    result = _extract_json(judge_fn(prompt))
    if "adherence" not in result:
        raise ValueError(f"adherence judge output missing 'adherence': {result}")
    score = float(result["adherence"])
    if not (0.0 <= score <= 1.0):
        raise ValueError(f"adherence out of range [0,1]: {score}")
    return {
        "skill": skill,
        "adherence": round(score, 3),
        "applicable": result.get("applicable"),
        "satisfied": result.get("satisfied"),
        "violations": result.get("violations"),
        "rationale": str(result.get("rationale", "")),
    }


def _skill_for_run(meta: dict, override: str | None) -> str | None:
    """Resolve the skill to grade against: explicit override, else manifest 'skill'."""
    if override:
        return override
    try:
        manifest = json.loads(MANIFEST_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        return None
    return manifest.get(meta.get("task", ""), {}).get("skill")


def score_run_adherence(
    run_dir: Path,
    *,
    skill: str | None = None,
    judge_fn: Callable[[str], str] = _judge_subprocess,
) -> dict:
    """Score the impl in *run_dir* for adherence to its skill's checklist."""
    def _unscorable(reason: str) -> dict:
        return {"adherence": None, "status": "unscorable", "reason": reason}

    if not (run_dir / "meta.json").exists():
        return _unscorable("meta.json missing")
    try:
        meta = json.loads((run_dir / "meta.json").read_text())
    except (json.JSONDecodeError, OSError) as exc:
        return _unscorable(f"meta.json unreadable: {exc}")

    sk = _skill_for_run(meta, skill)
    if not sk:
        return _unscorable("no skill resolved (manifest 'skill' field or --skill)")

    try:
        manifest = json.loads(MANIFEST_PATH.read_text())
        impl_name = manifest[meta["task"]]["impl"]
    except (json.JSONDecodeError, OSError, KeyError) as exc:
        return _unscorable(f"cannot resolve impl name: {exc}")

    impl_path = run_dir / "outputs" / impl_name
    if not impl_path.exists():
        return _unscorable(f"impl missing: {impl_name}")

    try:
        scored = adherence_judge(impl_path.read_text(encoding="utf-8"), sk, judge_fn=judge_fn)
    except (RuntimeError, ValueError, FileNotFoundError) as exc:
        return _unscorable(f"adherence judge failed: {exc}")

    scored["arm"] = meta.get("arm")
    scored["task"] = meta.get("task")
    scored["status"] = meta.get("status", "unknown")
    return scored


def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Skill-adherence scorer")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir", help="run dir with outputs/ and meta.json")
    group.add_argument("--impl", help="score a single impl file directly")
    ap.add_argument("--skill", help="skill name to grade against (required with --impl)")
    args = ap.parse_args(argv)

    if args.impl:
        if not args.skill:
            ap.error("--skill is required with --impl")
        try:
            result = adherence_judge(Path(args.impl).read_text(), args.skill)
        except (RuntimeError, ValueError, FileNotFoundError) as exc:
            print(json.dumps({"status": "unscorable", "reason": str(exc)}))
            sys.exit(1)
    else:
        result = score_run_adherence(Path(args.run_dir), skill=args.skill)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
