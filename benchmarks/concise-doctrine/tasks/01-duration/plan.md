# Plan: parse_duration

**Created:** 2026-06-16
**Status:** pending
**Complexity:** simple

---

## Context

Implement a duration parser in Python. This is a benchmark task for the concise-code-doctrine A/B evaluation. The build agent under test produces `outputs/duration.py` + `outputs/test_duration.py`.

---

### Phase 1: Implement parse_duration
**Model:** sonnet
**Gate:** Standard

**Goal:** Implement a module `duration.py` exposing one function that parses human-readable duration strings into total seconds.

**What to build:**

A module `duration.py` exposing one function:

```python
def parse_duration(s: str) -> int:
    """Parse a duration string like "1h30m" into a total number of seconds."""
```

Units: `h` (hours), `m` (minutes), `s` (seconds).

**Done when:**

- [ ] DW-1.1: A string of unit-tagged numbers parses to the summed total in seconds. `"1h30m"` → `5400`, `"45s"` → `45`, `"2h"` → `7200`.
- [ ] DW-1.2: A bare number with no unit is invalid → raise `ValueError`. `"90"` → `ValueError`.
- [ ] DW-1.3: An empty string is invalid → raise `ValueError`. `""` → `ValueError`.

**Produces:**

- `outputs/duration.py` — the implementation module
- `outputs/test_duration.py` — pytest suite (run and confirm passing before finishing)
