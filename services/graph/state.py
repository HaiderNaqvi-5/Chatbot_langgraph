from typing import TypedDict, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from langchain_core.messages import AIMessage, BaseMessage


class LoanStateExtraction(BaseModel):
    # NEW: Flag to detect irrelevant chatter
    is_loan_related: Optional[bool] = Field(
        default=True,
        description="True if the user's text is a greeting, loan inquiry, or providing personal details. False ONLY if completely off-topic (e.g. weather, coding, politics).",
    )

    name: Optional[str] = Field(default=None, description="The user's name")
    gender: Optional[Literal["male", "female", "others"]] = Field(default=None)
    marital_status: Optional[Literal["single", "married", "divorced"]] = Field(default=None)
    employment_status: Optional[Literal["studying", "employed", "unemployed"]] = Field(default=None)

    # Accept float to handle "22.8", we will convert it to int in the validator
    age: Optional[float] = Field(default=None)
    has_child: Optional[bool] = Field(default=None)

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
