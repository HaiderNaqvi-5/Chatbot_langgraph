"""Bridge between our `message` table and LangChain's message objects."""

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages

from helpers.config import settings
from models import Message, Role

_TO_LC = {
    Role.USER: HumanMessage,
    Role.ASSISTANT: AIMessage,
    Role.SYSTEM: SystemMessage,
}


async def load_history(conversation_id) -> list[BaseMessage]:
    """Read the thread from Postgres and hand LangChain a list of messages."""
    rows = await (
        Message.filter(conversation_id=conversation_id)
        .order_by("-created_at")
        .limit(settings.history_token_budget)
        .values("role", "content")
    )
    rows.reverse()
    messages = [_TO_LC[Role(r["role"])](r["content"]) for r in rows]
    return trim_history(messages)


def trim_history(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Keep the newest turns inside a token budget."""
    return trim_messages(
        messages,
        max_tokens=settings.history_token_budget,
        token_counter=count_tokens_approximately,
        strategy="last",
        start_on="human",
        include_system=True,
        allow_partial=False,
    )
