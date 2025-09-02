import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
import uuid

from app.core.database import SessionLocal
from app.models.campaign import Campaign
from app.models.submission import Submission
from app.models.user_profile import UserContactProfile
from app.services.browser_automation_service import BrowserAutomationService

logger = logging.getLogger(__name__)


class CampaignProcessor:
    """Processes campaigns by automating form submissions"""

    def __init__(self, campaign_id: str):
        self.campaign_id = (
            uuid.UUID(campaign_id) if isinstance(campaign_id, str) else campaign_id
        )
        self.db = SessionLocal()
        self.browser_service = BrowserAutomationService()
        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "email_fallback": 0,
        }

    async def run(self):
        """Main processing method"""
        try:
            logger.info(f"Starting campaign processing: {self.campaign_id}")

            # Get campaign
            campaign = (
                self.db.query(Campaign).filter(Campaign.id == self.campaign_id).first()
            )

            if not campaign:
                raise ValueError(f"Campaign {self.campaign_id} not found")

            # Update campaign status
            campaign.status = "processing"
            campaign.started_at = datetime.utcnow()
            self.db.commit()

            # Get user contact profile
            user_profile = (
                self.db.query(UserContactProfile)
                .filter(UserContactProfile.user_id == campaign.user_id)
                .first()
            )

            if not user_profile:
                raise ValueError("User contact profile not found")

            # Prepare user data
            user_data = {
                "first_name": user_profile.first_name or "John",
                "last_name": user_profile.last_name or "Doe",
                "email": user_profile.email or "contact@example.com",
                "phone_number": user_profile.phone_number,
                "company_name": user_profile.company_name,
                "subject": user_profile.subject or "Business Inquiry",
                "message": user_profile.message
                or campaign.message
                or "I am interested in learning more about your services.",
                "website_url": user_profile.website_url,
            }

            # Get pending submissions
            submissions = (
                self.db.query(Submission)
                .filter(
                    Submission.campaign_id == self.campaign_id,
                    Submission.status == "pending",
                )
                .all()
            )

            self.stats["total"] = len(submissions)
            logger.info(f"Found {len(submissions)} submissions to process")

            # Initialize browser
            await self.browser_service.initialize()

            # Process each submission
            for idx, submission in enumerate(submissions, 1):
                try:
                    logger.info(
                        f"Processing {idx}/{len(submissions)}: {submission.url}"
                    )

                    # Process website
                    result = await self.browser_service.process_website(
                        submission.url, user_data
                    )

                    # Update submission
                    submission.status = "success" if result["success"] else "failed"
                    submission.success = result["success"]
                    submission.contact_method = result["method"]
                    submission.error_message = result.get("error")
                    submission.processed_at = datetime.utcnow()

                    if result["method"] == "email" and result.get("details", {}).get(
                        "primary_email"
                    ):
                        submission.email_extracted = result["details"]["primary_email"]

                    self.db.commit()

                    # Update stats
                    self.stats["processed"] += 1
                    if result["success"]:
                        self.stats["successful"] += 1
                        if result["method"] == "email":
                            self.stats["email_fallback"] += 1
                    else:
                        self.stats["failed"] += 1

                    # Update campaign stats
                    campaign.submitted_count = self.stats["successful"]
                    campaign.failed_count = self.stats["failed"]
                    self.db.commit()

                    # Rate limiting
                    await asyncio.sleep(2)  # Wait 2 seconds between submissions

                except Exception as e:
                    logger.error(
                        f"Error processing submission {submission.id}: {str(e)}"
                    )
                    submission.status = "failed"
                    submission.error_message = str(e)[:500]
                    submission.processed_at = datetime.utcnow()
                    self.db.commit()
                    self.stats["failed"] += 1

            # Update campaign completion
            campaign.status = "completed"
            campaign.completed_at = datetime.utcnow()
            campaign.total_urls = self.stats["total"]
            campaign.submitted_count = self.stats["successful"]
            campaign.failed_count = self.stats["failed"]
            self.db.commit()

            logger.info(f"Campaign completed: {self.stats}")

        except Exception as e:
            logger.error(f"Campaign processing failed: {str(e)}")

            # Update campaign status
            campaign = (
                self.db.query(Campaign).filter(Campaign.id == self.campaign_id).first()
            )

            if campaign:
                campaign.status = "failed"
                campaign.completed_at = datetime.utcnow()
                self.db.commit()

            raise

        finally:
            # Cleanup
            await self.browser_service.cleanup()
            self.db.close()


async def process_campaign_async(campaign_id: str):
    """Async wrapper for campaign processing"""
    processor = CampaignProcessor(campaign_id)
    await processor.run()


def process_campaign(campaign_id: str):
    """Synchronous wrapper for campaign processing"""
    asyncio.run(process_campaign_async(campaign_id))
