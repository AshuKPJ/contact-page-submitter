# app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime


class UserProfileCreate(BaseModel):
    """Schema for creating user profile"""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    website_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=500)
    message: Optional[str] = None
    product_interest: Optional[str] = Field(None, max_length=255)
    budget_range: Optional[str] = Field(None, max_length=100)
    referral_source: Optional[str] = Field(None, max_length=255)
    preferred_contact: Optional[str] = Field(None, max_length=100)
    best_time_to_contact: Optional[str] = Field(None, max_length=100)
    contact_source: Optional[str] = Field(None, max_length=255)
    is_existing_customer: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=50)
    preferred_language: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    form_custom_field_1: Optional[str] = Field(None, max_length=500)
    form_custom_field_2: Optional[str] = Field(None, max_length=500)
    form_custom_field_3: Optional[str] = Field(None, max_length=500)
    dbc_username: Optional[str] = Field(None, max_length=255)
    dbc_password: Optional[str] = Field(None, max_length=255)

    @validator("email")
    def email_to_lower(cls, v):
        if v:
            return v.lower().strip()
        return v

    @validator("first_name", "last_name", "company_name", "job_title")
    def strip_strings(cls, v):
        if v:
            return v.strip()
        return v


class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)
    website_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    region: Optional[str] = Field(None, max_length=100)
    timezone: Optional[str] = Field(None, max_length=50)
    subject: Optional[str] = Field(None, max_length=500)
    message: Optional[str] = None
    product_interest: Optional[str] = Field(None, max_length=255)
    budget_range: Optional[str] = Field(None, max_length=100)
    referral_source: Optional[str] = Field(None, max_length=255)
    preferred_contact: Optional[str] = Field(None, max_length=100)
    best_time_to_contact: Optional[str] = Field(None, max_length=100)
    contact_source: Optional[str] = Field(None, max_length=255)
    is_existing_customer: Optional[bool] = None
    language: Optional[str] = Field(None, max_length=50)
    preferred_language: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    form_custom_field_1: Optional[str] = Field(None, max_length=500)
    form_custom_field_2: Optional[str] = Field(None, max_length=500)
    form_custom_field_3: Optional[str] = Field(None, max_length=500)

    @validator("first_name", "last_name", "company_name", "job_title")
    def strip_strings(cls, v):
        if v:
            return v.strip()
        return v


class UserContactProfileCreate(BaseModel):
    """Schema for creating user contact profile (simplified version)"""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=150)
    job_title: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=150)
    phone_number: Optional[str] = Field(None, max_length=50)
    website_url: Optional[str] = Field(None, max_length=200)
    subject: Optional[str] = Field(None, max_length=200)
    referral_source: Optional[str] = Field(None, max_length=200)
    message: Optional[str] = None
    preferred_contact: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    best_time_to_contact: Optional[str] = Field(None, max_length=100)
    budget_range: Optional[str] = Field(None, max_length=100)
    product_interest: Optional[str] = Field(None, max_length=150)
    is_existing_customer: Optional[bool] = False

    @validator("email")
    def email_to_lower(cls, v):
        if v:
            return v.lower().strip()
        return v


class UserProfileResponse(BaseModel):
    """Schema for user profile response"""

    id: int
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    phone_number: Optional[str] = None
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    industry: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None
    subject: Optional[str] = None
    message: Optional[str] = None
    product_interest: Optional[str] = None
    budget_range: Optional[str] = None
    referral_source: Optional[str] = None
    preferred_contact: Optional[str] = None
    best_time_to_contact: Optional[str] = None
    contact_source: Optional[str] = None
    is_existing_customer: Optional[bool] = None
    language: Optional[str] = None
    preferred_language: Optional[str] = None
    notes: Optional[str] = None
    form_custom_field_1: Optional[str] = None
    form_custom_field_2: Optional[str] = None
    form_custom_field_3: Optional[str] = None
    dbc_username: Optional[str] = None
    dbc_password: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user account"""

    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[Literal["user", "admin", "owner"]] = None
    profile_image_url: Optional[str] = None

    @validator("email")
    def email_to_lower(cls, v):
        if v:
            return v.lower().strip()
        return v

    @validator("first_name", "last_name")
    def strip_strings(cls, v):
        if v:
            return v.strip()
        return v


class UserStats(BaseModel):
    """Schema for user statistics"""

    user_id: str
    email: str
    total_campaigns: int = 0
    total_submissions: int = 0
    successful_submissions: int = 0
    failed_submissions: int = 0
    total_websites: int = 0
    success_rate: float = 0.0
    last_campaign_date: Optional[datetime] = None
    last_submission_date: Optional[datetime] = None


class UserSettings(BaseModel):
    """Schema for user settings"""

    user_id: str
    default_message_template: Optional[str] = None
    captcha_api_key: Optional[str] = None
    proxy_url: Optional[str] = None
    auto_submit: Optional[bool] = True


class UserSettingsUpdate(BaseModel):
    """Schema for updating user settings"""

    default_message_template: Optional[str] = None
    captcha_api_key: Optional[str] = None
    proxy_url: Optional[str] = None
    auto_submit: Optional[bool] = None
