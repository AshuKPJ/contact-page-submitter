from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CampaignCreate(BaseModel):
    """Schema for creating a campaign"""

    name: str = Field(..., max_length=255)
    csv_filename: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = None
    proxy: Optional[str] = Field(None, max_length=255)
    use_captcha: bool = True


class CampaignUpdate(BaseModel):
    """Schema for updating a campaign"""

    name: Optional[str] = Field(None, max_length=255)
    csv_filename: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = None
    proxy: Optional[str] = Field(None, max_length=255)
    use_captcha: Optional[bool] = None
    status: Optional[str] = Field(None, max_length=50)


class CampaignResponse(BaseModel):
    """Schema for campaign response"""

    id: str
    user_id: str
    name: str
    csv_filename: Optional[str] = None
    started_at: Optional[datetime] = None
    status: Optional[str] = None
    message: Optional[str] = None
    proxy: Optional[str] = None
    use_captcha: bool = True
    total_urls: int = 0
    submitted_count: int = 0
    failed_count: int = 0
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CampaignList(BaseModel):
    """Schema for paginated campaign list"""

    campaigns: List[CampaignResponse]
    total: int
    page: int = 1
    per_page: int = 10
