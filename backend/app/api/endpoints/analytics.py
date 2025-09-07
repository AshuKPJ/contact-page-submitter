# ============================================================================
# app/api/endpoints/analytics.py - FIXED
# ============================================================================
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.campaign import Campaign
from app.models.submission import Submission

router = APIRouter()


@router.get("/user")
async def get_user_analytics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get user analytics"""
    try:
        total_campaigns = (
            db.query(Campaign).filter(Campaign.user_id == current_user.id).count()
        )

        total_submissions = (
            db.query(Submission).filter(Submission.user_id == current_user.id).count()
        )

        successful = (
            db.query(Submission)
            .filter(
                Submission.user_id == current_user.id,
                Submission.status.in_(["success", "submitted"]),
            )
            .count()
        )

        failed = (
            db.query(Submission)
            .filter(
                Submission.user_id == current_user.id, Submission.status == "failed"
            )
            .count()
        )

        pending = (
            db.query(Submission)
            .filter(
                Submission.user_id == current_user.id, Submission.status == "pending"
            )
            .count()
        )

        success_rate = (
            (successful / total_submissions * 100) if total_submissions > 0 else 0
        )

        return {
            "user_id": str(current_user.id),
            "total_campaigns": total_campaigns,
            "total_submissions": total_submissions,
            "stats": {
                "total_submissions": total_submissions,
                "successful_submissions": successful,
                "failed_submissions": failed,
                "pending_submissions": pending,
                "success_rate": round(success_rate, 2),
            },
        }
    except Exception as e:
        print(f"[ANALYTICS ERROR] Failed to get user analytics: {str(e)}")
        return {
            "user_id": str(current_user.id),
            "total_campaigns": 0,
            "total_submissions": 0,
            "stats": {
                "total_submissions": 0,
                "successful_submissions": 0,
                "failed_submissions": 0,
                "pending_submissions": 0,
                "success_rate": 0,
            },
        }


@router.get("/daily-stats")
async def get_daily_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get daily submission statistics"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get daily counts
        daily_stats = []
        current_date = start_date

        while current_date <= end_date:
            day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)

            total = (
                db.query(Submission)
                .filter(
                    Submission.user_id == current_user.id,
                    Submission.created_at >= day_start,
                    Submission.created_at < day_end,
                )
                .count()
            )

            successful = (
                db.query(Submission)
                .filter(
                    Submission.user_id == current_user.id,
                    Submission.created_at >= day_start,
                    Submission.created_at < day_end,
                    Submission.status.in_(["success", "submitted"]),
                )
                .count()
            )

            failed = (
                db.query(Submission)
                .filter(
                    Submission.user_id == current_user.id,
                    Submission.created_at >= day_start,
                    Submission.created_at < day_end,
                    Submission.status == "failed",
                )
                .count()
            )

            daily_stats.append(
                {
                    "date": current_date.date().isoformat(),
                    "total": total,
                    "successful": successful,
                    "failed": failed,
                }
            )

            current_date += timedelta(days=1)

        return daily_stats

    except Exception as e:
        print(f"[ANALYTICS ERROR] Failed to get daily stats: {str(e)}")
        return []
