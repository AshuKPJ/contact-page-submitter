from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import traceback

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection - FIXED SQL
        result = db.execute(text("SELECT 1")).fetchone()
        db_status = "healthy"
        db_result = result[0] if result else None
    except Exception as e:
        print(f"[HEALTH] Database error: {str(e)}")
        db_status = "unhealthy"
        db_result = None

    return {
        "status": "ok" if db_status == "healthy" else "error",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "database_test": db_result,
        "cors_origins": settings.CORS_ORIGINS,
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong", "timestamp": datetime.utcnow().isoformat()}


# Debug endpoints for development
@router.get("/debug/db")
async def debug_database(db: Session = Depends(get_db)):
    """Debug database connection endpoint"""
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=404, detail="Debug endpoint not available in production"
        )

    try:
        # Test basic database operations - FIXED SQL
        result = db.execute(text("SELECT 1 as test_value")).fetchone()

        # Test user table exists - FIXED SQL
        user_test = db.execute(
            text("SELECT COUNT(*) as user_count FROM users")
        ).fetchone()

        return {
            "status": "healthy",
            "test_query": result[0] if result else None,
            "user_table": "exists",
            "user_count": user_test[0] if user_test else 0,
            "database_url": settings.DATABASE_URL,
            "environment": settings.ENVIRONMENT,
        }
    except Exception as e:
        print(f"[DEBUG] Database test error: {str(e)}")
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "database_url": settings.DATABASE_URL,
        }


@router.post("/debug/login-test")
async def debug_login_test(request: dict, db: Session = Depends(get_db)):
    """Debug login functionality without actual authentication"""
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=404, detail="Debug endpoint not available in production"
        )

    try:
        email = request.get("email")
        password = request.get("password")

        if not email or not password:
            return {
                "status": "error",
                "message": "Email and password required for test",
                "received": {"email": bool(email), "password": bool(password)},
            }

        # Check if user exists
        from app.models.user import User

        user = db.query(User).filter(User.email == email).first()

        return {
            "status": "debug_success",
            "message": "Login endpoint reachable",
            "user_exists": bool(user),
            "email_received": email,
            "database_connection": "healthy",
            "environment": settings.ENVIRONMENT,
        }
    except Exception as e:
        print(f"[DEBUG] Login test error: {str(e)}")
        traceback.print_exc()
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
