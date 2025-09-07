# app/main.py - Complete main application with all endpoints properly integrated

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import traceback

# Import all routers from endpoints
from app.api.endpoints import (
    health_router,
    auth_router,
    users_router,
    campaigns_router,
    submissions_router,
    analytics_router,
    admin_router,
)

# Create FastAPI app
app = FastAPI(
    title="CPS - Contact Processing System",
    description="Automated contact form submission system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# CORS CONFIGURATION - CRITICAL FOR YOUR FRONTEND AT localhost:5173
# ============================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Your Vite frontend
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",  # Allow all in development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# ============================================================================
# INCLUDE ROUTERS WITH PROPER PREFIXES
# ============================================================================

# Health check endpoints (no prefix for /api/health)
app.include_router(health_router, prefix="/api", tags=["Health"])

# Authentication endpoints
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# User endpoints
app.include_router(users_router, prefix="/api/users", tags=["Users"])

# Campaign endpoints
app.include_router(campaigns_router, prefix="/api/campaigns", tags=["Campaigns"])

# Submission endpoints
app.include_router(submissions_router, prefix="/api/submissions", tags=["Submissions"])

# Analytics endpoints
app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])

# Admin endpoints
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])


# ============================================================================
# ROOT ENDPOINT
# ============================================================================
@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "CPS API",
        "version": "1.0.0",
        "status": "running",
        "documentation": "http://localhost:8000/docs",
        "health": "http://localhost:8000/api/health",
        "frontend": "http://localhost:5173",
    }


# ============================================================================
# GLOBAL EXCEPTION HANDLER
# ============================================================================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions"""
    print(f"[GLOBAL ERROR] {request.method} {request.url.path}")
    print(f"[GLOBAL ERROR] {str(exc)}")
    traceback.print_exc()

    # Return CORS headers even on errors
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc) if app.debug else "An error occurred",
        },
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        },
    )


# ============================================================================
# STARTUP EVENT
# ============================================================================
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("\n" + "=" * 60)
    print("🚀 CPS API Starting Up")
    print("=" * 60)
    print("📝 Documentation: http://localhost:8000/docs")
    print("🏥 Health Check: http://localhost:8000/api/health")
    print("🎨 Frontend: http://localhost:5173")
    print("✅ CORS enabled for localhost:5173")
    print("=" * 60 + "\n")


# ============================================================================
# SHUTDOWN EVENT
# ============================================================================
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("\n🛑 CPS API Shutting Down\n")


# ============================================================================
# RUN APPLICATION
# ============================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
