# app/api/submissions.py (Updated section for start_campaign_processing)
"""Submission API endpoints with Windows-compatible background processing."""

import uuid
import logging
import sys
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    File,
    UploadFile,
    Form,
    BackgroundTasks,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.campaign import Campaign, CampaignStatus
from app.models.submission import Submission, SubmissionStatus

from app.services.submission_service import SubmissionService
from app.services.csv_parser_service import CSVParserService
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


@router.post("/start", response_model=Dict[str, Any])
async def start_campaign_processing(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    proxy: Optional[str] = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start automated campaign processing with CSV upload."""
    try:
        # Validate file type
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be CSV")

        # Parse CSV
        content = await file.read()
        urls, errors, headers = await CSVParserService.parse_csv_file(content)

        if not urls:
            error_msg = f"No URLs found. Headers detected: {headers}"
            if errors:
                error_msg += f". Errors: {errors[:5]}"
            raise HTTPException(status_code=400, detail=error_msg)

        # Create campaign
        campaign = Campaign(
            user_id=current_user.id,
            name=f"Campaign - {file.filename} - {datetime.utcnow():%Y%m%d_%H%M%S}",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
        )

        db.add(campaign)
        db.flush()

        # Create submissions
        service = SubmissionService(db)
        submissions, submission_errors = service.bulk_create_submissions(
            user_id=current_user.id, campaign_id=campaign.id, urls=urls
        )

        # Update campaign
        campaign.total_urls = len(submissions)
        db.commit()
        db.refresh(campaign)

        # Start background processing with Windows compatibility
        campaign_id_str = str(campaign.id)
        user_id_str = str(current_user.id)

        if sys.platform == "win32":
            # Use subprocess runner for Windows
            from app.workers.subprocess_runner import run_campaign_in_subprocess

            # Run in subprocess with ProactorEventLoop
            thread = run_campaign_in_subprocess(campaign_id_str, user_id_str)

            logger.info(
                f"Started campaign {campaign_id_str} in Windows-compatible subprocess"
            )
        else:
            # Use standard background task for non-Windows
            from app.workers import process_campaign_async

            background_tasks.add_task(
                process_campaign_async, campaign_id_str, user_id_str
            )

            logger.info(f"Started campaign {campaign_id_str} in background task")

        return {
            "success": True,
            "campaign_id": campaign_id_str,
            "total_urls": len(urls),
            "created_submissions": len(submissions),
            "errors": errors + submission_errors,
            "message": f"Campaign started with {len(submissions)} URLs",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Alternative approach: Create a dedicated endpoint for Windows users
@router.post("/start-windows", response_model=Dict[str, Any])
async def start_campaign_processing_windows(
    file: UploadFile = File(...),
    proxy: Optional[str] = Form(""),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start campaign processing with Windows-specific subprocess handling."""
    try:
        # Validate file type
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be CSV")

        # Parse CSV
        content = await file.read()
        urls, errors, headers = await CSVParserService.parse_csv_file(content)

        if not urls:
            error_msg = f"No URLs found. Headers detected: {headers}"
            if errors:
                error_msg += f". Errors: {errors[:5]}"
            raise HTTPException(status_code=400, detail=error_msg)

        # Create campaign
        campaign = Campaign(
            user_id=current_user.id,
            name=f"Campaign - {file.filename} - {datetime.utcnow():%Y%m%d_%H%M%S}",
            status=CampaignStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
        )

        db.add(campaign)
        db.flush()

        # Create submissions
        service = SubmissionService(db)
        submissions, submission_errors = service.bulk_create_submissions(
            user_id=current_user.id, campaign_id=campaign.id, urls=urls
        )

        # Update campaign
        campaign.total_urls = len(submissions)
        db.commit()
        db.refresh(campaign)

        # Use subprocess runner specifically designed for Windows
        from app.workers.subprocess_runner import run_campaign_in_subprocess

        campaign_id_str = str(campaign.id)
        user_id_str = str(current_user.id)

        # Run in subprocess with ProactorEventLoop
        thread = run_campaign_in_subprocess(campaign_id_str, user_id_str)

        logger.info(
            f"Started campaign {campaign_id_str} in Windows subprocess (thread: {thread.name})"
        )

        return {
            "success": True,
            "campaign_id": campaign_id_str,
            "total_urls": len(urls),
            "created_submissions": len(submissions),
            "errors": errors + submission_errors,
            "message": f"Campaign started with {len(submissions)} URLs (Windows mode)",
            "processing_mode": "windows_subprocess",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{campaign_id}", response_model=Dict[str, Any])
async def get_campaign_status(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get real-time campaign status with proper completion detection."""
    try:
        campaign_uuid = uuid.UUID(campaign_id)

        # Verify campaign
        campaign = (
            db.query(Campaign)
            .filter(Campaign.id == campaign_uuid, Campaign.user_id == current_user.id)
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Get submission counts
        total = (
            db.query(Submission).filter(Submission.campaign_id == campaign_uuid).count()
        )

        successful = (
            db.query(Submission)
            .filter(
                Submission.campaign_id == campaign_uuid,
                Submission.status == SubmissionStatus.SUCCESS,
            )
            .count()
        )

        failed = (
            db.query(Submission)
            .filter(
                Submission.campaign_id == campaign_uuid,
                Submission.status == SubmissionStatus.FAILED,
            )
            .count()
        )

        pending = (
            db.query(Submission)
            .filter(
                Submission.campaign_id == campaign_uuid,
                Submission.status == SubmissionStatus.PENDING,
            )
            .count()
        )

        processing = (
            db.query(Submission)
            .filter(
                Submission.campaign_id == campaign_uuid,
                Submission.status == SubmissionStatus.PROCESSING,
            )
            .count()
        )

        processed = successful + failed
        progress_percent = (processed / total * 100) if total > 0 else 0

        # Determine if campaign is truly complete
        is_complete = (
            pending == 0 and 
            processing == 0 and 
            processed == total and
            campaign.status in [CampaignStatus.COMPLETED, CampaignStatus.FAILED]
        )

        # If all submissions are done but campaign status isn't updated, fix it
        if pending == 0 and processing == 0 and processed > 0 and campaign.status == CampaignStatus.ACTIVE:
            logger.info(f"Auto-completing campaign {campaign_id} - all submissions processed")
            campaign.status = CampaignStatus.COMPLETED
            campaign.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(campaign)
            is_complete = True

        return {
            "campaign_id": campaign_id,
            "total": total,
            "processed": processed,
            "successful": successful,
            "failed": failed,
            "pending": pending,
            "processing": processing,
            "progress_percent": round(progress_percent, 2),
            "status": campaign.status.value,
            "is_complete": is_complete,  # Add this field
            "completed_at": campaign.completed_at.isoformat() if campaign.completed_at else None,
            "message": (
                f"Campaign completed! {successful} successful, {failed} failed" 
                if is_complete 
                else f"Processing {processed} of {total} URLs"
            ),
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting campaign status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get status")

@router.post("/", response_model=SubmissionResponse)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new submission."""
    service = SubmissionService(db)
    submission = service.create_submission(current_user.id, submission_data)
    return submission


@router.get("/", response_model=Dict[str, Any])
async def get_submissions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    campaign_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user submissions."""
    service = SubmissionService(db)

    # Convert campaign_id if provided
    campaign_uuid = None
    if campaign_id:
        try:
            campaign_uuid = uuid.UUID(campaign_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid campaign ID")

    submissions, total = (
        service.get_campaign_submissions(
            campaign_id=campaign_uuid,
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            status=status,
            search_query=search,
        )
        if campaign_uuid
        else ([], 0)
    )

    return {
        "submissions": submissions,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
    }


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific submission."""
    service = SubmissionService(db)
    submission = service.get_submission(submission_id, current_user.id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: uuid.UUID,
    submission_data: SubmissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a submission."""
    service = SubmissionService(db)
    submission = service.update_submission(
        submission_id, current_user.id, submission_data
    )

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.post("/campaigns/{campaign_id}/retry", response_model=Dict[str, Any])
async def retry_failed_submissions(
    campaign_id: uuid.UUID,
    max_retries: int = Query(3, ge=1, le=10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retry failed submissions."""
    service = SubmissionService(db)
    result = service.retry_failed_submissions(
        campaign_id=campaign_id, user_id=current_user.id, max_retries=max_retries
    )
    return result
