"""Hidden ground-truth suite for task 05 (RateLimiter). Never shown to the agent.

  test_dw_*    — behaviors the spec's Done-When items state or exemplify
  test_offdw_* — boundary and edge behaviors the spec did not exemplify

Window convention: a call at timestamp t counts toward the limit if
  t >= now - window_seconds  (i.e., it is within the window, inclusive).
Calls strictly older (t < now - window_seconds) are not counted.

Mutation surface targeted by test_offdw_*:
  - count boundary: >= vs > on max_calls (off-by-one)
  - window arithmetic: now - window vs now + window
  - bool return inversion
  - window boundary inclusivity: call at exactly t = now - window still counts
"""
from rate_limiter import RateLimiter


# ---- DW-stated behavior ----------------------------------------------------

def test_dw_calls_within_limit_succeed():
    rl = RateLimiter(max_calls=3, window_seconds=10)
    assert rl.allow("a", 0) is True
    assert rl.allow("a", 1) is True
    assert rl.allow("a", 2) is True

def test_dw_call_over_limit_rejected():
    rl = RateLimiter(max_calls=3, window_seconds=10)
    rl.allow("a", 0)
    rl.allow("a", 1)
    rl.allow("a", 2)
    assert rl.allow("a", 3) is False

def test_dw_expired_calls_do_not_count():
    rl = RateLimiter(max_calls=2, window_seconds=5)
    assert rl.allow("a", 0) is True    # t=0: within window
    assert rl.allow("a", 1) is True    # t=1: within window; limit reached
    # at t=6: cutoff = 6-5 = 1; t=0 < 1 → expired; t=1 >= 1 → still counts (1 slot used)
    # Only 1 of 2 slots used → free
    assert rl.allow("a", 6) is True

def test_dw_keys_are_independent():
    rl = RateLimiter(max_calls=1, window_seconds=10)
    assert rl.allow("a", 0) is True
    assert rl.allow("b", 0) is True    # different key, unaffected


# ---- Off-DW: boundary and edge behaviors -----------------------------------

def test_offdw_exactly_max_calls_allowed():
    # max_calls=1: first call is True, second (same window) is False.
    # Catches >= vs > off-by-one on the count check.
    rl = RateLimiter(max_calls=1, window_seconds=10)
    assert rl.allow("x", 0) is True
    assert rl.allow("x", 1) is False

def test_offdw_call_at_window_boundary_still_counts():
    # A call at exactly t = now - window_seconds is still within the window (inclusive).
    # at t=5: cutoff = 5-5 = 0; prior call at t=0: 0 >= 0 → still counts → slot occupied.
    rl = RateLimiter(max_calls=1, window_seconds=5)
    rl.allow("a", 0)
    assert rl.allow("a", 5) is False   # t=0 is at boundary → still counts → rejected

def test_offdw_call_just_outside_window_expires():
    # A call strictly before the cutoff is expired.
    # at t=5.001: cutoff = 5.001-5 = 0.001; t=0: 0 < 0.001 → expired → slot freed.
    rl = RateLimiter(max_calls=1, window_seconds=5)
    rl.allow("a", 0)
    assert rl.allow("a", 5.001) is True

def test_offdw_rejected_call_does_not_consume_slot():
    # A False return must not consume a slot.
    rl = RateLimiter(max_calls=2, window_seconds=10)
    rl.allow("a", 0)    # slot 1
    rl.allow("a", 1)    # slot 2 — at limit
    rl.allow("a", 2)    # rejected — must not consume slot
    # All prior successful calls expire at t=11
    assert rl.allow("a", 11) is True

def test_offdw_max_calls_zero_always_rejects():
    rl = RateLimiter(max_calls=0, window_seconds=10)
    assert rl.allow("a", 0) is False

def test_offdw_multiple_keys_track_separately_over_time():
    rl = RateLimiter(max_calls=2, window_seconds=10)
    rl.allow("a", 0)
    rl.allow("a", 1)
    assert rl.allow("b", 2) is True    # key "b" is unaffected
    assert rl.allow("a", 3) is False   # key "a" is at its limit
