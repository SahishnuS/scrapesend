"""
InternHunt — FastAPI Application Entry Point

This module bootstraps the FastAPI application, registers all routers,
configures middleware, and wires up the OpenAPI documentation.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import configure_logging
from app.api.v1.router import api_router
from app.db.session import engine

log = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown hooks."""
    configure_logging()
    log.info(
        "InternHunt starting",
        environment=settings.ENVIRONMENT,
        version=settings.APP_VERSION,
    )
    yield
    log.info("InternHunt shutting down")


def create_application() -> FastAPI:
    """Application factory — returns a fully configured FastAPI instance."""
    app = FastAPI(
        title="InternHunt",
        description=(
            "AI-powered internship monitoring and application management platform. "
            "Monitors companies 24×7, matches jobs against your resume, sends "
            "instant notifications, and tracks every application."
        ),
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
        )

    # ── Routers ────────────────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ── Health check ───────────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"], summary="Health check")
    async def health_check():
        return JSONResponse({"status": "ok", "version": settings.APP_VERSION})

    return app


app = create_application()
