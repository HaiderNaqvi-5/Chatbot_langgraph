"""Single place where every route is mounted."""

from fastapi import APIRouter

from controllers import chat, conversations, health

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(conversations.router)
api_router.include_router(chat.router)
