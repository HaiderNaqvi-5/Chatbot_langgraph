# FastAPI + LangChain + Groq + PostgreSQL chat backend

Simple chat API. Replies come from Groq through LangChain. Every turn is stored in PostgreSQL.

## Stack

| Layer | Choice |
|---|---|
| Web framework | FastAPI |
| LLM provider | Groq |
| LLM glue | LangChain |
| Database | PostgreSQL 16 |
| ORM | Tortoise ORM (asyncpg) |
| Settings | pydantic-settings |
| Tests | pytest + httpx |

## Folder structure

```
main.py                 # uvicorn entrypoint
models/                 # Tortoise models
controllers/            # HTTP routes
services/               # business logic + Groq
helpers/                # settings, db, deps
utils/                  # Pydantic request/response schemas
tests/                  # pytest
.env                    # local secrets + DATABASE_URL
```

## Quick start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements-dev.txt

# paste your GROQ_API_KEY into .env
# keep a local Postgres running, then start the API

uvicorn main:app --reload
# open http://127.0.0.1:8000/docs
```

Postgres is only the connection string in `.env` — no Docker:

```
DATABASE_URL=postgres://postgres:1122@127.0.0.1:5433/chatdb
```

Tables are created on first startup (`generate_schemas=True`).

## Try it

```bash
curl -X POST localhost:8000/api/v1/conversations \
  -H "content-type: application/json" \
  -d "{\"title\":\"FastAPI doubts\",\"owner_id\":\"student_01\"}"

curl -X POST localhost:8000/api/v1/conversations/<ID>/chat \
  -H "content-type: application/json" \
  -d "{\"message\":\"Explain dependency injection.\"}"
```

## Tests

```bash
pytest -q
```

Tests never call Groq. A fake LLM is injected through FastAPI dependency overrides.


## LangGraph workflow

The non-streaming `POST /conversations/{conversation_id}/chat` endpoint now runs through a LangGraph workflow:

```text
START
  ↓
load_history
  ↓
generate_reply (Groq / LangChain)
  ↓
persist_turn (Postgres)
  ↓
END
```

The existing `/chat/stream` endpoint keeps its LangChain streaming path so token-by-token SSE behavior is unchanged.
