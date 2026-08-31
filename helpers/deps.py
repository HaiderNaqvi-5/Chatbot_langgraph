"""Shared dependencies. Injecting the chain is what makes the API testable."""

from typing import Annotated

from fastapi import Depends
from langchain_core.runnables import Runnable

from services.llm import get_message_chain, get_text_chain


def message_chain() -> Runnable:
    """Override this in tests with app.dependency_overrides to avoid real API calls."""
    return get_message_chain()


def text_chain() -> Runnable:
    return get_text_chain()


MessageChain = Annotated[Runnable, Depends(message_chain)]
TextChain = Annotated[Runnable, Depends(text_chain)]
