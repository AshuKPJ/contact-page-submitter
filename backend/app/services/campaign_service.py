# app/services/campaign_service.py

from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Tuple, Optional, Dict, Any
import uuid
import traceback

from app.models.campaign import Campaign
from app.models.submission import Submission
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse


class CampaignService:
    """Enhanced campaign service with comprehensive logging"""

    def __init__(self, db: Session):
        self.db = db

    def create_campaign(
        self, user_id: uuid.UUID, campaign_data: CampaignCreate
    ) -> CampaignResponse:
        """Create a new campaign with detailed logging"""

        print(f"[CAMPAIGN SERVICE] 🚀 Creating new campaign")
        print(f"[CAMPAIGN SERVICE] User ID: {str(user_id)[:8]}...")
        print(f"[CAMPAIGN SERVICE] Campaign Name: {campaign_data.name}")
        print(
            f"[CAMPAIGN SERVICE] Message Length: {len(campaign_data.message or '')} chars"
        )

        try:
            # Create campaign
            campaign = Campaign(
                user_id=user_id,
                name=campaign_data.name,
                message=campaign_data.message,
                status="draft",
                total_urls=0,
                submitted_count=0,
                failed_count=0,
                created_at=datetime.utcnow(),
            )

            self.db.add(campaign)
            self.db.flush()

            print(f"[CAMPAIGN SERVICE] ✅ Campaign created with ID: {campaign.id}")

            self.db.commit()

            print(f"[CAMPAIGN SERVICE] 💾 Campaign committed to database")

            return self._campaign_to_response(campaign)

        except Exception as e:
            print(f"[CAMPAIGN SERVICE] ❌ Failed to create campaign: {str(e)}")
            traceback.print_exc()
            self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create campaign")

    def get_user_campaigns(
        self, user_id: uuid.UUID, page: int = 1, per_page: int = 10
    ) -> Tuple[List[CampaignResponse], int]:
        """Get user's campaigns with pagination and logging"""

        print(
            f"[CAMPAIGN SERVICE] 📋 Getting campaigns for user: {str(user_id)[:8]}..."
        )
        print(f"[CAMPAIGN SERVICE] Page: {page}, Per page: {per_page}")

        try:
            # Calculate offset
            offset = (page - 1) * per_page

            # Get campaigns
            campaigns = (
                self.db.query(Campaign)
                .filter(Campaign.user_id == user_id)
                .order_by(Campaign.created_at.desc())
                .offset(offset)
                .limit(per_page)
                .all()
            )

            # Get total count
            total = self.db.query(Campaign).filter(Campaign.user_id == user_id).count()

            print(
                f"[CAMPAIGN SERVICE] ✅ Found {len(campaigns)} campaigns (total: {total})"
            )

            # Log campaign details
            for campaign in campaigns:
                print(
                    f"[CAMPAIGN SERVICE] 📊 Campaign {str(campaign.id)[:8]}... - {campaign.name} - Status: {campaign.status}"
                )

            campaign_responses = [
                self._campaign_to_response(campaign) for campaign in campaigns
            ]

            return campaign_responses, total

        except Exception as e:
            print(f"[CAMPAIGN SERVICE] ❌ Failed to get campaigns: {str(e)}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Failed to retrieve campaigns")

    def get_campaign(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[CampaignResponse]:
        """Get specific campaign with logging"""

        print(f"[CAMPAIGN SERVICE] 🔍 Getting campaign: {str(campaign_id)[:8]}...")
        print(f"[CAMPAIGN SERVICE] User ID: {str(user_id)[:8]}...")

        try:
            campaign = (
                self.db.query(Campaign)
                .filter(Campaign.id == campaign_id, Campaign.user_id == user_id)
                .first()
            )

            if campaign:
                print(f"[CAMPAIGN SERVICE] ✅ Campaign found: {campaign.name}")
                print(
                    f"[CAMPAIGN SERVICE] 📊 Status: {campaign.status}, URLs: {campaign.total_urls}"
                )

                # Get submission statistics
                total_submissions = (
                    self.db.query(Submission)
                    .filter(Submission.campaign_id == campaign_id)
                    .count()
                )

                processed_submissions = (
                    self.db.query(Submission)
                    .filter(
                        Submission.campaign_id == campaign_id,
                        Submission.status != "pending",
                    )
                    .count()
                )

                print(
                    f"[CAMPAIGN SERVICE] 📈 Submissions: {processed_submissions}/{total_submissions} processed"
                )

                return self._campaign_to_response(campaign)
            else:
                print(f"[CAMPAIGN SERVICE] ❌ Campaign not found or access denied")
                return None

        except Exception as e:
            print(f"[CAMPAIGN SERVICE] ❌ Failed to get campaign: {str(e)}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Failed to retrieve campaign")

    def update_campaign(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID, campaign_data: CampaignUpdate
    ) -> Optional[CampaignResponse]:
        """Update campaign with logging"""

        print(f"[CAMPAIGN SERVICE] ✏️ Updating campaign: {str(campaign_id)[:8]}...")

        try:
            campaign = (
                self.db.query(Campaign)
                .filter(Campaign.id == campaign_id, Campaign.user_id == user_id)
                .first()
            )

            if not campaign:
                print(f"[CAMPAIGN SERVICE] ❌ Campaign not found for update")
                return None

            print(
                f"[CAMPAIGN SERVICE] 📝 Current: {campaign.name} -> New: {campaign_data.name}"
            )

            # Update fields
            if campaign_data.name is not None:
                campaign.name = campaign_data.name
            if campaign_data.message is not None:
                campaign.message = campaign_data.message

            campaign.updated_at = datetime.utcnow()

            self.db.commit()

            print(f"[CAMPAIGN SERVICE] ✅ Campaign updated successfully")

            return self._campaign_to_response(campaign)

        except Exception as e:
            print(f"[CAMPAIGN SERVICE] ❌ Failed to update campaign: {str(e)}")
            self.db.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Failed to update campaign")

    def delete_campaign(self, campaign_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Delete campaign with logging"""

        print(f"[CAMPAIGN SERVICE] 🗑️ Deleting campaign: {str(campaign_id)[:8]}...")

        try:
            campaign = (
                self.db.query(Campaign)
                .filter(Campaign.id == campaign_id, Campaign.user_id == user_id)
                .first()
            )

            if not campaign:
                print(f"[CAMPAIGN SERVICE] ❌ Campaign not found for deletion")
                return False

            print(f"[CAMPAIGN SERVICE] 🗑️ Deleting campaign: {campaign.name}")

            # Delete related submissions first
            submission_count = (
                self.db.query(Submission)
                .filter(Submission.campaign_id == campaign_id)
                .count()
            )

            self.db.query(Submission).filter(
                Submission.campaign_id == campaign_id
            ).delete()
            print(
                f"[CAMPAIGN SERVICE] 🗑️ Deleted {submission_count} related submissions"
            )

            # Delete campaign
            self.db.delete(campaign)
            self.db.commit()

            print(f"[CAMPAIGN SERVICE] ✅ Campaign deleted successfully")

            return True

        except Exception as e:
            print(f"[CAMPAIGN SERVICE] ❌ Failed to delete campaign: {str(e)}")
            self.db.rollback()
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Failed to delete campaign")

    def start_campaign(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Start campaign processing with logging"""

        print(f"[CAMPAIGN SERVICE] ▶️ Starting campaign: {str(campaign_id)[:8]}...")

        try:
            campaign = (
                self.db.query(Campaign)
                .filter(Campaign.id == campaign_id, Campaign.user_id == user_id)
                .first()
            )

            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")

            print(f"[CAMPAIGN SERVICE] 📋 Campaign: {campaign.name}")
            print(f"[CAMPAIGN SERVICE] 📊 Current status: {campaign.status}")

            campaign.status = "running"
            campaign.started_at = datetime.utcnow()

            self.db.commit()

            print(f"[CAMPAIGN SERVICE] ✅ Campaign started successfully")

            return self._campaign_to_response(campaign)

        except Exception as e:
            print(f"[CAMPAIGN SERVICE] ❌ Failed to start campaign: {str(e)}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Failed to start campaign")

    def stop_campaign(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Stop campaign processing with logging"""

        print(f"[CAMPAIGN SERVICE] ⏹️ Stopping campaign: {str(campaign_id)[:8]}...")

        try:
            campaign = (
                self.db.query(Campaign)
                .filter(Campaign.id == campaign_id, Campaign.user_id == user_id)
                .first()
            )

            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")

            print(f"[CAMPAIGN SERVICE] 📋 Campaign: {campaign.name}")
            print(f"[CAMPAIGN SERVICE] 📊 Current status: {campaign.status}")

            campaign.status = "stopped"
            campaign.completed_at = datetime.utcnow()

            self.db.commit()

            print(f"[CAMPAIGN SERVICE] ✅ Campaign stopped successfully")

            return self._campaign_to_response(campaign)

        except Exception as e:
            print(f"[CAMPAIGN SERVICE] ❌ Failed to stop campaign: {str(e)}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail="Failed to stop campaign")

    def get_campaign_stats(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get campaign statistics with logging"""

        print(
            f"[CAMPAIGN SERVICE] 📊 Getting stats for campaign: {str(campaign_id)[:8]}..."
        )

        try:
            campaign = (
                self.db.query(Campaign)
                .filter(Campaign.id == campaign_id, Campaign.user_id == user_id)
                .first()
            )

            if not campaign:
                raise HTTPException(status_code=404, detail="Campaign not found")

            # Get submission statistics using text() for SQL
            stats = self.db.execute(
                text(
                    """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed
                FROM submissions 
                WHERE campaign_id = :campaign_id
            """
                ),
                {"campaign_id": str(campaign_id)},
            ).fetchone()

            result = {
                "campaign_id": str(campaign_id),
                "name": campaign.name,
                "status": campaign.status,
                "total": stats.total if stats else 0,
                "pending": stats.pending if stats else 0,
                "successful": stats.successful if stats else 0,
                "failed": stats.failed if stats else 0,
                "progress_percent": round(
                    (
                        (stats.successful / stats.total * 100)
                        if stats and stats.total > 0
                        else 0
                    ),
                    2,
                ),
                "started_at": (
                    campaign.started_at.isoformat() if campaign.started_at else None
                ),
                "completed_at": (
                    campaign.completed_at.isoformat() if campaign.completed_at else None
                ),
            }

            print(
                f"[CAMPAIGN SERVICE] 📈 Stats: {result['successful']}/{result['total']} successful"
            )

            return result

        except Exception as e:
            print(f"[CAMPAIGN SERVICE] ❌ Failed to get campaign stats: {str(e)}")
            traceback.print_exc()
            raise HTTPException(
                status_code=500, detail="Failed to retrieve campaign statistics"
            )

    def _campaign_to_response(self, campaign: Campaign) -> CampaignResponse:
        """Convert campaign model to response schema"""
        return CampaignResponse(
            id=str(campaign.id),
            name=campaign.name,
            message=campaign.message,
            status=campaign.status,
            total_urls=campaign.total_urls or 0,
            submitted_count=campaign.submitted_count or 0,
            failed_count=campaign.failed_count or 0,
            started_at=campaign.started_at,
            completed_at=campaign.completed_at,
            created_at=campaign.created_at or datetime.utcnow(),
        )
