# Plan: refactor the theatrical-players statement

**Created:** 2026-06-22
**Status:** pending
**Complexity:** simple

---

## Context

A working `statement.py` is provided (copy from `starter/`). The `statement`
function produces a correct billing statement string but tangles amount
calculation, volume-credit logic, and string formatting in one function. Refactor
it to improve its internal quality while preserving its EXACT output. The build
agent under test produces `outputs/statement.py` + `outputs/test_statement.py`.

---

### Phase 1: Refactor statement()
**Model:** sonnet
**Gate:** Minimal

**Goal:** Refactor `statement` to improve its internal quality while preserving its
exact observable output.

**What to build:**

The module exposes one function:

```python
def statement(invoice, plays):
    """Return the formatted billing statement string."""
```

Preserve the public function name `statement` and its `(invoice, plays)` signature,
and do not change the output string for any input. (`invoice` is a dict with
`customer` and `performances`; `plays` maps playID → {name, type} where type is
"tragedy" or "comedy".)

**Done when:**

- [ ] DW-10.1: `statement(invoice, plays)` returns the same string as the original for the standard invoice and for varied audiences, play mixes, and boundary sizes.
- [ ] DW-10.2: An unknown play type still raises `ValueError`.

**Produces:**

- `outputs/statement.py` — the refactored module (copy starter, then refactor)
- `outputs/test_statement.py` — pytest suite (run and confirm passing before finishing)
