"""Thin DW-only suite (simulates the TDD arm scoped to Done-When items)."""
from duration import parse_duration


def test_DW_1_1_parses():
    assert parse_duration("1h30m") == 5400

def test_DW_1_2_bare_number_invalid():
    try:
        parse_duration("90")
        assert False
    except ValueError:
        pass

def test_DW_1_3_empty_invalid():
    try:
        parse_duration("")
        assert False
    except ValueError:
        pass
