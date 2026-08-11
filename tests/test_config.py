"""Tests for local and deployed configuration loading."""

import pytest
import streamlit as st

import src.config as config


def test_streamlit_secret_reader_uses_runtime_secrets(
    monkeypatch,
) -> None:
    """The Streamlit reader should return a configured cloud secret."""
    monkeypatch.setattr(st.runtime, "exists", lambda: True)
    monkeypatch.setattr(st, "secrets", {"OPENAI_MODEL": "cloud-model"})

    assert config.get_streamlit_secret("OPENAI_MODEL") == "cloud-model"


def test_environment_value_takes_priority(
    monkeypatch,
) -> None:
    """Environment variables should override Streamlit secrets."""
    monkeypatch.setenv("OPENAI_MODEL", "local-model")
    monkeypatch.setattr(
        config,
        "get_streamlit_secret",
        lambda _name: "cloud-model",
    )

    assert config.get_config_value("OPENAI_MODEL") == "local-model"


def test_streamlit_secret_is_used_as_fallback(
    monkeypatch,
) -> None:
    """Streamlit secrets should be used when no environment value exists."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(
        config,
        "get_streamlit_secret",
        lambda _name: "cloud-key",
    )

    assert config.get_config_value("OPENAI_API_KEY") == "cloud-key"


def test_config_default_is_used_without_other_sources(
    monkeypatch,
) -> None:
    """The model default should apply when neither source has a value."""
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    monkeypatch.setattr(
        config,
        "get_streamlit_secret",
        lambda _name: None,
    )

    assert config.get_config_value("OPENAI_MODEL", "default-model") == (
        "default-model"
    )


def test_positive_number_config_reads_a_valid_override(
    monkeypatch,
) -> None:
    """A valid numeric setting should override the default."""
    monkeypatch.setenv("RATE_LIMIT_COOLDOWN_SECONDS", "7.5")

    assert config.get_positive_number_config(
        "RATE_LIMIT_COOLDOWN_SECONDS", 3.0
    ) == 7.5


@pytest.mark.parametrize(
    "raw_value",
    ["", "abc", "0", "-5", "none", "3 seconds"],
)
def test_invalid_limit_falls_back_to_the_default(
    monkeypatch,
    raw_value: str,
) -> None:
    """A bad limit must fall back, never disable rate limiting.

    Treating an unparseable or non-positive value as "no limit" would let a
    typo in deployment secrets silently remove the spend ceiling.
    """
    monkeypatch.setenv("RATE_LIMIT_SESSION_PER_HOUR", raw_value)

    assert config.get_positive_number_config(
        "RATE_LIMIT_SESSION_PER_HOUR", 30
    ) == 30


def test_rate_limit_defaults_are_positive() -> None:
    """The shipped defaults should all be usable, positive limits."""
    assert config.RATE_LIMIT_COOLDOWN_SECONDS > 0
    assert config.RATE_LIMIT_SESSION_PER_HOUR > 0
    assert config.RATE_LIMIT_GLOBAL_PER_HOUR > 0
    assert config.RATE_LIMIT_GLOBAL_PER_DAY >= config.RATE_LIMIT_GLOBAL_PER_HOUR
