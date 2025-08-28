from pydantic import BaseModel, EmailStr, Field
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


class UserContactProfileCreate(BaseModel):
    """Schema for creating user contact profile"""

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
    country: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    linkedin_url: Optional[str] = None
    notes: Optional[str] = None
    form_custom_field_1: Optional[str] = None
    form_custom_field_2: Optional[str] = None
    form_custom_field_3: Optional[str] = None
    contact_source: Optional[str] = None
    preferred_language: Optional[str] = None
    region: Optional[str] = None
    zip_code: Optional[str] = None


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
