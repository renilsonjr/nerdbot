"""Core OpenAI response generation for Nerdbot."""

from openai import OpenAI

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from src.prompts import SYSTEM_PROMPT


def generate_response(topic: str) -> str:
    """Return Nerdbot's three-block study response for a topic."""
    cleaned_topic = topic.strip()
    if not cleaned_topic:
        return "Please enter a study topic."

    if not OPENAI_API_KEY:
        raise ValueError(
            "OPENAI_API_KEY is missing. Add it to your .env file and try again."
        )

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": cleaned_topic},
        ],
    )
    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("Nerdbot received an empty response from OpenAI.")

    return content.strip()
