from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, users, campaigns, submissions, analytics, admin, health
from app.middleware.logging import DevelopmentLoggingMiddleware, api_logger

# Import monitoring for development
if settings.ENVIRONMENT == "development":
    from app.api import monitoring


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[STARTUP] Validating configuration...")
    try:
        settings.validate_config()
    except ValueError as e:
        print(f"[ERROR] Configuration validation failed: {e}")
        raise

    init_db()
    print(f"[STARTUP] Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"[STARTUP] Environment: {settings.ENVIRONMENT}")
    print(f"[STARTUP] Debug mode: {settings.DEBUG}")
    print(f"[STARTUP] CORS origins: {settings.CORS_ORIGINS}")
    yield
    # Shutdown
    print("[SHUTDOWN] Application shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Add comprehensive logging middleware for development
if settings.DEBUG:
    app.add_middleware(DevelopmentLoggingMiddleware, enabled=True)

# CORS Configuration - FIXED with explicit origins and proper parsing
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Try to add env origins if they exist and are valid
try:
    if hasattr(settings, "CORS_ORIGINS") and settings.CORS_ORIGINS:
        env_origins = settings.CORS_ORIGINS
        # Handle both list and string formats
        if isinstance(env_origins, list):
            for origin in env_origins:
                origin = str(origin).strip().strip('"').strip("'")
                if origin and origin not in cors_origins and origin.startswith("http"):
                    cors_origins.append(origin)
        elif isinstance(env_origins, str):
            # Parse comma-separated string
            for origin in env_origins.split(","):
                origin = origin.strip().strip('"').strip("'")
                if origin and origin not in cors_origins and origin.startswith("http"):
                    cors_origins.append(origin)
except Exception as e:
    print(f"[CORS WARNING] Error parsing CORS_ORIGINS from settings: {e}")

print(f"[CORS] Final CORS origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRFToken",
        "Cache-Control",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["*"],
    max_age=86400,  # Cache preflight for 24 hours
)


# Add a root endpoint for testing
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API v{settings.APP_VERSION}"}


# Routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(submissions.router, prefix="/api/submit", tags=["submissions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])

# Add monitoring endpoints in development
if settings.ENVIRONMENT == "development":
    app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])


# Add global OPTIONS handler middleware - CRITICAL FIX
@app.middleware("http")
async def handle_options_requests(request, call_next):
    """Global middleware to handle OPTIONS requests"""
    if request.method == "OPTIONS":
        from fastapi.responses import Response

        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "Accept, Accept-Language, Content-Language, Content-Type, Authorization, X-Requested-With, X-CSRFToken, Cache-Control, Origin"
        )
        response.headers["Access-Control-Max-Age"] = "86400"
        response.status_code = 200
        print(f"[CORS] Handled OPTIONS request for: {request.url}")
        return response

    response = await call_next(request)
    return response


# Debug middleware for development
if settings.DEBUG:

    @app.middleware("http")
    async def debug_middleware(request, call_next):
        print(f"[DEBUG] {request.method} {request.url}")
        print(f"[DEBUG] Headers: {dict(request.headers)}")

        response = await call_next(request)

        print(f"[DEBUG] Response status: {response.status_code}")
        return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
