# app/schemas/auth.py

from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @validator("email")
    def email_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        return v.lower().strip()

    @validator("password")
    def password_must_not_be_empty(cls, v):
        if not v or len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

    @validator("email")
    def email_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        return v.lower().strip()

    @validator("password")
    def password_must_be_strong(cls, v):
        if not v or len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v

    @validator("first_name")
    def first_name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("First name cannot be empty")
        return v.strip()

    @validator("last_name")
    def last_name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Last name cannot be empty")
        return v.strip()


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool
    created_at: Optional[datetime] = None
    subscription_status: Optional[str] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
