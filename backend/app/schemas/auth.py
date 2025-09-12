# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime


class UserLogin(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str = Field(..., min_length=1)


class UserRegister(BaseModel):
    """Registration request schema"""

    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)

    @validator("email")
    def email_to_lower(cls, v):
        return v.lower().strip()

    @validator("first_name", "last_name")
    def name_validation(cls, v):
        if v:
            return v.strip()
        return v


class UserResponse(BaseModel):
    """User response schema"""

    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = "user"
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    subscription_status: Optional[str] = None
    profile_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response schema"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    message: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""

    old_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=6)


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""

    email: EmailStr

    @validator("email")
    def email_to_lower(cls, v):
        return v.lower().strip()


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""

    token: str
    new_password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    """Token response schema"""

    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
