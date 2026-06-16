# Plan: CSV column statistics

**Created:** 2026-06-16
**Status:** pending
**Complexity:** simple

---

## Context

Implement a CSV statistics function in Python. This is a greenfield benchmark task for the concise-code-doctrine A/B evaluation. The build agent under test produces `outputs/csv_stats.py` + `outputs/test_csv_stats.py`.

---

### Phase 1: Implement summarize_column
**Model:** sonnet
**Gate:** Standard

**Goal:** Implement a module `csv_stats.py` exposing one function that parses a CSV string and returns min/max/mean for a named column.

**What to build:**

A module `csv_stats.py` exposing one function:

```python
def summarize_column(csv_text: str, column: str) -> dict:
    """Parse csv_text and return {"min": float, "max": float, "mean": float}
    for the values in the named column.

    csv_text — a CSV string with a header row.
    column   — the name of the column to summarize.

    Raises KeyError if column does not exist in the header.
    Raises ValueError if there are no data rows (header only).
    Values are converted to float; non-numeric values raise ValueError.
    """
```

**Done when:**

- [ ] DW-6.1: A CSV with a header and numeric data rows returns the correct `min`, `max`, and `mean`. For the input `"score\n10\n20\n30"` with `column="score"`: `{"min": 10.0, "max": 30.0, "mean": 20.0}`.
- [ ] DW-6.2: A CSV with a header row but no data rows raises `ValueError`. `summarize_column("score\n", "score")` → `ValueError`.
- [ ] DW-6.3: A column name not present in the header raises `KeyError`. `summarize_column("score\n10", "grade")` → `KeyError`.

**Produces:**

- `outputs/csv_stats.py` — the implementation module
- `outputs/test_csv_stats.py` — pytest suite (run and confirm passing before finishing)
