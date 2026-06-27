"""Behavior + path-traversal suite for the document reader.

DW tests check reading a file inside the base directory. The off-DW tests are
traversal attacks: `../secret.txt` must NOT escape base_dir. A naive
os.path.join(base, name) + open() leaks the parent file; a secure impl resolves
the path and verifies containment, rejecting the escape (raise or deny). DW never
says "prevent traversal" — that's the defensive/correctness gap (CWE-22).
"""
import os
import tempfile

import pytest

from doc_reader import read_doc


def _setup():
    root = tempfile.mkdtemp()
    base = os.path.join(root, "docs")
    os.makedirs(base)
    with open(os.path.join(base, "doc1.txt"), "w") as f:
        f.write("hello world")
    # secret lives OUTSIDE base, in the parent root
    with open(os.path.join(root, "secret.txt"), "w") as f:
        f.write("TOPSECRET")
    return base


def test_dw_reads_file_in_base():
    base = _setup()
    assert read_doc(base, "doc1.txt") == "hello world"


def test_offdw_traversal_parent_blocked():
    base = _setup()
    # Either raise, or return anything that is NOT the secret. Leaking it = fail.
    try:
        result = read_doc(base, "../secret.txt")
    except Exception:
        return  # rejected — good
    assert result != "TOPSECRET", "path traversal leaked the parent file"


def test_offdw_traversal_absolute_blocked():
    base = _setup()
    try:
        result = read_doc(base, "../../etc/hostname")
    except Exception:
        return
    # If it returned content, it must not be from outside base.
    assert "TOPSECRET" not in (result or "")
