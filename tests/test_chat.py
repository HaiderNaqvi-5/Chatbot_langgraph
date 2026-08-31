"""End-to-end tests: HTTP in, Postgres rows out."""

import pytest

from tests.conftest import FAKE_REPLY

pytestmark = pytest.mark.anyio


async def _new_conversation(client) -> str:
    res = await client.post(
        "/api/v1/conversations", json={"title": "FastAPI doubts", "owner_id": "student_01"}
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


async def test_health(client):
    assert (await client.get("/api/v1/health")).json() == {"status": "ok"}


async def test_ready_touches_database(client):
    res = await client.get("/api/v1/ready")
    assert res.status_code == 200
    assert res.json()["database"] == "ok"


async def test_chat_persists_both_turns(client):
    cid = await _new_conversation(client)

    res = await client.post(f"/api/v1/conversations/{cid}/chat", json={"message": "hi"})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["reply"] == FAKE_REPLY
    assert body["history_length"] == 0

    stored = (await client.get(f"/api/v1/conversations/{cid}/messages")).json()
    assert [m["role"] for m in stored] == ["user", "assistant"]
    assert stored[0]["content"] == "hi"
    assert stored[1]["content"] == FAKE_REPLY


async def test_history_grows_and_is_replayed(client):
    cid = await _new_conversation(client)

    await client.post(f"/api/v1/conversations/{cid}/chat", json={"message": "first"})
    second = await client.post(f"/api/v1/conversations/{cid}/chat", json={"message": "second"})

    assert second.json()["history_length"] == 2
    stored = (await client.get(f"/api/v1/conversations/{cid}/messages")).json()
    assert len(stored) == 4


async def test_chat_on_missing_conversation_returns_404(client):
    res = await client.post(
        "/api/v1/conversations/00000000-0000-0000-0000-000000000000/chat",
        json={"message": "hello?"},
    )
    assert res.status_code == 404


async def test_empty_message_is_rejected(client):
    cid = await _new_conversation(client)
    res = await client.post(f"/api/v1/conversations/{cid}/chat", json={"message": ""})
    assert res.status_code == 422


async def test_streaming_endpoint_emits_sse_and_saves(client):
    cid = await _new_conversation(client)

    async with client.stream(
        "POST", f"/api/v1/conversations/{cid}/chat/stream", json={"message": "stream please"}
    ) as res:
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/event-stream")
        body = "".join([chunk async for chunk in res.aiter_text()])

    assert "data: [DONE]" in body
    stored = (await client.get(f"/api/v1/conversations/{cid}/messages")).json()
    assert stored[1]["content"] == FAKE_REPLY
