from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class SubmissionCreate(BaseModel):
    """Schema for creating a submission"""

    website_id: str
    campaign_id: str
    url: Optional[str] = None
    contact_method: Optional[str] = Field(None, max_length=50)
    status: Literal["pending", "processing", "success", "failed"] = "pending"


class SubmissionUpdate(BaseModel):
    """Schema for updating a submission"""

    status: Optional[Literal["pending", "processing", "success", "failed"]] = None
    success: Optional[bool] = None
    response_status: Optional[int] = None
    error_message: Optional[str] = None
    form_fields_sent: Optional[Dict[str, Any]] = None
    email_extracted: Optional[str] = Field(None, max_length=255)
    captcha_encountered: Optional[bool] = None
    captcha_solved: Optional[bool] = None
    retry_count: Optional[int] = None
    processed_at: Optional[datetime] = None


class SubmissionResponse(BaseModel):
    """Schema for submission response"""

    id: str
    website_id: Optional[str] = None
    campaign_id: Optional[str] = None
    user_id: Optional[str] = None
    url: Optional[str] = None
    contact_method: Optional[str] = None
    email_extracted: Optional[str] = None
    status: str
    success: Optional[bool] = None
    response_status: Optional[int] = None
    error_message: Optional[str] = None
    form_fields_sent: Optional[Dict[str, Any]] = None
    captcha_encountered: bool = False
    captcha_solved: bool = False
    retry_count: int = 0
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SubmissionList(BaseModel):
    """Schema for paginated submission list"""

    submissions: List[SubmissionResponse]
    total: int
    page: int = 1
    per_page: int = 10
