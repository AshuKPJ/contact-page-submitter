# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.middleware.cors import setup_cors
from app.middleware.timeout import TimeoutMiddleware
from app.core.database import init_db

# Import routers
from app.api import auth, users, campaigns, submissions, analytics, admin, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    settings.validate_config()
    yield
    # Shutdown


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # Add middleware
    app.add_middleware(TimeoutMiddleware, timeout=30.0)
    setup_cors(app)

    # Include routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(users.router, prefix="/api/users", tags=["users"])
    app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
    app.include_router(submissions.router, prefix="/api/submit", tags=["submissions"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
    app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

    return app


app = create_application()

# Add this only if you want to run with 'python app/main.py'
# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(
#         "app.main:app",
#         host="0.0.0.0",
#         port=8000,
#         reload=settings.DEBUG,
#         log_level="info" if not settings.DEBUG else "debug",
#     )
