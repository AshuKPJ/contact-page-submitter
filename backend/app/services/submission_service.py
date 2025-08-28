import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, and_
from fastapi import HTTPException

from app.models.submission import Submission
from app.models.submission_log import SubmissionLog
from app.models.campaign import Campaign
from app.models.website import Website
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionResponse,
)


class SubmissionService:
    """Service for managing form submissions"""

    def __init__(self, db: Session):
        self.db = db

    def create_submission(
        self, user_id: uuid.UUID, submission_data: SubmissionCreate
    ) -> Submission:
        """Create a new submission"""
        # Verify campaign belongs to user
        campaign = (
            self.db.query(Campaign)
            .filter(
                and_(
                    Campaign.id == submission_data.campaign_id,
                    Campaign.user_id == user_id,
                )
            )
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        submission = Submission(
            website_id=submission_data.website_id,
            campaign_id=submission_data.campaign_id,
            user_id=user_id,
            url=submission_data.url,
            contact_method=submission_data.contact_method,
            status=submission_data.status,
        )

        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def get_submission(
        self, submission_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Submission]:
        """Get a submission by ID"""
        return (
            self.db.query(Submission)
            .filter(and_(Submission.id == submission_id, Submission.user_id == user_id))
            .first()
        )

    def get_campaign_submissions(
        self,
        campaign_id: uuid.UUID,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None,
    ) -> tuple[List[Submission], int]:
        """Get submissions for a campaign"""
        # Verify campaign belongs to user
        campaign = (
            self.db.query(Campaign)
            .filter(and_(Campaign.id == campaign_id, Campaign.user_id == user_id))
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        query = self.db.query(Submission).filter(Submission.campaign_id == campaign_id)

        if status:
            query = query.filter(Submission.status == status)

        # Order by creation date (newest first)
        query = query.order_by(desc(Submission.created_at))

        total = query.count()
        submissions = query.offset((page - 1) * per_page).limit(per_page).all()

        return submissions, total

    def update_submission(
        self,
        submission_id: uuid.UUID,
        user_id: uuid.UUID,
        submission_data: SubmissionUpdate,
    ) -> Optional[Submission]:
        """Update a submission"""
        submission = self.get_submission(submission_id, user_id)
        if not submission:
            return None

        update_data = submission_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(submission, field, value)

        submission.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(submission)
        return submission

    def bulk_create_submissions(
        self, user_id: uuid.UUID, campaign_id: uuid.UUID, urls: List[str]
    ) -> List[Submission]:
        """Create multiple submissions for a campaign"""
        # Verify campaign belongs to user
        campaign = (
            self.db.query(Campaign)
            .filter(and_(Campaign.id == campaign_id, Campaign.user_id == user_id))
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        submissions = []
        for url in urls:
            submission = Submission(
                campaign_id=campaign_id, user_id=user_id, url=url, status="pending"
            )
            submissions.append(submission)

        self.db.add_all(submissions)
        self.db.commit()

        # Refresh all submissions
        for submission in submissions:
            self.db.refresh(submission)

        return submissions

    def get_user_submissions(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        per_page: int = 10,
        status: Optional[str] = None,
    ) -> tuple[List[Submission], int]:
        """Get all submissions for a user"""
        query = self.db.query(Submission).filter(Submission.user_id == user_id)

        if status:
            query = query.filter(Submission.status == status)

        query = query.order_by(desc(Submission.created_at))

        total = query.count()
        submissions = query.offset((page - 1) * per_page).limit(per_page).all()

        return submissions, total

    def retry_failed_submissions(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID
    ) -> int:
        """Retry all failed submissions in a campaign"""
        # Verify campaign belongs to user
        campaign = (
            self.db.query(Campaign)
            .filter(and_(Campaign.id == campaign_id, Campaign.user_id == user_id))
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Reset failed submissions to pending
        failed_submissions = (
            self.db.query(Submission)
            .filter(
                and_(
                    Submission.campaign_id == campaign_id, Submission.status == "failed"
                )
            )
            .all()
        )

        count = 0
        for submission in failed_submissions:
            submission.status = "pending"
            submission.retry_count += 1
            submission.error_message = None
            submission.updated_at = datetime.utcnow()
            count += 1

        self.db.commit()
        return count

    def log_submission_event(
        self, submission_id: uuid.UUID, action: str, details: str, status: str = "info"
    ):
        """Log a submission event"""
        submission = (
            self.db.query(Submission).filter(Submission.id == submission_id).first()
        )

        if submission:
            log = SubmissionLog(
                campaign_id=submission.campaign_id,
                submission_id=submission_id,
                user_id=submission.user_id,
                website_id=submission.website_id,
                target_url=submission.url,
                action=action,
                details=details,
                status=status,
                timestamp=datetime.utcnow(),
            )

            self.db.add(log)
            self.db.commit()

    def get_submission_logs(
        self, submission_id: uuid.UUID, user_id: uuid.UUID
    ) -> List[SubmissionLog]:
        """Get logs for a specific submission"""
        # Verify submission belongs to user
        submission = self.get_submission(submission_id, user_id)
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        return (
            self.db.query(SubmissionLog)
            .filter(SubmissionLog.submission_id == submission_id)
            .order_by(desc(SubmissionLog.timestamp))
            .all()
        )
