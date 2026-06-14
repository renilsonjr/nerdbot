# AGENTS.md — Nerdbot

Instructions for Codex and AI coding agents working on this project.

---

## Project summary

Nerdbot is an AI study mentor built in Python.

For a normal study topic, the bot responds in exactly 3 blocks:

1. Explanation
2. Real-World / Career Example
3. Practice Exercise

When the user asks for the previous exercise answer, the bot responds in
exactly 3 different blocks:

1. Suggested Answer
2. Why It Works
3. Common Mistake

These fixed structures are core product decisions. Do not change them.

---

## Tech stack

- Python 3.11+
- OpenAI Python SDK (`openai`)
- `python-dotenv` for environment variables
- `pytest` for testing
- Streamlit for the web interface

---

## Environment variables

All configuration is loaded from `.env`.

Required variables:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Never hardcode the API key or model name in Python files.
Always load them using `os.getenv()` via `src/config.py`.

---

## File responsibilities

| File | Purpose |
|---|---|
| `src/config.py` | Loads and exposes environment variables |
| `src/prompts.py` | Contains the topic and exercise-answer prompts |
| `src/bot.py` | Contains shared detection and response generation |
| `main.py` | Terminal chat loop — imports from `src/` only |
| `app.py` | Streamlit web interface — imports from `src/` only |
| `tests/test_bot.py` | Bot and terminal tests using mocked responses |
| `tests/test_app.py` | Streamlit tests using mocked responses |

---

## Core function signature

The main function in `src/bot.py` must follow this signature:

```python
def generate_response(topic: str) -> str:
    """
    Receives a study topic string.
    Returns a formatted string with exactly 3 blocks:
    1. Explanation
    2. Real-World / Career Example
    3. Practice Exercise
    """
```

Do not change this signature without updating the tests.

---

## System prompt rules

Both prompts live in `src/prompts.py` as `SYSTEM_PROMPT` and
`EXERCISE_ANSWER_PROMPT`.

The topic prompt must instruct the model to:

- Always respond in exactly 3 numbered blocks
- Keep explanations beginner-friendly by default
- Never add sections outside the 3 blocks
- Never mention that it is following a prompt
- Make a reasonable assumption if the topic is unclear and still respond

The exercise-answer prompt must require exactly:

1. Suggested Answer
2. Why It Works
3. Common Mistake

Do not modify either prompt structure without updating `tests/test_bot.py`.

Each set of three headings is a product contract shared by both interfaces. Future
features may change the detail or difficulty of an answer, but must not rename,
reorder, remove, or add to these blocks.

Required heading strings:

```text
1. Explanation
2. Real-World / Career Example
3. Practice Exercise
```

Required exercise-answer heading strings:

```text
1. Suggested Answer
2. Why It Works
3. Common Mistake
```

Do not create interface-specific prompts. Both `main.py` and `app.py` must use
the shared detection and generation helpers from `src/bot.py`.

---

## What NOT to build

Do not add any of the following unless explicitly instructed:

- Database or ORM
- User authentication or login
- Web search or YouTube search
- Book recommendation engine
- Vector database (ChromaDB, pgvector)
- FastAPI or any REST API layer
- Payments or subscriptions
- Animated character or mascot
- Mobile app
- Multi-user tracking
- Export buttons

---

## Current MVP

The following features are implemented and should remain working:

- Real OpenAI responses through `generate_response(topic)`
- Terminal chat in `main.py`, including blank input and `exit`
- Streamlit chat in `app.py` with session history
- Clear missing-key errors in both interfaces
- Offline bot, terminal, and Streamlit tests

Keep interface code thin. Shared response behavior belongs in `src/bot.py`;
configuration belongs in `src/config.py`; prompt rules belong in
`src/prompts.py`.

---

## Code style rules

- Use clear, readable variable names
- Add a short docstring to every function
- Keep functions small — one responsibility per function
- Do not print debug output in `src/` files — only in `main.py` and `app.py`

---

## Testing rules

Run tests with:

```bash
pytest
```

All tests must pass before moving to the next phase.

Never write a test that calls the real OpenAI API. Patch the OpenAI client or
`generate_response` before submitting test input. Use mocked responses that
simulate the expected three-block structure.

At minimum, tests must continue to verify:

- Empty input does not call the API
- Missing API configuration produces a clear error
- `SYSTEM_PROMPT` exists and includes all three headings
- `generate_response()` returns a string with all three headings
- Terminal exit behavior works without an API call
- Streamlit chat history renders with a mocked response

---

## Git rules

- Commit after each phase is complete and tested
- Use clear commit messages:

```
feat: phase 1 - api connection working
feat: phase 2 - system prompt and 3-block structure
feat: phase 3 - terminal chat loop
feat: phase 4 - streamlit web interface
feat: phase 5 - pytest unit tests
feat: phase 6 - readme, deploy, portfolio
```

- Never commit `.env`
- Never commit `venv/`
- Always verify `.gitignore` is working before the first push
