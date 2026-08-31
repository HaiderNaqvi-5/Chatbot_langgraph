"""Tortoise ORM configuration and FastAPI wiring."""

from functools import partial

from tortoise.contrib.fastapi import RegisterTortoise

from helpers.config import settings

MODELS = ["models", "aerich.models"]

TORTOISE_ORM: dict = {
    "connections": {"default": settings.database_url},
    "apps": {
        "models": {
            "models": MODELS,
            "default_connection": "default",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}

register_orm = partial(
    RegisterTortoise,
    config=TORTOISE_ORM,
    generate_schemas=True,
)
