"""Thin DW-only suite for task 06 _smoke calibration.

One test per DW item, no boundary/edge cases. Expected mutation score: < 1.0
(misses min-vs-max swap, mean arithmetic mutations, and multi-column selection).
"""
import pytest
from impl import summarize_column


def test_DW_6_1_basic_stats():
    result = summarize_column("score\n10\n20\n30", "score")
    assert result["min"] == 10.0
    assert result["max"] == 30.0
    assert result["mean"] == 20.0


def test_DW_6_2_no_data_rows_raises():
    with pytest.raises(ValueError):
        summarize_column("score\n", "score")


def test_DW_6_3_missing_column_raises():
    with pytest.raises(KeyError):
        summarize_column("score\n10", "grade")
