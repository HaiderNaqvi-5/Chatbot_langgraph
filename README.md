# Chatbot LangGraph API

A FastAPI chat backend built with LangChain, LangGraph, Groq, and PostgreSQL. It stores conversations and messages in the database, then uses an LLM workflow to generate responses.

## Features

- REST API for creating conversations and sending messages
- Groq-hosted LLM integration via LangChain
- LangGraph orchestration for chat workflow
- PostgreSQL persistence for conversation history
- FastAPI docs available at `/docs`
- Pytest-based test suite with mocked LLM behavior

## Tech stack

- Python 3.11+
- FastAPI
- LangChain
- LangGraph
- Groq
- PostgreSQL
- Tortoise ORM
- Pydantic Settings
- Pytest

## Project structure

```text
Chatbot_langgraph/
├── controllers/          # API route handlers
├── helpers/              # settings, DB config, dependency setup
├── models/               # database models
├── services/             # LLM, chat workflow, history logic
├── utils/                # request/response schemas
├── tests/                # automated tests
├── main.py               # FastAPI app entrypoint
├── requirements.txt      # Python dependencies
├── .env                  # local environment secrets (not committed)
├── .gitignore            # git exclusions
├── README.md             # project overview and setup guide
├── pyproject.toml        # Python project metadata/config
└── .env.example          # example environment file
```

## Prerequisites

- Python 3.11+
- PostgreSQL database running locally or on a reachable host
- Groq API key

## Setup

```bash
cd C:\Users\Admin\Chatbot_langgraph
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in the required values:

```env
DATABASE_URL=postgresql+asyncpg://postgres:your_password@127.0.0.1:5432/chatdb
groq_api_key=your_groq_api_key
groq_model=llama-3.1-8b-instant
groq_temperature=0.2
groq_max_tokens=512
groq_timeout_seconds=30
system_prompt=You are a helpful assistant.
```

## Run the app

```bash
uvicorn main:app --reload
```

Open:

- API docs: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

## Example API usage

Create a conversation:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/conversations \
  -H "Content-Type: application/json" \
  -d '{"title":"FastAPI doubts","owner_id":"student_01"}'
```

Send a message:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/conversations/<conversation_id>/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain dependency injection in simple terms."}'
```

## Testing

```bash
pytest -q
```

## Notes

- This app uses a LangGraph workflow for processing chat requests.
- The project is structured for local development and production-like deployment via environment-level configuration.
- Tests avoid calling Groq directly by overriding the LLM dependency.
