from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import (
    UserProfileCreate,
    UserContactProfileCreate,
    UserProfileResponse,
)
from app.services.user_service import UserService

router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile"""
    user_service = UserService(db)
    profile = user_service.get_user_profile(current_user.id)

    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    return profile


@router.post(
    "/profile", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED
)
async def create_or_update_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update user profile"""
    user_service = UserService(db)
    profile = user_service.create_user_profile(current_user.id, profile_data)
    return profile


@router.post("/contact-profile", status_code=status.HTTP_201_CREATED)
async def create_or_update_contact_profile(
    profile_data: UserContactProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update user contact profile"""
    user_service = UserService(db)
    profile = user_service.create_contact_profile(current_user.id, profile_data)
    return {"message": "Contact profile updated successfully"}


@router.put("/captcha-credentials")
async def update_captcha_credentials(
    username: str,
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update CAPTCHA service credentials"""
    user_service = UserService(db)
    user_service.update_captcha_credentials(current_user.id, username, password)
    return {"message": "CAPTCHA credentials updated successfully"}
