"""Tests for duration.parse_duration.

DW-1.1: unit-tagged strings sum correctly.
DW-1.2: bare numbers raise ValueError.
DW-1.3: empty string raises ValueError.
"""

import pytest
from outputs.duration import parse_duration


# ---------------------------------------------------------------------------
# DW-1.1  Happy-path: unit-tagged numbers parse to the correct total seconds
# ---------------------------------------------------------------------------

def test_DW_1_1_combined_units():
    """'1h30m' -> 3600 + 1800 = 5400."""
    assert parse_duration("1h30m") == 5400


def test_DW_1_1_seconds_only():
    """'45s' -> 45."""
    assert parse_duration("45s") == 45


def test_DW_1_1_hours_only():
    """'2h' -> 7200."""
    assert parse_duration("2h") == 7200


# ---------------------------------------------------------------------------
# DW-1.2  Bare number with no unit raises ValueError
# ---------------------------------------------------------------------------

def test_DW_1_2_bare_number_raises():
    with pytest.raises(ValueError):
        parse_duration("90")


# ---------------------------------------------------------------------------
# DW-1.3  Empty string raises ValueError
# ---------------------------------------------------------------------------

def test_DW_1_3_empty_string_raises():
    with pytest.raises(ValueError):
        parse_duration("")


# ---------------------------------------------------------------------------
# Additional edge-case and boundary tests
# ---------------------------------------------------------------------------

def test_minutes_only():
    """Pure minutes input."""
    assert parse_duration("30m") == 1800


def test_all_three_units():
    """Hours + minutes + seconds combined."""
    assert parse_duration("1h1m1s") == 3661


def test_zero_valued_unit():
    """Zero hours is a valid tagged token: '0h' -> 0."""
    assert parse_duration("0h") == 0


def test_large_value():
    """Large number of seconds parsed correctly."""
    assert parse_duration("3600s") == 3600


def test_only_whitespace_raises():
    """A string of spaces has no tokens -> ValueError."""
    with pytest.raises(ValueError):
        parse_duration("   ")


def test_unknown_unit_raises():
    """A tagged number with an unrecognised unit has no valid tokens -> ValueError."""
    with pytest.raises(ValueError):
        parse_duration("5d")


def test_bare_float_raises():
    """A decimal number with no unit -> ValueError."""
    with pytest.raises(ValueError):
        parse_duration("1.5")


def test_repeated_unit():
    """Two hour tokens are both counted: '1h2h' -> 3*3600."""
    assert parse_duration("1h2h") == 10800


def test_order_independence():
    """Units may appear in any order: 'm' before 'h'."""
    assert parse_duration("30m1h") == 5400
