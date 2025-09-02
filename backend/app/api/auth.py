# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import traceback
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister, UserResponse, AuthResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
async def register(request: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with comprehensive error handling"""
    try:
        print(f"\n[AUTH ENDPOINT] ========== REGISTRATION REQUEST ==========")
        print(f"[AUTH ENDPOINT] Email: {request.email}")
        print(f"[AUTH ENDPOINT] Name: {request.first_name} {request.last_name}")
        print(f"[AUTH ENDPOINT] Role: {request.role}")
        print(f"[AUTH ENDPOINT] Timestamp: {datetime.utcnow().isoformat()}")

        auth_service = AuthService(db)
        result = await auth_service.register_user(request)

        print(f"[AUTH ENDPOINT SUCCESS] Registration completed for: {request.email}")
        print(f"[AUTH ENDPOINT] ========================================\n")
        return result

    except HTTPException as e:
        # Log and re-raise HTTP exceptions with their specific messages
        print(f"[AUTH ENDPOINT ERROR] Registration failed with status {e.status_code}")
        print(f"[AUTH ENDPOINT ERROR] Details: {e.detail}")
        print(f"[AUTH ENDPOINT] ========================================\n")
        raise

    except Exception as e:
        # Log unexpected errors
        print(f"[AUTH ENDPOINT CRITICAL] Unexpected registration error: {str(e)}")
        traceback.print_exc()
        print(f"[AUTH ENDPOINT] ========================================\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again or contact support if the problem persists.",
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user with comprehensive error handling"""
    try:
        print(f"\n[AUTH ENDPOINT] ========== LOGIN REQUEST ==========")
        print(f"[AUTH ENDPOINT] Email: {request.email}")
        print(f"[AUTH ENDPOINT] Timestamp: {datetime.utcnow().isoformat()}")

        auth_service = AuthService(db)
        result = await auth_service.login_user(request)

        print(f"[AUTH ENDPOINT SUCCESS] Login completed for: {request.email}")
        print(f"[AUTH ENDPOINT] ====================================\n")
        return result

    except HTTPException as e:
        # Log and re-raise HTTP exceptions with their specific messages
        print(f"[AUTH ENDPOINT ERROR] Login failed with status {e.status_code}")
        print(f"[AUTH ENDPOINT ERROR] Details: {e.detail}")
        print(f"[AUTH ENDPOINT] ====================================\n")
        raise

    except Exception as e:
        # Log unexpected errors
        print(f"[AUTH ENDPOINT CRITICAL] Unexpected login error: {str(e)}")
        traceback.print_exc()
        print(f"[AUTH ENDPOINT] ====================================\n")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please check your internet connection and try again.",
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current authenticated user info"""
    try:
        print(f"[AUTH ENDPOINT] Fetching user info for: {current_user.email}")

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
        print(f"[AUTH ENDPOINT ERROR] Failed to get user info: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information. Please try logging in again.",
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user"""
    print(f"[AUTH ENDPOINT] User logged out: {current_user.email}")
    return {
        "message": "Successfully logged out",
        "detail": "Your session has been terminated. Please login again to continue.",
    }
