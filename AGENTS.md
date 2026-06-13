# AGENTS.md — Nerdbot

Instructions for Codex and AI coding agents working on this project.

---

## Project summary

Nerdbot is an AI study mentor built in Python.

The user types a study topic. The bot always responds in exactly 3 blocks:

1. Explanation
2. Real-World / Career Example
3. Practice Exercise

This fixed structure is the core product decision. Do not change it.

---

## Tech stack

- Python 3.11+
- OpenAI Python SDK (`openai`)
- `python-dotenv` for environment variables
- `pytest` for testing
- Streamlit for the web interface (Phase 4 only)

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
| `src/prompts.py` | Contains the system prompt string only |
| `src/bot.py` | Contains `generate_response(topic: str) -> str` |
| `main.py` | Terminal chat loop — imports from `src/` only |
| `app.py` | Streamlit web interface — imports from `src/` only |
| `tests/test_bot.py` | Unit tests using mocked OpenAI responses |

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

The system prompt lives in `src/prompts.py` as a string constant named `SYSTEM_PROMPT`.

The prompt must instruct the model to:

- Always respond in exactly 3 numbered blocks
- Keep explanations beginner-friendly by default
- Never add sections outside the 3 blocks
- Never mention that it is following a prompt
- Make a reasonable assumption if the topic is unclear and still respond

Do not modify the prompt structure without updating `tests/test_bot.py` to match.

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

## Build order

Always build in this order. Do not skip phases.

### Phase 1 — API Connection
- Load API key and model from `.env` via `src/config.py`
- Send a test message to the OpenAI API
- Print the response in the terminal
- Confirm connection works before moving on

### Phase 2 — System Prompt and 3-Block Structure
- Write `SYSTEM_PROMPT` in `src/prompts.py`
- Implement `generate_response(topic)` in `src/bot.py`
- The function must call the OpenAI API with the system prompt
- The response must always contain the 3 blocks

### Phase 3 — Terminal Chat Loop
- Implement the interactive loop in `main.py`
- User types a topic → bot responds
- User types `exit` → program ends with "Goodbye."
- Handle empty input gracefully (do not call the API)
- Handle missing API key with a clear error message

### Phase 4 — Streamlit Web Interface
- Build `app.py` using Streamlit
- Include: page title, short description, chat input, chat history, formatted 3-block responses
- Do not mix terminal logic into `app.py` — import from `src/` only

### Phase 5 — Tests
- All tests go in `tests/test_bot.py`
- Tests must NOT call the real OpenAI API
- Use `unittest.mock` or `pytest-mock` to mock the API response
- Tests must verify:
  - Empty input is handled without calling the API
  - `SYSTEM_PROMPT` exists and is not empty
  - `generate_response()` returns a string
  - The response contains the 3 required block headers

### Phase 6 — Portfolio and Deployment
- Complete `README.md` with screenshots and example outputs
- Deploy to Streamlit Community Cloud
- Confirm the public URL works

---

## Code style rules

- Use clear, readable variable names
- Add a short docstring to every function
- Keep functions small — one responsibility per function
- Do not use global variables
- Do not print debug output in `src/` files — only in `main.py` and `app.py`

---

## Testing rules

Run tests with:

```bash
pytest
```

All tests must pass before moving to the next phase.

Never write a test that calls the real OpenAI API.
Use mocked responses that simulate the expected 3-block structure.

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