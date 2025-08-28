from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date


class SubmissionStats(BaseModel):
    """Schema for submission statistics"""

    total_submissions: int = 0
    successful_submissions: int = 0
    failed_submissions: int = 0
    pending_submissions: int = 0
    success_rate: float = 0.0


class CampaignAnalytics(BaseModel):
    """Schema for campaign analytics"""

    campaign_id: str
    campaign_name: str
    total_urls: int = 0
    submitted_count: int = 0
    failed_count: int = 0
    success_rate: float = 0.0
    captcha_encounters: int = 0
    captcha_solve_rate: float = 0.0


class UserAnalytics(BaseModel):
    """Schema for user analytics"""

    user_id: str
    total_campaigns: int = 0
    total_submissions: int = 0
    stats: SubmissionStats


class SystemAnalytics(BaseModel):
    """Schema for system-wide analytics"""

    total_users: int = 0
    active_campaigns: int = 0
    total_submissions: int = 0
    stats: SubmissionStats
    top_performing_campaigns: List[CampaignAnalytics] = []
