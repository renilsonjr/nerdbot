"""Tests for Nerdbot's core response and terminal behavior."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import src.bot as bot
from main import run_chat
from src.config import MISSING_API_KEY_MESSAGE
from src.prompts import EXERCISE_ANSWER_PROMPT, SYSTEM_PROMPT


MOCK_RESPONSE = """1. Explanation
SQL joins combine related data from multiple tables.

2. Real-World / Career Example
A data analyst uses joins to combine customer and order data.

3. Practice Exercise
Write a query that joins a Customers table to an Orders table."""

MOCK_ANSWER_RESPONSE = """1. Suggested Answer
SELECT Customers.name, Orders.id
FROM Customers
LEFT JOIN Orders ON Customers.id = Orders.customer_id;

2. Why It Works
The LEFT JOIN keeps every customer and matches available orders.

3. Common Mistake
Using an INNER JOIN would remove customers who have no orders."""


def test_system_prompt_exists() -> None:
    """The system prompt should exist and define all required blocks."""
    assert SYSTEM_PROMPT.strip()
    assert "1. Explanation" in SYSTEM_PROMPT
    assert "2. Real-World / Career Example" in SYSTEM_PROMPT
    assert "3. Practice Exercise" in SYSTEM_PROMPT


@pytest.mark.parametrize(
    "user_input",
    ["done", "Show answer", "answer!", "I finished", "FINISHED"],
)
def test_answer_request_detection(user_input: str) -> None:
    """Common completion phrases should request the previous answer."""
    assert bot.is_answer_request(user_input)


def test_normal_topic_is_not_answer_request() -> None:
    """A regular study topic should keep the original response flow."""
    assert not bot.is_answer_request("Python functions")


@pytest.mark.parametrize(
    "user_input",
    [
        "Recommend a Python book",
        "Show me a SQL course",
        "Any JavaScript resources?",
        "Suggest an API article",
        "I need a cybersecurity video",
    ],
)
def test_resource_request_detection(user_input: str) -> None:
    """Common recommendation phrases should use the resource flow."""
    assert bot.is_resource_request(user_input)


def test_book_recommendation_request_is_detected() -> None:
    """A direct book request should be recognized."""
    assert bot.is_resource_request("Can you recommend a book for Python?")


def test_normal_topic_is_not_resource_request() -> None:
    """A regular topic should not be mistaken for a resource request."""
    assert not bot.is_resource_request("Explain Python decorators")


def test_answer_request_is_not_resource_request() -> None:
    """Exercise completion phrases should keep answer-request routing."""
    assert bot.is_answer_request("show answer")
    assert not bot.is_resource_request("show answer")


def test_generate_resource_response_uses_curated_data_without_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resource output should use the catalog and never call OpenAI."""
    openai_mock = Mock()
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    result = bot.generate_resource_response("Recommend a Python book")

    assert "1. Recommended Resource" in result
    assert "Automate the Boring Stuff with Python" in result
    assert "2. Why It Fits" in result
    assert "3. Practice Task" in result
    openai_mock.assert_not_called()


def test_generate_resource_response_uses_previous_topic() -> None:
    """A generic request should use the previous study topic."""
    result = bot.generate_resource_response(
        "Can you recommend a resource?",
        "SQL joins",
    )

    assert "SQLBolt" in result
    assert result.count("1. Recommended Resource") == 1
    assert result.count("2. Why It Fits") == 1
    assert result.count("3. Practice Task") == 1


def test_requested_resource_topic_overrides_previous_topic() -> None:
    """An explicit resource topic should take priority over chat context."""
    result = bot.generate_resource_response(
        "Recommend a JavaScript course",
        "SQL joins",
    )

    assert "MDN JavaScript Guide" in result
    assert "SQLBolt" not in result


def test_generate_response_returns_three_blocks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A mocked API response should be returned with all block headers."""
    create_mock = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=MOCK_RESPONSE)
                )
            ]
        )
    )
    client_mock = Mock()
    client_mock.chat.completions.create = create_mock
    openai_mock = Mock(return_value=client_mock)

    monkeypatch.setattr(bot, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    result = bot.generate_response("SQL joins")

    assert isinstance(result, str)
    assert "1. Explanation" in result
    assert "2. Real-World / Career Example" in result
    assert "3. Practice Exercise" in result
    openai_mock.assert_called_once_with(api_key="test-key")
    create_mock.assert_called_once_with(
        model=bot.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "SQL joins"},
        ],
    )


def test_generate_exercise_answer_uses_previous_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The answer helper should send prior exercise context to OpenAI."""
    create_mock = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=MOCK_ANSWER_RESPONSE)
                )
            ]
        )
    )
    client_mock = Mock()
    client_mock.chat.completions.create = create_mock
    openai_mock = Mock(return_value=client_mock)

    monkeypatch.setattr(bot, "OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    result = bot.generate_exercise_answer("SQL joins", MOCK_RESPONSE)

    assert "1. Suggested Answer" in result
    assert "2. Why It Works" in result
    assert "3. Common Mistake" in result
    create_mock.assert_called_once_with(
        model=bot.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": EXERCISE_ANSWER_PROMPT},
            {
                "role": "user",
                "content": (
                    "Study topic:\nSQL joins\n\n"
                    f"Previous Nerdbot response:\n{MOCK_RESPONSE}"
                ),
            },
        ],
    )


def test_generate_exercise_answer_without_context_skips_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An answer request without an exercise should not call OpenAI."""
    openai_mock = Mock()
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    result = bot.generate_exercise_answer("", "")

    assert result == bot.NO_PREVIOUS_EXERCISE_MESSAGE
    openai_mock.assert_not_called()


def test_generate_response_handles_empty_input_without_api_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Blank topics should return guidance without creating an API client."""
    openai_mock = Mock()
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    result = bot.generate_response("   ")

    assert result == "Please enter a study topic."
    openai_mock.assert_not_called()


def test_generate_response_rejects_long_input_without_api_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Oversized topics should be rejected before creating an API client."""
    openai_mock = Mock()
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    result = bot.generate_response("x" * (bot.MAX_USER_INPUT_LENGTH + 1))

    assert result == bot.INPUT_TOO_LONG_MESSAGE
    openai_mock.assert_not_called()


def test_generate_response_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A clear error should be raised when the API key is missing."""
    openai_mock = Mock()
    monkeypatch.setattr(bot, "OPENAI_API_KEY", None)
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    with pytest.raises(ValueError) as error:
        bot.generate_response("Python lists")

    assert str(error.value) == MISSING_API_KEY_MESSAGE
    openai_mock.assert_not_called()


def test_terminal_loop_handles_empty_input_and_exit(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The terminal loop should skip blank input and stop on exit."""
    generate_mock = Mock()
    answers = iter(["   ", "exit"])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    monkeypatch.setattr("main.generate_response", generate_mock)

    run_chat()

    output = capsys.readouterr().out
    assert "Please enter a study topic." in output
    assert "Goodbye." in output
    generate_mock.assert_not_called()


def test_terminal_loop_answers_previous_exercise(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The terminal should retain context for an answer request."""
    topic_mock = Mock(return_value=MOCK_RESPONSE)
    answer_mock = Mock(return_value=MOCK_ANSWER_RESPONSE)
    answers = iter(["SQL joins", "done", "exit"])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    monkeypatch.setattr("main.generate_response", topic_mock)
    monkeypatch.setattr("main.generate_exercise_answer", answer_mock)

    run_chat()

    output = capsys.readouterr().out
    assert "1. Suggested Answer" in output
    topic_mock.assert_called_once_with("SQL joins")
    answer_mock.assert_called_once_with("SQL joins", MOCK_RESPONSE)


def test_terminal_loop_routes_resource_request(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The terminal should use the curated resource helper."""
    resource_response = (
        "1. Recommended Resource\nSQLBolt\n\n"
        "2. Why It Fits\nInteractive SQL practice.\n\n"
        "3. Practice Task\nComplete one lesson."
    )
    resource_mock = Mock(return_value=resource_response)
    topic_mock = Mock()
    answers = iter(["Recommend a SQL course", "exit"])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    monkeypatch.setattr("main.generate_resource_response", resource_mock)
    monkeypatch.setattr("main.generate_response", topic_mock)

    run_chat()

    output = capsys.readouterr().out
    assert "1. Recommended Resource" in output
    resource_mock.assert_called_once_with("Recommend a SQL course", "")
    topic_mock.assert_not_called()


def test_terminal_loop_hides_internal_error_details(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Unexpected failures should not expose upstream error details."""
    answers = iter(["SQL joins", "exit"])
    generate_mock = Mock(
        side_effect=RuntimeError(
            "upstream response included /internal/path and secret-data"
        )
    )

    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))
    monkeypatch.setattr("main.generate_response", generate_mock)

    run_chat()

    output = capsys.readouterr().out
    assert bot.GENERATION_ERROR_MESSAGE in output
    assert "/internal/path" not in output
    assert "secret-data" not in output
