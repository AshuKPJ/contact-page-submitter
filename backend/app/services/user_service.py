import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User
from app.models.user_profile import UserProfile, UserProfile
from app.schemas.user import UserProfileCreate, UserContactProfileCreate
from app.core.security import hash_password
from app.core.encryption import encryption_service


class UserService:
    """Service for managing users and user profiles"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def create_user_profile(
        self, user_id: uuid.UUID, profile_data: UserProfileCreate
    ) -> UserProfile:
        """Create or update user profile"""
        # Check if profile already exists
        existing_profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )

        if existing_profile:
            # Update existing profile
            profile_dict = profile_data.dict(exclude_unset=True)
            for field, value in profile_dict.items():
                setattr(existing_profile, field, value)

            existing_profile.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_profile)
            return existing_profile
        else:
            # Create new profile
            profile = UserProfile(
                user_id=user_id,
                **profile_data.dict(exclude_unset=True),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile

    def create_contact_profile(
        self, user_id: uuid.UUID, profile_data: UserContactProfileCreate
    ) -> UserProfile:
        """Create or update user contact profile"""
        existing_profile = (
            self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        )

        if existing_profile:
            # Update existing profile
            profile_dict = profile_data.dict(exclude_unset=True)
            for field, value in profile_dict.items():
                setattr(existing_profile, field, value)

            self.db.commit()
            self.db.refresh(existing_profile)
            return existing_profile
        else:
            # Create new profile
            profile = UserProfile(
                user_id=user_id, **profile_data.dict(exclude_unset=True)
            )

            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
            return profile

    def update_captcha_credentials(
        self, user_id: uuid.UUID, username: str, password: str
    ) -> User:
        """Update user's CAPTCHA service credentials (encrypted)"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Encrypt credentials before storing
        user.captcha_username = encryption_service.encrypt(username)
        user.captcha_password_hash = encryption_service.encrypt(password)

        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_profile(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Get user profile"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def get_contact_profile(self, user_id: uuid.UUID) -> Optional[UserProfile]:
        """Get user contact profile"""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def delete_user(self, user_id: uuid.UUID) -> bool:
        """Delete a user and all related data"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        # Note: In production, you might want to soft delete
        # or archive data instead of hard delete
        self.db.delete(user)
        self.db.commit()
        return True

    def update_user_status(self, user_id: uuid.UUID, is_active: bool) -> User:
        """Update user active status"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user
