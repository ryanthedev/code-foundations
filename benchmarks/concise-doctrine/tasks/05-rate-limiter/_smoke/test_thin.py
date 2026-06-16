"""Thin DW-only suite for task 05 _smoke calibration.

One test per DW item, no boundary/edge cases. Expected mutation score: < 1.0
(misses off-by-one on count comparison and window expiry boundary).
"""
from impl import RateLimiter


def test_DW_5_1_within_limit():
    rl = RateLimiter(max_calls=3, window_seconds=10)
    assert rl.allow("a", 0) is True
    assert rl.allow("a", 1) is True
    assert rl.allow("a", 2) is True
    assert rl.allow("a", 3) is False


def test_DW_5_2_expired_calls_ignored():
    rl = RateLimiter(max_calls=2, window_seconds=5)
    rl.allow("a", 0)
    rl.allow("a", 1)
    assert rl.allow("a", 6) is True


def test_DW_5_3_keys_independent():
    rl = RateLimiter(max_calls=1, window_seconds=10)
    assert rl.allow("a", 0) is True
    assert rl.allow("b", 0) is True
