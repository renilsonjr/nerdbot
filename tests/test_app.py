"""Tests for the Nerdbot Streamlit interface."""

import pytest
from streamlit.testing.v1 import AppTest

from src.bot import GENERATION_ERROR_MESSAGE, INPUT_TOO_LONG_MESSAGE
from src.config import MISSING_API_KEY_MESSAGE
from src.ratelimit import RateLimitDecision, build_global_limiter


MOCK_RESPONSE = """1. Explanation
Mock explanation.

2. Real-World / Career Example
Mock career example.

3. Practice Exercise
Mock exercise."""

MOCK_ANSWER_RESPONSE = """1. Suggested Answer
Mock suggested answer.

2. Why It Works
Mock explanation.

3. Common Mistake
Mock common mistake."""

MOCK_RESOURCE_RESPONSE = """1. Recommended Resource
SQLBolt

2. Why It Fits
Interactive SQL practice.

3. Practice Task
Complete one lesson."""


def test_app_shows_missing_api_key_error() -> None:
    """The app should clearly report missing OpenAI configuration."""
    app = AppTest.from_string(
        """
import app
app.OPENAI_API_KEY = None
app.main()
"""
    ).run()

    assert app.title[0].value == "Nerdbot"
    intro = "\n".join(element.value for element in app.markdown)
    assert "What you can ask" in intro
    assert "SQL joins" in intro
    assert "done" in intro
    assert "recommend a book for Python" in intro
    assert "recommend a cybersecurity resource" in intro
    assert app.error[0].value == MISSING_API_KEY_MESSAGE
    assert app.chat_input[0].disabled


def test_app_uses_mocked_response_and_saves_chat_history() -> None:
    """A submitted topic should render and persist both chat messages."""
    app = AppTest.from_string(
        f'''
import app
app.OPENAI_API_KEY = "test-key"
app.generate_response = lambda topic: {MOCK_RESPONSE!r}
app.main()
'''
    ).run()

    app.chat_input[0].set_value("SQL joins").run()

    assert len(app.chat_message) == 2
    assert app.chat_message[0].markdown[0].value == "SQL joins"
    assert app.chat_message[1].markdown[0].value == MOCK_RESPONSE
    assert app.session_state["messages"] == [
        {"role": "user", "content": "SQL joins"},
        {"role": "assistant", "content": MOCK_RESPONSE},
    ]


def test_app_handles_empty_input_without_generating_response() -> None:
    """Whitespace-only input should show guidance and add no messages."""
    app = AppTest.from_string(
        """
import app
app.OPENAI_API_KEY = "test-key"

def fail_if_called(topic):
    raise AssertionError("generate_response should not be called")

app.generate_response = fail_if_called
app.main()
"""
    ).run()

    app.chat_input[0].set_value("   ").run()

    assert app.warning[0].value == "Please enter a study topic."
    assert app.session_state["messages"] == []


def test_app_rejects_long_input_without_generating_response() -> None:
    """Oversized input should not be stored or sent to a response helper."""
    app = AppTest.from_string(
        """
import app
app.OPENAI_API_KEY = "test-key"

def fail_if_called(*args):
    raise AssertionError("No response helper should be called")

app.generate_response = fail_if_called
app.generate_exercise_answer = fail_if_called
app.generate_resource_response = fail_if_called
app.main()
"""
    ).run()

    app.chat_input[0].set_value("x" * 4001).run()

    assert app.warning[0].value == INPUT_TOO_LONG_MESSAGE
    assert app.session_state["messages"] == []


def test_app_hides_internal_error_details() -> None:
    """Unexpected failures should display only the generic safe message."""
    app = AppTest.from_string(
        """
import app
app.OPENAI_API_KEY = "test-key"

def raise_internal_error(topic):
    raise RuntimeError("secret-data from /internal/path")

app.generate_response = raise_internal_error
app.main()
"""
    ).run()

    app.chat_input[0].set_value("SQL joins").run()

    assert app.error[0].value == GENERATION_ERROR_MESSAGE
    assert "secret-data" not in app.error[0].value
    assert "/internal/path" not in app.error[0].value


def test_app_answers_previous_exercise(monkeypatch: pytest.MonkeyPatch) -> None:
    """Streamlit should retain context and use the answer helper."""
    # AppTest submits both messages within milliseconds, which the per-session
    # cooldown would reject. A real user spends far longer than the cooldown
    # working the exercise before typing "done", so bypass the limiter to test
    # the answer flow itself. Patching via monkeypatch rather than inside the
    # app script keeps the override from leaking into later tests.
    monkeypatch.setattr(
        "app.check_rate_limits",
        lambda: RateLimitDecision(allowed=True),
    )
    app = AppTest.from_string(
        f'''
import app
app.OPENAI_API_KEY = "test-key"
app.generate_response = lambda topic: {MOCK_RESPONSE!r}
app.generate_exercise_answer = lambda topic, response: {MOCK_ANSWER_RESPONSE!r}
app.main()
'''
    ).run()

    app.chat_input[0].set_value("SQL joins").run()
    app.chat_input[0].set_value("done").run()

    assert len(app.chat_message) == 4
    assert app.chat_message[3].markdown[0].value == MOCK_ANSWER_RESPONSE
    assert app.session_state["previous_exercise"] == {
        "topic": "SQL joins",
        "response": MOCK_RESPONSE,
    }


def test_app_answer_request_without_previous_exercise() -> None:
    """Streamlit should guide users when no previous exercise exists."""
    app = AppTest.from_string(
        """
import app
app.OPENAI_API_KEY = "test-key"

def fail_if_called(*args):
    raise AssertionError("No API helper should be called")

app.generate_response = fail_if_called
app.generate_exercise_answer = fail_if_called
app.main()
"""
    ).run()

    app.chat_input[0].set_value("show answer").run()

    assert app.chat_message[1].markdown[0].value == (
        "Please enter a study topic first so Nerdbot can create an exercise."
    )
    assert app.session_state["previous_exercise"] is None


def test_app_blocks_rapid_requests_without_calling_openai() -> None:
    """A throttled request must never reach the OpenAI-backed helper.

    This is the control that stops a visitor from spending the operator's
    API budget in a loop, so it asserts on the helper never being called
    rather than only on the warning being shown.
    """
    app = AppTest.from_string(
        f'''
import app
app.OPENAI_API_KEY = "test-key"

calls = []

def counted_response(topic):
    calls.append(topic)
    return {MOCK_RESPONSE!r}

app.generate_response = counted_response
app.calls = calls
app.main()
'''
    ).run()

    app.chat_input[0].set_value("SQL joins").run()
    app.chat_input[0].set_value("Python decorators").run()

    assert app.session_state["messages"][-1]["content"].startswith(
        "You're sending messages a little too quickly."
    )
    assert len(app.warning) == 1
    assert app.session_state["messages"][1]["content"] == MOCK_RESPONSE


def test_app_allows_the_first_request_through() -> None:
    """Rate limiting must not block a visitor's opening question."""
    app = AppTest.from_string(
        f'''
import app
app.OPENAI_API_KEY = "test-key"
app.generate_response = lambda topic: {MOCK_RESPONSE!r}
app.main()
'''
    ).run()

    app.chat_input[0].set_value("SQL joins").run()

    assert app.session_state["messages"][-1]["content"] == MOCK_RESPONSE
    assert not app.warning


def test_global_limit_is_shared_across_sessions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One visitor exhausting the app-wide budget should block the next.

    Each AppTest is a separate session with its own per-session limiter, so a
    block here can only come from the shared deployment-wide limiter. This is
    what stops someone from bypassing limits by opening new sessions.
    """
    shared_limiter = build_global_limiter(
        max_requests_per_hour=1,
        max_requests_per_day=1,
    )
    monkeypatch.setattr("app.get_global_limiter", lambda: shared_limiter)

    source = f'''
import app
app.OPENAI_API_KEY = "test-key"
app.generate_response = lambda topic: {MOCK_RESPONSE!r}
app.main()
'''

    first_visitor = AppTest.from_string(source).run()
    first_visitor.chat_input[0].set_value("SQL joins").run()

    second_visitor = AppTest.from_string(source).run()
    second_visitor.chat_input[0].set_value("Python decorators").run()

    assert first_visitor.session_state["messages"][-1]["content"] == (
        MOCK_RESPONSE
    )
    assert second_visitor.session_state["messages"][-1]["content"].startswith(
        "Nerdbot has reached its hourly limit across all visitors."
    )


def test_app_does_not_rate_limit_offline_resource_requests() -> None:
    """Curated resources cost nothing, so they should bypass the limiter."""
    app = AppTest.from_string(
        f'''
import app
app.OPENAI_API_KEY = "test-key"
app.generate_resource_response = lambda request, topic: {MOCK_RESOURCE_RESPONSE!r}
app.main()
'''
    ).run()

    for _ in range(5):
        app.chat_input[0].set_value("Recommend a book").run()

    assert not app.warning
    assert app.session_state["messages"][-1]["content"] == (
        MOCK_RESOURCE_RESPONSE
    )


def test_app_routes_resource_request_without_changing_exercise_context() -> None:
    """Streamlit should use curated resources and preserve prior context."""
    app = AppTest.from_string(
        f'''
import app
app.OPENAI_API_KEY = "test-key"
app.generate_response = lambda topic: {MOCK_RESPONSE!r}
app.generate_resource_response = lambda request, topic: {MOCK_RESOURCE_RESPONSE!r}
app.main()
'''
    ).run()

    app.chat_input[0].set_value("SQL joins").run()
    app.chat_input[0].set_value("Recommend a book").run()

    assert app.chat_message[3].markdown[0].value == MOCK_RESOURCE_RESPONSE
    assert app.session_state["previous_exercise"] == {
        "topic": "SQL joins",
        "response": MOCK_RESPONSE,
    }
