"""Tests for Nerdbot's request rate limiting."""

import threading

import pytest

from src.ratelimit import (
    RateLimiter,
    _Window,
    build_global_limiter,
    build_session_limiter,
    describe_retry_after,
    rate_limit_message,
)


def make_limiter(max_requests: int, window_seconds: float) -> RateLimiter:
    """Build a single-window limiter for focused tests."""
    return RateLimiter([_Window("Limit reached.", max_requests, window_seconds)])


def test_requests_under_the_limit_are_allowed() -> None:
    """A limiter should allow requests up to its configured maximum."""
    limiter = make_limiter(3, 60)

    assert all(limiter.try_acquire(now=0.0).allowed for _ in range(3))


def test_request_over_the_limit_is_blocked() -> None:
    """The request past the maximum should be rejected."""
    limiter = make_limiter(2, 60)
    limiter.try_acquire(now=0.0)
    limiter.try_acquire(now=0.0)

    decision = limiter.try_acquire(now=0.0)

    assert not decision.allowed
    assert decision.reason == "Limit reached."


def test_retry_after_reports_when_the_window_frees_up() -> None:
    """A blocked request should report the wait until the oldest event ages."""
    limiter = make_limiter(1, 60)
    limiter.try_acquire(now=100.0)

    decision = limiter.try_acquire(now=120.0)

    assert not decision.allowed
    assert decision.retry_after_seconds == pytest.approx(40.0)


def test_window_slides_and_allows_requests_again() -> None:
    """Budget should return once earlier requests fall outside the window."""
    limiter = make_limiter(1, 60)
    limiter.try_acquire(now=0.0)

    assert not limiter.try_acquire(now=30.0).allowed
    assert limiter.try_acquire(now=61.0).allowed


def test_blocked_request_does_not_consume_budget() -> None:
    """A rejected request must not spend budget in any window.

    Without two-phase acquisition a caller blocked by a later window would
    still burn the earlier window, throttling far harder than configured.
    """
    limiter = RateLimiter(
        [
            _Window("Generous window.", max_requests=10, window_seconds=60),
            _Window("Strict window.", max_requests=1, window_seconds=60),
        ]
    )
    assert limiter.try_acquire(now=0.0).allowed

    for _ in range(5):
        assert not limiter.try_acquire(now=0.0).allowed

    # The strict window frees up at t=61. If the rejected attempts above had
    # consumed the generous window, it would now be nearly exhausted too.
    assert limiter.try_acquire(now=61.0).allowed


def test_tightest_window_reports_the_block() -> None:
    """The first window with no room should supply the user-facing reason."""
    limiter = RateLimiter(
        [
            _Window("Hourly limit.", max_requests=10, window_seconds=3600),
            _Window("Cooldown.", max_requests=1, window_seconds=5),
        ]
    )
    limiter.try_acquire(now=0.0)

    assert limiter.try_acquire(now=1.0).reason == "Cooldown."


def test_concurrent_callers_cannot_exceed_the_limit() -> None:
    """Parallel requests must not over-admit past the maximum."""
    limiter = make_limiter(50, 3600)
    allowed: list[bool] = []
    allowed_lock = threading.Lock()
    start = threading.Barrier(16)

    def attempt() -> None:
        start.wait()
        for _ in range(20):
            decision = limiter.try_acquire(now=0.0)
            with allowed_lock:
                allowed.append(decision.allowed)

    threads = [threading.Thread(target=attempt) for _ in range(16)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert sum(allowed) == 50


@pytest.mark.parametrize(
    ("max_requests", "window_seconds"),
    [(0, 60), (-1, 60), (1, 0), (1, -5)],
)
def test_invalid_window_configuration_is_rejected(
    max_requests: int,
    window_seconds: float,
) -> None:
    """Nonsensical limits should fail loudly rather than disable limiting."""
    with pytest.raises(ValueError):
        _Window("Limit reached.", max_requests, window_seconds)


def test_session_limiter_enforces_cooldown_then_hourly_cap() -> None:
    """The session limiter should apply both its cooldown and hourly cap."""
    limiter = build_session_limiter(cooldown_seconds=3, max_requests_per_hour=5)

    assert limiter.try_acquire(now=0.0).allowed
    assert not limiter.try_acquire(now=1.0).allowed

    for index in range(1, 5):
        assert limiter.try_acquire(now=index * 10.0).allowed

    decision = limiter.try_acquire(now=100.0)
    assert not decision.allowed
    assert "session's hourly" in decision.reason


def test_global_limiter_enforces_daily_cap_across_hours() -> None:
    """The daily cap should still bind after hourly windows have reset."""
    limiter = build_global_limiter(
        max_requests_per_hour=2,
        max_requests_per_day=3,
    )

    assert limiter.try_acquire(now=0.0).allowed
    assert limiter.try_acquire(now=0.0).allowed
    assert limiter.try_acquire(now=3601.0).allowed

    decision = limiter.try_acquire(now=7202.0)
    assert not decision.allowed
    assert "daily limit" in decision.reason


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0.1, "1 second"),
        (1, "1 second"),
        (2, "2 seconds"),
        (59, "59 seconds"),
        (59.2, "1 minute"),
        (60, "1 minute"),
        (90, "2 minutes"),
        (3600, "1 hour"),
        (7200, "2 hours"),
    ],
)
def test_describe_retry_after_formats_wait_times(
    seconds: float,
    expected: str,
) -> None:
    """Wait times should read naturally and always round up."""
    assert describe_retry_after(seconds) == expected


def test_rate_limit_message_combines_reason_and_wait() -> None:
    """The user-facing message should explain the limit and the wait."""
    limiter = make_limiter(1, 60)
    limiter.try_acquire(now=0.0)

    message = rate_limit_message(limiter.try_acquire(now=30.0))

    assert message == "Limit reached. Please try again in about 30 seconds."
