"""
Rate Limiter

Tracks API calls per user and blocks requests that exceed the configured limit
within a sliding time window.

Design Decisions (from cc-routine-and-class-design):
- Information hiding: Storage mechanism and time calculations are hidden
- Consistent abstraction: All methods operate at "rate limiting" level
- No inheritance needed: Standalone class with no "is-a" relationship

Defensive Programming (from cc-defensive-programming):
- Barricade pattern: All public methods validate input
- Error handling for anticipated bad input (empty user_id)
- Thread-safety via threading.Lock for concurrent access
"""

import threading
import time
from typing import Dict, List


# Named constants (from cc-data-organization: eliminate magic numbers)
DEFAULT_MAX_REQUESTS = 100
DEFAULT_WINDOW_SECONDS = 60
MINIMUM_MAX_REQUESTS = 1
MINIMUM_WINDOW_SECONDS = 1


class RateLimiterError(ValueError):
    """Base exception for rate limiter configuration errors."""
    pass


class InvalidMaxRequestsError(RateLimiterError):
    """Raised when max_requests is less than minimum allowed."""
    pass


class InvalidWindowSecondsError(RateLimiterError):
    """Raised when window_seconds is less than minimum allowed."""
    pass


class EmptyUserIdError(RateLimiterError):
    """Raised when user_id is empty or None."""
    pass


class RateLimiter:
    """
    Tracks API calls per user and blocks requests exceeding the limit.

    Uses a sliding window algorithm: maintains timestamps of recent requests
    and removes those outside the current window before counting.

    Thread-safe: All public methods are protected by a lock.

    Attributes:
        max_requests: Maximum requests allowed per window
        window_seconds: Duration of the sliding window in seconds
    """

    def __init__(
        self,
        max_requests: int = DEFAULT_MAX_REQUESTS,
        window_seconds: int = DEFAULT_WINDOW_SECONDS
    ) -> None:
        """
        Initialize rate limiter with request limit and time window.

        Args:
            max_requests: Maximum requests allowed per window (default: 100)
            window_seconds: Duration of sliding window in seconds (default: 60)

        Raises:
            InvalidMaxRequestsError: If max_requests < 1
            InvalidWindowSecondsError: If window_seconds < 1
        """
        # Validate inputs at barricade (from cc-defensive-programming)
        if max_requests < MINIMUM_MAX_REQUESTS:
            raise InvalidMaxRequestsError(
                f"max_requests must be at least {MINIMUM_MAX_REQUESTS}, "
                f"got {max_requests}"
            )

        if window_seconds < MINIMUM_WINDOW_SECONDS:
            raise InvalidWindowSecondsError(
                f"window_seconds must be at least {MINIMUM_WINDOW_SECONDS}, "
                f"got {window_seconds}"
            )

        self._max_requests = max_requests
        self._window_seconds = window_seconds

        # Private data (from cc-routine-and-class-design: hide implementation)
        # Maps user_id to list of request timestamps
        self._request_timestamps: Dict[str, List[float]] = {}

        # Thread safety (from cc-defensive-programming: concurrent access)
        self._lock = threading.Lock()

    @property
    def max_requests(self) -> int:
        """Maximum requests allowed per window (read-only)."""
        return self._max_requests

    @property
    def window_seconds(self) -> int:
        """Duration of sliding window in seconds (read-only)."""
        return self._window_seconds

    def _validate_user_id(self, user_id: str) -> None:
        """
        Validate user_id is non-empty string.

        Args:
            user_id: The user identifier to validate

        Raises:
            EmptyUserIdError: If user_id is None or empty string
        """
        # Guard clause (from cc-control-flow-quality)
        if not user_id:
            raise EmptyUserIdError("user_id cannot be None or empty")

    def _remove_expired_timestamps(
        self,
        user_id: str,
        current_time: float
    ) -> None:
        """
        Remove timestamps older than the sliding window.

        Args:
            user_id: The user whose timestamps to clean
            current_time: Current timestamp for window calculation

        Note:
            Must be called while holding _lock.
            Creates empty list if user not in timestamps dict.
        """
        # Ensure user has an entry
        if user_id not in self._request_timestamps:
            self._request_timestamps[user_id] = []
            return

        # Calculate window boundary
        window_start = current_time - self._window_seconds

        # Filter to keep only timestamps within window
        # (from cc-control-flow-quality: functional pipeline over explicit loop)
        self._request_timestamps[user_id] = [
            timestamp
            for timestamp in self._request_timestamps[user_id]
            if timestamp > window_start
        ]

    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a request from this user is allowed and record it if so.

        Implements sliding window rate limiting:
        1. Remove timestamps older than window
        2. If count < max, allow and record timestamp
        3. Otherwise, deny

        Args:
            user_id: Unique identifier for the user making the request

        Returns:
            True if request is allowed, False if rate limit exceeded

        Raises:
            EmptyUserIdError: If user_id is None or empty

        Example:
            >>> limiter = RateLimiter(max_requests=2, window_seconds=60)
            >>> limiter.is_allowed("user1")  # First request
            True
            >>> limiter.is_allowed("user1")  # Second request
            True
            >>> limiter.is_allowed("user1")  # Third request - blocked
            False
        """
        # Validate at barricade (from cc-defensive-programming)
        self._validate_user_id(user_id)

        current_time = time.time()

        with self._lock:
            # Remove expired timestamps from window
            self._remove_expired_timestamps(user_id, current_time)

            # Get count of requests in current window
            request_count = len(self._request_timestamps[user_id])

            # Check if under limit
            # (from cc-control-flow-quality: nominal case in if)
            if request_count < self._max_requests:
                # Record this request
                self._request_timestamps[user_id].append(current_time)
                return True

            # Rate limit exceeded
            return False

    def get_remaining(self, user_id: str) -> int:
        """
        Get the number of requests remaining for this user in current window.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Number of requests remaining (0 if limit reached)

        Raises:
            EmptyUserIdError: If user_id is None or empty

        Example:
            >>> limiter = RateLimiter(max_requests=5, window_seconds=60)
            >>> limiter.get_remaining("user1")
            5
            >>> limiter.is_allowed("user1")
            True
            >>> limiter.get_remaining("user1")
            4
        """
        # Validate at barricade
        self._validate_user_id(user_id)

        current_time = time.time()

        with self._lock:
            self._remove_expired_timestamps(user_id, current_time)

            request_count = len(self._request_timestamps.get(user_id, []))
            remaining = self._max_requests - request_count

            # Ensure non-negative (defensive)
            return max(0, remaining)

    def reset(self, user_id: str) -> None:
        """
        Clear all request history for a specific user.

        Administrative function for cases like:
        - User paid for higher tier
        - Testing/debugging
        - Account recovery

        Args:
            user_id: Unique identifier for the user to reset

        Raises:
            EmptyUserIdError: If user_id is None or empty
        """
        # Validate at barricade
        self._validate_user_id(user_id)

        with self._lock:
            if user_id in self._request_timestamps:
                del self._request_timestamps[user_id]

    def reset_all(self) -> None:
        """
        Clear all request history for all users.

        Administrative function for system-wide reset.
        Use with caution in production.
        """
        with self._lock:
            self._request_timestamps.clear()


if __name__ == "__main__":
    # Example usage demonstrating rate limiting behavior

    print("Rate Limiter Demo")
    print("=" * 40)

    # Create limiter: 3 requests per 60 seconds
    limiter = RateLimiter(max_requests=3, window_seconds=60)

    print(f"Configuration: {limiter.max_requests} requests "
          f"per {limiter.window_seconds} seconds")
    print()

    # Simulate requests from a user
    test_user = "user_123"

    for request_number in range(1, 6):
        is_allowed = limiter.is_allowed(test_user)
        remaining = limiter.get_remaining(test_user)
        status = "ALLOWED" if is_allowed else "BLOCKED"

        print(f"Request {request_number}: {status} "
              f"(remaining: {remaining})")

    print()
    print("Resetting user...")
    limiter.reset(test_user)
    print(f"After reset, remaining: {limiter.get_remaining(test_user)}")
