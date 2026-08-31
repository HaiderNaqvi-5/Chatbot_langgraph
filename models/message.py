"""Message model — a single turn inside a conversation."""

from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class Role(StrEnum):
    """Who produced the message. Mirrors the LangChain message types."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Message(Model):
    """One stored turn. This table IS our chat memory."""

    id = fields.UUIDField(primary_key=True)
    conversation: fields.ForeignKeyRelation["Conversation"] = fields.ForeignKeyField(  # noqa: F821
        "models.Conversation",
        related_name="messages",
        on_delete=fields.OnDelete.CASCADE,
        db_index=True,
    )
    role = fields.CharEnumField(Role, max_length=16)
    content = fields.TextField()
    model = fields.CharField(max_length=100, null=True)
    input_tokens = fields.IntField(null=True)
    output_tokens = fields.IntField(null=True)
    latency_ms = fields.IntField(null=True)
    finish_reason = fields.CharField(max_length=32, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "message"
        table_description = "Chat turns"
        ordering = ["created_at"]
        indexes = (("conversation", "created_at"),)

    def __str__(self) -> str:
        return f"[{self.role}] {self.content[:40]}"
