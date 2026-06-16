"""run_matrix.py — detached-safe orchestrator for the concise-doctrine A/B matrix.

Drives the full grid: arms{baseline,concise} × tasks × models{sonnet,opus} × N runs.
For each cell it calls the Phase-3 runner (run_build.execute) then the Phase-4
aggregate scorer (score_all.score_one_run) and writes per-run rows to CSV.

Resumable/idempotent: a cell whose run dir already contains meta.json is skipped —
re-running the orchestrator after a partial failure picks up where it left off.

Safe to run detached (no interactive prompts; errors go to stderr; exit code
reflects completion status).

Setup (Python 3.12, detached run):
    uv venv .venv -p 3.12
    uv pip install --python .venv/bin/python pytest radon
    .venv/bin/python run_matrix.py --n-runs 5 --out results/

NOTE: Run with --rubric to enable the rubric (LLM readability) judge.  The
pre-registered verdict rule requires the readability dimension (rubric_score)
to produce a rule-valid GO/NO-GO verdict.  Without --rubric, rubric_score is
empty and the readability half of the verdict rule cannot be evaluated.

Dependencies: run_build (Phase 3), score_all (Phase 4), arms/swap (Phase 2).

CLI:
    run_matrix.py --n-runs <n> --out <root>
                  [--tasks <id>...]          # default: all manifest tasks
                  [--arms <arm>...]          # default: baseline concise
                  [--models <model>...]      # default: sonnet opus
                  [--dry-run]               # print cells, don't execute
                  [--score-only]            # re-score existing run dirs, no builds
                  [--rubric]                # enable rubric judge (LLM cost; required for rule-valid verdict)
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterator

HERE = Path(__file__).resolve().parent  # benchmarks/concise-doctrine
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_build as rb  # noqa: E402
from score_all import score_one_run, ROW_FIELDS  # noqa: E402
from score_rubric import _judge_subprocess  # noqa: E402
from arms import swap  # noqa: E402

# Default matrix dimensions (the full 2×6×2×N experiment).
_DEFAULT_ARMS = ("baseline", "concise")
_DEFAULT_MODELS = ("sonnet", "opus")


# --------------------------------------------------------------------------- #
# Configuration                                                                 #
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class MatrixSpec:
    """All coordinates + tunables for one matrix run.

    A config object so orchestrate() takes one parameter, not 7+.
    """

    tasks: tuple[str, ...]
    arms: tuple[str, ...]
    models: tuple[str, ...]
    n_runs: int
    out_root: Path          # where run dirs land (passed to run_build.execute)
    results_dir: Path       # where CSV files are written
    run_rubric: bool = False  # enable rubric judge (LLM cost; off by default)

    @staticmethod
    def build(
        n_runs: int,
        out_root: Path | str,
        *,
        tasks: tuple[str, ...] | None = None,
        arms: tuple[str, ...] | None = None,
        models: tuple[str, ...] | None = None,
        run_rubric: bool = False,
    ) -> "MatrixSpec":
        """Construct a MatrixSpec, defaulting missing dimensions.

        Validates arm names against swap.valid_arms() and n_runs > 0 at entry.

        Parameters
        ----------
        run_rubric: whether to invoke the rubric (LLM readability) judge for
            each cell.  Off by default to avoid LLM cost.  Required for a
            rule-valid verdict (the readability dimension of the pre-registered
            rule requires rubric_score to be populated).
        """
        if n_runs < 1:
            raise ValueError(f"n_runs must be >= 1, got {n_runs}")

        manifest_tasks = tuple(rb._manifest())
        resolved_tasks = tasks if tasks is not None else manifest_tasks
        for t in resolved_tasks:
            if t not in manifest_tasks:
                raise ValueError(f"unknown task {t!r}; expected one of {manifest_tasks}")

        resolved_arms = arms if arms is not None else _DEFAULT_ARMS
        valid = swap.valid_arms()
        for a in resolved_arms:
            if a not in valid:
                raise ValueError(f"unknown arm {a!r}; expected one of {valid}")

        resolved_models = models if models is not None else _DEFAULT_MODELS

        root = Path(out_root)
        return MatrixSpec(
            tasks=resolved_tasks,
            arms=resolved_arms,
            models=resolved_models,
            n_runs=n_runs,
            out_root=root,
            results_dir=root / "results",
            run_rubric=run_rubric,
        )


# --------------------------------------------------------------------------- #
# Pure helpers                                                                  #
# --------------------------------------------------------------------------- #

def iter_cells(spec: MatrixSpec) -> Iterator[tuple[str, str, str, int]]:
    """Yield (task, arm, model, run_n) for every cell in the matrix.

    run_n is 1-based (run-1 .. run-N) to match the run_build.py convention.
    Pure generator, no I/O.
    """
    for task, arm, model, run_n in itertools.product(
        spec.tasks, spec.arms, spec.models, range(1, spec.n_runs + 1)
    ):
        yield task, arm, model, run_n


def cell_run_dir(task: str, arm: str, model: str, run_n: int, out_root: Path) -> Path:
    """Pure path: <out_root>/<task>/<arm>/<model>/run-<n>. No I/O."""
    return out_root / task / arm / model / f"run-{run_n}"


def cell_is_done(run_dir: Path) -> bool:
    """Return True if this cell already has a meta.json (idempotent skip)."""
    return (run_dir / "meta.json").is_file()


# --------------------------------------------------------------------------- #
# Cell execution — the mockable seam                                           #
# --------------------------------------------------------------------------- #

def run_and_score_cell(
    task: str,
    arm: str,
    model: str,
    run_n: int,
    spec: MatrixSpec,
    *,
    judge_fn: Callable[[str], str] | None = None,
) -> dict:
    """Execute one cell: build → score → return a full-schema row dict.

    This is the primary mockable seam for unit tests. Tests inject a replacement
    for the entire function so no real builds or LLM calls happen.

    On any exception from the runner or scorer, returns an 'unscorable' row rather
    than crashing the orchestrator — one bad cell must not abort the matrix.

    Parameters
    ----------
    judge_fn: injectable seam for mocking the rubric subprocess in tests.
        Passed through to score_one_run only when spec.run_rubric is True.
        Defaults to None, which makes score_one_run use the real subprocess judge.
    """
    rspec = rb.RunSpec.validated(
        task=task, arm=arm, model=model, run=run_n,
        out_root=spec.out_root,
    )
    try:
        rd = rb.execute(rspec)
    except Exception as exc:  # noqa: BLE001
        # Runner failed entirely (e.g. provisioning error): record unscorable.
        print(f"  RUNNER ERROR {task}/{arm}/{model}/run-{run_n}: {exc}", file=sys.stderr)
        return _unscorable_row(task, arm, model, run_n, spec.out_root)

    score_kwargs: dict = {"run_rubric": spec.run_rubric}
    if judge_fn is not None:
        score_kwargs["judge_fn"] = judge_fn
    try:
        row = score_one_run(rd, spec.out_root, **score_kwargs)
    except Exception as exc:  # noqa: BLE001
        # Scorer failed: record unscorable but keep whatever the runner wrote.
        print(f"  SCORER ERROR {task}/{arm}/{model}/run-{run_n}: {exc}", file=sys.stderr)
        return _unscorable_row(task, arm, model, run_n, spec.out_root)

    return row


def score_only_cell(
    task: str,
    arm: str,
    model: str,
    run_n: int,
    spec: MatrixSpec,
    *,
    judge_fn: Callable[[str], str] | None = None,
) -> dict:
    """Score an already-executed cell without running the build.

    Used with --score-only to re-score existing run dirs.

    Parameters
    ----------
    judge_fn: injectable seam for mocking the rubric subprocess in tests.
        Passed through to score_one_run only when spec.run_rubric is True.
        Defaults to None, which makes score_one_run use the real subprocess judge.
    """
    rd = cell_run_dir(task, arm, model, run_n, spec.out_root)
    if not rd.is_dir():
        return _unscorable_row(task, arm, model, run_n, spec.out_root)
    score_kwargs: dict = {"run_rubric": spec.run_rubric}
    if judge_fn is not None:
        score_kwargs["judge_fn"] = judge_fn
    try:
        return score_one_run(rd, spec.out_root, **score_kwargs)
    except Exception as exc:  # noqa: BLE001
        print(f"  SCORER ERROR {task}/{arm}/{model}/run-{run_n}: {exc}", file=sys.stderr)
        return _unscorable_row(task, arm, model, run_n, spec.out_root)


def _unscorable_row(
    task: str, arm: str, model: str, run_n: int, out_root: Path
) -> dict:
    """Minimal row for a cell that could not be built or scored."""
    run_id = str(cell_run_dir(task, arm, model, run_n, out_root).relative_to(out_root))
    row: dict = {f: None for f in ROW_FIELDS}
    row["run_id"] = run_id
    row["task"] = task
    row["arm"] = arm
    row["model"] = model
    row["status"] = "unscorable"
    return row


# --------------------------------------------------------------------------- #
# Orchestrator                                                                  #
# --------------------------------------------------------------------------- #

CellFn = Callable[[str, str, str, int, MatrixSpec], dict]


def orchestrate(
    spec: MatrixSpec,
    cell_fn: CellFn = run_and_score_cell,
    *,
    dry_run: bool = False,
) -> list[dict]:
    """Drive the full matrix, skipping done cells, and return all rows.

    Parameters
    ----------
    spec:     the matrix dimensions and output paths.
    cell_fn:  injectable seam — default runs a real build + score; tests inject a mock.
    dry_run:  if True, print cells and return without executing or writing anything.
    """
    rows: list[dict] = []
    total = len(spec.tasks) * len(spec.arms) * len(spec.models) * spec.n_runs
    done = 0
    skipped = 0

    for task, arm, model, run_n in iter_cells(spec):
        rd = cell_run_dir(task, arm, model, run_n, spec.out_root)
        label = f"{task}/{arm}/{model}/run-{run_n}"

        if dry_run:
            if cell_is_done(rd):
                print(f"[dry-run] SKIP {label}")
            else:
                print(f"[dry-run] WOULD RUN {label}")
            continue

        if cell_is_done(rd):
            # Already scored: load the existing meta.json and produce a row.
            print(f"  skip (done) {label}")
            row = score_only_cell(task, arm, model, run_n, spec)
            rows.append(row)
            skipped += 1
            continue

        print(f"  run {done + skipped + 1}/{total} {label}")
        row = cell_fn(task, arm, model, run_n, spec)
        rows.append(row)
        done += 1

    if not dry_run:
        print(
            f"\norchestrate complete: {done} run(s), {skipped} skipped",
            file=sys.stderr,
        )

    return rows


# --------------------------------------------------------------------------- #
# CSV output                                                                    #
# --------------------------------------------------------------------------- #

def write_csv(rows: list[dict], path: Path) -> None:
    """Write per-run rows to a CSV using the Phase 4 ROW_FIELDS schema.

    Creates parent directories as needed. Overwrites an existing file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=ROW_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


# --------------------------------------------------------------------------- #
# Report generation                                                             #
# --------------------------------------------------------------------------- #

# Metrics that form the quality signal (lower = better for concise arm).
_QUALITY_METRICS = ("loc", "cc_avg", "cc_max", "fn_len_max")
# Metrics that are guardrail (must not regress below noise floor).
_GUARDRAIL_METRICS = ("hidden_dw", "hidden_offdw", "mutation")
# Noise floor: regression must exceed this threshold to count as real.
NOISE_THRESHOLD = 0.05


def load_rows(csv_path: Path) -> list[dict]:
    """Load per-run rows from a CSV into a list of dicts."""
    with open(csv_path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _to_float(val: object) -> float | None:
    """Convert a CSV string value to float, returning None for empty/null."""
    if val is None or str(val).strip() in ("", "None", "null"):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def compute_medians(rows: list[dict]) -> dict:
    """Return medians[arm][model][metric] for all numeric metrics.

    Only 'ok' runs contribute to quality medians (partial/unscorable excluded).
    All numeric fields in ROW_FIELDS are included; non-numeric fields are skipped.
    """
    numeric_fields = [
        f for f in ROW_FIELDS
        if f not in ("run_id", "task", "arm", "model", "status")
    ]

    # Group: medians[arm][model] -> {metric: [values]}
    buckets: dict[str, dict[str, dict[str, list[float]]]] = {}
    for row in rows:
        arm = row.get("arm") or "unknown"
        model = row.get("model") or "unknown"
        status = row.get("status", "")
        # Exclude unscorable from medians; include partial (partial artifact coverage).
        if status == "unscorable":
            continue
        buckets.setdefault(arm, {}).setdefault(model, {})
        for metric in numeric_fields:
            val = _to_float(row.get(metric))
            if val is not None:
                buckets[arm][model].setdefault(metric, []).append(val)

    medians: dict[str, dict[str, dict[str, float | None]]] = {}
    for arm, by_model in buckets.items():
        medians[arm] = {}
        for model, by_metric in by_model.items():
            medians[arm][model] = {}
            for metric, vals in by_metric.items():
                medians[arm][model][metric] = _median(vals)

    return medians


def _median(vals: list[float]) -> float | None:
    """Return the median of a non-empty list, or None."""
    if not vals:
        return None
    s = sorted(vals)
    n = len(s)
    mid = n // 2
    if n % 2 == 1:
        return s[mid]
    return round((s[mid - 1] + s[mid]) / 2, 4)


def compute_deltas(medians: dict, models: tuple[str, ...]) -> dict:
    """Return deltas[model][metric] = concise_median - baseline_median.

    A negative delta means the concise arm is lower (better for quality metrics).
    Returns None for a metric if either arm is missing data for that model.
    """
    deltas: dict[str, dict[str, float | None]] = {}
    for model in models:
        concise_vals = medians.get("concise", {}).get(model, {})
        baseline_vals = medians.get("baseline", {}).get(model, {})
        all_metrics = set(concise_vals) | set(baseline_vals)
        deltas[model] = {}
        for metric in all_metrics:
            c = concise_vals.get(metric)
            b = baseline_vals.get(metric)
            if c is not None and b is not None:
                deltas[model][metric] = round(c - b, 4)
            else:
                deltas[model][metric] = None
    return deltas


def check_guardrail(deltas: dict, models: tuple[str, ...]) -> tuple[bool, str]:
    """Check whether correctness + mutation do NOT regress beyond noise.

    Returns (passed: bool, rationale: str).
    Passed = True iff for every model, every guardrail metric delta is either
    None (no data) or >= -NOISE_THRESHOLD.
    """
    violations: list[str] = []
    for model in models:
        model_deltas = deltas.get(model, {})
        for metric in _GUARDRAIL_METRICS:
            delta = model_deltas.get(metric)
            if delta is not None and delta < -NOISE_THRESHOLD:
                violations.append(
                    f"{model}/{metric}: delta={delta:+.4f} (threshold={-NOISE_THRESHOLD:.2f})"
                )
    if violations:
        return False, "REGRESSION detected: " + "; ".join(violations)
    return True, "no regression beyond noise (threshold=0.05)"


def compute_verdict(
    medians: dict,
    deltas: dict,
    guardrail_passed: bool,
    models: tuple[str, ...],
) -> tuple[str, str]:
    """Apply the pre-registered verdict rule and return (verdict, rationale).

    GO iff:
      (1) quality_up: median LOC or cc_avg or cc_max decreases (concise < baseline)
          for >= 1 model, AND rubric_score concise >= baseline (equal-or-better readability)
      (2) guardrail_passed: correctness + mutation do not regress beyond noise

    NO-GO if either condition fails.
    Boundary: regression exactly at -NOISE_THRESHOLD resolves as NO-GO (strict).
    """
    if not guardrail_passed:
        return "NO-GO", (
            "correctness or mutation regressed beyond the noise threshold (0.05). "
            "Quality improvement is irrelevant when fault detection regresses."
        )

    # Check quality_up: any model shows improvement in at least one quality metric.
    quality_improved = False
    improved_notes: list[str] = []
    for model in models:
        model_deltas = deltas.get(model, {})
        for metric in _QUALITY_METRICS:
            delta = model_deltas.get(metric)
            # Negative delta = concise lower = improvement for quality metrics.
            if delta is not None and delta < 0:
                quality_improved = True
                improved_notes.append(f"{model}/{metric}: {delta:+.4f}")

    # Check rubric non-regression (concise rubric_score >= baseline).
    rubric_ok = True
    rubric_notes: list[str] = []
    for model in models:
        delta = deltas.get(model, {}).get("rubric_score")
        if delta is not None and delta < -NOISE_THRESHOLD:
            rubric_ok = False
            rubric_notes.append(f"{model}/rubric_score: {delta:+.4f}")

    if not quality_improved:
        return "NO-GO", (
            "no quality improvement detected: concise arm shows no reduction in "
            f"LOC/complexity metrics ({_QUALITY_METRICS}) across any model."
        )

    if not rubric_ok:
        return "NO-GO", (
            "readability regressed: rubric_score concise < baseline beyond noise threshold. "
            "Improvements in static metrics do not compensate for readability loss. "
            f"Rubric regressions: {'; '.join(rubric_notes)}"
        )

    # All conditions met: GO.
    rationale = (
        "quality improved (reduced LOC/complexity: "
        + ", ".join(improved_notes[:3])
        + (f" and {len(improved_notes)-3} more" if len(improved_notes) > 3 else "")
        + ") with no correctness or mutation regression and equal-or-better readability."
    )
    return "GO", rationale


def count_accounting(rows: list[dict]) -> dict:
    """Count N, partial, unscorable per (arm, model) cell.

    Returns accounting[arm][model] = {n, ok, partial, unscorable, all_partial}.
    all_partial is True when every run in the cell is partial (flag, never impute).
    """
    buckets: dict[str, dict[str, dict[str, int]]] = {}
    for row in rows:
        arm = row.get("arm") or "unknown"
        model = row.get("model") or "unknown"
        status = row.get("status", "unknown")
        cell = buckets.setdefault(arm, {}).setdefault(model, {
            "n": 0, "ok": 0, "partial": 0, "unscorable": 0
        })
        cell["n"] += 1
        if status == "ok":
            cell["ok"] += 1
        elif status == "partial":
            cell["partial"] += 1
        else:
            cell["unscorable"] += 1

    # Mark all-partial cells.
    accounting: dict[str, dict[str, dict]] = {}
    for arm, by_model in buckets.items():
        accounting[arm] = {}
        for model, counts in by_model.items():
            all_partial = (
                counts["partial"] > 0
                and counts["ok"] == 0
                and counts["unscorable"] == 0
            )
            accounting[arm][model] = counts | {"all_partial": all_partial}

    return accounting


def render_report(
    medians: dict,
    deltas: dict,
    guardrail_passed: bool,
    guardrail_rationale: str,
    verdict: str,
    verdict_rationale: str,
    accounting: dict,
    models: tuple[str, ...],
    arms: tuple[str, ...],
    n_runs: int,
    n_tasks: int,
) -> str:
    """Render the BRAG-style REPORT.md content as a string.

    Ends with 'VERDICT: GO | NO-GO — <rationale>' on the last line.
    """
    lines: list[str] = []

    lines += [
        "# Concise-Code Doctrine Benchmark — Results Report",
        "",
        f"**Arms:** {', '.join(arms)}  |  **Models:** {', '.join(models)}  "
        f"|  **N per cell:** {n_runs}  |  **Tasks:** {n_tasks}",
        "",
        "> **Caveats:** Small N (reported honestly). Results at this sample size may not",
        "> generalise; the report states medians and caveats rather than overclaiming.",
        "> Mutation score may saturate at 1.0 for well-specified tasks, limiting",
        "> upper-end discrimination. Rubric score is an LLM judgment and carries",
        "> additional variance; objective static + mutation metrics are the spine.",
        "",
    ]

    # ----- Run accounting -------------------------------------------------- #
    lines += ["## Run Accounting", ""]
    lines += [
        "| arm | model | N | ok | partial | unscorable | all-partial-flag |",
        "|-----|-------|---|----|---------|-----------:|-----------------|",
    ]
    has_all_partial = False
    for arm in arms:
        for model in models:
            cell = accounting.get(arm, {}).get(model, {
                "n": 0, "ok": 0, "partial": 0, "unscorable": 0, "all_partial": False
            })
            flag = "FLAG" if cell["all_partial"] else ""
            if cell["all_partial"]:
                has_all_partial = True
            lines.append(
                f"| {arm} | {model} | {cell['n']} | {cell['ok']} "
                f"| {cell['partial']} | {cell['unscorable']} | {flag} |"
            )
    lines.append("")

    if has_all_partial:
        lines += [
            "> **WARNING:** One or more cells are all-partial (every run is partial).",
            "> Medians for these cells exclude unscorable rows and may be based on",
            "> incomplete artifacts. These cells are NOT imputed — they are reported",
            "> as-is with a FLAG.",
            "",
        ]

    # ----- Median table per arm×model --------------------------------------- #
    lines += ["## Medians per Arm × Model", ""]

    numeric_fields = [
        f for f in ROW_FIELDS
        if f not in ("run_id", "task", "arm", "model", "status")
    ]
    col_header = " | ".join(["arm", "model"] + numeric_fields)
    col_sep = "|".join(["---"] * (len(numeric_fields) + 2))
    lines += [f"| {col_header} |", f"|{col_sep}|"]

    for arm in arms:
        for model in models:
            vals = medians.get(arm, {}).get(model, {})
            cells_str = " | ".join(
                _fmt(vals.get(m)) for m in numeric_fields
            )
            lines.append(f"| {arm} | {model} | {cells_str} |")
    lines.append("")

    # ----- Arm deltas ------------------------------------------------------- #
    lines += ["## Arm Deltas (concise − baseline)", ""]
    lines += [
        "> Negative = concise is lower (better for quality metrics).",
        "> Positive = concise is higher.",
        "",
    ]
    col_header_d = " | ".join(["model"] + numeric_fields)
    col_sep_d = "|".join(["---"] * (len(numeric_fields) + 1))
    lines += [f"| {col_header_d} |", f"|{col_sep_d}|"]

    for model in models:
        model_deltas = deltas.get(model, {})
        cells_str = " | ".join(
            _fmt(model_deltas.get(m)) for m in numeric_fields
        )
        lines.append(f"| {model} | {cells_str} |")
    lines.append("")

    # ----- Guardrail check -------------------------------------------------- #
    lines += ["## Guardrail: Correctness + Mutation Non-Regression", ""]
    guardrail_symbol = "PASS" if guardrail_passed else "FAIL"
    lines += [
        f"**Status: {guardrail_symbol}**",
        "",
        f"Noise threshold: {NOISE_THRESHOLD} (5 percentage points).",
        f"Result: {guardrail_rationale}",
        "",
    ]

    # ----- Verdict ---------------------------------------------------------- #
    lines += ["## Verdict", ""]
    lines += [
        "Pre-registered rule: GO iff concise arm shows quality improvement (lower LOC/",
        "complexity at equal-or-better readability via rubric) AND correctness + mutation",
        "do NOT regress beyond noise (threshold=0.05).",
        "",
        f"**{verdict}** — {verdict_rationale}",
        "",
    ]

    # Last line: machine-readable verdict tag (Phase 6 reads this).
    lines.append(f"VERDICT: {verdict} — {verdict_rationale}")

    return "\n".join(lines) + "\n"


def _fmt(val: object) -> str:
    """Format a median/delta value for the table."""
    if val is None:
        return "—"
    if isinstance(val, float):
        return f"{val:.4f}"
    return str(val)


def generate_report(
    csv_path: Path,
    out_path: Path,
    *,
    models: tuple[str, ...] = _DEFAULT_MODELS,
    arms: tuple[str, ...] = _DEFAULT_ARMS,
    n_runs: int | None = None,
    n_tasks: int | None = None,
) -> str:
    """Load rows from csv_path, compute all metrics, write REPORT.md to out_path.

    Returns the report content string (for testing without filesystem).
    """
    rows = load_rows(csv_path)

    # Infer n_runs and n_tasks from the data if not supplied.
    if n_tasks is None:
        n_tasks = len({r.get("task") for r in rows if r.get("task")})
    if n_runs is None:
        # Best estimate: max run count in any arm/model cell.
        from collections import Counter
        cell_counts: Counter = Counter(
            (r.get("arm"), r.get("model")) for r in rows
            if r.get("arm") and r.get("model")
        )
        n_runs = max(cell_counts.values()) if cell_counts else 0

    medians = compute_medians(rows)
    deltas = compute_deltas(medians, models)
    guardrail_passed, guardrail_rationale = check_guardrail(deltas, models)
    verdict, verdict_rationale = compute_verdict(
        medians, deltas, guardrail_passed, models
    )
    accounting = count_accounting(rows)

    content = render_report(
        medians=medians,
        deltas=deltas,
        guardrail_passed=guardrail_passed,
        guardrail_rationale=guardrail_rationale,
        verdict=verdict,
        verdict_rationale=verdict_rationale,
        accounting=accounting,
        models=models,
        arms=arms,
        n_runs=n_runs,
        n_tasks=n_tasks,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(content, encoding="utf-8")
    return content


# --------------------------------------------------------------------------- #
# CLI                                                                           #
# --------------------------------------------------------------------------- #

def _cli(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="run_matrix.py",
        description=(
            "Detached-safe orchestrator: drives arms×tasks×models×N-runs, "
            "scores each cell, writes results CSVs and REPORT.md."
        ),
    )
    ap.add_argument("--n-runs", type=int, required=True, help="runs per cell")
    ap.add_argument("--out", required=True, help="output root directory")
    ap.add_argument("--tasks", nargs="+", default=None, help="task IDs (default: all)")
    ap.add_argument("--arms", nargs="+", default=None, help="arm names (default: all)")
    ap.add_argument("--models", nargs="+", default=None, help="model names (default: all)")
    ap.add_argument("--dry-run", action="store_true", help="print cells, don't build")
    ap.add_argument("--score-only", action="store_true",
                    help="re-score existing run dirs without building")
    ap.add_argument("--report-only", action="store_true",
                    help="generate REPORT.md from existing CSV, no builds")
    ap.add_argument("--rubric", action="store_true", default=False,
                    help=(
                        "enable rubric (LLM readability) judge per cell (costs money). "
                        "Required for a rule-valid verdict — the pre-registered rule needs "
                        "rubric_score to evaluate the readability dimension."
                    ))
    args = ap.parse_args(argv)

    out_root = Path(args.out)

    # Build spec — validates inputs at the boundary.
    try:
        spec = MatrixSpec.build(
            n_runs=args.n_runs,
            out_root=out_root,
            tasks=tuple(args.tasks) if args.tasks else None,
            arms=tuple(args.arms) if args.arms else None,
            models=tuple(args.models) if args.models else None,
            run_rubric=args.rubric,
        )
    except ValueError as exc:
        ap.error(str(exc))
        return 2  # unreachable; ap.error() raises SystemExit

    csv_path = spec.results_dir / "matrix-runs.csv"
    report_path = out_root / "REPORT.md"

    if args.report_only:
        if not csv_path.exists():
            print(f"ERROR: CSV not found at {csv_path}", file=sys.stderr)
            return 2
        print(f"generating report from {csv_path} ...")
        generate_report(csv_path, report_path,
                        models=spec.models, arms=spec.arms,
                        n_runs=spec.n_runs, n_tasks=len(spec.tasks))
        print(f"wrote {report_path}")
        return 0

    # Choose cell function.
    cell_fn: CellFn = score_only_cell if args.score_only else run_and_score_cell

    print(
        f"matrix: {len(spec.tasks)} tasks × {len(spec.arms)} arms "
        f"× {len(spec.models)} models × {spec.n_runs} runs "
        f"= {len(spec.tasks)*len(spec.arms)*len(spec.models)*spec.n_runs} cells"
    )

    rows = orchestrate(spec, cell_fn, dry_run=args.dry_run)

    if args.dry_run:
        return 0

    # Write per-run CSV.
    write_csv(rows, csv_path)
    print(f"wrote {len(rows)} rows -> {csv_path}")

    # Generate the REPORT.md.
    generate_report(csv_path, report_path,
                    models=spec.models, arms=spec.arms,
                    n_runs=spec.n_runs, n_tasks=len(spec.tasks))
    print(f"wrote report -> {report_path}")

    # Exit code: 0 = all cells ok/partial, 1 = any cell failed.
    fail_count = sum(1 for r in rows if r.get("status") == "fail")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(_cli())
