"""Thorough suite for task 06 _smoke calibration.

DW items + boundary cases that kill all 4 mutants.
Expected mutation score: 1.0 on the reference impl.

Mutation surface:
  Site 0: or/and in fieldnames check  → killed by test_DW_6_3 (KeyError on valid column)
  Site 1: == 0 → == 1 in empty-check  → killed by test_single_row (1 row, should succeed)
  Site 2: == 0 → != 0 in empty-check  → killed by test_DW_6_2 (0 rows should raise)
  Site 3: / → * in mean arithmetic    → killed by test_mean_differs_from_min_and_max
"""
import pytest
from impl import summarize_column


def test_DW_6_1_basic_stats():
    result = summarize_column("score\n10\n20\n30", "score")
    assert result["min"] == 10.0
    assert result["max"] == 30.0
    assert result["mean"] == 20.0


def test_DW_6_2_no_data_rows_raises():
    # Kills site 2 (== 0 → != 0): if not-equal, non-empty list raises → wrong.
    with pytest.raises(ValueError):
        summarize_column("score\n", "score")


def test_DW_6_3_missing_column_raises():
    # Kills site 0 (or → and): fieldnames and [] → [] → column never in [] → always raises.
    with pytest.raises(KeyError):
        summarize_column("score\n10", "grade")


def test_single_row_succeeds():
    # Kills site 1 (== 0 → == 1): single row would raise ValueError with mutation.
    result = summarize_column("val\n42", "val")
    assert result["min"] == 42.0
    assert result["max"] == 42.0
    assert result["mean"] == 42.0


def test_mean_differs_from_min_and_max():
    # Kills site 3 (/ → *): mean=sum*len would be wrong (1+2+3+4)*4=40 not 2.5.
    result = summarize_column("n\n1\n2\n3\n4", "n")
    assert result["mean"] == 2.5
    assert result["mean"] != result["min"]
    assert result["mean"] != result["max"]


def test_min_is_not_max():
    # Verifies min/max distinction (no specific mutation site, but correctness).
    result = summarize_column("x\n1\n100", "x")
    assert result["min"] == 1.0
    assert result["max"] == 100.0


def test_multi_column_selects_correct_one():
    csv = "a,b,c\n1,10,100\n2,20,200"
    result = summarize_column(csv, "b")
    assert result["min"] == 10.0
    assert result["max"] == 20.0
    assert result["mean"] == 15.0
