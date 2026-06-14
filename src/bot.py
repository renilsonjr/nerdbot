"""Core OpenAI response generation for Nerdbot."""

import re

from openai import OpenAI

from src.config import (
    MISSING_API_KEY_MESSAGE,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from src.prompts import EXERCISE_ANSWER_PROMPT, SYSTEM_PROMPT


NO_PREVIOUS_EXERCISE_MESSAGE = (
    "Please enter a study topic first so Nerdbot can create an exercise."
)
ANSWER_REQUEST_PHRASES = {
    "answer",
    "done",
    "finished",
    "i finished",
    "show answer",
}


def is_answer_request(user_input: str) -> bool:
    """Return whether the input asks for the previous exercise answer."""
    normalized_input = re.sub(r"[^\w\s]", "", user_input.lower())
    normalized_input = " ".join(normalized_input.split())
    return normalized_input in ANSWER_REQUEST_PHRASES


def _create_completion(system_prompt: str, user_content: str) -> str:
    """Call OpenAI and return a non-empty response string."""
    if not OPENAI_API_KEY:
        raise ValueError(MISSING_API_KEY_MESSAGE)

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Nerdbot received an empty response from OpenAI.")

    return content.strip()


def generate_response(topic: str) -> str:
    """Return Nerdbot's three-block study response for a topic."""
    cleaned_topic = topic.strip()
    if not cleaned_topic:
        return "Please enter a study topic."

    return _create_completion(SYSTEM_PROMPT, cleaned_topic)


def generate_exercise_answer(
    previous_topic: str,
    previous_response: str,
) -> str:
    """Return a three-block answer to the previous practice exercise."""
    if not previous_topic.strip() or not previous_response.strip():
        return NO_PREVIOUS_EXERCISE_MESSAGE

    context = (
        f"Study topic:\n{previous_topic.strip()}\n\n"
        f"Previous Nerdbot response:\n{previous_response.strip()}"
    )
    return _create_completion(EXERCISE_ANSWER_PROMPT, context)
