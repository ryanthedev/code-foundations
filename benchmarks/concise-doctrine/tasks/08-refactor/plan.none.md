# Plan: refactor shipping-cost module

**Created:** 2026-06-19
**Status:** pending
**Complexity:** simple

---

## Context

A working shipping-cost module `shipping.py` is provided in your working directory (copy from `starter/shipping.py`). It computes correct costs but is hard to maintain. This is a refactor task: improve the module internal quality while preserving its EXACT observable behavior. The build agent under test produces `outputs/shipping.py` + `outputs/test_shipping.py`.

---

### Phase 1: Refactor shipping.py
**Model:** sonnet
**Gate:** Minimal
**Goal:** Refactor the provided `shipping.py` to improve its internal quality while preserving its exact observable behavior.

**What to build:**

The provided module exposes one function:

```python
def calc(weight, zone, speed, member):
    """Return the shipping cost. zone in {1,2,3}; speed in {"express","standard"}."""
```

Preserve the public function name `calc` and its positional parameter order (weight, zone, speed, member) — callers depend on them. Do not change what any valid input returns.

**Done when:**

- [ ] DW-8.1: `calc` returns the same cost as the original module for every valid input (zones 1-3, both speeds, all weight tiers). The function name `calc` and positional signature are unchanged.
- [ ] DW-8.2: A member (member=True) receives a 10% discount off the base cost; a non-member pays the base cost.

**Produces:**

- `outputs/shipping.py` — the refactored module (copy starter, then refactor)
- `outputs/test_shipping.py` — pytest suite (run and confirm passing before finishing)
