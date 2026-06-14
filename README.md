# Nerdbot

**Connect what you study to real-world career examples and practice.**

Nerdbot is an AI-powered study mentor for students, career changers, and
early-career developers. Enter a topic and receive a focused lesson through
either a terminal chatbot or a Streamlit web app.

Every response follows one consistent learning structure:

1. Explanation
2. Real-World / Career Example
3. Practice Exercise

## Problem It Solves

Learning resources often explain what a concept means without showing where
it appears in professional work or how to practice it. That gap can make
technical subjects feel disconnected from internships, projects, and entry-
level roles.

Nerdbot combines those three learning needs in one response: understand the
concept, see its career relevance, and apply it immediately.

## MVP Features

- Accepts any study topic through a terminal or browser interface
- Returns every answer in a predictable three-block learning format
- Connects academic concepts to internships, jobs, and portfolio projects
- Provides a small practice exercise with each explanation
- Keeps chat history during a Streamlit session
- Handles blank input and missing API configuration clearly
- Uses a configurable OpenAI model
- Includes an eight-test offline suite that mocks OpenAI API calls

## Tech Stack

| Area | Technology |
|---|---|
| Language | Python 3.11+ |
| AI | OpenAI Python SDK |
| Web interface | Streamlit |
| Configuration | python-dotenv |
| Testing | pytest and Streamlit AppTest |

## Project Structure

```text
nerdbot/
├── .env.example
├── .gitignore
├── AGENTS.md
├── README.md
├── app.py                  # Streamlit web interface
├── main.py                 # Terminal interface
├── pytest.ini
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── bot.py              # OpenAI request and response logic
│   ├── config.py           # Environment configuration
│   └── prompts.py          # Three-block system prompt
├── tests/
│   ├── test_app.py         # Streamlit interface tests
│   └── test_bot.py         # Bot and terminal tests
└── docs/
    ├── build-phases.md
    ├── product-requirements.md
    └── prompt-design.md
```

## macOS Setup

### 1. Clone the repository

```bash
git clone https://github.com/renilsonjr/nerdbot.git
cd nerdbot
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

## Environment Configuration

Create a local `.env` file from the included template:

```bash
cp .env.example .env
```

Open `.env` and provide an OpenAI API key and model:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

The `.env` file is ignored by Git and must never be committed. An OpenAI API
key can be created at [platform.openai.com](https://platform.openai.com/).
API usage may incur charges on the associated OpenAI account.

## Run the Terminal Version

Activate the virtual environment, then run:

```bash
python3 main.py
```

Enter a study topic at the prompt. Type `exit` to close Nerdbot.

## Run the Streamlit Version

```bash
streamlit run app.py
```

Streamlit will print a local address, normally
[`http://localhost:8501`](http://localhost:8501), and may open it
automatically in a browser.

## Run Tests

```bash
pytest
```

The tests replace the OpenAI client with mocked responses. Running the test
suite does not send requests to the real OpenAI API.

## Example Topics

- SQL joins
- Python list comprehensions
- REST API fundamentals
- Git branching
- Object-oriented programming
- Data normalization
- Binary search
- CSS Flexbox

## Example Output Format

Every successful answer follows exactly this structure:

```text
1. Explanation
A clear, beginner-friendly explanation of the topic.

2. Real-World / Career Example
An example of how the topic appears in an internship, job, or portfolio
project.

3. Practice Exercise
A small hands-on task that applies the topic.
```

## MVP Limitations

- Requires an internet connection and a valid OpenAI API key
- Generated answers may be incomplete or inaccurate and should be verified
- Chat history exists only for the current Streamlit session
- No saved accounts, persistent study history, or multi-user support
- No automatic scoring or feedback for completed exercises
- The three-block format is prompted but not programmatically repaired if a
  model response violates it

## Future Roadmap

- Deploy the Streamlit app to a public hosting service
- Add automated response-format validation
- Add continuous integration for the pytest suite
- Improve accessibility and responsive presentation
- Add optional difficulty levels while preserving the three-block format
- Add exercise follow-up and feedback without persistent user tracking

## Author

**Renilson Rodrigues (RJ)**

[GitHub](https://github.com/renilsonjr) |
[LinkedIn](https://linkedin.com/in/renilsonjr)

## License

MIT
