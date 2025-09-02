# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import uuid


class UserLogin(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str = Field(..., min_length=6)


class UserRegister(BaseModel):
    """Registration request schema"""

    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    role: Optional[str] = Field(default="user", pattern="^(user|admin|owner)$")

    @validator("email")
    def email_to_lower(cls, v):
        return v.lower()

    @validator("first_name", "last_name")
    def name_validation(cls, v):
        return v.strip()


class UserResponse(BaseModel):
    """User response schema"""

    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    subscription_status: Optional[str]

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response schema"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    message: Optional[str] = None
