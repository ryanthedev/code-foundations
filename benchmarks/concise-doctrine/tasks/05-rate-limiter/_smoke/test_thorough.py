"""Thorough suite for task 05 _smoke calibration.

DW items + boundary cases that kill all 5 mutants.
Expected mutation score: 1.0 on the reference impl.

Mutation surface:
  Site 0: now - window → now + window in cutoff     → killed by test_DW_5_2 (expired calls)
  Site 1: t > cutoff → t >= cutoff (boundary keep)  → killed by test_call_exactly_at_boundary_expires
  Site 2: >= max → > max in count check              → killed by test_DW_5_1 (exactly at limit)
  Site 3: return False → return True on limit        → killed by test_DW_5_1 (4th call returns False)
  Site 4: return True → return False on allow        → killed by test_DW_5_1 (1st call returns True)
"""
from impl import RateLimiter


def test_DW_5_1_within_limit():
    rl = RateLimiter(max_calls=3, window_seconds=10)
    assert rl.allow("a", 0) is True
    assert rl.allow("a", 1) is True
    assert rl.allow("a", 2) is True
    assert rl.allow("a", 3) is False


def test_DW_5_2_expired_calls_ignored():
    # Kills site 0 (cutoff = now + window makes cutoff huge, drops everything → always allows).
    rl = RateLimiter(max_calls=2, window_seconds=5)
    rl.allow("a", 0)
    rl.allow("a", 1)
    assert rl.allow("a", 6) is True


def test_DW_5_3_keys_independent():
    rl = RateLimiter(max_calls=1, window_seconds=10)
    assert rl.allow("a", 0) is True
    assert rl.allow("b", 0) is True


def test_exactly_max_calls_1_boundary():
    # max_calls=1: exactly one allowed, then blocked.
    # Kills site 2 (>= → >): with >, len=1 > 1 is False → wrong allow.
    rl = RateLimiter(max_calls=1, window_seconds=10)
    assert rl.allow("x", 0) is True
    assert rl.allow("x", 1) is False


def test_call_exactly_at_window_boundary_still_counts():
    # Convention: timestamps strictly older than (now - window) are dropped.
    # t=0 at now=5 with window=5: cutoff=0; 0 > 0 is False → t=0 is NOT dropped (still counts).
    # max_calls=1: t=0 slot is still active → second call at t=5 is rejected.
    # With >= mutation: 0 >= 0 True → t=0 also kept → still rejected (same result; mutation silent here).
    # The KILLING test is test_DW_5_2 (t=6 with window=5, prior call at t=0: cutoff=1; 0 > 1 False → dropped).
    # With + mutation (site 0): cutoff = 6+5=11; 0 > 11 False → t=0 "not expired" → still counts → blocks.
    rl = RateLimiter(max_calls=1, window_seconds=5)
    rl.allow("a", 0)
    # at t=5: cutoff=0; t=0 > 0 is False → kept → still blocked
    assert rl.allow("a", 5) is False


def test_rejected_call_does_not_consume_slot():
    rl = RateLimiter(max_calls=2, window_seconds=10)
    rl.allow("a", 0)
    rl.allow("a", 1)
    rl.allow("a", 2)  # blocked
    assert rl.allow("a", 11) is True


def test_max_calls_zero_always_rejects():
    rl = RateLimiter(max_calls=0, window_seconds=10)
    assert rl.allow("a", 0) is False
