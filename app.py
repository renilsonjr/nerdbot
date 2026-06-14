"""Streamlit web interface for Nerdbot."""

import streamlit as st

from src.bot import (
    NO_PREVIOUS_EXERCISE_MESSAGE,
    generate_exercise_answer,
    generate_response,
    is_answer_request,
)
from src.config import MISSING_API_KEY_MESSAGE, OPENAI_API_KEY


def initialize_chat_history() -> None:
    """Create the session chat history on the first app run."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "previous_exercise" not in st.session_state:
        st.session_state.previous_exercise = None


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

    cleaned_topic = topic.strip()
    if not cleaned_topic:
        st.warning("Please enter a study topic.")
        return

    st.session_state.messages.append(
        {"role": "user", "content": cleaned_topic}
    )
    with st.chat_message("user"):
        st.markdown(cleaned_topic)

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
                else:
                    response = generate_response(cleaned_topic)
                    st.session_state.previous_exercise = {
                        "topic": cleaned_topic,
                        "response": response,
                    }
            st.markdown(response)
    except ValueError as error:
        st.error(f"Configuration error: {error}")
        return
    except Exception as error:
        st.error(f"Nerdbot could not generate a response: {error}")
        return

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )


if __name__ == "__main__":
    main()
