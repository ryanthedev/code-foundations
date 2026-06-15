"""Grade one or more agent run directories for the TDD-vs-SIV pilot.

For each run it computes:
  agent_tests_pass   — does the agent's own suite pass against its own code? (sanity)
  n_agent_tests      — how many test functions the agent wrote (breadth proxy)
  hidden_dw          — pass rate on hidden DW-derivable tests       (correctness)
  hidden_offdw       — pass rate on hidden off-DW edge tests        (breadth/correctness)
  mutation_score     — killed/total mutants under the agent's tests (test quality, HEADLINE)

A run dir is any directory containing an `outputs/` folder with the task's impl
+ test files. Pass --run for a single dir, or --runs-root + --eval to walk a
skill-eval iteration tree (.../<eval>/<config>/run-*/).
"""
from __future__ import annotations
import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from mutate import mutation_score  # noqa: E402

MANIFEST = json.loads((ROOT / "tasks" / "manifest.json").read_text())


def _run_pytest(workdir: Path, test_file: str, name_filter: str | None = None):
    """Return (passed, total) parsed from pytest, or (0, 0) on collection error."""
    cmd = [sys.executable, "-m", "pytest", test_file, "-q", "--no-header", "-p", "no:cacheprovider"]
    if name_filter:
        cmd += ["-k", name_filter]
    try:
        r = subprocess.run(cmd, cwd=workdir, capture_output=True, timeout=120, text=True)
    except subprocess.TimeoutExpired:
        return 0, 0
    out = r.stdout + r.stderr
    passed = sum(int(m.group(1)) for m in re.finditer(r"(\d+) passed", out))
    failed = sum(int(m.group(1)) for m in re.finditer(r"(\d+) failed", out))
    errors = sum(int(m.group(1)) for m in re.finditer(r"(\d+) error", out))
    total = passed + failed + errors
    return passed, total


def grade_run(run_dir: Path, eval_id: str) -> dict:
    spec = MANIFEST[eval_id]
    outputs = run_dir / "outputs"
    impl = outputs / spec["impl"]
    tests = outputs / spec["tests"]
    row = {"run": str(run_dir), "eval": eval_id, "impl_found": impl.exists(),
           "tests_found": tests.exists(), "n_agent_tests": 0, "agent_tests_pass": "",
           "hidden_dw": "", "hidden_offdw": "", "mutation_killed": "",
           "mutation_total": "", "mutation_score": ""}
    if not impl.exists():
        return row
    if tests.exists():
        row["n_agent_tests"] = len(re.findall(r"^\s*def test_", tests.read_text(), re.M))

    with tempfile.TemporaryDirectory() as d:
        work = Path(d)
        shutil.copy(impl, work / spec["impl"])
        # 1. agent suite against agent code (sanity)
        if tests.exists():
            shutil.copy(tests, work / spec["tests"])
            p, t = _run_pytest(work, spec["tests"])
            row["agent_tests_pass"] = (t > 0 and p == t)
        # 2. hidden suite — correctness, bucketed
        hidden = ROOT / spec["hidden"]
        shutil.copy(hidden, work / "test_hidden.py")
        dwp, dwt = _run_pytest(work, "test_hidden.py", name_filter="test_dw_")
        ofp, oft = _run_pytest(work, "test_hidden.py", name_filter="test_offdw_")
        row["hidden_dw"] = f"{dwp}/{dwt}"
        row["hidden_offdw"] = f"{ofp}/{oft}"
        (work / "test_hidden.py").unlink()
        # 3. mutation score — agent tests vs seeded faults in agent code (HEADLINE)
        #    Only meaningful when the unmutated suite passes: otherwise every
        #    mutant "fails" for reasons unrelated to the seeded fault.
        if tests.exists() and row["agent_tests_pass"] is True:
            k, n, _ = mutation_score(work / spec["impl"], work / spec["tests"])
            row["mutation_killed"], row["mutation_total"] = k, n
            row["mutation_score"] = round(k / n, 3) if n else ""
        else:
            row["mutation_score"] = "n/a (suite not green)"
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", help="a single run dir containing outputs/")
    ap.add_argument("--runs-root", help="skill-eval iteration dir to walk")
    ap.add_argument("--eval", required=True, help="eval id (key in manifest.json)")
    ap.add_argument("--out", default=str(ROOT / "results.csv"))
    args = ap.parse_args()

    rows = []
    if args.run:
        rows.append({**grade_run(Path(args.run), args.eval), "config": "single"})
    else:
        base = Path(args.runs_root) / args.eval
        for config_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            for run_dir in sorted(config_dir.glob("run-*")):
                rows.append({**grade_run(run_dir, args.eval), "config": config_dir.name})

    fields = ["config", "eval", "run", "impl_found", "tests_found", "n_agent_tests",
              "agent_tests_pass", "hidden_dw", "hidden_offdw",
              "mutation_killed", "mutation_total", "mutation_score"]
    with open(args.out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(json.dumps({k: r.get(k) for k in fields}))
    print(f"\nwrote {len(rows)} rows -> {args.out}")


if __name__ == "__main__":
    main()
