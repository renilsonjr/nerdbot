# Nerdbot

**Connect what you study to real-world career examples and practice.**

Nerdbot is an AI-powered study mentor for students, career changers, and
early-career developers. Enter a topic and receive a focused lesson through
either a terminal chatbot or a Streamlit web app.

Nerdbot supports three focused response modes:

1. Study a topic
2. Review a practice exercise answer
3. Find a curated learning resource

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
- Shows a suggested answer when the user finishes an exercise
- Recommends curated beginner resources without web search
- Keeps chat history during a Streamlit session
- Handles blank input and missing API configuration clearly
- Uses a configurable OpenAI model
- Includes an offline test suite that mocks OpenAI API calls

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
├── data/
│   └── resources.json      # Curated learning resources
├── main.py                 # Terminal interface
├── pytest.ini
├── requirements.txt
├── screenshots/           # Portfolio screenshots
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

Configuration is loaded in this order:

1. Environment variables, including values loaded from a local `.env` file
2. Streamlit Community Cloud secrets
3. The default model value, when `OPENAI_MODEL` is not configured

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

## Deploy to Streamlit Community Cloud

1. Push the project to a GitHub repository. Confirm that `.env` is not
   committed.
2. Sign in to
   [Streamlit Community Cloud](https://share.streamlit.io/).
3. Create a new app and select the Nerdbot repository and branch.
4. Set the app entry point to `app.py`.
5. Open the app's **Advanced settings** or **Secrets** editor.
6. Add the configuration shown below, replacing the placeholder key.
7. Save the secrets and deploy the app.

### Streamlit Secrets

Add these values using TOML syntax in the Streamlit secrets editor:

```toml
OPENAI_API_KEY = "your_key_here"
OPENAI_MODEL = "gpt-4o-mini"
```

Do not paste a real API key into `README.md`, source code, GitHub, deployment
logs, or screenshots. Streamlit makes these values available to the deployed
app through `st.secrets`; Nerdbot does not display their contents.

## Screenshots

The following placeholders are reserved for authentic captures of the
Streamlit app. No generated or simulated screenshots are used.

### Home Screen

![Nerdbot home screen](screenshots/nerdbot-home.png)

### SQL Example

![Nerdbot SQL example](screenshots/nerdbot-sql-example.png)

### Chat History

![Nerdbot chat history](screenshots/nerdbot-chat-history.png)

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

## Response Modes

### 1. Study Topic

Enter a topic such as `SQL joins`. Nerdbot responds with exactly:

```text
1. Explanation
A clear, beginner-friendly explanation of the topic.

2. Real-World / Career Example
An example of how the topic appears in an internship, job, or portfolio
project.

3. Practice Exercise
A small hands-on task that applies the topic.
```

### 2. Exercise Answer

After completing an exercise, enter `done`, `show answer`, `answer`,
`I finished`, or `finished`. Nerdbot uses the previous exercise and responds
with exactly:

```text
1. Suggested Answer
An example of a correct solution.

2. Why It Works
A beginner-friendly explanation of the solution.

3. Common Mistake
A likely mistake and guidance for avoiding it.
```

### 3. Curated Resource

Ask for a book, course, article, video, resource, or recommendation to receive
an offline recommendation from Nerdbot's curated catalog. The response uses
exactly:

```text
1. Recommended Resource
A beginner-friendly resource and its link.

2. Why It Fits
Why the resource matches the requested topic.

3. Practice Task
A small task to complete while using the resource.
```

The catalog currently covers Python, SQL, HTML/CSS, JavaScript, APIs, data
analysis, and cybersecurity basics. Resource requests do not use web search.

## Release History

| Release | Highlights |
|---|---|
| `v0.1-streamlit-mvp` | Terminal and Streamlit chat interfaces with the original study-topic response format |
| `v0.2-exercise-answer` | Previous-exercise context and suggested answer responses |
| `v0.3-curated-resources` | Offline, curated recommendations across seven beginner topics |

## MVP Limitations

- Requires an internet connection and a valid OpenAI API key
- Messages are limited to 4,000 characters to control request size
- Generated answers may be incomplete or inaccurate and should be verified
- Chat history exists only for the current Streamlit session
- Exercise context exists only for the current terminal or Streamlit session
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
