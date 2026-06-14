"""Configuration loading for local and Streamlit deployments."""

import os

from dotenv import load_dotenv


load_dotenv()

MISSING_API_KEY_MESSAGE = (
    "OPENAI_API_KEY is missing. Add it to Streamlit Secrets for deployment "
    "or to your local .env file for local development."
)


def get_streamlit_secret(name: str) -> str | None:
    """Return a Streamlit secret when running inside Streamlit."""
    try:
        import streamlit as st

        if not st.runtime.exists():
            return None

        value = st.secrets.get(name)
        return str(value) if value is not None else None
    except (AttributeError, FileNotFoundError, KeyError):
        return None


def get_config_value(name: str, default: str | None = None) -> str | None:
    """Load a value from the environment, then Streamlit secrets."""
    return os.getenv(name) or get_streamlit_secret(name) or default


OPENAI_API_KEY = get_config_value("OPENAI_API_KEY")
OPENAI_MODEL = get_config_value("OPENAI_MODEL", "gpt-4o-mini")
