"""Static metrics scorer for the concise-doctrine benchmark (Phase 4).

Computes LOC, cyclomatic complexity (avg + max), max function length, and
function count from a Python implementation file using the `radon` library.

CLI:
  score_static.py --run-dir <d>
  score_static.py --impl <path>      # score a single file directly

Barricade: inputs validated at entry. Non-parseable Python raises ValueError
(caller records unscorable, not a crash). Empty file returns zeroed metrics.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

MANIFEST_PATH = HERE / "tasks" / "manifest.json"


# ---------------------------------------------------------------------------
# core scorers — pure functions, one operation each
# ---------------------------------------------------------------------------

def static_metrics(impl_path: Path) -> dict:
    """Return {loc, cc_avg, cc_max, fn_len_max, n_funcs} for *impl_path*.

    Raises:
        FileNotFoundError: if *impl_path* does not exist.
        ValueError: if the source cannot be parsed as Python.
    """
    # Defer radon import so callers get a clear ImportError if it's missing.
    from radon.raw import analyze  # noqa: PLC0415
    from radon.visitors import ComplexityVisitor  # noqa: PLC0415

    if not impl_path.exists():
        raise FileNotFoundError(f"impl not found: {impl_path}")

    src = impl_path.read_text(encoding="utf-8")

    # Empty file — return zeroed metrics, not an error.
    if not src.strip():
        return {"loc": 0, "cc_avg": 0.0, "cc_max": 0, "fn_len_max": 0, "n_funcs": 0}

    # LOC from radon raw analysis (physical line count including blanks + comments).
    try:
        raw = analyze(src)
    except Exception as exc:
        raise ValueError(f"radon raw analysis failed on {impl_path}: {exc}") from exc

    # Cyclomatic complexity and function length from ComplexityVisitor.
    # ComplexityVisitor.from_code raises SyntaxError on unparseable source.
    try:
        cv = ComplexityVisitor.from_code(src)
    except SyntaxError as exc:
        raise ValueError(f"syntax error in {impl_path}: {exc}") from exc

    functions = cv.functions  # includes top-level functions + methods

    if not functions:
        return {"loc": raw.loc, "cc_avg": 0.0, "cc_max": 0, "fn_len_max": 0, "n_funcs": 0}

    complexities = [f.complexity for f in functions]
    fn_lengths = [f.endline - f.lineno + 1 for f in functions]

    n = len(functions)
    cc_avg = round(sum(complexities) / n, 3)
    cc_max = max(complexities)
    fn_len_max = max(fn_lengths)

    return {
        "loc": raw.loc,
        "cc_avg": cc_avg,
        "cc_max": cc_max,
        "fn_len_max": fn_len_max,
        "n_funcs": n,
    }


def score_run_static(run_dir: Path) -> dict:
    """Score the impl file in *run_dir* and return the metrics dict.

    Looks up the task name from *run_dir*'s meta.json, resolves the impl
    filename from the manifest, then calls static_metrics.

    Returns metrics dict with all keys set, or sets all metric keys to None
    and adds status='unscorable' with a reason on any failure.
    """
    _UNSCORABLE_KEYS = ("loc", "cc_avg", "cc_max", "fn_len_max", "n_funcs")

    def _unscorable(reason: str) -> dict:
        return {k: None for k in _UNSCORABLE_KEYS} | {"status": "unscorable", "reason": reason}

    # Validate run_dir structure.
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

    impl_name = manifest[task]["impl"]
    impl_path = run_dir / "outputs" / impl_name

    if not impl_path.exists():
        return _unscorable(f"impl file missing: {impl_path.name}")

    try:
        metrics = static_metrics(impl_path)
    except (ValueError, FileNotFoundError) as exc:
        return _unscorable(f"static_metrics failed: {exc}")

    return metrics | {"status": meta.get("status", "unknown")}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Static metrics scorer")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--run-dir", help="run dir containing outputs/ and meta.json")
    group.add_argument("--impl", help="score a single impl file directly")
    args = ap.parse_args(argv)

    if args.impl:
        try:
            result = static_metrics(Path(args.impl))
        except (FileNotFoundError, ValueError) as exc:
            print(json.dumps({"status": "unscorable", "reason": str(exc)}))
            sys.exit(1)
    else:
        result = score_run_static(Path(args.run_dir))

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    _cli()
