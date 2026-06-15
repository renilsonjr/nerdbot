"""Core OpenAI response generation for Nerdbot."""

import json
import re
from pathlib import Path
from typing import Any

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
MAX_USER_INPUT_LENGTH = 4000
INPUT_TOO_LONG_MESSAGE = (
    f"Please keep your message under {MAX_USER_INPUT_LENGTH} characters."
)
GENERATION_ERROR_MESSAGE = (
    "Nerdbot could not generate a response. Please try again."
)
ANSWER_REQUEST_PHRASES = {
    "answer",
    "done",
    "finished",
    "i finished",
    "show answer",
}
RESOURCE_REQUEST_TERMS = {
    "article",
    "articles",
    "book",
    "books",
    "course",
    "courses",
    "recommend",
    "recommendations",
    "recommendation",
    "resource",
    "resources",
    "suggest",
    "video",
    "videos",
}
RESOURCES_PATH = Path(__file__).resolve().parent.parent / "data" / "resources.json"


class MissingAPIKeyError(ValueError):
    """Raised when no OpenAI API key is configured."""


def is_answer_request(user_input: str) -> bool:
    """Return whether the input asks for the previous exercise answer."""
    normalized_input = re.sub(r"[^\w\s]", "", user_input.lower())
    normalized_input = " ".join(normalized_input.split())
    return normalized_input in ANSWER_REQUEST_PHRASES


def validate_user_input(user_input: str) -> str | None:
    """Return a user-facing validation error, if any."""
    if not user_input.strip():
        return "Please enter a study topic."
    if len(user_input) > MAX_USER_INPUT_LENGTH:
        return INPUT_TOO_LONG_MESSAGE
    return None


def is_resource_request(user_input: str) -> bool:
    """Return whether the input asks for a learning resource."""
    normalized_input = re.sub(r"[^\w\s]", " ", user_input.lower())
    words = set(normalized_input.split())
    return bool(words & RESOURCE_REQUEST_TERMS)


def _load_resources() -> list[dict[str, Any]]:
    """Load the curated resource catalog from disk."""
    with RESOURCES_PATH.open(encoding="utf-8") as resources_file:
        return json.load(resources_file)


def _find_resource(
    request: str,
    previous_topic: str = "",
) -> dict[str, Any] | None:
    """Find a curated resource using the request or previous topic."""
    resources = _load_resources()
    for searchable_text in (request.lower(), previous_topic.lower()):
        if not searchable_text:
            continue
        for resource in resources:
            aliases = resource.get("aliases", [])
            if any(
                re.search(rf"\b{re.escape(alias.lower())}\b", searchable_text)
                for alias in aliases
            ):
                return resource
    return None


def generate_resource_response(
    request: str,
    previous_topic: str = "",
) -> str:
    """Return a three-block recommendation from the curated catalog."""
    resource = _find_resource(request, previous_topic)
    if resource is None:
        return (
            "1. Recommended Resource\n"
            "Tell me which topic you want a resource for: Python, SQL, "
            "HTML/CSS, JavaScript, APIs, data analysis, or cybersecurity "
            "basics.\n\n"
            "2. Why It Fits\n"
            "Knowing the topic lets Nerdbot choose a focused, "
            "beginner-friendly resource from its curated catalog.\n\n"
            "3. Practice Task\n"
            "Choose one topic from the list and ask for a book, course, "
            "video, article, or resource."
        )

    return (
        "1. Recommended Resource\n"
        f"{resource['resource']} ({resource['type']}): {resource['url']}\n\n"
        "2. Why It Fits\n"
        f"{resource['why']}\n\n"
        "3. Practice Task\n"
        f"{resource['practice_task']}"
    )


def _create_completion(system_prompt: str, user_content: str) -> str:
    """Call OpenAI and return a non-empty response string."""
    if not OPENAI_API_KEY:
        raise MissingAPIKeyError(MISSING_API_KEY_MESSAGE)

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
    validation_error = validate_user_input(topic)
    if validation_error:
        return validation_error

    return _create_completion(SYSTEM_PROMPT, topic.strip())


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
