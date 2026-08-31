"""The two endpoints that actually talk to Groq."""

import json
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from helpers.deps import MessageChain, TextChain
from services.chat_service import ConversationNotFound, generate_reply, stream_reply
from utils.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/conversations", tags=["chat"])


@router.post("/{conversation_id}/chat", response_model=ChatResponse)
async def chat(conversation_id: UUID, payload: ChatRequest, chain: MessageChain) -> dict:
    try:
        return await generate_reply(conversation_id, payload.message, chain)
    except ConversationNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found") from None


@router.post("/{conversation_id}/chat/stream")
async def chat_stream(
    conversation_id: UUID,
    payload: ChatRequest,
    chain: TextChain,
    request: Request,
) -> StreamingResponse:
    async def event_source():
        try:
            async for token in stream_reply(conversation_id, payload.message, chain):
                if await request.is_disconnected():
                    break
                yield f"data: {json.dumps({'delta': token})}\n\n"
            yield "data: [DONE]\n\n"
        except ConversationNotFound:
            yield f"data: {json.dumps({'error': 'Conversation not found'})}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
