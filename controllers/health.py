"""Liveness and readiness. Readiness actually touches the database."""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from tortoise import Tortoise

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@router.get("/ready")
async def ready() -> JSONResponse:
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(
            {"status": "unavailable", "database": str(exc)},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return JSONResponse({"status": "ok", "database": "ok"})
