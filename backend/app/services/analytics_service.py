import uuid
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_

from app.models.user import User
from app.models.campaign import Campaign
from app.models.submission import Submission
from app.models.website import Website
from app.models.captcha_log import CaptchaLog
from app.schemas.analytics import (
    SubmissionStats,
    CampaignAnalytics,
    UserAnalytics,
    SystemAnalytics,
)


class AnalyticsService:
    """Service for generating analytics and reports"""

    def __init__(self, db: Session):
        self.db = db

    def get_user_analytics(
        self,
        user_id: uuid.UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> UserAnalytics:
        """Get analytics for a specific user"""
        query = self.db.query(Campaign).filter(Campaign.user_id == user_id)

        if start_date:
            query = query.filter(Campaign.started_at >= start_date)
        if end_date:
            query = query.filter(Campaign.started_at <= end_date)

        total_campaigns = query.count()

        # Get submission stats for this user
        submission_query = self.db.query(Submission).filter(
            Submission.user_id == user_id
        )

        if start_date:
            submission_query = submission_query.filter(
                Submission.created_at >= start_date
            )
        if end_date:
            submission_query = submission_query.filter(
                Submission.created_at <= end_date
            )

        total_submissions = submission_query.count()
        successful_submissions = submission_query.filter(
            Submission.status.in_(["submitted", "success"])
        ).count()
        failed_submissions = submission_query.filter(
            Submission.status == "failed"
        ).count()
        pending_submissions = submission_query.filter(
            Submission.status == "pending"
        ).count()

        success_rate = (
            (successful_submissions / total_submissions * 100)
            if total_submissions > 0
            else 0
        )

        stats = SubmissionStats(
            total_submissions=total_submissions,
            successful_submissions=successful_submissions,
            failed_submissions=failed_submissions,
            pending_submissions=pending_submissions,
            success_rate=round(success_rate, 2),
        )

        return UserAnalytics(
            user_id=str(user_id),
            total_campaigns=total_campaigns,
            total_submissions=total_submissions,
            stats=stats,
        )

    def get_campaign_analytics(
        self, campaign_id: uuid.UUID, user_id: uuid.UUID
    ) -> CampaignAnalytics:
        """Get analytics for a specific campaign"""
        # Verify campaign belongs to user
        campaign = (
            self.db.query(Campaign)
            .filter(and_(Campaign.id == campaign_id, Campaign.user_id == user_id))
            .first()
        )

        if not campaign:
            raise HTTPException(status_code=404, detail="Campaign not found")

        # Get submission counts
        submission_counts = (
            self.db.query(Submission.status, func.count(Submission.id))
            .filter(Submission.campaign_id == campaign_id)
            .group_by(Submission.status)
            .all()
        )

        successful = sum(
            count
            for status, count in submission_counts
            if status in ["submitted", "success"]
        )
        failed = sum(count for status, count in submission_counts if status == "failed")
        total = sum(count for status, count in submission_counts)

        # Get CAPTCHA stats
        captcha_encountered = (
            self.db.query(Submission)
            .filter(
                and_(
                    Submission.campaign_id == campaign_id,
                    Submission.captcha_encountered == True,
                )
            )
            .count()
        )

        captcha_solved = (
            self.db.query(Submission)
            .filter(
                and_(
                    Submission.campaign_id == campaign_id,
                    Submission.captcha_solved == True,
                )
            )
            .count()
        )

        success_rate = (successful / total * 100) if total > 0 else 0
        captcha_solve_rate = (
            (captcha_solved / captcha_encountered * 100)
            if captcha_encountered > 0
            else 0
        )

        return CampaignAnalytics(
            campaign_id=str(campaign_id),
            campaign_name=campaign.name or "Unnamed Campaign",
            total_urls=campaign.total_urls or 0,
            submitted_count=campaign.submitted_count or 0,
            failed_count=campaign.failed_count or 0,
            success_rate=round(success_rate, 2),
            captcha_encounters=captcha_encountered,
            captcha_solve_rate=round(captcha_solve_rate, 2),
        )

    def get_system_analytics(self) -> SystemAnalytics:
        """Get system-wide analytics"""
        total_users = self.db.query(User).filter(User.is_active == True).count()
        active_campaigns = (
            self.db.query(Campaign)
            .filter(Campaign.status.in_(["running", "created"]))
            .count()
        )

        # Get overall submission stats
        total_submissions = self.db.query(Submission).count()
        successful_submissions = (
            self.db.query(Submission)
            .filter(Submission.status.in_(["submitted", "success"]))
            .count()
        )
        failed_submissions = (
            self.db.query(Submission).filter(Submission.status == "failed").count()
        )
        pending_submissions = (
            self.db.query(Submission).filter(Submission.status == "pending").count()
        )

        success_rate = (
            (successful_submissions / total_submissions * 100)
            if total_submissions > 0
            else 0
        )

        stats = SubmissionStats(
            total_submissions=total_submissions,
            successful_submissions=successful_submissions,
            failed_submissions=failed_submissions,
            pending_submissions=pending_submissions,
            success_rate=round(success_rate, 2),
        )

        # Get top performing campaigns
        top_campaigns_query = (
            self.db.query(
                Campaign.id,
                Campaign.name,
                Campaign.submitted_count,
                Campaign.total_urls,
                Campaign.user_id,
            )
            .filter(Campaign.total_urls > 0)
            .order_by(desc(Campaign.submitted_count))
            .limit(5)
        )

        top_performing_campaigns = []
        for campaign_data in top_campaigns_query.all():
            success_rate = (
                (campaign_data.submitted_count / campaign_data.total_urls * 100)
                if campaign_data.total_urls > 0
                else 0
            )
            top_performing_campaigns.append(
                CampaignAnalytics(
                    campaign_id=str(campaign_data.id),
                    campaign_name=campaign_data.name or "Unnamed Campaign",
                    total_urls=campaign_data.total_urls,
                    submitted_count=campaign_data.submitted_count,
                    failed_count=campaign_data.total_urls
                    - campaign_data.submitted_count,
                    success_rate=round(success_rate, 2),
                    captcha_encounters=0,  # Would need separate query
                    captcha_solve_rate=0,  # Would need separate query
                )
            )

        return SystemAnalytics(
            total_users=total_users,
            active_campaigns=active_campaigns,
            total_submissions=total_submissions,
            stats=stats,
            top_performing_campaigns=top_performing_campaigns,
        )

    def get_daily_stats(
        self,
        user_id: Optional[uuid.UUID] = None,
        campaign_id: Optional[uuid.UUID] = None,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get daily submission statistics"""
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)

        query = self.db.query(
            func.date(Submission.created_at).label("date"),
            func.count(Submission.id).label("total"),
            func.sum(
                func.case(
                    [(Submission.status.in_(["submitted", "success"]), 1)], else_=0
                )
            ).label("successful"),
            func.sum(func.case([(Submission.status == "failed", 1)], else_=0)).label(
                "failed"
            ),
        ).filter(func.date(Submission.created_at) >= start_date)

        if user_id:
            query = query.filter(Submission.user_id == user_id)
        if campaign_id:
            query = query.filter(Submission.campaign_id == campaign_id)

        results = (
            query.group_by(func.date(Submission.created_at))
            .order_by(func.date(Submission.created_at))
            .all()
        )

        daily_stats = []
        for result in results:
            daily_stats.append(
                {
                    "date": str(result.date),
                    "total": result.total,
                    "successful": result.successful,
                    "failed": result.failed,
                    "success_rate": round(
                        (
                            (result.successful / result.total * 100)
                            if result.total > 0
                            else 0
                        ),
                        2,
                    ),
                }
            )

        return daily_stats
