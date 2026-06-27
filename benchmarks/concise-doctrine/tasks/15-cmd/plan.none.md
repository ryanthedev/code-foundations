# Plan: line counter

**Created:** 2026-06-22
**Status:** pending
**Complexity:** simple

---

## Context

Implement a helper that counts the number of lines in a file. The build agent
under test produces `outputs/line_counter.py` + `outputs/test_line_counter.py`.

---

### Phase 1: Implement count_lines
**Model:** sonnet
**Gate:** Minimal

**Goal:** Implement a module `line_counter.py` exposing one function.

**What to build:**

```python
def count_lines(filename):
    """Return the number of lines in the file `filename` (in the current directory)."""
```

**Done when:**

- [ ] DW-15.1: Returns the correct line count for a file (e.g. a 3-line file returns 3).
- [ ] DW-15.2: Returns 0 for an empty file.

**Produces:**

- `outputs/line_counter.py` — the implementation module
- `outputs/test_line_counter.py` — pytest suite (run and confirm passing before finishing)
