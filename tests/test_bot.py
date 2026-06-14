"""Tests for Nerdbot's core response and terminal behavior."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import src.bot as bot
from main import run_chat
from src.prompts import SYSTEM_PROMPT


MOCK_RESPONSE = """1. Explanation
SQL joins combine related data from multiple tables.

2. Real-World / Career Example
A data analyst uses joins to combine customer and order data.

3. Practice Exercise
Write a query that joins a Customers table to an Orders table."""


def test_system_prompt_exists() -> None:
    """The system prompt should exist and define all required blocks."""
    assert SYSTEM_PROMPT.strip()
    assert "1. Explanation" in SYSTEM_PROMPT
    assert "2. Real-World / Career Example" in SYSTEM_PROMPT
    assert "3. Practice Exercise" in SYSTEM_PROMPT


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


def test_generate_response_handles_empty_input_without_api_call(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Blank topics should return guidance without creating an API client."""
    openai_mock = Mock()
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    result = bot.generate_response("   ")

    assert result == "Please enter a study topic."
    openai_mock.assert_not_called()


def test_generate_response_requires_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A clear error should be raised when the API key is missing."""
    openai_mock = Mock()
    monkeypatch.setattr(bot, "OPENAI_API_KEY", None)
    monkeypatch.setattr(bot, "OpenAI", openai_mock)

    with pytest.raises(ValueError, match="OPENAI_API_KEY is missing"):
        bot.generate_response("Python lists")

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
