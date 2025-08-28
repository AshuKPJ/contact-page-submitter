from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class WebsiteCreate(BaseModel):
    """Schema for creating a website"""

    campaign_id: str
    domain: str = Field(..., max_length=255)
    contact_url: Optional[str] = None


class WebsiteUpdate(BaseModel):
    """Schema for updating a website"""

    domain: Optional[str] = Field(None, max_length=255)
    contact_url: Optional[str] = None
    form_detected: Optional[bool] = None
    form_type: Optional[str] = Field(None, max_length=100)
    form_labels: Optional[List[str]] = None
    form_field_count: Optional[int] = None
    has_captcha: Optional[bool] = None
    captcha_type: Optional[str] = Field(None, max_length=100)
    form_name_variants: Optional[List[str]] = None
    status: Optional[str] = Field(None, max_length=50)
    failure_reason: Optional[str] = None
    requires_proxy: Optional[bool] = None
    proxy_block_type: Optional[str] = None
    last_proxy_used: Optional[str] = None
    captcha_difficulty: Optional[str] = None
    captcha_solution_time: Optional[int] = None
    captcha_metadata: Optional[Dict[str, Any]] = None
    form_field_types: Optional[Dict[str, Any]] = None
    form_field_options: Optional[Dict[str, Any]] = None
    question_answer_fields: Optional[Dict[str, Any]] = None


class WebsiteResponse(BaseModel):
    """Schema for website response"""

    id: str
    campaign_id: Optional[str] = None
    user_id: Optional[str] = None
    domain: Optional[str] = None
    contact_url: Optional[str] = None
    form_detected: bool = False
    form_type: Optional[str] = None
    form_labels: Optional[List[str]] = None
    form_field_count: Optional[int] = None
    has_captcha: bool = False
    captcha_type: Optional[str] = None
    form_name_variants: Optional[List[str]] = None
    status: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    requires_proxy: bool = False
    proxy_block_type: Optional[str] = None
    last_proxy_used: Optional[str] = None
    captcha_difficulty: Optional[str] = None
    captcha_solution_time: Optional[int] = None
    captcha_metadata: Optional[Dict[str, Any]] = None
    form_field_types: Optional[Dict[str, Any]] = None
    form_field_options: Optional[Dict[str, Any]] = None
    question_answer_fields: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True
