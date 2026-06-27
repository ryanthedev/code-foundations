# Plan: a Counter

**Created:** 2026-06-22
**Status:** pending
**Complexity:** simple

---

## Context

Implement a simple counter in Python. The build agent under test produces
`outputs/counter.py` + `outputs/test_counter.py`.

---

### Phase 1: Implement Counter
**Model:** sonnet
**Gate:** Minimal

**Goal:** Implement a module `counter.py` with a `Counter` class.

**What to build:**

A module `counter.py` exposing one class:

```python
class Counter:
    def __init__(self) -> None:
        """A counter that starts at zero."""

    def increment(self) -> None:
        """Increase the count by one."""

    @property
    def value(self) -> int:
        """The current count."""
```

**Done when:**

- [ ] DW-11.1: A new `Counter` has `value == 0`.
- [ ] DW-11.2: Each call to `increment()` raises `value` by exactly one (e.g. three calls → `value == 3`).

**Produces:**

- `outputs/counter.py` — the implementation module
- `outputs/test_counter.py` — pytest suite (run and confirm passing before finishing)
