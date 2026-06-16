"""score_all.py — aggregate scorer for the concise-doctrine benchmark (Phase 4).

For each run dir, emits one CSV row with the full schema:

  {run_id, task, arm, model, loc, cc_avg, cc_max, fn_len_max, n_funcs,
   mutation, hidden_dw, hidden_offdw, rubric_score, status}

run_id = "<task>/<arm>/<model>/run-<n>" (relative to the output root).

Behavior on failure modes:
  - missing meta.json, unparseable Python → status='unscorable', metric fields null.
  - partial run (missing impl or tests) → score what's present; flag the rest.
  - non-compiling impl → static_metrics raises ValueError → static fields null.

The rubric judge is skipped by default (--no-rubric) to avoid LLM cost during
matrix runs; Phase 5 can enable it selectively.

CLI:
  score_all.py --out-root <root>           # walk all run dirs under root
  score_all.py --run-dir <d>               # score a single run dir
  score_all.py --out <csv>                 # write CSV (default: stdout)
  score_all.py --no-rubric                 # skip rubric judge (default: True)
  score_all.py --rubric                    # enable rubric judge
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from score_static import static_metrics  # noqa: E402
from score_correctness import score_run, grade_run_dir, MANIFEST_PATH, HIDDEN_ROOT  # noqa: E402
from score_rubric import rubric_judge, _judge_subprocess  # noqa: E402

# Full row schema — field order matches the plan's Produces contract.
ROW_FIELDS = [
    "run_id", "task", "arm", "model",
    "loc", "cc_avg", "cc_max", "fn_len_max", "n_funcs",
    "mutation", "hidden_dw", "hidden_offdw",
    "rubric_score",
    "status",
]


# ---------------------------------------------------------------------------
# row builder — one operation, ≤5 params
# ---------------------------------------------------------------------------

def score_one_run(
    run_dir: Path,
    out_root: Path,
    *,
    run_rubric: bool = False,
    judge_fn: Callable[[str], str] = _judge_subprocess,
) -> dict:
    """Score one run dir and return a full-schema row dict.

    Parameters
    ----------
    run_dir:    the run dir (contains meta.json + outputs/).
    out_root:   the matrix root (used to compute run_id as a relative path).
    run_rubric: whether to invoke the rubric judge (LLM cost).
    judge_fn:   injectable seam for mocking the rubric subprocess.
    """
    # Initialise row with all metric fields as None.
    row: dict = {f: None for f in ROW_FIELDS}

    # run_id is the path relative to out_root.
    try:
        row["run_id"] = str(run_dir.relative_to(out_root))
    except ValueError:
        row["run_id"] = str(run_dir)

    # Read meta.json — sets task/arm/model/status.
    meta_path = run_dir / "meta.json"
    if not meta_path.exists():
        row["status"] = "unscorable"
        return row

    try:
        meta = json.loads(meta_path.read_text())
    except (json.JSONDecodeError, OSError):
        row["status"] = "unscorable"
        return row

    row["task"] = meta.get("task")
    row["arm"] = meta.get("arm")
    row["model"] = meta.get("model")
    row["status"] = meta.get("status", "unknown")

    task = row["task"]
    if not task:
        row["status"] = "unscorable"
        return row

    # Load manifest.
    try:
        manifest = json.loads(MANIFEST_PATH.read_text())
    except (json.JSONDecodeError, OSError):
        row["status"] = "unscorable"
        return row

    if task not in manifest:
        row["status"] = "unscorable"
        return row

    spec = manifest[task]
    impl_path = run_dir / "outputs" / spec["impl"]

    # --- Static metrics ---------------------------------------------------
    if impl_path.exists():
        try:
            sm = static_metrics(impl_path)
            row["loc"] = sm["loc"]
            row["cc_avg"] = sm["cc_avg"]
            row["cc_max"] = sm["cc_max"]
            row["fn_len_max"] = sm["fn_len_max"]
            row["n_funcs"] = sm["n_funcs"]
        except (ValueError, FileNotFoundError):
            # Non-parseable impl: leave static fields None.
            pass

    # --- Correctness + mutation -------------------------------------------
    correctness = score_run(run_dir, task, manifest, HIDDEN_ROOT)
    if correctness.get("status") != "unscorable":
        row["mutation"] = correctness.get("mutation_score")
        row["hidden_dw"] = correctness.get("hidden_dw")
        row["hidden_offdw"] = correctness.get("hidden_offdw")
    # If unscorable (missing impl), these stay None.

    # --- Rubric judge (optional, costs LLM $) ----------------------------
    if run_rubric and impl_path.exists():
        try:
            impl_text = impl_path.read_text(encoding="utf-8")
            scored = rubric_judge(impl_text, judge_fn=judge_fn)
            row["rubric_score"] = scored["score"]
        except (RuntimeError, ValueError, OSError):
            # Record as None — don't let a rubric failure crash the row.
            pass

    return row


def _discover_run_dirs(out_root: Path) -> list[Path]:
    """Walk *out_root* and return all dirs containing a meta.json file.

    Expected tree: <root>/<task>/<arm>/<model>/run-<n>/
    """
    return sorted(p.parent for p in out_root.rglob("meta.json"))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Aggregate scorer: emits one CSV row per run")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--out-root", help="matrix root to walk for all run dirs")
    group.add_argument("--run-dir", help="score a single run dir")
    ap.add_argument("--out", default="-", help="output CSV path (default: stdout)")
    # Rubric judge is opt-in (costs LLM money).
    rubric_group = ap.add_mutually_exclusive_group()
    rubric_group.add_argument("--rubric", dest="run_rubric", action="store_true",
                              help="enable rubric judge (LLM cost)")
    rubric_group.add_argument("--no-rubric", dest="run_rubric", action="store_false",
                              help="skip rubric judge (default)")
    ap.set_defaults(run_rubric=False)
    args = ap.parse_args(argv)

    if args.run_dir:
        run_dirs = [Path(args.run_dir)]
        out_root = Path(args.run_dir).parent
    else:
        out_root = Path(args.out_root)
        run_dirs = _discover_run_dirs(out_root)

    rows = [
        score_one_run(rd, out_root, run_rubric=args.run_rubric)
        for rd in run_dirs
    ]

    if args.out == "-":
        f = io.StringIO()
        w = csv.DictWriter(f, fieldnames=ROW_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
        sys.stdout.write(f.getvalue())
    else:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=ROW_FIELDS, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"wrote {len(rows)} rows -> {out_path}")

    # Print summary to stderr so it doesn't pollute CSV stdout.
    print(f"scored {len(rows)} run(s)", file=sys.stderr)


if __name__ == "__main__":
    _cli()
