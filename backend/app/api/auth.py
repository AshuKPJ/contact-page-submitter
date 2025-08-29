# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, UserResponse, AuthResponse
from app.services.auth_service import AuthService

router = APIRouter()


# Add explicit OPTIONS handler for login endpoint
@router.options("/login")
async def login_options():
    """Handle preflight requests for login"""
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",
        },
    )


# Add explicit OPTIONS handler for register endpoint
@router.options("/register")
async def register_options():
    """Handle preflight requests for register"""
    return JSONResponse(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",
        },
    )


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(request: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        print(f"[AUTH] Registration attempt for email: {request.email}")
        auth_service = AuthService(db)
        result = await auth_service.register_user(request)
        print(f"[AUTH] Registration successful for: {request.email}")
        return result
    except Exception as e:
        print(f"[AUTH ERROR] Registration failed: {str(e)}")
        traceback.print_exc()
        raise


@router.post("/login", response_model=AuthResponse)
async def login(request: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    try:
        print(f"[AUTH] Login attempt for email: {request.email}")
        auth_service = AuthService(db)
        result = await auth_service.login_user(request)
        print(f"[AUTH] Login successful for: {request.email}")
        return result
    except HTTPException as e:
        print(f"[AUTH ERROR] Login failed for {request.email}: {e.detail}")
        raise
    except Exception as e:
        print(f"[AUTH ERROR] Unexpected login error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login",
        )


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current authenticated user info"""
    try:
        print(f"[AUTH] Getting user info for: {current_user.email}")
        return UserResponse(
            id=str(current_user.id),
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            role=current_user.role,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            subscription_status=current_user.subscription_status,
        )
    except Exception as e:
        print(f"[AUTH ERROR] Failed to get user info: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information",
        )
