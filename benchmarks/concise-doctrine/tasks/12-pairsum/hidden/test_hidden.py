"""Behavior + efficiency suite for the pair-sum task.

DW tests check correctness on small inputs. The off-DW test is the bite: a large
input with NO qualifying pair forces a full scan. A naive O(n^2) double loop blows
the time budget; an O(n) set-based solution finishes instantly. The DW never asks
for efficiency — anticipating it is what a performance skill should add.
"""
import time

from pairsum import has_pair_sum


def test_dw_finds_pair():
    assert has_pair_sum([1, 2, 3], 5) is True       # 2 + 3


def test_dw_no_pair():
    assert has_pair_sum([1, 2, 3], 100) is False


def test_dw_empty_and_single():
    assert has_pair_sum([], 5) is False
    assert has_pair_sum([5], 5) is False            # needs two distinct elements


def test_offdw_large_input_is_efficient():
    # all even -> no two sum to an odd target -> full scan required either way.
    nums = [2 * i for i in range(15_000)]
    start = time.perf_counter()
    result = has_pair_sum(nums, 1)
    elapsed = time.perf_counter() - start
    assert result is False
    # O(n) finishes in milliseconds; O(n^2) on 15k takes many seconds.
    assert elapsed < 3.0, f"too slow ({elapsed:.1f}s) — likely O(n^2)"
