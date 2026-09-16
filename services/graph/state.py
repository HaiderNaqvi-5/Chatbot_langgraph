from typing import Literal, TypedDict
from uuid import UUID

from langchain_core.messages import AIMessage, BaseMessage
from pydantic import BaseModel, Field, field_validator


class LoanStateExtraction(BaseModel):
    # NEW: Flag to detect irrelevant chatter
    is_loan_related: bool | None = Field(
        default=True,
        description="True if the user's text is a greeting, loan inquiry, or providing personal details. False ONLY if completely off-topic (e.g. weather, coding, politics).",
    )

    name: str | None = Field(default=None, description="The user's name")
    gender: Literal["male", "female", "others"] | None = Field(default=None)
    marital_status: Literal["single", "married", "divorced"] | None = Field(default=None)
    employment_status: Literal["studying", "employed", "unemployed"] | None = Field(default=None)

    # Accept float to handle "22.8", we will convert it to int in the validator
    age: float | None = Field(default=None)
    has_child: bool | None = Field(default=None)

    @field_validator("age")
    @classmethod
    def validate_age(cls, v):
        if v is not None:
            v = int(v)  # Converts 22.8 to 22 safely
            if v < 18 or v > 120:
                raise ValueError("Age must be between 18 and 120.")
        return v


class ChatState(TypedDict, total=False):
    conversation_id: UUID
    user_text: str
    history: list[BaseMessage]
    ai_message: AIMessage
    latency_ms: int
    extracted_data: LoanStateExtraction
    directive: str  # Added to hold instructions for the LLM
