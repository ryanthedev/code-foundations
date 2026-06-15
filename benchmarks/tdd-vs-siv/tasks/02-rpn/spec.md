# Task: evaluate (Reverse Polish Notation)

Implement an RPN expression evaluator in Python. Apply the **build-doctrine** skill.

## What to build

A module `rpn.py` exposing one function:

```python
def evaluate(expr: str) -> float:
    """Evaluate a space-separated Reverse Polish Notation expression of integers."""
```

Operators: `+`, `-`, `*`, `/`.

## Done-When items

- DW-2.1: A well-formed RPN expression evaluates to its result. `evaluate("3 4 +")` -> `7`. The four operators `+ - * /` are supported.
- DW-2.2: An expression with too few operands for an operator raises `ValueError`. `evaluate("3 +")` -> `ValueError`.
- DW-2.3: An unknown token raises `ValueError`. `evaluate("3 4 %")` -> `ValueError`.

## Output paths

- Implementation: `outputs/rpn.py`
- Tests: `outputs/test_rpn.py` (pytest)

Run your tests and make sure they pass before finishing.
