"""Tests for doc_reader.py"""

import os
import pytest

from doc_reader import read_doc


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def doc_dir(tmp_path):
    """A temporary directory with a few pre-written documents."""
    (tmp_path / "doc1.txt").write_text("Hello, world!", encoding="utf-8")
    (tmp_path / "doc2.txt").write_text("Line 1\nLine 2\nLine 3", encoding="utf-8")
    (tmp_path / "empty.txt").write_text("", encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# DW-14.1 — returns contents of a document that exists in base_dir
# ---------------------------------------------------------------------------

def test_DW_14_1_returns_doc_contents(doc_dir):
    result = read_doc(str(doc_dir), "doc1.txt")
    assert result == "Hello, world!"


def test_DW_14_1_returns_multiline_doc_contents(doc_dir):
    result = read_doc(str(doc_dir), "doc2.txt")
    assert result == "Line 1\nLine 2\nLine 3"


# ---------------------------------------------------------------------------
# Additional coverage: edge cases and error paths
# ---------------------------------------------------------------------------

def test_returns_empty_string_for_empty_file(doc_dir):
    result = read_doc(str(doc_dir), "empty.txt")
    assert result == ""


def test_raises_file_not_found_for_missing_doc(doc_dir):
    with pytest.raises(FileNotFoundError):
        read_doc(str(doc_dir), "no_such_doc.txt")


def test_raises_value_error_for_empty_name(doc_dir):
    with pytest.raises(ValueError):
        read_doc(str(doc_dir), "")


def test_raises_value_error_for_none_name(doc_dir):
    with pytest.raises(ValueError):
        read_doc(str(doc_dir), None)


def test_raises_value_error_for_empty_base_dir(doc_dir):
    with pytest.raises(ValueError):
        read_doc("", "doc1.txt")


def test_raises_value_error_for_none_base_dir(doc_dir):
    with pytest.raises(ValueError):
        read_doc(None, "doc1.txt")


def test_returns_exact_bytes_written(tmp_path):
    content = "Unicode: éàü\n"
    (tmp_path / "unicode.txt").write_text(content, encoding="utf-8")
    assert read_doc(str(tmp_path), "unicode.txt") == content
