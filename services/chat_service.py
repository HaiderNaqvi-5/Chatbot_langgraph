"""Orchestration layer: DB history -> LLM -> DB persistence."""

import time
from uuid import UUID

from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from tortoise.transactions import in_transaction

from helpers.config import settings
from models import Conversation, Message, Role
from services.graph import chat_graph
from services.history import load_history


class ConversationNotFound(Exception):
    """Raised when a conversation id does not exist."""


async def _get_conversation(conversation_id: UUID) -> Conversation:
    conversation = await Conversation.get_or_none(id=conversation_id)
    if conversation is None:
        raise ConversationNotFound(str(conversation_id))
    return conversation


async def generate_reply(
    conversation_id: UUID,
    user_text: str,
    chain: Runnable,
) -> dict:
    """Run one chat turn through the LangGraph workflow."""
    conversation = await _get_conversation(conversation_id)

    result = await chat_graph.ainvoke(
        {
            "conversation_id": conversation_id,
            "user_text": user_text,
        }
    )
    ai: AIMessage = result["ai_message"]
    return {
        "conversation_id": conversation_id,
        "reply": ai.text,
        "model": settings.groq_model,
        "latency_ms": result.get("latency_ms", 0),
        "history_length": len(result.get("history", [])),
    }


async def stream_reply(conversation_id: UUID, user_text: str, chain: Runnable):
    """Async generator of token deltas; saves the full turn once the stream ends."""
    conversation = await _get_conversation(conversation_id)
    history = await load_history(conversation_id)

    started = time.perf_counter()
    chunks: list[str] = []

    async for token in chain.astream({"history": history, "input": user_text}):
        if not token:
            continue
        chunks.append(token)
        yield token

    full_text = "".join(chunks)
    latency_ms = int((time.perf_counter() - started) * 1000)

    async with in_transaction():
        await Message.create(conversation=conversation, role=Role.USER, content=user_text)
        await Message.create(
            conversation=conversation,
            role=Role.ASSISTANT,
            content=full_text,
            model=settings.groq_model,
            latency_ms=latency_ms,
        )
        await conversation.save(update_fields=["updated_at"])
