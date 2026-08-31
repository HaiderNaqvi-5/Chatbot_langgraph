"""Conversation model — one chat thread."""

from tortoise import fields
from tortoise.models import Model


class Conversation(Model):
    """A chat thread that groups an ordered list of messages."""

    id = fields.UUIDField(primary_key=True)
    title = fields.CharField(max_length=200)
    owner_id = fields.CharField(max_length=64, db_index=True)
    is_archived = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    messages: fields.ReverseRelation["Message"]  # noqa: F821

    class Meta:
        table = "conversation"
        table_description = "Chat threads"
        ordering = ["-updated_at"]
        indexes = (("owner_id", "is_archived"),)

    def __str__(self) -> str:
        return f"{self.title} <{self.id}>"
