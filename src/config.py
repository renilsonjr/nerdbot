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


def get_positive_number_config(name: str, default: float) -> float:
    """Load a positive numeric setting, falling back to the default.

    A misconfigured limit must never disable rate limiting, so anything
    unparseable or non-positive falls back to the documented default rather
    than raising or being used as-is.
    """
    raw_value = get_config_value(name)
    if raw_value is None:
        return default

    try:
        value = float(str(raw_value).strip())
    except ValueError:
        return default

    return value if value > 0 else default


OPENAI_API_KEY = get_config_value("OPENAI_API_KEY")
OPENAI_MODEL = get_config_value("OPENAI_MODEL", "gpt-4o-mini")

# Rate limits for the public deployment. Every request spends the operator's
# OpenAI budget, so these bound both a single visitor and the whole app.
RATE_LIMIT_COOLDOWN_SECONDS = get_positive_number_config(
    "RATE_LIMIT_COOLDOWN_SECONDS", 3.0
)
RATE_LIMIT_SESSION_PER_HOUR = int(
    get_positive_number_config("RATE_LIMIT_SESSION_PER_HOUR", 30)
)
RATE_LIMIT_GLOBAL_PER_HOUR = int(
    get_positive_number_config("RATE_LIMIT_GLOBAL_PER_HOUR", 250)
)
RATE_LIMIT_GLOBAL_PER_DAY = int(
    get_positive_number_config("RATE_LIMIT_GLOBAL_PER_DAY", 1000)
)
