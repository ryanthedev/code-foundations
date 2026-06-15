# Task: add per-item discounts to Inventory

Apply the **build-doctrine** skill. This is a MODIFY-EXISTING task.

An existing module `inventory.py` is provided in your working directory:

```python
class Inventory:
    def __init__(self): ...
    def add_item(self, name, price, qty): ...
    def remove_item(self, name): ...
    def total_value(self): ...
```

Add per-item discount support.

## Done-When items

- DW-3.1: `add_item` gains an optional `discount` parameter — a fraction in `[0, 1]`, default `0`. `total_value` applies it per item: a $10 item with qty 2 and `discount=0.1` contributes `10 * 2 * (1 - 0.1) = 18.0`.
- DW-3.2: `total_value` sums the discounted value across all items. With items `("a", 10, 2, discount=0.1)` and `("b", 5, 4, discount=0)`, `total_value()` is `18.0 + 20.0 = 38.0`.

## Output paths

- Implementation: `outputs/inventory.py` (the full modified module)
- Tests: `outputs/test_inventory.py` (pytest)

Run your tests and make sure they pass before finishing.
