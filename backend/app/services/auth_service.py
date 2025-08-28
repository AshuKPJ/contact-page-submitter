# app/services/auth_service.py

import asyncio
from typing import Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
import uuid

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import UserLogin, UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def register_user(self, request: UserRegister) -> Dict[str, Any]:
        """Register a new user"""
        # Check if email exists
        existing_user = self.db.query(User).filter(User.email == request.email).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash password asynchronously
        loop = asyncio.get_event_loop()
        hashed_pwd = await loop.run_in_executor(None, hash_password, request.password)

        # Create new user
        new_user = User(
            email=request.email,
            hashed_password=hashed_pwd,
            first_name=request.firstName,
            last_name=request.lastName,
            role=request.role or "user",
        )

        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)

        # Create access token - FIX: Pass user_id as string
        access_token = create_access_token({"user_id": str(new_user.id)})

        return {"access_token": access_token, "user": self._user_to_dict(new_user)}

    async def login_user(self, request: UserLogin) -> Dict[str, Any]:
        """Authenticate user and return token"""
        # Find user
        user = self.db.query(User).filter(User.email == request.email).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Verify password asynchronously
        loop = asyncio.get_event_loop()
        pw_ok = await loop.run_in_executor(
            None, verify_password, request.password, user.hashed_password
        )

        if not pw_ok:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create token - FIX: Pass user_id as string
        access_token = create_access_token({"user_id": str(user.id)})

        return {"access_token": access_token, "user": self._user_to_dict(user)}

    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Convert user model to dictionary"""
        return {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "subscription_status": user.subscription_status,
        }
