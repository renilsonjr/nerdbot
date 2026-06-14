"""Tests for the Nerdbot Streamlit interface."""

from streamlit.testing.v1 import AppTest


MOCK_RESPONSE = """1. Explanation
Mock explanation.

2. Real-World / Career Example
Mock career example.

3. Practice Exercise
Mock exercise."""


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
    assert "OPENAI_API_KEY is missing" in app.error[0].value
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
