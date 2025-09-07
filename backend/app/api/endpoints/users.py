# ============================================================================
# app/api/endpoints/users.py - FIXED PROFILE ENDPOINT
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.user_profile import UserProfile
from app.schemas.user import UserProfileCreate, UserProfileResponse

router = APIRouter()


@router.get("/profile")
async def get_user_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get current user's profile"""
    try:
        profile = (
            db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        )

        if profile:
            return {
                "id": profile.id,
                "user_id": str(profile.user_id),
                "first_name": profile.first_name or current_user.first_name,
                "last_name": profile.last_name or current_user.last_name,
                "email": profile.email or current_user.email,
                "phone_number": profile.phone_number,
                "company_name": profile.company_name,
                "job_title": profile.job_title,
                "website_url": profile.website_url,
                "message": profile.message,
                "city": profile.city,
                "state": profile.state,
                "country": profile.country,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at,
            }
        else:
            # Return basic user info if no profile exists
            return {
                "user_id": str(current_user.id),
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "email": current_user.email,
                "created_at": current_user.created_at,
            }
    except Exception as e:
        print(f"[USERS ERROR] Failed to get profile: {str(e)}")
        # Return minimal profile on error
        return {"user_id": str(current_user.id), "email": current_user.email}


@router.post("/profile")
async def create_or_update_profile(
    profile_data: UserProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create or update user profile"""
    try:
        profile = (
            db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        )

        if profile:
            # Update existing profile
            for field, value in profile_data.dict(exclude_unset=True).items():
                setattr(profile, field, value)
        else:
            # Create new profile
            profile = UserProfile(
                user_id=current_user.id, **profile_data.dict(exclude_unset=True)
            )
            db.add(profile)

        db.commit()
        db.refresh(profile)

        return {"message": "Profile updated successfully", "id": profile.id}

    except Exception as e:
        db.rollback()
        print(f"[USERS ERROR] Failed to update profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile",
        )
