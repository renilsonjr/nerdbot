"""Tests for the Nerdbot Streamlit interface."""

from streamlit.testing.v1 import AppTest

from src.config import MISSING_API_KEY_MESSAGE


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


def test_app_answers_previous_exercise() -> None:
    """Streamlit should retain context and use the answer helper."""
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
