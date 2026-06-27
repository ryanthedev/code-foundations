# Plan: sliding-window rate limiter

**Created:** 2026-06-19
**Status:** pending
**Complexity:** simple

---

## Context

Implement a sliding-window rate limiter in Python. Adherence-test task: the build agent under test produces `outputs/rate_limiter.py` + `outputs/test_rate_limiter.py`.

---

### Phase 1: Implement RateLimiter
**Model:** sonnet
**Gate:** Minimal
**Skills:** code-clarity-and-docs

**Goal:** Implement a module `rate_limiter.py` with a `RateLimiter` class that enforces a maximum call count per sliding time window.

**What to build:**

A module `rate_limiter.py` exposing one class:

```python
class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: float) -> None:
        """Create a limiter that allows at most max_calls in any window_seconds window."""

    def allow(self, key: str, now: float) -> bool:
        """Return True if this call is within the rate limit, False if it exceeds it.

        now — current timestamp in seconds (injected for determinism).
        Calls older than window_seconds before now are not counted.
        """
```

The limiter tracks calls per `key` independently. Each call that returns `True` counts toward the limit; calls that return `False` do not consume a slot.

**Done when:**

- [ ] DW-5.1: `max_calls` calls with the same key in a window all return `True`; the next call in the same window returns `False`. With `max_calls=3, window=10`, calls at t=0,1,2 → `True, True, True`; call at t=3 → `False`.
- [ ] DW-5.2: Calls older than `window_seconds` before the current call do not count. With `max_calls=2, window=5`, calls at t=0,1 → `True, True`; call at t=6 → `True` (t=0 has expired).
- [ ] DW-5.3: Keys are tracked independently. Calls for key `"a"` do not affect the limit for key `"b"`.

**Produces:**

- `outputs/rate_limiter.py` — the implementation module
- `outputs/test_rate_limiter.py` — pytest suite (run and confirm passing before finishing)
