# app/api/submissions.py

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)
from sqlalchemy.orm import Session
from sqlalchemy import and_, text
from typing import Optional, List
from pydantic import BaseModel
import csv
import io
import asyncio
import sys
import traceback
from datetime import datetime
from urllib.parse import urlparse
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.submission import Submission
from app.models.campaign import Campaign
from app.models.website import Website
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionResponse,
    SubmissionList,
)
from app.services.submission_service import SubmissionService
from app.workers import process_campaign

router = APIRouter()


# Define the request schema
class SubmissionStartRequest(BaseModel):
    campaign_id: str
    headless: Optional[bool] = None  # None means use config default


@router.post("/start")
async def start_submission_campaign(
    request: SubmissionStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start submission campaign processing"""
    try:
        print(
            f"[SUBMISSIONS] Starting browser automation for campaign {request.campaign_id}"
        )

        # Get campaign and verify ownership
        campaign = (
            db.query(Campaign)
            .filter(
                Campaign.id == request.campaign_id, Campaign.user_id == current_user.id
            )
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Check if already processing
        if campaign.status == "processing":
            raise HTTPException(
                status_code=400, detail="Campaign is already being processed"
            )

        # Update campaign status to processing
        campaign.status = "processing"
        db.commit()

        # Start processing in background
        from threading import Thread

        def run_campaign():
            try:
                # Use headless setting from request or config
                process_campaign(str(campaign.id), headless=request.headless)
            except Exception as e:
                print(f"[SUBMISSIONS ERROR] Campaign processing failed: {e}")
                # Update status to failed
                from app.core.database import SessionLocal

                db_session = SessionLocal()
                try:
                    failed_campaign = (
                        db_session.query(Campaign)
                        .filter(Campaign.id == campaign.id)
                        .first()
                    )
                    if failed_campaign:
                        failed_campaign.status = "failed"
                        db_session.commit()
                finally:
                    db_session.close()

        # Start in background thread
        thread = Thread(target=run_campaign, daemon=True)
        thread.start()

        return {
            "status": "started",
            "campaign_id": str(campaign.id),
            "message": "Campaign processing started in background",
            "headless": (
                request.headless
                if request.headless is not None
                else "using config default"
            ),
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"[SUBMISSIONS ERROR] Failed to start automation: {e}")
        traceback.print_exc()

        # Update campaign status back to pending
        if "campaign" in locals() and campaign:
            campaign.status = "pending"
            db.commit()

        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{campaign_id}")
async def get_campaign_status(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get campaign processing status"""

    # Validate UUID format
    try:
        uuid.UUID(campaign_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid campaign ID format")

    # Verify ownership
    campaign = (
        db.query(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
        .first()
    )

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get counts
    total = db.query(Submission).filter(Submission.campaign_id == campaign_id).count()

    processed = (
        db.query(Submission)
        .filter(Submission.campaign_id == campaign_id, Submission.status != "pending")
        .count()
    )

    successful = (
        db.query(Submission)
        .filter(Submission.campaign_id == campaign_id, Submission.success == True)
        .count()
    )

    failed = (
        db.query(Submission)
        .filter(Submission.campaign_id == campaign_id, Submission.status == "failed")
        .count()
    )

    # Determine status
    if campaign.status:
        status = campaign.status
    elif processed == total and total > 0:
        status = "completed"
    elif processed > 0:
        status = "processing"
    else:
        status = "pending"

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "status": status,
        "total": total,
        "processed": processed,
        "successful": successful,
        "failed": failed,
        "pending": total - processed,
        "progress_percent": round((processed / total * 100) if total > 0 else 0, 2),
        "started_at": campaign.created_at.isoformat() if campaign.created_at else None,
        "completed_at": (
            campaign.completed_at.isoformat() if campaign.completed_at else None
        ),
    }


@router.post("/stop/{campaign_id}")
async def stop_campaign(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Stop a running campaign"""

    # Verify ownership
    campaign = (
        db.query(Campaign)
        .filter(Campaign.id == campaign_id, Campaign.user_id == current_user.id)
        .first()
    )

    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.status != "processing":
        raise HTTPException(
            status_code=400,
            detail=f"Campaign is not currently processing (status: {campaign.status})",
        )

    # Update status to stopped
    campaign.status = "stopped"
    campaign.completed_at = datetime.utcnow()
    db.commit()

    return {
        "campaign_id": campaign_id,
        "status": "stopped",
        "message": "Campaign processing stopped",
    }


@router.post("/", response_model=SubmissionResponse, status_code=201)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new submission"""
    submission_service = SubmissionService(db)
    submission = submission_service.create_submission(current_user.id, submission_data)
    return submission


@router.get("/", response_model=SubmissionList)
async def get_user_submissions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    campaign_id: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's submissions with optional filtering"""
    submission_service = SubmissionService(db)

    # Build filters
    filters = {}
    if status:
        filters["status"] = status
    if campaign_id:
        filters["campaign_id"] = campaign_id

    submissions, total = submission_service.get_user_submissions(
        current_user.id, page, per_page, **filters
    )

    return SubmissionList(
        submissions=submissions, total=total, page=page, per_page=per_page
    )


@router.get("/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific submission"""
    try:
        submission_uuid = uuid.UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid submission ID")

    submission_service = SubmissionService(db)
    submission = submission_service.get_submission(submission_uuid, current_user.id)

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: str,
    submission_data: SubmissionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a submission"""
    try:
        submission_uuid = uuid.UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid submission ID")

    submission_service = SubmissionService(db)
    submission = submission_service.update_submission(
        submission_uuid, current_user.id, submission_data
    )

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


@router.delete("/{submission_id}")
async def delete_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a submission"""
    try:
        submission_uuid = uuid.UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid submission ID")

    submission = (
        db.query(Submission)
        .filter(
            Submission.id == submission_uuid,
            Submission.campaign_id.in_(
                db.query(Campaign.id).filter(Campaign.user_id == current_user.id)
            ),
        )
        .first()
    )

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    db.delete(submission)
    db.commit()

    return {"message": "Submission deleted successfully"}


@router.post("/retry/{submission_id}")
async def retry_submission(
    submission_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retry a failed submission"""
    try:
        submission_uuid = uuid.UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid submission ID")

    submission = (
        db.query(Submission)
        .filter(
            Submission.id == submission_uuid,
            Submission.campaign_id.in_(
                db.query(Campaign.id).filter(Campaign.user_id == current_user.id)
            ),
        )
        .first()
    )

    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.status not in ["failed", "error"]:
        raise HTTPException(
            status_code=400,
            detail=f"Can only retry failed submissions (current status: {submission.status})",
        )

    # Reset submission status
    submission.status = "pending"
    submission.success = False
    submission.error_message = None
    submission.processed_at = None
    db.commit()

    return {
        "submission_id": str(submission.id),
        "status": "pending",
        "message": "Submission queued for retry",
    }


@router.post("/upload-and-start")
async def upload_and_start_campaign(
    file: UploadFile = File(...),
    campaign_name: str = Form(...),
    message: str = Form(None),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    """Upload CSV and start campaign"""
    try:
        # Validate file
        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="File must be a CSV")

        # Read CSV
        content = await file.read()
        csv_data = content.decode("utf-8")

        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_data))
        urls = []

        for row in reader:
            # Look for URL in various column names
            url = (
                row.get("website")
                or row.get("url")
                or row.get("Website")
                or row.get("URL")
            )
            if url:
                urls.append(url.strip())

        if not urls:
            raise HTTPException(status_code=400, detail="No URLs found in CSV")

        # Create campaign
        campaign = Campaign(
            id=uuid.uuid4(),
            user_id=current_user.id,
            name=campaign_name,
            message=message,
            status="pending",
            total_urls=len(urls),
            created_at=datetime.utcnow(),
        )
        db.add(campaign)
        db.flush()

        # Create submissions
        for url in urls:
            submission = Submission(
                id=uuid.uuid4(),
                campaign_id=campaign.id,
                user_id=current_user.id,
                url=url,
                status="pending",
                created_at=datetime.utcnow(),
            )
            db.add(submission)

        db.commit()

        # Start processing in background
        background_tasks.add_task(process_campaign, str(campaign.id))

        return {
            "status": "started",
            "campaign_id": str(campaign.id),
            "total_urls": len(urls),
            "message": "Campaign processing started",
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to start campaign: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
