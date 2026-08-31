"""ASGI entrypoint: uvicorn main:app --reload"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise.contrib.fastapi import tortoise_exception_handlers

from controllers import api_router
from helpers.config import settings
from helpers.db import register_orm


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Open DB connections on startup, close them on shutdown."""
    async with register_orm(app):
        yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        debug=settings.debug,
        lifespan=lifespan,
        exception_handlers=tortoise_exception_handlers(),
    )
    app.include_router(api_router)
    return app


app = create_app()
