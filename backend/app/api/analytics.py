from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    SubmissionStats,
    CampaignAnalytics,
    UserAnalytics,
    SystemAnalytics,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/user", response_model=UserAnalytics)
async def get_user_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get analytics for current user"""
    analytics_service = AnalyticsService(db)
    analytics = analytics_service.get_user_analytics(
        current_user.id, start_date, end_date
    )
    return analytics


@router.get("/campaign/{campaign_id}", response_model=CampaignAnalytics)
async def get_campaign_analytics(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get analytics for a specific campaign"""
    import uuid

    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")

    analytics_service = AnalyticsService(db)
    analytics = analytics_service.get_campaign_analytics(campaign_uuid, current_user.id)
    return analytics


@router.get("/daily-stats")
async def get_daily_stats(
    days: int = Query(7, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get daily submission statistics"""
    analytics_service = AnalyticsService(db)
    stats = analytics_service.get_daily_stats(user_id=current_user.id, days=days)
    return {"daily_stats": stats}
