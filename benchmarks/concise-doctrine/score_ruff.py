"""Static-analysis issue-count scorer (the beyond-correctness quality metric).

Motivated by the literature (RACE; "Static Analysis as a Feedback Loop", arXiv
2508.14419): LLM code that PASSES tests still carries latent static-analysis issues
(~1.45-1.77/task), which correctness benchmarks can't see. This runs `ruff check`
with a broad ruleset on each produced impl and counts issues — deterministic, no LLM,
and it discriminates where cyclomatic complexity and mutation saturate.

Ruleset: a curated broad set that flags real quality smells (bugs, comprehensions,
simplifications, naming, unused, complexity) without being noisy about formatting:
  E,F (pyflakes/pycodestyle errors), B (bugbear), SIM (simplify), C90 (mccabe),
  PERF (performance anti-patterns), RUF, UP (pyupgrade), N (naming).

CLI:
  score_ruff.py --impl path/to/x.py        # issue count + breakdown for one file
  score_ruff.py --root results-dir         # mean issues per task across run dirs
"""
from __future__ import annotations

import argparse
import json
import statistics as st
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "tasks" / "manifest.json"

_SELECT = "E,F,B,SIM,C90,PERF,RUF,UP,N"
# mccabe complexity threshold: flag functions above this (C901). 10 is ruff's
# conventional default; keeps the signal about genuinely complex routines.
_MAX_COMPLEXITY = "10"


def ruff_issues(impl_path: Path) -> dict:
    """Return {count, by_rule} from `ruff check` on *impl_path*. count=None on error."""
    cmd = [
        sys.executable, "-m", "ruff", "check", str(impl_path),
        "--select", _SELECT, "--max-complexity", _MAX_COMPLEXITY,
        "--output-format", "json", "--no-cache", "--isolated",
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        return {"count": None, "by_rule": {}, "error": str(exc)}
    try:
        items = json.loads(r.stdout or "[]")
    except json.JSONDecodeError:
        return {"count": None, "by_rule": {}, "error": (r.stderr or r.stdout)[:200]}
    by_rule = Counter(it.get("code") or "?" for it in items)
    return {"count": len(items), "by_rule": dict(by_rule.most_common())}


def _impl_name(task: str) -> str | None:
    try:
        return json.loads(MANIFEST_PATH.read_text())[task]["impl"]
    except (json.JSONDecodeError, OSError, KeyError):
        return None


def aggregate(root: Path) -> dict:
    """Mean ruff issue-count per task across its run dirs under *root*."""
    out = {}
    for task_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        impl = _impl_name(task_dir.name)
        if not impl:
            continue
        counts, rules = [], Counter()
        for run in sorted(task_dir.glob("*/*/run-*")):
            f = run / "outputs" / impl
            if not f.is_file():
                continue
            r = ruff_issues(f)
            if r["count"] is not None:
                counts.append(r["count"])
                rules.update(r["by_rule"])
        if counts:
            out[task_dir.name] = {
                "n": len(counts),
                "issues_mean": round(st.mean(counts), 2),
                "issues_per_run": counts,
                "top_rules": dict(rules.most_common(6)),
            }
    return out


def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="ruff issue-count scorer")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--impl")
    g.add_argument("--root")
    args = ap.parse_args(argv)
    if args.impl:
        print(json.dumps(ruff_issues(Path(args.impl)), indent=2))
    else:
        print(json.dumps(aggregate(Path(args.root)), indent=2))


if __name__ == "__main__":
    _cli()
