# ============================================================================
# app/api/endpoints/submissions.py - FIXED
# ============================================================================
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.submission import Submission
from app.models.campaign import Campaign

router = APIRouter()


@router.get("/")
@router.get("")
async def get_submissions(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    campaign_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's submissions"""
    try:
        query = db.query(Submission).filter(Submission.user_id == current_user.id)

        if campaign_id:
            try:
                campaign_uuid = uuid.UUID(campaign_id)
                query = query.filter(Submission.campaign_id == campaign_uuid)
            except ValueError:
                pass

        if status:
            query = query.filter(Submission.status == status)

        total = query.count()

        offset = (page - 1) * per_page
        submissions = (
            query.order_by(Submission.created_at.desc())
            .offset(offset)
            .limit(per_page)
            .all()
        )

        submission_list = []
        for s in submissions:
            submission_list.append(
                {
                    "id": str(s.id),
                    "campaign_id": str(s.campaign_id) if s.campaign_id else None,
                    "website_id": str(s.website_id) if s.website_id else None,
                    "url": s.url,
                    "status": s.status or "pending",
                    "success": s.success,
                    "contact_method": s.contact_method,
                    "email_extracted": s.email_extracted,
                    "error_message": s.error_message,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
            )

        return {
            "submissions": submission_list,
            "total": total,
            "page": page,
            "per_page": per_page,
        }
    except Exception as e:
        print(f"[SUBMISSIONS ERROR] Failed to get submissions: {str(e)}")
        return {"submissions": [], "total": 0, "page": page, "per_page": per_page}
