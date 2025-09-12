# app/workers/database_handler.py
"""Database operations for workers."""

import uuid
import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.submission import Submission, SubmissionStatus
from app.models.campaign import Campaign, CampaignStatus

logger = logging.getLogger(__name__)


def mark_submission_processing(db: Session, submission_id: uuid.UUID) -> bool:
    """Mark submission as processing."""
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()

        if not submission:
            logger.warning(f"Submission {submission_id} not found")
            return False

        submission.status = SubmissionStatus.PROCESSING
        submission.started_at = datetime.utcnow()
        db.commit()

        logger.debug(f"Marked submission {submission_id} as PROCESSING")
        return True

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        return False


def mark_submission_result(
    db: Session,
    submission_id: uuid.UUID,
    *,
    success: bool,
    method: Optional[str] = None,
    error_message: Optional[str] = None,
    email_extracted: Optional[str] = None,
) -> bool:
    """Mark submission with result."""
    try:
        submission = db.query(Submission).filter(Submission.id == submission_id).first()

        if not submission:
            logger.warning(f"Submission {submission_id} not found")
            return False

        submission.status = (
            SubmissionStatus.SUCCESS if success else SubmissionStatus.FAILED
        )
        submission.success = success
        submission.contact_method = method
        submission.error_message = error_message[:500] if error_message else None
        submission.processed_at = datetime.utcnow()

        if email_extracted:
            submission.email_extracted = email_extracted

        db.commit()

        logger.debug(f"Marked submission {submission_id}: success={success}")
        return True

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        return False


def pending_for_campaign(db: Session, campaign_id: uuid.UUID) -> List[Submission]:
    """Get pending submissions for campaign."""
    try:
        return (
            db.query(Submission)
            .filter(
                Submission.campaign_id == campaign_id,
                Submission.status == SubmissionStatus.PENDING,
            )
            .order_by(Submission.created_at.asc())
            .all()
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        return []


def update_campaign_status(
    db: Session, campaign_id: uuid.UUID, status: CampaignStatus, **fields
) -> bool:
    """Update campaign status."""
    try:
        campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()

        if not campaign:
            logger.warning(f"Campaign {campaign_id} not found")
            return False

        campaign.status = status

        for field_name, field_value in fields.items():
            if hasattr(campaign, field_name):
                setattr(campaign, field_name, field_value)

        db.commit()

        logger.debug(f"Updated campaign {campaign_id} to {status}")
        return True

    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        return False
