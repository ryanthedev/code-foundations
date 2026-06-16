# Plan: add per-item discounts to Inventory

**Created:** 2026-06-16
**Status:** pending
**Complexity:** simple

---

## Context

Extend an existing Inventory module to support per-item discounts. This is a MODIFY-EXISTING benchmark task for the concise-code-doctrine A/B evaluation. The build agent under test modifies `inventory.py` (provided in `starter/`) and produces `outputs/inventory.py` + `outputs/test_inventory.py`.

---

### Phase 1: Add discount support to Inventory
**Model:** sonnet
**Gate:** Standard

**Goal:** Modify the provided `inventory.py` (copy from `starter/inventory.py`) to add per-item discount support.

**What to build:**

An existing module `inventory.py` is provided in your working directory with this interface:

```python
class Inventory:
    def __init__(self): ...
    def add_item(self, name, price, qty): ...
    def remove_item(self, name): ...
    def total_value(self): ...
```

Add per-item discount support.

**Done when:**

- [ ] DW-3.1: `add_item` gains an optional `discount` parameter — a fraction in `[0, 1]`, default `0`. `total_value` applies it per item: a $10 item with qty 2 and `discount=0.1` contributes `10 * 2 * (1 - 0.1) = 18.0`.
- [ ] DW-3.2: `total_value` sums the discounted value across all items. With items `("a", 10, 2, discount=0.1)` and `("b", 5, 4, discount=0)`, `total_value()` is `18.0 + 20.0 = 38.0`.

**Produces:**

- `outputs/inventory.py` — the full modified module (copy starter, then modify)
- `outputs/test_inventory.py` — pytest suite (run and confirm passing before finishing)
