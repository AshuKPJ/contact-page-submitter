# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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
    """Register a new user"""
    auth_service = AuthService(db)
    result = await auth_service.register_user(request)
    return result


@router.post("/login", response_model=AuthResponse)
async def login(request: UserLogin, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    auth_service = AuthService(db)
    result = await auth_service.login_user(request)
    return result


@router.post("/logout")
async def logout():
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current authenticated user info"""
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
