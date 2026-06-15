"""Hidden ground-truth suite for task 04 (password validation). Never shown.

  test_dw_*    — the new digit/uppercase rules the spec states
  test_offdw_* — preserved length rule + combined edges the spec did not exemplify
"""
from password import validate


# ---- DW-stated new behavior ------------------------------------------------

def test_dw_requires_digit():
    assert validate("Password") is False     # 8+ chars, upper, no digit

def test_dw_requires_uppercase():
    assert validate("password1") is False     # 8+ chars, digit, no upper

def test_dw_valid_password():
    assert validate("Password1") is True      # 8+ chars, upper, digit


# ---- Off-DW: preserved length rule + combined edges ------------------------

def test_offdw_length_rule_preserved():
    assert validate("Pass1") is False         # has upper+digit but < 8 chars

def test_offdw_empty_string():
    assert validate("") is False

def test_offdw_exactly_eight_valid():
    assert validate("Passwor1") is True       # exactly 8, upper, digit

def test_offdw_all_digits_no_upper():
    assert validate("12345678") is False      # 8+, digit, but no uppercase

def test_offdw_long_valid():
    assert validate("MyServerPassword2024") is True
