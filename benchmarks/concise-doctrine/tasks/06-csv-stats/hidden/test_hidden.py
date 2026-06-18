"""Hidden ground-truth suite for task 06 (csv_stats). Never shown to the agent.

  test_dw_*    — behaviors the spec's Done-When items state or exemplify
  test_offdw_* — boundary and edge behaviors the spec did not exemplify

Mutation surface targeted by test_offdw_*:
  - min vs max confusion (arithmetic mutation swaps comparisons)
  - mean arithmetic: sum / len — mutation changes + to - or * to /
  - off-by-one: single-row CSV (min == max == mean)
  - whitespace/blank-line handling in CSV rows
  - multi-column CSV (correct column selected, not first or last)
"""
import pytest
from csv_stats import summarize_column


# ---- DW-stated behavior ----------------------------------------------------

def test_dw_basic_three_rows():
    result = summarize_column("score\n10\n20\n30", "score")
    assert result["min"] == 10.0
    assert result["max"] == 30.0
    assert result["mean"] == 20.0

def test_dw_no_data_rows_raises_value_error():
    with pytest.raises(ValueError):
        summarize_column("score\n", "score")

def test_dw_missing_column_raises_key_error():
    with pytest.raises(KeyError):
        summarize_column("score\n10", "grade")


# ---- Off-DW: boundary and edge behaviors -----------------------------------

def test_offdw_single_row_min_max_mean_equal():
    # Single data row: min == max == mean == that value.
    # Catches min/max confusion (if swapped, all three are still equal — but
    # combined with test_dw_basic they will catch it).
    result = summarize_column("val\n42", "val")
    assert result["min"] == 42.0
    assert result["max"] == 42.0
    assert result["mean"] == 42.0

def test_offdw_min_is_not_max():
    # Two distinct values: explicitly checks min < max.
    # Kills min-vs-max swap mutation.
    result = summarize_column("x\n1\n100", "x")
    assert result["min"] == 1.0
    assert result["max"] == 100.0

def test_offdw_mean_is_not_min_or_max():
    # Four values where mean differs from both min and max.
    # Kills mean-computed-as-min or mean-computed-as-max mutation.
    result = summarize_column("n\n1\n2\n3\n4", "n")
    assert result["mean"] == 2.5
    assert result["mean"] != result["min"]
    assert result["mean"] != result["max"]

def test_offdw_multi_column_correct_column_selected():
    # CSV has multiple columns; only the named one is summarized.
    # Kills "always use first column" or "always use last column" mutations.
    csv = "a,b,c\n1,10,100\n2,20,200"
    result = summarize_column(csv, "b")
    assert result["min"] == 10.0
    assert result["max"] == 20.0
    assert result["mean"] == 15.0

def test_offdw_negative_values():
    # Negative values: min is negative, mean may be negative.
    result = summarize_column("v\n-5\n0\n5", "v")
    assert result["min"] == -5.0
    assert result["max"] == 5.0
    assert result["mean"] == 0.0

def test_offdw_float_values():
    # Floating-point input values round-tripped through float() correctly.
    result = summarize_column("p\n1.5\n2.5\n3.0", "p")
    assert result["min"] == 1.5
    assert result["max"] == 3.0
    assert abs(result["mean"] - 2.333333) < 0.0001

def test_offdw_header_only_no_newline_raises():
    # Header with no trailing newline and no data rows still raises ValueError.
    with pytest.raises(ValueError):
        summarize_column("score", "score")
