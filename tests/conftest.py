"""Shared test fixtures."""

import pytest

import app


@pytest.fixture(autouse=True)
def reset_global_rate_limiter() -> None:
    """Give every test a fresh deployment-wide rate-limit budget.

    ``get_global_limiter`` is cached with ``st.cache_resource``, so its
    counters live for the whole pytest process rather than one test. Without
    this reset the budget would accumulate across the suite and tests would
    begin failing once the suite grew past the configured hourly cap.
    """
    app.get_global_limiter.clear()
