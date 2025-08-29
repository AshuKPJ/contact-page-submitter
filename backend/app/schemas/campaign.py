# app/schemas/campaign.py

from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List


class CampaignCreate(BaseModel):
    name: str
    message: Optional[str] = None

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Campaign name cannot be empty")
        return v.strip()


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None

    @validator("name")
    def name_must_not_be_empty(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("Campaign name cannot be empty")
        return v.strip() if v else None


class CampaignResponse(BaseModel):
    id: str
    name: str
    message: Optional[str] = None
    status: str
    total_urls: int = 0
    submitted_count: int = 0
    failed_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CampaignList(BaseModel):
    campaigns: List[CampaignResponse]
    total: int
    page: int
    per_page: int
