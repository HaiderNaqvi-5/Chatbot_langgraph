"""Groq chat model, prompt template, and LangChain runnables."""

from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq

from helpers.config import settings


@lru_cache
def get_chat_prompt() -> ChatPromptTemplate:
    # ⚡ Bolt Optimization: Cache the ChatPromptTemplate instance to avoid
    # initialization overhead on every prompt usage and avoid top-level Pydantic validation errors.
    return ChatPromptTemplate.from_messages(
        [
            ("system", settings.system_prompt),
            MessagesPlaceholder("history", optional=True),
            ("human", "{input}"),
        ]
    )


@lru_cache
def get_llm() -> ChatGroq:
    """One ChatGroq instance per process."""
    return ChatGroq(
        model=settings.groq_model,
        temperature=settings.groq_temperature,
        max_tokens=settings.groq_max_tokens,
        timeout=settings.groq_timeout_seconds,
        max_retries=2,
        api_key=settings.groq_api_key or None,
    )


@lru_cache
def get_message_chain() -> Runnable:
    """prompt | llm  ->  RunnableSequence[dict, AIMessage]."""
    return get_chat_prompt() | get_llm()


@lru_cache
def get_text_chain() -> Runnable:
    """prompt | llm | parser  ->  RunnableSequence[dict, str]."""
    return get_chat_prompt() | get_llm() | StrOutputParser()
