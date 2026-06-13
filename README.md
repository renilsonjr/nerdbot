# Nerdbot 🤖

An AI-powered study mentor that connects academic topics to real-world career examples and hands-on practice exercises.

---

## What it does

You type a study topic. Nerdbot always responds with exactly three blocks:

```
1. Explanation
   A clear, beginner-friendly explanation of the topic.

2. Real-World / Career Example
   How this topic appears in a real internship, job, or portfolio project.

3. Practice Exercise
   A small hands-on task to apply what you just learned.
```

---

## Who it is for

- Computer Science, Data Science, IT, and Web Development students
- Bootcamp students and recent graduates
- Career changers breaking into tech
- Anyone preparing for internships or their first tech job

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.11+ |
| AI API | OpenAI API |
| Model | Configurable via `.env` (default: `gpt-4o-mini`) |
| Phase 1 interface | Terminal |
| Phase 2 interface | Streamlit |
| Tests | pytest |
| Version control | Git + GitHub |

---

## Project structure

```
nerdbot/
├── .env                  # Your API key and model config (never push this)
├── .env.example          # Template showing required environment variables
├── .gitignore
├── README.md
├── AGENTS.md             # Instructions for Codex and AI coding agents
├── requirements.txt
├── main.py               # Terminal chatbot entry point
├── app.py                # Streamlit web app entry point
├── src/
│   ├── __init__.py
│   ├── config.py         # Loads environment variables
│   ├── prompts.py        # System prompt
│   └── bot.py            # Core response logic
├── tests/
│   └── test_bot.py       # Unit tests (no real API calls)
└── docs/
    ├── product-requirements.md
    ├── build-phases.md
    └── prompt-design.md
```

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/renilsonjr/nerdbot.git
cd nerdbot
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini
```

Get your API key at: [platform.openai.com](https://platform.openai.com)

---

## Running the terminal bot

```bash
python3 main.py
```

Example session:

```
Welcome to Nerdbot.
Type a study topic, or type 'exit' to quit.

You: SQL joins

Nerdbot:
1. Explanation
SQL joins combine rows from two or more tables using a shared column...

2. Real-World / Career Example
In a data analyst internship, you may be asked to find customers who
registered but never made a purchase. This is a LEFT JOIN use case...

3. Practice Exercise
You have two tables: Customers and Orders.
Write a query that returns all customers, including those without orders.
Type "done" when you finish and Nerdbot will show you the answer.

You: exit
Goodbye.
```

---

## Running the web app

```bash
streamlit run app.py
```

Opens Nerdbot in your browser at `localhost:8501`.

---

## Running tests

```bash
pytest
```

Tests verify bot logic using mocked responses — no real API calls needed.

---

## Build phases

| Phase | Name | Status |
|---|---|---|
| 1 | API Connection | 🔲 |
| 2 | System Prompt & 3-Block Structure | 🔲 |
| 3 | Terminal Chat Loop | 🔲 |
| 4 | Streamlit Web Interface | 🔲 |
| 5 | Tests | 🔲 |
| 6 | Portfolio & Deployment | 🔲 |

---

## Future roadmap

- Book recommendations per topic
- YouTube / podcast search
- Portfolio project generator
- Interview question generator
- Resume bullet generator
- User study history
- Animated mascot character

---

## Author

**Renilson Rodrigues (RJ)**
[github.com/renilsonjr](https://github.com/renilsonjr) · [linkedin.com/in/renilsonjr](https://linkedin.com/in/renilsonjr)

---

## License

MIT