"""Hidden ground-truth suite for task 02 (RPN evaluate). Never shown to the agent.

  test_dw_*    — behaviors the spec's Done-When items state or exemplify
  test_offdw_* — UNAMBIGUOUS RPN behaviors the spec did not exemplify
"""
import pytest
from rpn import evaluate


# ---- DW-stated behavior ----------------------------------------------------

def test_dw_addition():
    assert evaluate("3 4 +") == 7

def test_dw_too_few_operands():
    with pytest.raises(ValueError):
        evaluate("3 +")

def test_dw_unknown_token():
    with pytest.raises(ValueError):
        evaluate("3 4 %")


# ---- Off-DW but unambiguous standard RPN -----------------------------------

def test_offdw_subtraction_is_order_sensitive():
    assert evaluate("10 3 -") == 7

def test_offdw_multiplication():
    assert evaluate("6 7 *") == 42

def test_offdw_exact_division():
    assert evaluate("12 4 /") == 3

def test_offdw_chained_operators():
    assert evaluate("2 3 4 * +") == 14

def test_offdw_negative_result():
    assert evaluate("3 5 -") == -2

def test_offdw_leftover_operands_invalid():
    # more than one value remains on the stack -> malformed
    with pytest.raises(ValueError):
        evaluate("1 2 3 +")

def test_offdw_division_by_zero():
    with pytest.raises((ZeroDivisionError, ValueError)):
        evaluate("5 0 /")
