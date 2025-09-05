"""
Database handler for all campaign-related database operations
Uses existing database setup from app.core.database
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.database import SessionLocal


class DatabaseHandler:
    """Handles all database operations for campaign processing"""

    def __init__(self, db: Session = None):
        """Initialize with existing session or create new one"""
        # Use provided session or create a new one
        self.session = db if db else SessionLocal()
        self.owns_session = db is None  # Track if we created the session

    def get_campaign(self, campaign_id: str):
        """Get campaign by ID"""
        from app.models.campaign import Campaign

        return self.session.query(Campaign).filter(Campaign.id == campaign_id).first()

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user contact profile for form filling"""
        from app.models.user_profile import UserProfile

        profile = (
            self.session.query(UserProfile)
            .filter(UserProfile.user_id == user_id)
            .first()
        )

        if profile:
            return {
                "first_name": profile.first_name or "John",
                "last_name": profile.last_name or "Doe",
                "email": profile.email or "contact@example.com",
                "phone_number": profile.phone_number,
                "company_name": profile.company_name,
                "message": profile.message
                or (
                    "Hello, I am interested in learning more about your services. "
                    "Please contact me at your earliest convenience. Thank you."
                ),
                "website_url": profile.website_url,
                "linkedin_url": profile.linkedin_url,
            }

        # Return default profile if none exists
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": "contact@example.com",
            "phone_number": "+1-555-0123",
            "company_name": "Example Company",
            "message": (
                "Hello, I am interested in learning more about your services. "
                "Please contact me at your earliest convenience. Thank you."
            ),
        }

    def get_pending_submissions(self, campaign_id: str, limit: int = 100) -> List:
        """Get pending submissions for a campaign"""
        from app.models.submission import Submission

        return (
            self.session.query(Submission)
            .filter(
                Submission.campaign_id == campaign_id, Submission.status == "pending"
            )
            .limit(limit)
            .all()
        )

    def update_submission(self, submission, result: Dict[str, Any]):
        """Update submission with processing result"""
        try:
            submission.status = result["status"]
            submission.success = result["success"]
            submission.contact_method = result.get("method")
            submission.email_extracted = result.get("email_extracted")
            submission.error_message = result.get("error")
            submission.processed_at = datetime.utcnow()

            # Store details if available
            if result.get("details"):
                details_str = " | ".join(result["details"])
                if len(details_str) > 500:
                    details_str = details_str[:497] + "..."
                submission.error_message = details_str

            self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"Error updating submission: {e}")
            raise

    def update_campaign_stats(
        self, campaign_id: str, successful: int, failed: int, status: str
    ):
        """Update campaign statistics and status"""
        from app.models.campaign import Campaign

        try:
            campaign = (
                self.session.query(Campaign).filter(Campaign.id == campaign_id).first()
            )

            if campaign:
                campaign.submitted_count = successful
                campaign.failed_count = failed
                campaign.status = status

                if status in ["completed", "failed"]:
                    campaign.completed_at = datetime.utcnow()

                self.session.commit()

        except Exception as e:
            self.session.rollback()
            print(f"Error updating campaign stats: {e}")
            raise

    def log_submission_result(self, campaign_id: str, result: Dict[str, Any]):
        """Log submission processing result (optional)"""
        try:
            # Check if SubmissionLog model exists
            from app.models.submission_log import SubmissionLog

            log = SubmissionLog(
                campaign_id=campaign_id,
                submission_id=result.get("submission_id"),
                target_url=result.get("url"),
                status=result.get("status"),
                action="PROCESSED",
                details=str(result)[:1000],
                timestamp=datetime.utcnow(),
            )

            self.session.add(log)
            self.session.commit()

        except ImportError:
            # SubmissionLog model doesn't exist, skip logging
            pass
        except Exception as e:
            # Don't fail on logging errors
            self.session.rollback()
            print(f"Warning: Could not log submission result: {e}")

    def close(self):
        """Close database connection only if we own it"""
        if self.owns_session and self.session:
            try:
                self.session.close()
            except Exception as e:
                print(f"Error closing database session: {e}")
