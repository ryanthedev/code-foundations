# Plan: pair-sum check

**Created:** 2026-06-22
**Status:** pending
**Complexity:** simple

---

## Context

Implement a function that reports whether any two distinct elements of a list sum
to a target. The build agent under test produces `outputs/pairsum.py` +
`outputs/test_pairsum.py`.

---

### Phase 1: Implement has_pair_sum
**Model:** sonnet
**Gate:** Minimal

**Goal:** Implement a module `pairsum.py` exposing one function.

**What to build:**

```python
def has_pair_sum(nums: list[int], target: int) -> bool:
    """Return True if any two DISTINCT elements of nums sum to target."""
```

**Done when:**

- [ ] DW-12.1: Returns True when two distinct elements sum to target (`has_pair_sum([1,2,3], 5)` → True).
- [ ] DW-12.2: Returns False when no two distinct elements sum to target (`has_pair_sum([1,2,3], 100)` → False).
- [ ] DW-12.3: Returns False for an empty list or a single element.

**Produces:**

- `outputs/pairsum.py` — the implementation module
- `outputs/test_pairsum.py` — pytest suite (run and confirm passing before finishing)
