import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from fastapi import HTTPException

from app.models.campaign import Campaign
from app.models.submission import Submission
from app.models.website import Website
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse


class CampaignService:
    """Service for managing campaigns"""

    def __init__(self, db: Session):
        self.db = db

    def create_campaign(
        self, user_id: uuid.UUID, campaign_data: CampaignCreate
    ) -> Campaign:
        """Create a new campaign"""
        campaign = Campaign(
            user_id=user_id,
            name=campaign_data.name,
            csv_filename=campaign_data.csv_filename,
            message=campaign_data.message,
            proxy=campaign_data.proxy,
            use_captcha=campaign_data.use_captcha,
            status="created",
        )

        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def get_campaign(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Campaign]:
        """Get a campaign by ID"""
        return (
            self.db.query(Campaign)
            .filter(Campaign.id == campaign_id, Campaign.user_id == user_id)
            .first()
        )

    def get_user_campaigns(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[List[Campaign], int]:
        """Get campaigns for a user with pagination"""
        query = self.db.query(Campaign).filter(Campaign.user_id == user_id)

        # Apply sorting
        order_col = getattr(Campaign, sort_by, Campaign.id)
        if sort_order == "desc":
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(asc(order_col))

        total = query.count()
        campaigns = query.offset((page - 1) * per_page).limit(per_page).all()

        return campaigns, total

    def update_campaign(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID, campaign_data: CampaignUpdate
    ) -> Optional[Campaign]:
        """Update a campaign"""
        campaign = self.get_campaign(campaign_id, user_id)
        if not campaign:
            return None

        update_data = campaign_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(campaign, field, value)

        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def delete_campaign(self, campaign_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete a campaign"""
        campaign = self.get_campaign(campaign_id, user_id)
        if not campaign:
            return False

        # Check if campaign has running submissions
        if campaign.status == "running":
            raise HTTPException(
                status_code=400,
                detail="Cannot delete campaign that is currently running",
            )

        self.db.delete(campaign)
        self.db.commit()
        return True

    def start_campaign(self, campaign_id: uuid.UUID, user_id: uuid.UUID) -> Campaign:
        """Start a campaign"""
        campaign = self.get_campaign(campaign_id, user_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        if campaign.status == "running":
            raise HTTPException(status_code=400, detail="Campaign is already running")

        campaign.status = "running"
        campaign.started_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def stop_campaign(self, campaign_id: uuid.UUID, user_id: uuid.UUID) -> Campaign:
        """Stop a running campaign"""
        campaign = self.get_campaign(campaign_id, user_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        if campaign.status != "running":
            raise HTTPException(status_code=400, detail="Campaign is not running")

        campaign.status = "stopped"
        campaign.completed_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def get_campaign_stats(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get campaign statistics"""
        campaign = self.get_campaign(campaign_id, user_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Get submission counts by status
        submission_stats = (
            self.db.query(Submission.status, self.db.func.count(Submission.id))
            .filter(Submission.campaign_id == campaign_id)
            .group_by(Submission.status)
            .all()
        )

        stats = {
            "total_urls": campaign.total_urls,
            "submitted_count": campaign.submitted_count,
            "failed_count": campaign.failed_count,
            "status_breakdown": {status: count for status, count in submission_stats},
        }

        return stats

    def add_urls_to_campaign(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID, urls: List[str]
    ) -> List[Website]:
        """Add URLs to a campaign"""
        campaign = self.get_campaign(campaign_id, user_id)
        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        websites = []
        for url in urls:
            website = Website(
                campaign_id=campaign_id,
                user_id=user_id,
                contact_url=url,
                status="pending",
            )
            websites.append(website)

        self.db.add_all(websites)

        # Update campaign URL count
        campaign.total_urls += len(urls)

        self.db.commit()
        return websites
