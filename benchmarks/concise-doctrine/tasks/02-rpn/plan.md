# Plan: evaluate (Reverse Polish Notation)

**Created:** 2026-06-16
**Status:** pending
**Complexity:** simple

---

## Context

Implement an RPN expression evaluator in Python. This is a benchmark task for the concise-code-doctrine A/B evaluation. The build agent under test produces `outputs/rpn.py` + `outputs/test_rpn.py`.

---

### Phase 1: Implement RPN evaluate
**Model:** sonnet
**Gate:** Standard

**Goal:** Implement a module `rpn.py` exposing one function that evaluates space-separated Reverse Polish Notation expressions.

**What to build:**

A module `rpn.py` exposing one function:

```python
def evaluate(expr: str) -> float:
    """Evaluate a space-separated Reverse Polish Notation expression of integers."""
```

Operators: `+`, `-`, `*`, `/`.

**Done when:**

- [ ] DW-2.1: A well-formed RPN expression evaluates to its result. `evaluate("3 4 +")` → `7`. The four operators `+ - * /` are supported.
- [ ] DW-2.2: An expression with too few operands for an operator raises `ValueError`. `evaluate("3 +")` → `ValueError`.
- [ ] DW-2.3: An unknown token raises `ValueError`. `evaluate("3 4 %")` → `ValueError`.

**Produces:**

- `outputs/rpn.py` — the implementation module
- `outputs/test_rpn.py` — pytest suite (run and confirm passing before finishing)
