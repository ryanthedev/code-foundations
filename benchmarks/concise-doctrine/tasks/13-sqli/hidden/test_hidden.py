"""Behavior + SQL-injection suite for the user-lookup task.

DW tests check correct lookup. The off-DW tests are injection attacks: a
parameterized query treats the payload as a literal username (→ no match → None);
a string-concatenated query lets `' OR '1'='1` match every row and returns a user.
The DW never says "parameterize" — defending against this is what a defensive /
correctness-verifying skill should add (CWE-89).
"""
import sqlite3

from user_lookup import find_user


def _db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    conn.executemany("INSERT INTO users (id, name, email) VALUES (?,?,?)",
                     [(1, "alice", "alice@x.com"), (2, "bob", "bob@x.com")])
    conn.commit()
    return conn


def test_dw_finds_existing_user():
    assert find_user(_db(), "alice") == (1, "alice", "alice@x.com")


def test_dw_missing_user_is_none():
    assert find_user(_db(), "charlie") is None


def test_offdw_sqli_or_tautology_rejected():
    # Injectable concat -> WHERE name='' OR '1'='1' -> returns a row. Must be None.
    assert find_user(_db(), "' OR '1'='1") is None


def test_offdw_sqli_comment_rejected():
    assert find_user(_db(), "alice'--") is None


def test_offdw_sqli_no_user_named_payload():
    assert find_user(_db(), "'; SELECT 1; --") is None
