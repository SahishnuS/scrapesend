"""Health check endpoints."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/", summary="Liveness probe")
async def health():
    return JSONResponse({"status": "ok"})


@router.get("/ready", summary="Readiness probe")
async def ready():
    # TODO: check DB connectivity in Phase 2
    return JSONResponse({"status": "ready"})
