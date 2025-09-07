# ============================================================================
# app/api/endpoints/campaigns.py - FIXED
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import uuid
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.campaign import Campaign
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignList,
)

router = APIRouter()


@router.get("/", response_model=CampaignList)
@router.get(
    "", response_model=CampaignList
)  # Support both with and without trailing slash
async def get_campaigns(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's campaigns"""
    try:
        offset = (page - 1) * per_page

        campaigns = (
            db.query(Campaign)
            .filter(Campaign.user_id == current_user.id)
            .order_by(Campaign.created_at.desc())
            .offset(offset)
            .limit(per_page)
            .all()
        )

        total = db.query(Campaign).filter(Campaign.user_id == current_user.id).count()

        campaign_responses = []
        for c in campaigns:
            campaign_responses.append(
                CampaignResponse(
                    id=str(c.id),
                    name=c.name,
                    message=c.message,
                    status=c.status or "draft",
                    total_urls=c.total_urls or 0,
                    submitted_count=c.submitted_count or 0,
                    failed_count=c.failed_count or 0,
                    started_at=c.started_at,
                    completed_at=c.completed_at,
                    created_at=c.created_at or datetime.utcnow(),
                )
            )

        return CampaignList(
            campaigns=campaign_responses, total=total, page=page, per_page=per_page
        )
    except Exception as e:
        print(f"[CAMPAIGNS ERROR] Failed to get campaigns: {str(e)}")
        # Return empty list on error
        return CampaignList(campaigns=[], total=0, page=page, per_page=per_page)


@router.post("/", response_model=CampaignResponse)
@router.post("", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new campaign"""
    try:
        campaign = Campaign(
            id=uuid.uuid4(),
            user_id=current_user.id,
            name=campaign_data.name,
            message=campaign_data.message,
            status="draft",
            total_urls=0,
            submitted_count=0,
            failed_count=0,
            created_at=datetime.utcnow(),
        )

        db.add(campaign)
        db.commit()
        db.refresh(campaign)

        return CampaignResponse(
            id=str(campaign.id),
            name=campaign.name,
            message=campaign.message,
            status=campaign.status,
            total_urls=0,
            submitted_count=0,
            failed_count=0,
            created_at=campaign.created_at,
        )
    except Exception as e:
        db.rollback()
        print(f"[CAMPAIGNS ERROR] Failed to create campaign: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create campaign",
        )


@router.get("/{campaign_id}/stats")
async def get_campaign_stats(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get campaign statistics"""
    try:
        campaign_uuid = uuid.UUID(campaign_id)

        campaign = (
            db.query(Campaign)
            .filter(Campaign.id == campaign_uuid, Campaign.user_id == current_user.id)
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        return {
            "campaign_id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status,
            "total": campaign.total_urls or 0,
            "successful": campaign.submitted_count or 0,
            "failed": campaign.failed_count or 0,
            "pending": (campaign.total_urls or 0)
            - (campaign.submitted_count or 0)
            - (campaign.failed_count or 0),
            "progress_percent": round(
                (
                    ((campaign.submitted_count or 0) / campaign.total_urls * 100)
                    if campaign.total_urls and campaign.total_urls > 0
                    else 0
                ),
                2,
            ),
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[CAMPAIGNS ERROR] Failed to get stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get campaign statistics")
