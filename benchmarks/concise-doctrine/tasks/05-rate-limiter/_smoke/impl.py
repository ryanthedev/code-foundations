"""Reference implementation for task 05 (RateLimiter). Used in _smoke calibration only.

Window convention: a call at timestamp t counts if t >= now - window_seconds.
Calls strictly older than (now - window_seconds) are dropped.
"""
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_calls: int, window_seconds: float) -> None:
        self._max = max_calls
        self._window = window_seconds
        self._log: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str, now: float) -> bool:
        cutoff = now - self._window
        self._log[key] = [t for t in self._log[key] if t >= cutoff]
        if len(self._log[key]) >= self._max:
            return False
        self._log[key].append(now)
        return True
