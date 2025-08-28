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
from sqlalchemy import and_
from typing import Optional, List
import csv
import io
import asyncio
import sys
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

router = APIRouter()


@router.post("/start")
async def start_submission_campaign(
    background_tasks: BackgroundTasks,  # Moved before optional parameters
    file: UploadFile = File(...),
    proxy: Optional[str] = Form(None),
    haltOnCaptcha: Optional[str] = Form("true"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Start a new submission campaign from uploaded CSV file"""

    # Validate file type
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # Read and parse CSV file
    try:
        contents = await file.read()

        # Try different encodings
        csv_text = None
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
            try:
                csv_text = contents.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        if csv_text is None:
            raise HTTPException(
                status_code=400,
                detail="Unable to decode CSV file. Please save as UTF-8",
            )

        # Remove BOM if present
        if csv_text.startswith("\ufeff"):
            csv_text = csv_text[1:]

        csv_reader = csv.DictReader(io.StringIO(csv_text))

        # Clean up header names
        cleaned_rows = []
        for row in csv_reader:
            cleaned_row = {
                key.strip().lower(): value for key, value in row.items() if key
            }
            cleaned_rows.append(cleaned_row)

        # Extract URLs from CSV
        urls = []
        for row in cleaned_rows:
            url = (
                row.get("website")
                or row.get("url")
                or row.get("contact_url")
                or row.get("site")
                or row.get("domain")
                or row.get("web")
            )

            if url:
                url = url.strip()
                if url and not url.startswith(("http://", "https://")):
                    url = "http://" + url
                urls.append(url)

        if not urls:
            headers_found = list(cleaned_rows[0].keys()) if cleaned_rows else []
            raise HTTPException(
                status_code=400,
                detail=f"No valid URLs found. Headers found: {headers_found}",
            )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

    # Create campaign
    campaign = Campaign(
        user_id=current_user.id,
        name=f"Campaign {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        csv_filename=file.filename,
        message="",
        proxy=proxy,
        use_captcha=(haltOnCaptcha.lower() != "false" if haltOnCaptcha else True),
        status="running",
        started_at=datetime.utcnow(),
        total_urls=len(urls),
        submitted_count=0,
        failed_count=0,
    )

    db.add(campaign)
    db.flush()

    # Create websites and submissions
    for url in urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or url
        except:
            domain = url

        website = Website(
            campaign_id=campaign.id,
            user_id=current_user.id,
            domain=domain,
            contact_url=url,
            status="pending",
        )
        db.add(website)
        db.flush()

        submission = Submission(
            website_id=website.id,
            campaign_id=campaign.id,
            user_id=current_user.id,
            url=url,
            status="pending",
        )
        db.add(submission)

    db.commit()

    # START THE AUTOMATION IN BACKGROUND
    from app.workers.processor import process_campaign

    background_tasks.add_task(process_campaign, str(campaign.id))

    return {
        "success": True,
        "message": f"Campaign started! Processing {len(urls)} URLs in background...",
        "campaign_id": str(campaign.id),
        "job_id": str(campaign.id),
        "total_urls": len(urls),
        "status": "processing",
        "csv_filename": file.filename,
    }


@router.get("/status/{campaign_id}")
async def get_campaign_status(
    campaign_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get campaign processing status"""

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

    return {
        "campaign_id": campaign_id,
        "total": total,
        "processed": processed,
        "successful": successful,
        "pending": total - processed,
        "progress_percent": round((processed / total * 100) if total > 0 else 0, 2),
        "status": "completed" if processed == total else "processing",
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's submissions"""
    submission_service = SubmissionService(db)
    submissions, total = submission_service.get_user_submissions(
        current_user.id, page, per_page, status
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
