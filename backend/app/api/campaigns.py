# app/api/campaigns.py - Enhanced version with better integration and error handling
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    BackgroundTasks,
    status,
    Request,
    Query,
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from uuid import UUID
from typing import List, Optional
import time
import uuid
import traceback
from datetime import datetime

from app.core.database import get_db
from app.models.campaign import Campaign, CampaignStatus
from app.models.submission import Submission, SubmissionStatus
from app.schemas.campaign import CampaignCreate, CampaignResponse
from app.core.dependencies import get_current_user
from app.services.log_service import LogService as ApplicationInsightsLogger
from app.models.user import User

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"], redirect_slashes=False)


def _safe_log(callable_):
    try:
        callable_()
    except Exception:
        pass


def _ensure_owner(
    db: Session, user: User, campaign_id: UUID, logger: ApplicationInsightsLogger
) -> Campaign:
    try:
        query_start = time.time()
        campaign = (
            db.query(Campaign)
            .filter(Campaign.id == campaign_id, Campaign.user_id == user.id)
            .first()
        )
        query_time = (time.time() - query_start) * 1000

        _safe_log(
            lambda: logger.track_database_operation(
                operation="SELECT",
                table="campaigns",
                query_time_ms=query_time,
                success=True,
            )
        )

        if not campaign:
            _safe_log(
                lambda: logger.track_user_action(
                    action="campaign_access_denied",
                    target="campaign",
                    properties={
                        "campaign_id": str(campaign_id),
                        "reason": "not_found_or_not_owner",
                    },
                )
            )
            raise HTTPException(status_code=404, detail="Campaign not found")

        return campaign
    except SQLAlchemyError as e:
        db.rollback()
        _safe_log(lambda: logger.track_exception(e, handled=True))
        raise HTTPException(status_code=500, detail="Database error occurred")


def _to_response(c: Campaign) -> CampaignResponse:
    """Convert Campaign model to response with enhanced data"""
    # Calculate additional stats
    total_submissions = 0
    successful_submissions = 0
    failed_submissions = 0
    pending_submissions = 0

    if hasattr(c, "submissions") and c.submissions:
        total_submissions = len(c.submissions)
        successful_submissions = sum(
            1 for s in c.submissions if s.status == SubmissionStatus.SUCCESS
        )
        failed_submissions = sum(
            1 for s in c.submissions if s.status == SubmissionStatus.FAILED
        )
        pending_submissions = sum(
            1 for s in c.submissions if s.status == SubmissionStatus.PENDING
        )

    # Calculate progress
    progress_percent = 0
    if total_submissions > 0:
        processed = successful_submissions + failed_submissions
        progress_percent = round((processed / total_submissions) * 100, 2)

    # Calculate success rate
    success_rate = 0
    processed_total = successful_submissions + failed_submissions
    if processed_total > 0:
        success_rate = round((successful_submissions / processed_total) * 100, 2)

    return CampaignResponse(
        id=str(c.id),
        user_id=str(c.user_id),
        name=getattr(c, "name", "Untitled Campaign"),
        message=getattr(c, "message", ""),
        status=(
            getattr(c, "status", CampaignStatus.DRAFT).value
            if hasattr(getattr(c, "status", None), "value")
            else str(getattr(c, "status", "draft"))
        ),
        created_at=getattr(c, "created_at", datetime.utcnow()),
        updated_at=getattr(c, "updated_at", datetime.utcnow()),
        started_at=getattr(c, "started_at", None),
        completed_at=getattr(c, "completed_at", None),
        total_urls=getattr(c, "total_urls", total_submissions),
        submitted_count=getattr(c, "submitted_count", successful_submissions),
        failed_count=getattr(c, "failed_count", failed_submissions),
        csv_filename=getattr(c, "csv_filename", None),
        progress_percent=progress_percent,
        success_rate=success_rate,
        pending_count=pending_submissions,
    )


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(
    payload: CampaignCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enhanced campaign creation with better validation and error handling"""
    logger = ApplicationInsightsLogger(db)
    _safe_log(lambda: logger.set_context(user_id=str(user.id)))

    _safe_log(
        lambda: logger.track_workflow_step(
            workflow_name="campaign_creation",
            step_name="start",
            step_number=1,
            total_steps=3,
        )
    )
    _safe_log(
        lambda: logger.track_user_action(
            action="create_campaign_initiated",
            target="campaign",
            properties={
                "campaign_name": payload.name,
                "has_message": bool(payload.message),
                "message_length": len(payload.message or ""),
            },
        )
    )

    try:
        # Enhanced validation
        campaign_name = payload.name.strip() if payload.name else "Untitled Campaign"
        if len(campaign_name) > 255:
            raise HTTPException(
                status_code=400, detail="Campaign name too long (max 255 characters)"
            )

        campaign_message = payload.message.strip() if payload.message else ""
        if len(campaign_message) > 5000:
            raise HTTPException(
                status_code=400,
                detail="Campaign message too long (max 5000 characters)",
            )

        # Check for duplicate campaign names
        existing_campaign = (
            db.query(Campaign)
            .filter(Campaign.user_id == user.id, Campaign.name == campaign_name)
            .first()
        )

        if existing_campaign:
            # Auto-append timestamp to make it unique
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            campaign_name = f"{campaign_name}_{timestamp}"

        campaign = Campaign(
            user_id=user.id,
            name=campaign_name,
            message=campaign_message,
            status=CampaignStatus.DRAFT,  # Use enum
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        db_start = time.time()
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        db_time = (time.time() - db_start) * 1000

        _safe_log(lambda: logger.set_context(campaign_id=str(campaign.id)))
        _safe_log(
            lambda: logger.track_database_operation(
                operation="INSERT",
                table="campaigns",
                query_time_ms=db_time,
                affected_rows=1,
                success=True,
            )
        )
        _safe_log(
            lambda: logger.track_business_event(
                event_name="campaign_created",
                properties={
                    "campaign_id": str(campaign.id),
                    "campaign_name": campaign.name,
                    "status": campaign.status.value,
                    "has_message": bool(campaign.message),
                },
                metrics={"creation_time_ms": db_time},
            )
        )

        return _to_response(campaign)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        _safe_log(lambda: logger.track_exception(e, handled=False))
        _safe_log(
            lambda: logger.track_workflow_step(
                workflow_name="campaign_creation",
                step_name="error",
                step_number=0,
                total_steps=3,
                success=False,
                properties={"error": str(e)},
            )
        )
        raise HTTPException(status_code=500, detail="Failed to create campaign")
    except Exception as e:
        db.rollback()
        logger.info(f"Unexpected error in create_campaign: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("", response_model=List[CampaignResponse])
def list_campaigns(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    limit: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """Enhanced campaign listing with filtering and better pagination"""
    logger = ApplicationInsightsLogger(db)
    _safe_log(lambda: logger.set_context(user_id=str(user.id)))

    eff_limit = limit if limit is not None else per_page

    _safe_log(
        lambda: logger.track_user_action(
            action="list_campaigns",
            target="campaigns",
            properties={
                "limit": eff_limit,
                "page": page,
                "per_page": per_page,
                "status_filter": status_filter,
            },
        )
    )

    try:
        query_start = time.time()

        # Build query with optional status filter
        q = db.query(Campaign).filter(Campaign.user_id == user.id)

        if status_filter:
            try:
                status_enum = CampaignStatus(status_filter.upper())
                q = q.filter(Campaign.status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid status filter: {status_filter}"
                )

        # Order by creation date (newest first)
        q = q.order_by(Campaign.created_at.desc())

        # Get total count for pagination
        total_count = q.count()

        # Apply pagination
        offset = (page - 1) * eff_limit
        rows = q.offset(offset).limit(eff_limit).all()

        query_time = (time.time() - query_start) * 1000

        _safe_log(
            lambda: logger.track_database_operation(
                operation="SELECT",
                table="campaigns",
                query_time_ms=query_time,
                affected_rows=len(rows),
                success=True,
            )
        )
        _safe_log(
            lambda: logger.track_metric(
                name="campaigns_retrieved",
                value=len(rows),
                properties={
                    "user_id": str(user.id),
                    "total_available": total_count,
                    "page": page,
                    "filtered": bool(status_filter),
                },
            )
        )

        return [_to_response(c) for c in rows]

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        _safe_log(lambda: logger.track_exception(e, handled=True))
        raise HTTPException(status_code=500, detail="Failed to fetch campaigns")
    except Exception as e:
        logger.info(f"Unexpected error in list_campaigns: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/{campaign_id}", response_model=CampaignResponse)
def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enhanced campaign retrieval with detailed statistics"""
    logger = ApplicationInsightsLogger(db)
    _safe_log(
        lambda: logger.set_context(user_id=str(user.id), campaign_id=str(campaign_id))
    )
    _safe_log(
        lambda: logger.track_user_action(
            action="view_campaign",
            target="campaign",
            properties={"campaign_id": str(campaign_id)},
        )
    )

    try:
        campaign = _ensure_owner(db, user, campaign_id, logger)

        # Load related submissions for enhanced statistics
        campaign.submissions = (
            db.query(Submission).filter(Submission.campaign_id == campaign_id).all()
        )

        return _to_response(campaign)

    except HTTPException:
        raise
    except Exception as e:
        logger.info(f"Unexpected error in get_campaign: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.put("/{campaign_id}", response_model=CampaignResponse)
def update_campaign(
    campaign_id: UUID,
    payload: CampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enhanced campaign update with validation"""
    logger = ApplicationInsightsLogger(db)
    _safe_log(
        lambda: logger.set_context(user_id=str(user.id), campaign_id=str(campaign_id))
    )
    _safe_log(
        lambda: logger.track_user_action(
            action="update_campaign_initiated",
            target="campaign",
            properties={
                "campaign_id": str(campaign_id),
                "has_name_change": bool(payload.name),
                "has_message_change": bool(payload.message),
            },
        )
    )

    try:
        campaign = _ensure_owner(db, user, campaign_id, logger)

        # Check if campaign can be updated
        if campaign.status == CampaignStatus.ACTIVE:
            raise HTTPException(
                status_code=400,
                detail="Cannot update active campaign. Please stop the campaign first.",
            )

        # Enhanced validation
        changes = {}

        if payload.name and payload.name.strip():
            new_name = payload.name.strip()
            if len(new_name) > 255:
                raise HTTPException(
                    status_code=400,
                    detail="Campaign name too long (max 255 characters)",
                )

            if new_name != campaign.name:
                # Check for duplicate names
                existing = (
                    db.query(Campaign)
                    .filter(
                        Campaign.user_id == user.id,
                        Campaign.name == new_name,
                        Campaign.id != campaign_id,
                    )
                    .first()
                )

                if existing:
                    raise HTTPException(
                        status_code=400, detail="Campaign name already exists"
                    )

                changes["name"] = {"old": campaign.name, "new": new_name}
                campaign.name = new_name

        if payload.message is not None:
            new_message = payload.message.strip()
            if len(new_message) > 5000:
                raise HTTPException(
                    status_code=400,
                    detail="Campaign message too long (max 5000 characters)",
                )

            if new_message != (campaign.message or ""):
                changes["message"] = {
                    "old_length": len(campaign.message or ""),
                    "new_length": len(new_message),
                }
                campaign.message = new_message

        if changes:
            campaign.updated_at = datetime.utcnow()

            db_start = time.time()
            db.add(campaign)
            db.commit()
            db.refresh(campaign)
            db_time = (time.time() - db_start) * 1000

            _safe_log(
                lambda: logger.track_database_operation(
                    operation="UPDATE",
                    table="campaigns",
                    query_time_ms=db_time,
                    affected_rows=1,
                    success=True,
                )
            )
            _safe_log(
                lambda: logger.track_business_event(
                    event_name="campaign_updated",
                    properties={
                        "campaign_id": str(campaign_id),
                        "changes": list(changes.keys()),
                    },
                    metrics={"update_time_ms": db_time},
                )
            )
        else:
            _safe_log(
                lambda: logger.track_user_action(
                    action="update_campaign_no_changes",
                    target="campaign",
                    properties={"campaign_id": str(campaign_id)},
                )
            )

        return _to_response(campaign)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        _safe_log(lambda: logger.track_exception(e, handled=False))
        raise HTTPException(status_code=500, detail="Failed to update campaign")
    except Exception as e:
        db.rollback()
        logger.info(f"Unexpected error in update_campaign: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/{campaign_id}")
def delete_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enhanced campaign deletion with safety checks"""
    logger = ApplicationInsightsLogger(db)
    _safe_log(
        lambda: logger.set_context(user_id=str(user.id), campaign_id=str(campaign_id))
    )
    _safe_log(
        lambda: logger.track_user_action(
            action="delete_campaign_initiated",
            target="campaign",
            properties={"campaign_id": str(campaign_id)},
        )
    )

    try:
        campaign = _ensure_owner(db, user, campaign_id, logger)

        # Enhanced safety checks
        if campaign.status == CampaignStatus.ACTIVE:
            _safe_log(
                lambda: logger.track_user_action(
                    action="delete_campaign_blocked",
                    target="campaign",
                    properties={
                        "campaign_id": str(campaign_id),
                        "reason": "campaign_running",
                    },
                )
            )
            raise HTTPException(
                status_code=400,
                detail="Cannot delete a running campaign. Please stop the campaign first.",
            )

        # Get submission count for logging
        submission_count = (
            db.query(Submission).filter(Submission.campaign_id == campaign_id).count()
        )

        db_start = time.time()

        # Delete related submissions first (cascading delete)
        db.query(Submission).filter(Submission.campaign_id == campaign_id).delete()

        # Delete the campaign
        db.delete(campaign)
        db.commit()

        db_time = (time.time() - db_start) * 1000

        _safe_log(
            lambda: logger.track_database_operation(
                operation="DELETE",
                table="campaigns",
                query_time_ms=db_time,
                affected_rows=1,
                success=True,
            )
        )
        _safe_log(
            lambda: logger.track_business_event(
                event_name="campaign_deleted",
                properties={
                    "campaign_id": str(campaign_id),
                    "campaign_name": campaign.name,
                    "submission_count": submission_count,
                },
                metrics={"delete_time_ms": db_time},
            )
        )

        return {
            "success": True,
            "message": f"Campaign '{campaign.name}' and {submission_count} submissions deleted successfully",
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        _safe_log(lambda: logger.track_exception(e, handled=False))
        raise HTTPException(status_code=500, detail="Failed to delete campaign")
    except Exception as e:
        db.rollback()
        logger.info(f"Unexpected error in delete_campaign: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/{campaign_id}/start")
def start_campaign(
    campaign_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enhanced campaign start with validation and background processing"""
    logger = ApplicationInsightsLogger(db)
    _safe_log(
        lambda: logger.set_context(user_id=str(user.id), campaign_id=str(campaign_id))
    )
    _safe_log(
        lambda: logger.track_user_action(
            action="start_campaign_initiated",
            target="campaign",
            properties={"campaign_id": str(campaign_id)},
        )
    )

    try:
        campaign = _ensure_owner(db, user, campaign_id, logger)

        # Validation checks
        if campaign.status == CampaignStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Campaign is already running")

        if campaign.status == CampaignStatus.COMPLETED:
            raise HTTPException(status_code=400, detail="Campaign is already completed")

        # Check if there are pending submissions
        pending_count = (
            db.query(Submission)
            .filter(
                Submission.campaign_id == campaign_id,
                Submission.status == SubmissionStatus.PENDING,
            )
            .count()
        )

        if pending_count == 0:
            raise HTTPException(
                status_code=400,
                detail="No pending submissions found. Please upload a CSV file first.",
            )

        # Update campaign status
        campaign.status = CampaignStatus.ACTIVE
        campaign.started_at = datetime.utcnow()
        campaign.updated_at = datetime.utcnow()

        db.add(campaign)
        db.commit()

        # Start background processing
        try:
            from app.workers.campaign_processor import process_campaign

            background_tasks.add_task(process_campaign, str(campaign_id))

            _safe_log(
                lambda: logger.track_business_event(
                    event_name="campaign_started",
                    properties={
                        "campaign_id": str(campaign_id),
                        "pending_submissions": pending_count,
                        "processing_method": "background_task",
                    },
                )
            )

            return {
                "success": True,
                "message": f"Campaign started successfully! Processing {pending_count} websites in background.",
                "campaign_id": str(campaign_id),
                "pending_submissions": pending_count,
                "status": "processing",
            }

        except ImportError as e:
            # Fallback if background processing is not available
            campaign.status = CampaignStatus.DRAFT
            db.add(campaign)
            db.commit()

            _safe_log(lambda: logger.track_exception(e, handled=True))
            raise HTTPException(
                status_code=500,
                detail="Background processing is not available. Please check server configuration.",
            )

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        _safe_log(lambda: logger.track_exception(e, handled=False))
        raise HTTPException(status_code=500, detail="Failed to start campaign")
    except Exception as e:
        db.rollback()
        logger.info(f"Unexpected error in start_campaign: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/{campaign_id}/stop")
def stop_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Enhanced campaign stop with proper state management"""
    logger = ApplicationInsightsLogger(db)
    _safe_log(
        lambda: logger.set_context(user_id=str(user.id), campaign_id=str(campaign_id))
    )

    try:
        campaign = _ensure_owner(db, user, campaign_id, logger)

        if campaign.status != CampaignStatus.ACTIVE:
            raise HTTPException(
                status_code=400, detail="Campaign is not currently running"
            )

        # Update campaign status to paused
        campaign.status = CampaignStatus.PAUSED
        campaign.updated_at = datetime.utcnow()

        # Get current stats
        total_submissions = (
            db.query(Submission).filter(Submission.campaign_id == campaign_id).count()
        )

        successful_submissions = (
            db.query(Submission)
            .filter(
                Submission.campaign_id == campaign_id,
                Submission.status == SubmissionStatus.SUCCESS,
            )
            .count()
        )

        failed_submissions = (
            db.query(Submission)
            .filter(
                Submission.campaign_id == campaign_id,
                Submission.status == SubmissionStatus.FAILED,
            )
            .count()
        )

        db.add(campaign)
        db.commit()

        _safe_log(
            lambda: logger.track_business_event(
                event_name="campaign_stopped",
                properties={
                    "campaign_id": str(campaign_id),
                    "total_submissions": total_submissions,
                    "successful_submissions": successful_submissions,
                    "failed_submissions": failed_submissions,
                },
            )
        )

        return {
            "success": True,
            "message": "Campaign stopped successfully",
            "campaign_id": str(campaign_id),
            "status": "paused",
            "stats": {
                "total": total_submissions,
                "successful": successful_submissions,
                "failed": failed_submissions,
            },
        }

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        _safe_log(lambda: logger.track_exception(e, handled=False))
        raise HTTPException(status_code=500, detail="Failed to stop campaign")
    except Exception as e:
        db.rollback()
        logger.info(f"Unexpected error in stop_campaign: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
