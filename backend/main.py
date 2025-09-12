# app/main.py
"""
FastAPI entrypoint with Windows ProactorEventLoop policy (for Playwright subprocess support),
structured logging, CORS, and router registration.
"""

# --- MUST be first: use ProactorEventLoop on Windows for Playwright subprocess support
import sys
import asyncio

if sys.platform == "win32":
    # Use ProactorEventLoop for Windows subprocess support (required for Playwright)
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Logging
from app.logging import (
    configure_logging,
    get_logger,
    LoggingMiddleware,
)
from app.logging.config import LoggingConfig

# --- Routers
from app.api import (
    auth,
    health,
    analytics,
    campaigns,
    logs,
    submissions,
    users,
    activity,
    websocket,
    captcha,  # Add CAPTCHA router import
)


# ----------------------------
# Helpers
# ----------------------------
def _parse_cors_origins() -> list[str]:
    """Parse CORS_ORIGINS environment variable."""
    raw = os.getenv("CORS_ORIGINS", "*").strip()
    if raw == "*":
        return ["*"]
    try:
        val = json.loads(raw)
        if isinstance(val, list):
            return [str(x) for x in val]
    except Exception:
        pass
    return [s.strip() for s in raw.split(",") if s.strip()]


# ----------------------------
# Lifespan
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = get_logger("app.main")
    logger.info("Application starting up")

    # Log event loop policy for debugging
    policy = asyncio.get_event_loop_policy()
    logger.info(f"Event loop policy: {type(policy).__name__}")

    # Log CAPTCHA integration status
    logger.info(
        "CAPTCHA integration: Death By Captcha support enabled via user profiles"
    )

    yield
    logger.info("Application shutting down")


# ----------------------------
# Factory
# ----------------------------
def create_app() -> FastAPI:
    # Configure logging
    try:
        log_cfg = LoggingConfig()
        configure_logging(log_cfg)
    except Exception as e:
        import logging

        logging.getLogger("uvicorn.error").warning(f"configure_logging() failed: {e}")

    app = FastAPI(
        lifespan=lifespan,
        title=os.getenv("APP_NAME", "Contact Page Submitter"),
        version=os.getenv(
            "APP_VERSION", "2.0.0"
        ),  # Updated version for CAPTCHA integration
        description="Automated contact form submission system with Death By Captcha integration",
    )

    # CORS middleware
    allow_origins = _parse_cors_origins()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Request logging middleware
    app.add_middleware(LoggingMiddleware, logger_name="http")

    # Register routers
    app.include_router(auth.router, prefix="/api/auth")
    app.include_router(users.router)
    app.include_router(health.router)
    app.include_router(analytics.router)
    app.include_router(campaigns.router)
    app.include_router(logs.router)
    app.include_router(submissions.router)
    app.include_router(activity.router)
    app.include_router(websocket.router)
    app.include_router(captcha.router)  # Add CAPTCHA router

    # Log routes on startup
    @app.on_event("startup")
    async def _log_routes():
        lg = get_logger("app.routes")
        for r in app.router.routes:
            methods = getattr(r, "methods", None)
            lg.info(
                "ROUTE registered",
                context={
                    "methods": sorted(list(methods)) if methods else [],
                    "path": r.path,
                },
            )

    # Add root endpoint with feature list
    @app.get("/")
    async def root():
        """Root endpoint with system information."""
        return {
            "name": os.getenv("APP_NAME", "Contact Page Submitter"),
            "version": os.getenv("APP_VERSION", "2.0.0"),
            "status": "operational",
            "features": {
                "authentication": "JWT-based user authentication",
                "campaigns": "Campaign creation and management",
                "automation": "Automated form submission with 120 websites/hour",
                "captcha": "Death By Captcha integration (user-specific)",
                "fallback": "Email extraction when forms not found",
                "tracking": "Real-time progress monitoring",
                "analytics": "Campaign performance metrics",
            },
            "captcha_integration": {
                "provider": "Death By Captcha",
                "configuration": "Per-user credentials",
                "success_rate": "95% with CAPTCHA solving vs 60% without",
            },
            "documentation": "/docs",
            "health_check": "/health",
        }

    return app


# ASGI application
app = create_app()

# ----------------------------
# Dev server
# ----------------------------
if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("RELOAD", "true").lower() == "true"

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["app"],
        log_level="info",
    )
