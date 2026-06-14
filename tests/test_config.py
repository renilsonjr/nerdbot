"""Tests for local and deployed configuration loading."""

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
