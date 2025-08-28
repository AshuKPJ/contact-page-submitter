from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.campaign import (
    CampaignCreate,
    CampaignUpdate,
    CampaignResponse,
    CampaignList,
)
from app.services.campaign_service import CampaignService

router = APIRouter()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new campaign"""
    campaign_service = CampaignService(db)
    campaign = campaign_service.create_campaign(current_user.id, campaign_data)
    return campaign


@router.get("/", response_model=CampaignList)
async def get_campaigns(
    page: int = 1,
    per_page: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's campaigns"""
    campaign_service = CampaignService(db)
    campaigns, total = campaign_service.get_user_campaigns(
        current_user.id, page, per_page
    )
    return CampaignList(campaigns=campaigns, total=total, page=page, per_page=per_page)


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific campaign"""
    import uuid

    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")

    campaign_service = CampaignService(db)
    campaign = campaign_service.get_campaign(campaign_uuid, current_user.id)

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a campaign"""
    import uuid

    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")

    campaign_service = CampaignService(db)
    campaign = campaign_service.update_campaign(
        campaign_uuid, current_user.id, campaign_data
    )

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return campaign


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a campaign"""
    import uuid

    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")

    campaign_service = CampaignService(db)
    success = campaign_service.delete_campaign(campaign_uuid, current_user.id)

    if not success:
        raise HTTPException(status_code=404, detail="Campaign not found")

    return {"message": "Campaign deleted successfully"}


@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a campaign"""
    import uuid

    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")

    campaign_service = CampaignService(db)
    campaign = campaign_service.start_campaign(campaign_uuid, current_user.id)

    return {"message": "Campaign started successfully", "campaign": campaign}


@router.post("/{campaign_id}/stop")
async def stop_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stop a campaign"""
    import uuid

    try:
        campaign_uuid = uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")

    campaign_service = CampaignService(db)
    campaign = campaign_service.stop_campaign(campaign_uuid, current_user.id)

    return {"message": "Campaign stopped successfully", "campaign": campaign}
