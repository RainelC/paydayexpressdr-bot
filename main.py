"""FastAPI application entry point for PayDay Express DR WhatsApp Bot."""

from __future__ import annotations

import logging
import logging.config
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from database.config import settings
from database.connection import init_db
from routers import notifications, webhook

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Initialising database…")
    await init_db()
    logger.info("PayDay Express DR WhatsApp Bot started ✅")
    yield
    logger.info("PayDay Express DR WhatsApp Bot shutting down…")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="PayDay Express DR – WhatsApp Bot",
    description=(
        "Professional-grade WhatsApp Bot built with FastAPI and Twilio.\n\n"
        "Handles inbound messages, a guided conversation menu (FAQ + loan-status), "
        "and proactive push notifications for external status-change events."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(webhook.router)
app.include_router(notifications.router)


# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"], summary="Service health check")
async def health() -> dict[str, str]:
    return {"status": "ok"}
