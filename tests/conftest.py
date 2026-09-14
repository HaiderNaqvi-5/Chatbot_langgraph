"""Test fixtures: real Postgres, fake LLM.

DATABASE_URL is set BEFORE `main` is imported, because Settings is cached the
first time it is constructed.
"""

import os

os.environ.setdefault(
    "DATABASE_URL", "sqlite://:memory:"
)

from collections.abc import AsyncGenerator  # noqa: E402

import pytest  # noqa: E402
from asgi_lifespan import LifespanManager  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel  # noqa: E402
from langchain_core.messages import AIMessage  # noqa: E402
from langchain_core.output_parsers import StrOutputParser  # noqa: E402
from tortoise import Tortoise  # noqa: E402

from helpers.deps import message_chain, text_chain  # noqa: E402
from main import app  # noqa: E402
from services.llm import CHAT_PROMPT  # noqa: E402

FAKE_REPLY = "This is a canned reply."


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    return "asyncio"


def _fake_llm() -> GenericFakeChatModel:
    """Yields FAKE_REPLY forever, so no Groq credits are spent in CI."""
    return GenericFakeChatModel(messages=iter([AIMessage(FAKE_REPLY)] * 100))


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[message_chain] = lambda: CHAT_PROMPT | _fake_llm()
    app.dependency_overrides[text_chain] = lambda: CHAT_PROMPT | _fake_llm() | StrOutputParser()

    async with LifespanManager(app):
        await Tortoise.generate_schemas(safe=True)
        conn = Tortoise.get_connection("default")
        await conn.execute_script('DELETE FROM "message"; DELETE FROM "conversation";')

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    app.dependency_overrides.clear()
