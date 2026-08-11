"""Request rate limiting for Nerdbot's public deployment.

The Streamlit app calls OpenAI with the operator's own API key, so every
visitor spends the operator's budget. Without a cap, one person in a loop can
run up an arbitrary bill. These limiters bound how fast a single session - and
the deployment as a whole - can consume that budget.

This module deliberately does not import Streamlit, so the limiting logic
stays unit testable and the caller decides where each limiter lives. Callers
inject ``now`` in tests; production uses ``time.monotonic``, which is immune
to system clock changes.
"""

import math
import threading
import time
from collections.abc import Sequence
from collections import deque
from dataclasses import dataclass


SECONDS_PER_HOUR = 3600.0
SECONDS_PER_DAY = 86400.0


@dataclass(frozen=True)
class RateLimitDecision:
    """The outcome of a single rate-limit check."""

    allowed: bool
    retry_after_seconds: float = 0.0
    reason: str = ""


class _Window:
    """A sliding window over recent request timestamps.

    Not thread-safe on its own. ``RateLimiter`` owns the lock and serializes
    every call, which keeps the two-phase check-then-record below atomic.
    """

    def __init__(
        self,
        reason: str,
        max_requests: int,
        window_seconds: float,
    ) -> None:
        if max_requests < 1:
            raise ValueError("max_requests must be at least 1.")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be greater than zero.")

        self.reason = reason
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._events: deque[float] = deque()

    def retry_after(self, now: float) -> float | None:
        """Return seconds until the window has room, or None if it has room."""
        cutoff = now - self._window_seconds
        while self._events and self._events[0] <= cutoff:
            self._events.popleft()

        if len(self._events) < self._max_requests:
            return None
        return max(self._events[0] + self._window_seconds - now, 0.0)

    def record(self, now: float) -> None:
        """Record one consumed request."""
        self._events.append(now)


class RateLimiter:
    """Composite limiter that consumes budget only when every window allows.

    The check is two-phase on purpose: if one window were consumed before a
    later window rejected the request, a blocked caller would still burn
    budget in the earlier window and be throttled far more harshly than the
    configured limits describe.
    """

    def __init__(self, windows: Sequence[_Window]) -> None:
        self._windows = tuple(windows)
        self._lock = threading.Lock()

    def try_acquire(self, now: float | None = None) -> RateLimitDecision:
        """Consume one request when every window has room."""
        moment = time.monotonic() if now is None else now

        with self._lock:
            for window in self._windows:
                retry_after = window.retry_after(moment)
                if retry_after is not None:
                    return RateLimitDecision(
                        allowed=False,
                        retry_after_seconds=retry_after,
                        reason=window.reason,
                    )

            for window in self._windows:
                window.record(moment)

        return RateLimitDecision(allowed=True)


def build_session_limiter(
    cooldown_seconds: float,
    max_requests_per_hour: int,
) -> RateLimiter:
    """Build the per-session limiter for one visitor's browser session."""
    return RateLimiter(
        [
            _Window(
                "You're sending messages a little too quickly.",
                max_requests=1,
                window_seconds=cooldown_seconds,
            ),
            _Window(
                "You've reached this session's hourly question limit.",
                max_requests=max_requests_per_hour,
                window_seconds=SECONDS_PER_HOUR,
            ),
        ]
    )


def build_global_limiter(
    max_requests_per_hour: int,
    max_requests_per_day: int,
) -> RateLimiter:
    """Build the deployment-wide limiter shared by every session."""
    return RateLimiter(
        [
            _Window(
                "Nerdbot has reached its hourly limit across all visitors.",
                max_requests=max_requests_per_hour,
                window_seconds=SECONDS_PER_HOUR,
            ),
            _Window(
                "Nerdbot has reached its daily limit across all visitors.",
                max_requests=max_requests_per_day,
                window_seconds=SECONDS_PER_DAY,
            ),
        ]
    )


def describe_retry_after(seconds: float) -> str:
    """Return a short, human-readable wait time such as "2 minutes"."""
    total_seconds = max(math.ceil(seconds), 1)
    if total_seconds < 60:
        unit = "second" if total_seconds == 1 else "seconds"
        return f"{total_seconds} {unit}"

    minutes = math.ceil(total_seconds / 60)
    if minutes < 60:
        unit = "minute" if minutes == 1 else "minutes"
        return f"{minutes} {unit}"

    hours = math.ceil(minutes / 60)
    unit = "hour" if hours == 1 else "hours"
    return f"{hours} {unit}"


def rate_limit_message(decision: RateLimitDecision) -> str:
    """Return the user-facing message for a blocked request."""
    wait = describe_retry_after(decision.retry_after_seconds)
    return f"{decision.reason} Please try again in about {wait}."
