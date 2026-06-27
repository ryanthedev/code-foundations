"""Objective adversarial-robustness probe for the password-validator task.

Why this exists: the LLM adherence rubric saturated (~0.9 with AND without the
cc-defensive-programming skill) and mis-applied GC-2 — it flagged "no assertions"
as a violation on boundary-validation code where the skill itself (GC-3/RF-9) says
assertions DON'T belong. This probe replaces that judgment with a deterministic
behavioral test: feed each implementation genuinely hostile inputs and classify the
outcome. No LLM, no ceiling.

Outcome classes per hostile input:
  GRACEFUL  — returns a bool, OR raises a deliberate, documented error
              (TypeError / ValueError). The code anticipated the input.
  CRASH     — raises anything else (AttributeError, KeyError, IndexError, a
              non-deliberate TypeError from an unguarded `len(None)`, etc.).
              The code did NOT defend against the input.

robustness = graceful / total. A defensively-written validator guards its input
type at the boundary, so `validate(None)` raises a clean TypeError rather than
crashing inside `len()`. That is exactly the GC-1 behavior the skill targets — and
it is observable without an LLM.

CLI:
  probe_defense.py --root results-adherence            # aggregate with vs without
  probe_defense.py --impl path/to/password.py          # one file
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics as st
import sys
import uuid
from pathlib import Path

# Hostile inputs the Done-When items never mention. A defensive validator should
# handle each WITHOUT an incidental crash — either by returning a bool or by
# raising a deliberate TypeError/ValueError at its boundary.
_HOSTILE = [
    ("none", None),
    ("int", 12345678),
    ("bytes", b"Password1"),
    ("list", ["P", "a", "s", "s", "1", "A", "x", "y"]),
    ("dict", {"pw": "Password1"}),
    ("empty", ""),
    ("whitespace", " " * 12),
    ("very_long", "Aa1" + "x" * 100_000),
    ("null_byte", "Passw0rd\x00A"),
    ("unicode", "Pâsswörd1Ä"),
    ("newline", "Password1\n"),
    ("bool", True),
]

# A deliberate, boundary-level rejection. Anything else raised = an undefended crash.
_DELIBERATE = (TypeError, ValueError)


def _load_validate(impl_path: Path):
    """Import the impl module in isolation and return its `validate` callable."""
    mod_name = f"_probe_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(mod_name, impl_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {impl_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "validate"):
        raise AttributeError(f"{impl_path} has no validate()")
    return mod.validate


def probe_impl(impl_path: Path) -> dict:
    """Return {robustness, graceful, total, crashes:[(label, exc_type)]} for one impl."""
    validate = _load_validate(impl_path)
    graceful = 0
    crashes = []
    for label, value in _HOSTILE:
        try:
            result = validate(value)
            if isinstance(result, bool):
                graceful += 1
            else:
                # Returned a non-bool (e.g. None) — not a clean validator contract.
                crashes.append((label, f"non-bool:{type(result).__name__}"))
        except _DELIBERATE:
            graceful += 1  # deliberate boundary rejection — defended
        except Exception as exc:  # noqa: BLE001 — classification, not handling
            crashes.append((label, type(exc).__name__))
    total = len(_HOSTILE)
    return {
        "robustness": round(graceful / total, 3),
        "graceful": graceful,
        "total": total,
        "crashes": crashes,
    }


def _impls_for_task(root: Path, task: str) -> list[Path]:
    return sorted(p / "outputs" / "password.py"
                  for p in (root / task).glob("*/*/run-*")
                  if (p / "outputs" / "password.py").is_file())


def aggregate(root: Path) -> dict:
    """Probe the with-skill and without-skill password impls under *root*."""
    out = {}
    for cond, task in (("with_skill", "adh-def-with"), ("without_skill", "adh-def-none")):
        scores, all_crashes = [], []
        for impl in _impls_for_task(root, task):
            r = probe_impl(impl)
            scores.append(r["robustness"])
            all_crashes += [c[0] for c in r["crashes"]]
        out[cond] = {
            "n": len(scores),
            "robustness_mean": round(st.mean(scores), 3) if scores else None,
            "per_run": scores,
            "crash_inputs": sorted(set(all_crashes)),
        }
    a, b = out.get("with_skill", {}), out.get("without_skill", {})
    if a.get("robustness_mean") is not None and b.get("robustness_mean") is not None:
        out["delta_with_minus_without"] = round(a["robustness_mean"] - b["robustness_mean"], 3)
    return out


def _cli(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Objective adversarial-robustness probe")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--root", help="results root containing adh-def-with / adh-def-none")
    g.add_argument("--impl", help="probe a single password.py")
    args = ap.parse_args(argv)
    if args.impl:
        print(json.dumps(probe_impl(Path(args.impl)), indent=2))
    else:
        print(json.dumps(aggregate(Path(args.root)), indent=2))


if __name__ == "__main__":
    _cli()
