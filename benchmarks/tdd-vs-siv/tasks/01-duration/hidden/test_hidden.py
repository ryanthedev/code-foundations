"""Hidden ground-truth suite for task 01 (parse_duration). Never shown to the agent.

Test buckets (by name prefix):
  test_dw_*    — behaviors derivable from the spec's Done-When items
  test_offdw_* — conventional edge behaviors the spec did NOT enumerate
"""
import pytest
from duration import parse_duration


# ---- DW-derivable behavior -------------------------------------------------

def test_dw_hours_minutes():
    assert parse_duration("1h30m") == 5400

def test_dw_seconds():
    assert parse_duration("45s") == 45

def test_dw_hours_only():
    assert parse_duration("2h") == 7200

def test_dw_bare_number_invalid():
    with pytest.raises(ValueError):
        parse_duration("90")

def test_dw_empty_invalid():
    with pytest.raises(ValueError):
        parse_duration("")

def test_dw_all_three_units():
    assert parse_duration("1h2m3s") == 3723


# ---- Off-DW conventional edges (NOT in the spec) ---------------------------

def test_offdw_surrounding_whitespace_stripped():
    assert parse_duration("  1h  ") == 3600

def test_offdw_case_insensitive():
    assert parse_duration("1H") == 3600

def test_offdw_order_independent():
    assert parse_duration("30m1h") == 5400

def test_offdw_zero_is_valid():
    assert parse_duration("0s") == 0

def test_offdw_garbage_token_invalid():
    with pytest.raises(ValueError):
        parse_duration("1h!x")
