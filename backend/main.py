from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db
from app.api import auth, users, campaigns, submissions, analytics, admin, health
from app.middleware.logging import DevelopmentLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[STARTUP] Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"[STARTUP] Environment: {settings.ENVIRONMENT}")
    print(f"[STARTUP] Debug mode: {settings.DEBUG}")

    # Validate configuration
    try:
        settings.validate_config()
        print("[STARTUP] Configuration validated successfully")
    except ValueError as e:
        print(f"[WARNING] Configuration issues: {e}")
        # Don't exit in development, just warn
        if settings.ENVIRONMENT == "production":
            raise

    # Initialize database
    init_db()
    print(f"[STARTUP] Database initialized")
    print(f"[STARTUP] CORS origins: {settings.CORS_ORIGINS}")

    yield

    # Shutdown
    print("[SHUTDOWN] Application shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Add logging middleware in development
if settings.DEBUG:
    app.add_middleware(DevelopmentLoggingMiddleware, enabled=True)

# Configure CORS
cors_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Add additional origins from settings if available
try:
    if hasattr(settings, "CORS_ORIGINS") and settings.CORS_ORIGINS:
        env_origins = settings.CORS_ORIGINS
        if isinstance(env_origins, list):
            for origin in env_origins:
                origin = str(origin).strip().strip('"').strip("'")
                if origin and origin not in cors_origins and origin.startswith("http"):
                    cors_origins.append(origin)
        elif isinstance(env_origins, str):
            for origin in env_origins.split(","):
                origin = origin.strip().strip('"').strip("'")
                if origin and origin not in cors_origins and origin.startswith("http"):
                    cors_origins.append(origin)
except Exception as e:
    print(f"[CORS WARNING] Error parsing additional CORS origins: {e}")

print(f"[CORS] Configured origins: {cors_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=86400,
)


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "health": "/api/health",
    }


# API Routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(submissions.router, prefix="/api/submit", tags=["submissions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


# Global OPTIONS handler for CORS preflight
@app.middleware("http")
async def handle_options_requests(request, call_next):
    """Handle OPTIONS requests for CORS preflight"""
    if request.method == "OPTIONS":
        from fastapi.responses import Response

        # Get origin from request
        origin = request.headers.get("origin", "*")

        # Check if origin is allowed
        if origin in cors_origins or "*" in cors_origins:
            allowed_origin = origin
        else:
            allowed_origin = cors_origins[0] if cors_origins else "*"

        response = Response()
        response.headers["Access-Control-Allow-Origin"] = allowed_origin
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
        )
        response.headers["Access-Control-Allow-Headers"] = (
            "Accept, Content-Type, Authorization"
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = "86400"
        response.status_code = 200
        return response

    response = await call_next(request)
    return response


# Debug logging middleware (only in development)
if settings.DEBUG:

    @app.middleware("http")
    async def debug_logging(request, call_next):
        """Log requests for debugging"""
        # Skip logging for health checks
        if "/health" in str(request.url):
            return await call_next(request)

        print(f"[REQUEST] {request.method} {request.url.path}")

        # Log body for POST/PUT requests (be careful with sensitive data)
        if request.method in ["POST", "PUT", "PATCH"]:
            # Don't log auth endpoints bodies (contain passwords)
            if "/auth" not in str(request.url):
                print(f"[REQUEST] Query params: {request.query_params}")

        response = await call_next(request)
        print(f"[RESPONSE] Status: {response.status_code}")

        return response


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"detail": "Resource not found", "path": str(request.url.path)}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {
        "detail": "Internal server error",
        "message": "An unexpected error occurred",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,  # Use app directly, not "app.main:app"
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
