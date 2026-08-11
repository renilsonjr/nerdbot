"""Streamlit web interface for Nerdbot."""

import streamlit as st

from src.bot import (
    GENERATION_ERROR_MESSAGE,
    MissingAPIKeyError,
    NO_PREVIOUS_EXERCISE_MESSAGE,
    generate_exercise_answer,
    generate_resource_response,
    generate_response,
    is_answer_request,
    is_resource_request,
    validate_user_input,
)
from src.config import (
    MISSING_API_KEY_MESSAGE,
    OPENAI_API_KEY,
    RATE_LIMIT_COOLDOWN_SECONDS,
    RATE_LIMIT_GLOBAL_PER_DAY,
    RATE_LIMIT_GLOBAL_PER_HOUR,
    RATE_LIMIT_SESSION_PER_HOUR,
)
from src.ratelimit import (
    RateLimitDecision,
    RateLimiter,
    build_global_limiter,
    build_session_limiter,
    rate_limit_message,
)


@st.cache_resource
def get_global_limiter() -> RateLimiter:
    """Return the deployment-wide limiter shared by every session.

    ``st.cache_resource`` gives one instance per app process, so all visitors
    draw from the same budget. The counter is in memory: it resets if the app
    restarts or is replicated, which makes this a spend ceiling for casual
    abuse rather than an exact ledger.
    """
    return build_global_limiter(
        RATE_LIMIT_GLOBAL_PER_HOUR,
        RATE_LIMIT_GLOBAL_PER_DAY,
    )


def initialize_chat_history() -> None:
    """Create the session chat history on the first app run."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "previous_exercise" not in st.session_state:
        st.session_state.previous_exercise = None
    if "rate_limiter" not in st.session_state:
        st.session_state.rate_limiter = build_session_limiter(
            RATE_LIMIT_COOLDOWN_SECONDS,
            RATE_LIMIT_SESSION_PER_HOUR,
        )


def uses_openai(topic: str, previous_exercise: dict | None) -> bool:
    """Return whether answering this input will call the OpenAI API.

    Curated resource recommendations are served from local data and cost
    nothing, so they are deliberately left unlimited.
    """
    if is_answer_request(topic):
        return previous_exercise is not None
    if is_resource_request(topic):
        return False
    return True


def check_rate_limits() -> RateLimitDecision:
    """Consume one unit of session and deployment-wide budget.

    The session limiter is checked first so a single visitor sees their own
    limit rather than a shared one. When the global limiter then rejects, the
    session unit is already spent - harmless, since the app is capped for
    everyone at that point anyway.
    """
    session_decision = st.session_state.rate_limiter.try_acquire()
    if not session_decision.allowed:
        return session_decision
    return get_global_limiter().try_acquire()


def display_chat_history() -> None:
    """Render all saved user and assistant messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def main() -> None:
    """Render the Nerdbot Streamlit application."""
    st.set_page_config(page_title="Nerdbot")
    st.title("Nerdbot")
    st.write(
        "Connect what you study to real-world career examples and practice."
    )
    st.markdown(
        """
**What you can ask**

- Enter a study topic to get an explanation, career example, and exercise.
- Type `done` after an exercise to see a suggested answer.
- Ask for a book, course, article, video, or resource recommendation.

**Try one of these**

`SQL joins` ·  `recommend a book for Python` ·
`recommend a cybersecurity resource`
"""
    )

    initialize_chat_history()
    display_chat_history()

    if not OPENAI_API_KEY:
        st.error(MISSING_API_KEY_MESSAGE)

    topic = st.chat_input(
        "Enter a study topic",
        disabled=not OPENAI_API_KEY,
    )
    if topic is None:
        return

    validation_error = validate_user_input(topic)
    if validation_error:
        st.warning(validation_error)
        return
    cleaned_topic = topic.strip()

    st.session_state.messages.append(
        {"role": "user", "content": cleaned_topic}
    )
    with st.chat_message("user"):
        st.markdown(cleaned_topic)

    if uses_openai(cleaned_topic, st.session_state.previous_exercise):
        decision = check_rate_limits()
        if not decision.allowed:
            limit_message = rate_limit_message(decision)
            with st.chat_message("assistant"):
                st.warning(limit_message)
            st.session_state.messages.append(
                {"role": "assistant", "content": limit_message}
            )
            return

    try:
        with st.chat_message("assistant"):
            with st.spinner("Connecting the dots..."):
                if is_answer_request(cleaned_topic):
                    previous_exercise = st.session_state.previous_exercise
                    if previous_exercise is None:
                        response = NO_PREVIOUS_EXERCISE_MESSAGE
                    else:
                        response = generate_exercise_answer(
                            previous_exercise["topic"],
                            previous_exercise["response"],
                        )
                elif is_resource_request(cleaned_topic):
                    previous_exercise = st.session_state.previous_exercise
                    previous_topic = (
                        previous_exercise["topic"]
                        if previous_exercise is not None
                        else ""
                    )
                    response = generate_resource_response(
                        cleaned_topic,
                        previous_topic,
                    )
                else:
                    response = generate_response(cleaned_topic)
                    st.session_state.previous_exercise = {
                        "topic": cleaned_topic,
                        "response": response,
                    }
            st.markdown(response)
    except MissingAPIKeyError as error:
        st.error(f"Configuration error: {error}")
        return
    except Exception:
        st.error(GENERATION_ERROR_MESSAGE)
        return

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )


if __name__ == "__main__":
    main()
