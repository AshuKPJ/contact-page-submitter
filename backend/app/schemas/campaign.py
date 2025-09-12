# app/schemas/campaign.py
from __future__ import annotations
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import datetime


class CampaignCreate(BaseModel):
    """Schema for creating a campaign"""

    name: str = Field(..., min_length=1, max_length=255)
    message: Optional[str] = None
    proxy: Optional[str] = Field(None, max_length=255)
    use_captcha: Optional[bool] = True
    # Optional URLs to seed the campaign with
    urls: Optional[List[str]] = Field(default_factory=list)

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if v:
            return v.strip()
        raise ValueError("Campaign name cannot be empty")


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = None
    proxy: Optional[str] = Field(None, max_length=255)
    use_captcha: Optional[bool] = None
    status: Optional[
        Literal["DRAFT", "RUNNING", "PAUSED", "COMPLETED", "STOPPED", "FAILED"]
    ] = None

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if v is not None:
            return v.strip()
        return v


class CampaignResponse(BaseModel):
    """Schema for campaign response"""

    id: str
    user_id: Optional[str] = None
    name: Optional[str] = None
    csv_filename: Optional[str] = None
    started_at: Optional[datetime] = None
    status: Optional[str] = None
    message: Optional[str] = None
    proxy: Optional[str] = None
    use_captcha: Optional[bool] = None
    total_urls: Optional[int] = 0
    submitted_count: Optional[int] = 0
    failed_count: Optional[int] = 0
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    total_websites: Optional[int] = 0
    processed: Optional[int] = 0
    successful: Optional[int] = 0
    file_name: Optional[str] = None
    failed: Optional[int] = 0
    email_fallback: Optional[int] = 0
    no_form: Optional[int] = 0

    class Config:
        from_attributes = True


class CampaignList(BaseModel):
    """Schema for paginated campaign list"""

    campaigns: List[CampaignResponse]
    total: int
    page: int = 1
    per_page: int = 10


class CampaignStats(BaseModel):
    """Schema for campaign statistics"""

    campaign_id: str
    status: str
    total_submissions: int = 0
    completed_submissions: int = 0
    successful_submissions: int = 0
    failed_submissions: int = 0
    pending_submissions: int = 0
    progress_percent: float = 0.0
    success_rate: float = 0.0
    completion_status: Literal["not_started", "processing", "completed", "failed"] = (
        "not_started"
    )
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class CampaignUploadRequest(BaseModel):
    """Schema for campaign CSV upload"""

    file_name: str
    proxy: Optional[str] = None
    halt_on_captcha: Optional[bool] = True
    use_captcha: Optional[bool] = True


class CampaignUploadResponse(BaseModel):
    """Schema for campaign upload response"""

    success: bool
    message: str
    campaign_id: Optional[str] = None
    job_id: Optional[str] = None
    total_urls: int = 0
    status: str = "processing"
    csv_filename: Optional[str] = None


class CampaignActionRequest(BaseModel):
    """Schema for campaign actions (start/stop/pause)"""

    action: Literal["start", "stop", "pause", "resume"]
    reason: Optional[str] = None


class CampaignActionResponse(BaseModel):
    """Schema for campaign action response"""

    success: bool
    message: str
    campaign_id: str
    old_status: str
    new_status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
