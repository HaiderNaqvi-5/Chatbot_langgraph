# FlowChat API

> A persistent FastAPI chat backend that uses LangGraph and Groq to generate and stream replies while keeping conversation history in PostgreSQL.

Repository: [HaiderNaqvi-5/FlowChat-API](https://github.com/HaiderNaqvi-5/FlowChat-API)

A FastAPI chat backend built with LangChain, LangGraph, Groq, and PostgreSQL. It stores conversations and messages in the database, then uses an LLM workflow to generate responses.

## Features

- REST API for creating conversations and sending messages
- Groq-hosted LLM integration via LangChain
- LangGraph orchestration for chat workflow
- PostgreSQL persistence for conversation history
- FastAPI docs available at `/docs`
- Pytest-based test suite with mocked LLM behavior

## Request flow

```text
Create conversation → send a message → load stored history → LangGraph workflow → Groq response
                                                               └→ save user and assistant messages
```

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

Clone the repository and enter it:

```bash
git clone https://github.com/HaiderNaqvi-5/FlowChat-API.git
cd FlowChat-API
```

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell, activate it with:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
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

Stream a response as server-sent events:

```bash
curl -N -X POST http://127.0.0.1:8000/api/v1/conversations/<conversation_id>/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"Explain dependency injection in simple terms."}'
```

## API overview

| Endpoint | Purpose |
| --- | --- |
| `GET /api/v1/health` | Liveness check. |
| `GET /api/v1/ready` | Database readiness check. |
| `POST /api/v1/conversations` | Create a conversation. |
| `GET /api/v1/conversations` | List conversations, optionally by owner. |
| `GET /api/v1/conversations/{id}/messages` | Read stored messages. |
| `POST /api/v1/conversations/{id}/chat` | Generate and store a complete reply. |
| `POST /api/v1/conversations/{id}/chat/stream` | Stream a reply with server-sent events. |

## Testing

```bash
pytest -q
```

## Notes

- This app uses a LangGraph workflow for processing chat requests.
- The project is structured for local development and production-like deployment via environment-level configuration.
- Tests avoid calling Groq directly by overriding the LLM dependency.
- Store credentials only in `.env`; `.env.example` documents the required configuration without exposing secrets.
