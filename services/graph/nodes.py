import time
from functools import lru_cache
from pydantic import ValidationError # NEW IMPORT
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from tortoise.transactions import in_transaction

from helpers.config import settings
from models import Conversation, Message, Role
from services.history import load_history
from services.graph.state import ChatState, LoanStateExtraction

@lru_cache
def get_extraction_chain():
    """Cache the prompt and structured LLM initialization to avoid ~85ms overhead per call."""
    llm = ChatGroq(
        model=settings.groq_model, 
        temperature=0.0, # STRICT: 0.0 prevents extraction hallucinations
        max_tokens=settings.groq_max_tokens,
        timeout=settings.groq_timeout_seconds
    )
    structured_llm = llm.with_structured_output(LoanStateExtraction)

    prompt = ChatPromptTemplate.from_messages([
        ("system", settings.system_prompt),
        ("placeholder", "{history}"),
        ("human", "{input}")
    ])

    return prompt | structured_llm

@lru_cache
def get_generation_chain():
    """Cache the prompt and LLM initialization for the generation node."""
    llm = ChatGroq(model=settings.groq_model, temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a highly constrained, professional loan assistant.
        Your ONLY task is to convert the System Directive into a natural, friendly response.

        CRITICAL GUARDRAILS:
        1. DO NOT invent numbers or ask questions that are not in the directive.
        2. ALWAYS use 'Rs.' for currency. NEVER use the Indian Rupee symbol (₹)."""),
        ("human", "System Directive: {directive}")
    ])

    return prompt | llm

async def load_history_node(state: ChatState) -> dict:
    return {"history": await load_history(state["conversation_id"])}

async def extract_data_node(state: ChatState) -> dict:
    started = time.perf_counter()

    chain = get_extraction_chain()

    try:
        extracted: LoanStateExtraction = await chain.ainvoke({
            "history": state.get("history", []),
            "input": state["user_text"]
        })
    except ValidationError as e:
        # Pydantic caught a hallucination (e.g., age = 5)
        print(f"Guardrail triggered (Pydantic): {e}")
        extracted = LoanStateExtraction() 
    except Exception as e:
        # Groq failed to format JSON (e.g., user just said "hi")
        print(f"Guardrail triggered (Parse Error): {e}")
        extracted = LoanStateExtraction() 

    return {
        "extracted_data": extracted, 
        "latency_ms": int((time.perf_counter() - started) * 1000)
    }

# Strategy Nodes: Set the instruction (directive), not the final text.
async def off_topic_node(state: ChatState) -> dict:
    return {"directive": "Politely inform the user that you are a specialized loan assistant and cannot assist with unrelated queries."}
async def ask_name_node(state: ChatState) -> dict:
    return {"directive": "Welcome the user and politely ask for their name to begin the loan application."}

async def ask_gender_node(state: ChatState) -> dict:
    # If name is None for any reason, it falls back to "there"
    name = state["extracted_data"].name or "there" 
    
    return {"directive": f"Address the user as {name} and ask them to specify their gender (Male, Female, or Others)."}

async def ask_age_node(state: ChatState) -> dict:
    return {"directive": "Politely ask the user to provide their age."}

async def ask_marital_status_node(state: ChatState) -> dict:
    return {"directive": "Ask the user for their marital status (Single, Married, or Divorced)."}

async def ask_employment_node(state: ChatState) -> dict:
    data = state.get("extracted_data")
    marital = data.marital_status.lower() if data and data.marital_status else ""
    
    # If married or divorced, they don't get the student loan tier anyway
    if marital in ["married", "divorced"]:
        directive = "Ask the user if they are currently employed or unemployed."
    else:
        # If single or young, studying is a valid tier
        directive = "Ask the user if they are currently studying, employed, or unemployed."
        
    return {"directive": directive}

async def ask_child_node(state: ChatState) -> dict:
    return {"directive": "Ask the user if they have any children."}

async def reject_node(state: ChatState) -> dict:
    return {"directive": "Politely inform the user that they must be 18 or older to apply for a loan. End the conversation."}

async def other_dept_node(state: ChatState) -> dict:
    return {"directive": "Politely inform the user that their application will be dealt with by another department."}

async def calculate_loan_node(state: ChatState) -> dict:
    data = state["extracted_data"]
    age = data.age
    marital = data.marital_status if data.marital_status else ""
    emp = data.employment_status if data.employment_status else ""
    has_child = data.has_child

    amount = 0
    interest_rate = 0

    if age >= 61:
        amount, interest_rate = 1000000, 0
    elif 18 <= age <= 20 or marital == "single":
        amount, interest_rate = (500000, 0) if emp == "studying" else (600000, 30)
    elif marital == "married":
        amount = 800000 if emp == "employed" else 600000
        interest_rate = 10 if has_child else 20
    elif marital == "divorced":
        amount = 900000 if has_child else 700000
        interest_rate = 0

    # Explicitly add "Rs." to the formatting instructions
    directive = (
        f"Congratulate {data.name}. Approve a loan of {amount // 100000} lacs (Rs. {amount:,}) with an interest rate of {interest_rate}%. "
        f"If the interest is greater than 0, calculate the exact interest amount and state the final total payable amount. "
        f"Ensure all monetary values are formatted with 'Rs.'"
    )
    return {"directive": directive}

async def generate_reply_node(state: ChatState) -> dict:
    directive = state["directive"]
    
    chain = get_generation_chain()
    
    response = await chain.ainvoke({"directive": directive})
    return {"ai_message": response}

async def persist_turn_node(state: ChatState) -> dict:
    conversation = await Conversation.get(id=state["conversation_id"])
    ai = state["ai_message"]

    async with in_transaction():
        await Message.create(
            conversation=conversation,
            role=Role.USER,
            content=state["user_text"],
        )
        await Message.create(
            conversation=conversation,
            role=Role.ASSISTANT,
            content=ai.content,
            model=settings.groq_model,
            latency_ms=state.get("latency_ms"),
        )
        await conversation.save(update_fields=["updated_at"])

    return {}