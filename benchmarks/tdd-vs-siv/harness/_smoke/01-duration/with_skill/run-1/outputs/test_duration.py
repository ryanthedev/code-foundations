"""Thorough suite — DW items plus discovered edges (simulates the SIV arm)."""
import pytest
from duration import parse_duration


def test_DW_1_1_hours_minutes():
    assert parse_duration("1h30m") == 5400

def test_DW_1_1_seconds():
    assert parse_duration("45s") == 45

def test_DW_1_1_hours_only():
    assert parse_duration("2h") == 7200

def test_DW_1_2_bare_number():
    with pytest.raises(ValueError):
        parse_duration("90")

def test_DW_1_3_empty():
    with pytest.raises(ValueError):
        parse_duration("")

def test_all_three_units():
    assert parse_duration("1h2m3s") == 3723

def test_zero_seconds():
    assert parse_duration("0s") == 0

def test_case_insensitive():
    assert parse_duration("1H") == 3600

def test_garbage_rejected():
    with pytest.raises(ValueError):
        parse_duration("1h!x")
