"""
FastAPI application factory — main entry point.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.config.settings import settings
from backend.core.exceptions import register_exception_handlers
from backend.core.schemas import HealthResponse
from backend.security.rate_limiter import limiter

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # ── Startup ──────────────────────────────────────────────
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AI Provider: {settings.AI_PROVIDER}")

    # Ensure uploads directory exists
    uploads_path = Path(settings.UPLOAD_DIR)
    uploads_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Uploads directory: {uploads_path.resolve()}")

    # Create tables in development
    # Create tables on startup (auto-migration for SQLite)
    from backend.database.session import create_tables
    await create_tables()
    logger.info("Database tables verified.")

    yield

    # ── Shutdown ─────────────────────────────────────────────
    logger.info("Shutting down application.")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-ready AI Meeting Summarizer with transcription, summarization, and export.",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware ────────────────────────────────────────────────

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # ── Exception Handlers ───────────────────────────────────────
    register_exception_handlers(app)

    # ── Routers ──────────────────────────────────────────────────
    from backend.api.auth import router as auth_router
    from backend.api.meetings import router as meetings_router
    from backend.api.settings_api import router as settings_router

    app.include_router(auth_router)
    app.include_router(meetings_router)
    app.include_router(settings_router)

    # ── Health Check ─────────────────────────────────────────────
    @app.get("/api/health", response_model=HealthResponse, tags=["Health"])
    async def health_check():
        return HealthResponse(
            status="healthy",
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
        )

    # ── Static Files (uploaded audio) ────────────────────────────────
    uploads_path = Path(settings.UPLOAD_DIR)
    uploads_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

    # ── Serve frontend build (production) ─────────────────────────────
    frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        from fastapi.responses import FileResponse

        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="frontend-assets")

        @app.get("/{full_path:path}")
        async def serve_frontend(full_path: str):
            """Serve the React SPA — all non-API routes fall through to index.html."""
            file_path = frontend_dist / full_path
            if full_path and file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            return FileResponse(str(frontend_dist / "index.html"))

    return app


# Application instance
app = create_app()
