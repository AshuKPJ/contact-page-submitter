from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime


class UserLogin(BaseModel):
    """Schema for user login request"""

    email: EmailStr
    password: str = Field(..., min_length=6)


class UserRegister(BaseModel):
    """Schema for user registration request"""

    email: EmailStr
    password: str = Field(..., min_length=6)
    firstName: str = Field(..., min_length=1, max_length=100, alias="first_name")
    lastName: str = Field(..., min_length=1, max_length=100, alias="last_name")
    role: Optional[Literal["user", "admin", "owner"]] = "user"


class UserResponse(BaseModel):
    """Schema for user response data"""

    id: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    subscription_status: Optional[str] = None

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for authentication response"""

    access_token: str
    user: UserResponse
