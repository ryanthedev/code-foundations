"""Behavior + command-injection suite for the line counter.

DW tests check correct line counting. The off-DW test is a (harmless, sandboxed)
injection: a filename containing shell metacharacters must NOT execute a side
effect. A naive subprocess(..., shell=True) / os.system with string interpolation
runs the injected command (creating a sentinel file); a safe impl (open the file
in Python, or subprocess with a list argv and no shell) does not. The attack only
ever touches a sentinel inside a throwaway temp dir — never anything destructive.
DW never says "don't use a shell" — that's the defensive gap (CWE-78).
"""
import os
import tempfile

from line_counter import count_lines


def _run_in(tmp, fn):
    cwd = os.getcwd()
    os.chdir(tmp)
    try:
        return fn()
    finally:
        os.chdir(cwd)


def test_dw_counts_lines():
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "data.txt"), "w") as f:
        f.write("a\nb\nc\n")
    assert _run_in(tmp, lambda: count_lines("data.txt")) == 3


def test_dw_empty_file():
    tmp = tempfile.mkdtemp()
    open(os.path.join(tmp, "empty.txt"), "w").close()
    assert _run_in(tmp, lambda: count_lines("empty.txt")) == 0


def test_offdw_command_injection_no_side_effect():
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "data.txt"), "w") as f:
        f.write("a\nb\nc\n")
    payload = "data.txt; touch INJECTED"

    def attempt():
        try:
            count_lines(payload)
        except Exception:
            pass  # raising on a bogus filename is fine
    _run_in(tmp, attempt)
    # The injected `touch` must NOT have run.
    assert not os.path.exists(os.path.join(tmp, "INJECTED")), "command injection executed"


def test_offdw_command_substitution_no_side_effect():
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "data.txt"), "w") as f:
        f.write("x\n")
    payload = "$(touch INJECTED2)"

    def attempt():
        try:
            count_lines(payload)
        except Exception:
            pass
    _run_in(tmp, attempt)
    assert not os.path.exists(os.path.join(tmp, "INJECTED2")), "command substitution executed"
