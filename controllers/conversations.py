"""CRUD for conversations and reading stored messages."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from models import Conversation, Message
from utils.schemas import ConversationCreate, ConversationOut, MessageOut

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def create_conversation(payload: ConversationCreate) -> Conversation:
    return await Conversation.create(**payload.model_dump())


@router.get("", response_model=list[ConversationOut])
async def list_conversations(
    owner_id: str | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> list[Conversation]:
    query = Conversation.all()
    if owner_id:
        query = query.filter(owner_id=owner_id)
    return await query.order_by("-updated_at").limit(limit).offset(offset)


@router.get("/{conversation_id}", response_model=ConversationOut)
async def get_conversation(conversation_id: UUID) -> Conversation:
    conversation = await Conversation.get_or_none(id=conversation_id)
    if conversation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    return conversation


@router.get("/{conversation_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conversation_id: UUID,
    limit: int = Query(100, ge=1, le=500),
) -> list[Message]:
    if not await Conversation.exists(id=conversation_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
    return await (
        Message.filter(conversation_id=conversation_id).order_by("created_at").limit(limit)
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(conversation_id: UUID) -> None:
    deleted = await Conversation.filter(id=conversation_id).delete()
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Conversation not found")
