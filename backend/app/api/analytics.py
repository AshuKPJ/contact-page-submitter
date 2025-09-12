# app/api/analytics.py - Enhanced analytics API with comprehensive logging
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.log_service import LogService as ApplicationInsightsLogger
from app.logging import get_logger, log_function, log_exceptions
from app.logging.core import request_id_var, user_id_var

# Initialize structured logger
logger = get_logger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"], redirect_slashes=False)


class TimeRange(BaseModel):
    start_date: Optional[str] = Field(None, description="Start date (ISO format)")
    end_date: Optional[str] = Field(None, description="End date (ISO format)")


class AnalyticsFilter(BaseModel):
    campaign_ids: Optional[List[str]] = Field(None, description="Filter by specific campaigns")
    website_ids: Optional[List[str]] = Field(None, description="Filter by specific websites")
    status_filter: Optional[str] = Field(None, description="Filter by submission status")
    time_range: Optional[TimeRange] = None


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request headers with logging"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        ip = forwarded_for.split(",")[0].strip()
        logger.debug(f"Client IP extracted from X-Forwarded-For: {ip}")
        return ip

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        logger.debug(f"Client IP extracted from X-Real-IP: {real_ip}")
        return real_ip

    if request and request.client:
        ip = request.client.host
        logger.debug(f"Client IP extracted from request.client: {ip}")
        return ip

    logger.warning("Unable to determine client IP address")
    return "unknown"


@router.get("/user")
@log_function("get_user_analytics")
def analytics_user(
    request: Request,
    include_detailed: bool = Query(False, description="Include detailed breakdowns"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive user analytics summary"""
    # Set context variables for structured logging
    user_id_var.set(str(current_user.id))
    
    app_logger = ApplicationInsightsLogger(db)
    app_logger.set_context(user_id=str(current_user.id))

    client_ip = get_client_ip(request)

    logger.info(
        "User analytics request started",
        context={
            "user_id": str(current_user.id),
            "client_ip": client_ip,
            "include_detailed": include_detailed,
            "user_agent": request.headers.get("User-Agent", "")[:200]
        },
    )

    # Track analytics access
    app_logger.track_user_action(
        action="view_analytics",
        target="user_analytics",
        properties={
            "user_id": str(current_user.id), 
            "ip": client_ip,
            "detailed": include_detailed
        },
    )

    # Track workflow
    app_logger.track_workflow_step(
        workflow_name="analytics_retrieval",
        step_name="start",
        step_number=1,
        total_steps=4 if include_detailed else 3,
    )

    try:
        total_start = time.time()

        # Step 1: Get enhanced submission stats
        app_logger.track_workflow_step(
            workflow_name="analytics_retrieval",
            step_name="fetch_submissions",
            step_number=2,
            total_steps=4 if include_detailed else 3,
        )

        submissions_start = time.time()
        # Enhanced query with more detailed statistics
        submission_query = text(
            """
            SELECT
                COUNT(*)::int AS total_submissions,
                COALESCE(SUM(CASE WHEN s.success = true THEN 1 ELSE 0 END), 0) AS successful_submissions,
                COALESCE(SUM(CASE WHEN s.success = false THEN 1 ELSE 0 END), 0) AS failed_submissions,
                COALESCE(SUM(CASE WHEN s.captcha_encountered = true THEN 1 ELSE 0 END), 0) AS captcha_submissions,
                COALESCE(SUM(CASE WHEN s.captcha_solved = true THEN 1 ELSE 0 END), 0) AS captcha_solved,
                COALESCE(AVG(s.retry_count), 0) AS avg_retry_count,
                COALESCE(SUM(CASE WHEN s.email_extracted IS NOT NULL THEN 1 ELSE 0 END), 0) AS emails_extracted,
                COALESCE(COUNT(DISTINCT s.campaign_id), 0) AS unique_campaigns_used
            FROM submissions s
            WHERE s.user_id = :uid
            """
        )
        submission_row = db.execute(submission_query, {"uid": str(current_user.id)}).mappings().first() or {}
        submissions_time = (time.time() - submissions_start) * 1000

        logger.database_operation(
            operation="AGGREGATE",
            table="submissions",
            duration_ms=submissions_time,
            success=True
        )

        app_logger.track_database_operation(
            operation="AGGREGATE",
            table="submissions",
            query_time_ms=submissions_time,
            success=True,
            query="Enhanced submission statistics",
        )

        # Step 2: Get counts for campaigns and websites
        app_logger.track_workflow_step(
            workflow_name="analytics_retrieval",
            step_name="fetch_entity_counts",
            step_number=3,
            total_steps=4 if include_detailed else 3,
        )

        counts_start = time.time()
        counts_query = text(
            """
            SELECT
                (SELECT COUNT(*)::int FROM campaigns c WHERE c.user_id = :uid) AS campaigns_count,
                (SELECT COUNT(*)::int FROM websites w WHERE w.user_id = :uid) AS websites_count,
                (SELECT COUNT(*)::int FROM campaigns c WHERE c.user_id = :uid AND c.status = 'running') AS active_campaigns,
                (SELECT COUNT(*)::int FROM websites w WHERE w.user_id = :uid AND w.form_detected = true) AS websites_with_forms,
                (SELECT COUNT(*)::int FROM websites w WHERE w.user_id = :uid AND w.has_captcha = true) AS websites_with_captcha
            """
        )
        counts_row = db.execute(counts_query, {"uid": str(current_user.id)}).mappings().first() or {}
        counts_time = (time.time() - counts_start) * 1000

        logger.database_operation(
            operation="AGGREGATE",
            table="campaigns,websites",
            duration_ms=counts_time,
            success=True
        )

        app_logger.track_database_operation(
            operation="AGGREGATE",
            table="campaigns,websites",
            query_time_ms=counts_time,
            success=True,
            query="Entity counts and status",
        )

        # Step 3: Get recent activity if detailed view requested
        recent_activity = {}
        detailed_time = 0

        if include_detailed:
            app_logger.track_workflow_step(
                workflow_name="analytics_retrieval",
                step_name="fetch_detailed_stats",
                step_number=4,
                total_steps=4,
            )

            detailed_start = time.time()
            
            # Get recent submissions by status
            recent_query = text(
                """
                SELECT 
                    status,
                    COUNT(*) as count,
                    MAX(created_at) as last_activity
                FROM submissions 
                WHERE user_id = :uid 
                AND created_at >= NOW() - INTERVAL '7 days'
                GROUP BY status
                ORDER BY count DESC
                """
            )
            recent_results = db.execute(recent_query, {"uid": str(current_user.id)}).mappings().all()
            
            # Get top domains by activity
            domains_query = text(
                """
                SELECT 
                    w.domain,
                    COUNT(s.id) as submission_count,
                    AVG(CASE WHEN s.success THEN 100.0 ELSE 0.0 END) as success_rate
                FROM submissions s
                JOIN websites w ON s.website_id = w.id
                WHERE s.user_id = :uid
                AND s.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY w.domain
                ORDER BY submission_count DESC
                LIMIT 10
                """
            )
            domains_results = db.execute(domains_query, {"uid": str(current_user.id)}).mappings().all()
            
            detailed_time = (time.time() - detailed_start) * 1000

            logger.database_operation(
                operation="SELECT",
                table="submissions,websites",
                duration_ms=detailed_time,
                success=True
            )

            recent_activity = {
                "recent_submissions_by_status": [dict(row) for row in recent_results],
                "top_domains": [dict(row) for row in domains_results]
            }

        # Prepare comprehensive response
        payload: Dict[str, Any] = {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            
            # Core metrics
            "campaigns_count": int(counts_row.get("campaigns_count", 0) or 0),
            "websites_count": int(counts_row.get("websites_count", 0) or 0),
            "active_campaigns": int(counts_row.get("active_campaigns", 0) or 0),
            "websites_with_forms": int(counts_row.get("websites_with_forms", 0) or 0),
            "websites_with_captcha": int(counts_row.get("websites_with_captcha", 0) or 0),
            
            # Submission metrics
            "total_submissions": int(submission_row.get("total_submissions", 0) or 0),
            "successful_submissions": int(submission_row.get("successful_submissions", 0) or 0),
            "failed_submissions": int(submission_row.get("failed_submissions", 0) or 0),
            "captcha_submissions": int(submission_row.get("captcha_submissions", 0) or 0),
            "captcha_solved": int(submission_row.get("captcha_solved", 0) or 0),
            "emails_extracted": int(submission_row.get("emails_extracted", 0) or 0),
            "avg_retry_count": round(float(submission_row.get("avg_retry_count", 0) or 0), 2),
            "unique_campaigns_used": int(submission_row.get("unique_campaigns_used", 0) or 0),
        }

        # Add detailed activity if requested
        if include_detailed:
            payload["recent_activity"] = recent_activity

        # Calculate enhanced success rates and metrics
        total_submissions = payload["total_submissions"]
        if total_submissions > 0:
            success_rate = (payload["successful_submissions"] / total_submissions) * 100
            captcha_encounter_rate = (payload["captcha_submissions"] / total_submissions) * 100
        else:
            success_rate = 0
            captcha_encounter_rate = 0

        # Calculate CAPTCHA success rate
        captcha_success_rate = 0
        if payload["captcha_submissions"] > 0:
            captcha_success_rate = (payload["captcha_solved"] / payload["captcha_submissions"]) * 100

        # Add calculated metrics
        payload.update({
            "success_rate": round(success_rate, 2),
            "captcha_encounter_rate": round(captcha_encounter_rate, 2),
            "captcha_success_rate": round(captcha_success_rate, 2),
            "form_detection_rate": round(
                (payload["websites_with_forms"] / payload["websites_count"] * 100) 
                if payload["websites_count"] > 0 else 0, 2
            )
        })

        total_time = (time.time() - total_start) * 1000

        # Enhanced metric tracking
        logger.performance_metric("user_analytics_total_duration", total_time, "ms")

        app_logger.track_metric(
            name="user_submission_success_rate",
            value=success_rate,
            properties={
                "user_id": str(current_user.id),
                "total_submissions": total_submissions,
                "include_detailed": include_detailed
            },
        )

        # Track comprehensive business event
        app_logger.track_business_event(
            event_name="user_analytics_retrieved",
            properties={
                "type": "user_summary",
                "user_id": str(current_user.id),
                "has_campaigns": payload["campaigns_count"] > 0,
                "has_submissions": total_submissions > 0,
                "include_detailed": include_detailed,
                "active_campaigns": payload["active_campaigns"] > 0
            },
            metrics={
                "total_query_time_ms": total_time,
                "submissions_query_ms": submissions_time,
                "counts_query_ms": counts_time,
                "detailed_query_ms": detailed_time,
                "campaigns_count": payload["campaigns_count"],
                "submissions_count": total_submissions,
                "success_rate": success_rate,
                "captcha_success_rate": captcha_success_rate
            },
        )

        logger.info(
            "User analytics retrieved successfully",
            context={
                "user_id": str(current_user.id),
                "total_duration_ms": total_time,
                "campaigns_count": payload["campaigns_count"],
                "submissions_count": total_submissions,
                "success_rate": success_rate,
                "include_detailed": include_detailed
            }
        )

        return payload

    except SQLAlchemyError as e:
        db.rollback()
        
        logger.error(
            "Database error in user analytics",
            context={
                "user_id": str(current_user.id),
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )

        app_logger.track_exception(e, handled=True, properties={"endpoint": "/analytics/user"})
        app_logger.track_workflow_step(
            workflow_name="analytics_retrieval",
            step_name="database_error",
            step_number=0,
            total_steps=4 if include_detailed else 3,
            success=False,
            properties={"error": str(e)},
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics data"
        )

    except Exception as e:
        logger.error(
            "Unexpected error in user analytics",
            context={
                "user_id": str(current_user.id),
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )

        app_logger.track_exception(e, handled=True, properties={"endpoint": "/analytics/user"})
        app_logger.track_workflow_step(
            workflow_name="analytics_retrieval",
            step_name="error",
            step_number=0,
            total_steps=4 if include_detailed else 3,
            success=False,
            properties={"error": str(e)},
        )

        # Return basic structure on error
        return {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "campaigns_count": 0,
            "websites_count": 0,
            "total_submissions": 0,
            "successful_submissions": 0,
            "failed_submissions": 0,
            "success_rate": 0,
            "error": "Failed to retrieve complete analytics data"
        }


@router.get("/daily-stats")
@log_function("get_daily_analytics")
def analytics_daily_stats(
    request: Request,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    campaign_id: Optional[str] = Query(None, description="Filter by specific campaign"),
    include_trends: bool = Query(False, description="Include trend analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get enhanced daily submission statistics with trend analysis"""
    # Set context variables for structured logging
    user_id_var.set(str(current_user.id))
    
    app_logger = ApplicationInsightsLogger(db)
    app_logger.set_context(user_id=str(current_user.id))

    client_ip = get_client_ip(request)

    logger.info(
        "Daily analytics request started",
        context={
            "user_id": str(current_user.id),
            "client_ip": client_ip,
            "days": days,
            "campaign_id": campaign_id,
            "include_trends": include_trends
        }
    )

    # Track analytics access
    app_logger.track_user_action(
        action="view_daily_stats",
        target="analytics",
        properties={
            "user_id": str(current_user.id),
            "days_requested": days,
            "campaign_filter": campaign_id,
            "include_trends": include_trends,
            "ip": client_ip,
        },
    )

    try:
        query_start = time.time()
        
        # Build base query with optional campaign filter
        where_clause = "s.user_id = :uid AND s.created_at >= (NOW() - make_interval(days => :days))"
        params = {"uid": str(current_user.id), "days": int(days)}
        
        if campaign_id:
            where_clause += " AND s.campaign_id = :campaign_id"
            params["campaign_id"] = campaign_id

        # Enhanced daily statistics query
        daily_query = text(
            f"""
            SELECT
                CAST(date_trunc('day', s.created_at) AS date) AS day,
                COUNT(*)::int AS total,
                SUM(CASE WHEN s.success = true THEN 1 ELSE 0 END)::int AS success,
                SUM(CASE WHEN s.success = false THEN 1 ELSE 0 END)::int AS failed,
                SUM(CASE WHEN s.captcha_encountered = true THEN 1 ELSE 0 END)::int AS captcha_encountered,
                SUM(CASE WHEN s.captcha_solved = true THEN 1 ELSE 0 END)::int AS captcha_solved,
                AVG(s.retry_count)::numeric(10,2) AS avg_retries,
                COUNT(DISTINCT s.campaign_id)::int AS unique_campaigns,
                COUNT(DISTINCT s.website_id)::int AS unique_websites
            FROM submissions s
            WHERE {where_clause}
            GROUP BY 1
            ORDER BY 1 ASC
            """
        )

        rows = db.execute(daily_query, params).mappings().all()
        query_time = (time.time() - query_start) * 1000

        logger.database_operation(
            operation="AGGREGATE",
            table="submissions",
            duration_ms=query_time,
            affected_rows=len(rows),
            success=True
        )

        app_logger.track_database_operation(
            operation="AGGREGATE",
            table="submissions",
            query_time_ms=query_time,
            affected_rows=len(rows),
            success=True,
            query="Enhanced daily stats aggregation",
        )

        # Format data with enhanced metrics
        data = []
        for r in rows:
            day_data = {
                "day": (
                    r["day"].isoformat()
                    if hasattr(r["day"], "isoformat")
                    else str(r["day"])
                ),
                "total": int(r.get("total", 0) or 0),
                "success": int(r.get("success", 0) or 0),
                "failed": int(r.get("failed", 0) or 0),
                "captcha_encountered": int(r.get("captcha_encountered", 0) or 0),
                "captcha_solved": int(r.get("captcha_solved", 0) or 0),
                "avg_retries": float(r.get("avg_retries", 0) or 0),
                "unique_campaigns": int(r.get("unique_campaigns", 0) or 0),
                "unique_websites": int(r.get("unique_websites", 0) or 0),
            }
            
            # Calculate success rate for the day
            if day_data["total"] > 0:
                day_data["success_rate"] = round((day_data["success"] / day_data["total"]) * 100, 2)
            else:
                day_data["success_rate"] = 0

            data.append(day_data)

        # Calculate comprehensive aggregate metrics
        total_submissions = sum(d["total"] for d in data)
        total_success = sum(d["success"] for d in data)
        total_failed = sum(d["failed"] for d in data)
        avg_daily = total_submissions / days if days > 0 else 0
        overall_success_rate = (total_success / total_submissions * 100) if total_submissions > 0 else 0

        # Enhanced trend analysis if requested
        trends = {}
        if include_trends and len(data) >= 7:  # Need at least a week of data for trends
            # Calculate 7-day moving average
            for i in range(6, len(data)):
                week_data = data[i-6:i+1]
                week_total = sum(d["total"] for d in week_data)
                week_success = sum(d["success"] for d in week_data)
                data[i]["moving_avg_submissions"] = round(week_total / 7, 2)
                data[i]["moving_avg_success_rate"] = round(
                    (week_success / week_total * 100) if week_total > 0 else 0, 2
                )

            # Calculate overall trends
            if len(data) >= 14:
                first_half = data[:len(data)//2]
                second_half = data[len(data)//2:]
                
                first_avg = sum(d["total"] for d in first_half) / len(first_half)
                second_avg = sum(d["total"] for d in second_half) / len(second_half)
                
                trends = {
                    "submission_trend": "increasing" if second_avg > first_avg else "decreasing",
                    "trend_percentage": round(((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0, 2),
                    "peak_day": max(data, key=lambda x: x["total"]) if data else None,
                    "best_success_rate_day": max(data, key=lambda x: x["success_rate"]) if data else None
                }

        # Enhanced performance metrics
        logger.performance_metric("daily_stats_query_duration", query_time, "ms")
        logger.performance_metric("daily_stats_data_points", len(data), "count")

        app_logger.track_metric(
            name="daily_stats_query_performance",
            value=query_time,
            properties={
                "days": days,
                "data_points": len(data),
                "campaign_filter": bool(campaign_id),
                "include_trends": include_trends
            },
        )

        app_logger.track_metric(
            name="average_daily_submissions",
            value=avg_daily,
            properties={"user_id": str(current_user.id), "period_days": days},
        )

        # Enhanced business event tracking
        app_logger.track_business_event(
            event_name="daily_stats_retrieved",
            properties={
                "user_id": str(current_user.id),
                "days": days,
                "has_data": len(data) > 0,
                "campaign_filter": campaign_id,
                "include_trends": include_trends,
            },
            metrics={
                "query_time_ms": query_time,
                "total_submissions": total_submissions,
                "total_success": total_success,
                "overall_success_rate": overall_success_rate,
                "data_points": len(data),
                "avg_daily_submissions": avg_daily,
            },
        )

        logger.info(
            "Daily analytics retrieved successfully",
            context={
                "user_id": str(current_user.id),
                "days": days,
                "data_points": len(data),
                "total_submissions": total_submissions,
                "success_rate": overall_success_rate,
                "query_duration_ms": query_time
            }
        )

        response = {
            "days": int(days),
            "campaign_filter": campaign_id,
            "series": data,
            "summary": {
                "total_submissions": total_submissions,
                "total_success": total_success,
                "total_failed": total_failed,
                "overall_success_rate": round(overall_success_rate, 2),
                "avg_daily_submissions": round(avg_daily, 2),
                "active_days": len([d for d in data if d["total"] > 0]),
                "data_points": len(data)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        if include_trends and trends:
            response["trends"] = trends

        return response

    except SQLAlchemyError as e:
        db.rollback()
        
        logger.error(
            "Database error in daily analytics",
            context={
                "user_id": str(current_user.id),
                "days": days,
                "campaign_id": campaign_id,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )

        app_logger.track_exception(
            e,
            handled=True,
            properties={"endpoint": "/analytics/daily-stats", "days": days},
        )

        app_logger.track_business_event(
            event_name="daily_stats_error",
            properties={"user_id": str(current_user.id), "error": str(e), "days": days},
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve daily statistics"
        )

    except Exception as e:
        logger.error(
            "Unexpected error in daily analytics",
            context={
                "user_id": str(current_user.id),
                "days": days,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )

        app_logger.track_exception(e, handled=True)
        
        return {
            "days": int(days),
            "campaign_filter": campaign_id,
            "series": [],
            "summary": {
                "total_submissions": 0,
                "total_success": 0,
                "total_failed": 0,
                "overall_success_rate": 0,
                "avg_daily_submissions": 0,
                "active_days": 0,
                "data_points": 0
            },
            "error": "Failed to retrieve daily statistics",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }


@router.get("/performance")
@log_function("get_performance_analytics")
def analytics_performance(
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Limit results per category"),
    time_range: int = Query(30, ge=1, le=365, description="Days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive performance analytics for campaigns and submissions"""
    # Set context variables for structured logging
    user_id_var.set(str(current_user.id))
    
    app_logger = ApplicationInsightsLogger(db)
    app_logger.set_context(user_id=str(current_user.id))

    client_ip = get_client_ip(request)

    logger.info(
        "Performance analytics request started",
        context={
            "user_id": str(current_user.id),
            "client_ip": client_ip,
            "limit": limit,
            "time_range": time_range
        }
    )

    app_logger.track_user_action(
        action="view_performance_analytics",
        target="analytics",
        properties={
            "user_id": str(current_user.id),
            "limit": limit,
            "time_range": time_range
        },
    )

    try:
        total_start = time.time()

        # Enhanced campaign performance analysis
        campaign_start = time.time()
        campaign_query = text(
            """
            SELECT 
                c.id,
                c.name,
                c.status,
                c.total_urls,
                c.total_websites,
                c.processed,
                c.successful,
                c.failed,
                c.submitted_count,
                c.failed_count,
                CASE 
                    WHEN c.total_websites > 0 
                    THEN ROUND((c.processed::float / c.total_websites) * 100, 2)
                    ELSE 0 
                END as processing_rate,
                CASE 
                    WHEN c.processed > 0 
                    THEN ROUND((c.successful::float / c.processed) * 100, 2)
                    ELSE 0 
                END as success_rate,
                c.created_at,
                c.started_at,
                c.completed_at,
                CASE 
                    WHEN c.started_at IS NOT NULL AND c.completed_at IS NOT NULL
                    THEN EXTRACT(EPOCH FROM (c.completed_at - c.started_at)) / 3600
                    ELSE NULL
                END as duration_hours
            FROM campaigns c
            WHERE c.user_id = :uid
            AND c.created_at >= NOW() - make_interval(days => :time_range)
            ORDER BY c.created_at DESC
            LIMIT :limit
            """
        )
        campaigns = (
            db.execute(campaign_query, {
                "uid": str(current_user.id), 
                "time_range": time_range,
                "limit": limit
            }).mappings().all()
        )
        campaign_time = (time.time() - campaign_start) * 1000

        logger.database_operation(
            operation="SELECT",
            table="campaigns",
            duration_ms=campaign_time,
            affected_rows=len(campaigns),
            success=True
        )

        app_logger.track_database_operation(
            operation="SELECT",
            table="campaigns",
            query_time_ms=campaign_time,
            affected_rows=len(campaigns),
            success=True,
        )

        # Enhanced domain performance analysis
        domain_start = time.time()
        domain_query = text(
            """
            SELECT 
                w.domain,
                COUNT(s.id) as total_attempts,
                SUM(CASE WHEN s.success = true THEN 1 ELSE 0 END) as successes,
                SUM(CASE WHEN s.success = false THEN 1 ELSE 0 END) as failures,
                ROUND(AVG(CASE WHEN s.retry_count IS NOT NULL THEN s.retry_count ELSE 0 END), 2) as avg_retries,
                COUNT(CASE WHEN s.captcha_encountered = true THEN 1 END) as captcha_count,
                COUNT(CASE WHEN s.captcha_solved = true THEN 1 END) as captcha_solved,
                COUNT(CASE WHEN s.email_extracted IS NOT NULL THEN 1 END) as emails_found,
                ROUND((SUM(CASE WHEN s.success = true THEN 1 ELSE 0 END)::float / COUNT(s.id)) * 100, 2) as success_rate,
                MAX(s.created_at) as last_attempt
            FROM submissions s
            JOIN websites w ON s.website_id = w.id
            WHERE s.user_id = :uid
            AND s.created_at >= NOW() - make_interval(days => :time_range)
            GROUP BY w.domain
            HAVING COUNT(s.id) > 0
            ORDER BY total_attempts DESC, success_rate DESC
            LIMIT :limit
            """
        )
        domain_stats = (
            db.execute(domain_query, {
                "uid": str(current_user.id),
                "time_range": time_range,
                "limit": limit
            }).mappings().all()
        )
        domain_time = (time.time() - domain_start) * 1000

        logger.database_operation(
            operation="AGGREGATE",
            table="submissions,websites",
            duration_ms=domain_time,
            affected_rows=len(domain_stats),
            success=True
        )

        app_logger.track_database_operation(
            operation="AGGREGATE",
            table="submissions,websites",
            query_time_ms=domain_time,
            affected_rows=len(domain_stats),
            success=True,
        )

        # Get overall performance summary
        summary_start = time.time()
        summary_query = text(
            """
            SELECT
                COUNT(DISTINCT c.id) as total_campaigns,
                COUNT(DISTINCT CASE WHEN c.status = 'running' THEN c.id END) as active_campaigns,
                COUNT(DISTINCT CASE WHEN c.status = 'completed' THEN c.id END) as completed_campaigns,
                COUNT(DISTINCT w.domain) as unique_domains,
                AVG(CASE WHEN c.successful > 0 AND c.processed > 0 THEN (c.successful::float / c.processed) * 100 END) as avg_campaign_success_rate
            FROM campaigns c
            LEFT JOIN websites w ON w.campaign_id = c.id AND w.user_id = c.user_id
            WHERE c.user_id = :uid
            AND c.created_at >= NOW() - make_interval(days => :time_range)
            """
        )
        summary_row = db.execute(summary_query, {
            "uid": str(current_user.id),
            "time_range": time_range
        }).mappings().first() or {}
        summary_time = (time.time() - summary_start) * 1000

        total_time = (time.time() - total_start) * 1000

        # Format comprehensive response
        performance_data = {
            "time_range_days": time_range,
            "limit": limit,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            
            "campaigns": [
                {
                    **dict(c),
                    "created_at": c["created_at"].isoformat() if c["created_at"] else None,
                    "started_at": c["started_at"].isoformat() if c["started_at"] else None,
                    "completed_at": c["completed_at"].isoformat() if c["completed_at"] else None,
                }
                for c in campaigns
            ],
            
            "domain_statistics": [dict(d) for d in domain_stats],
            
            "summary": {
                "total_campaigns": int(summary_row.get("total_campaigns", 0) or 0),
                "active_campaigns": int(summary_row.get("active_campaigns", 0) or 0),
                "completed_campaigns": int(summary_row.get("completed_campaigns", 0) or 0),
                "unique_domains": int(summary_row.get("unique_domains", 0) or 0),
                "avg_campaign_success_rate": round(float(summary_row.get("avg_campaign_success_rate", 0) or 0), 2),
                "top_performing_domains": [
                    d["domain"] for d in sorted(domain_stats, key=lambda x: x["success_rate"], reverse=True)[:5]
                ],
                "most_active_domains": [d["domain"] for d in domain_stats[:5]],
            },
            
            "query_performance": {
                "total_time_ms": round(total_time, 2),
                "campaign_query_ms": round(campaign_time, 2),
                "domain_query_ms": round(domain_time, 2),
                "summary_query_ms": round(summary_time, 2)
            }
        }

        # Enhanced metric tracking
        logger.performance_metric("performance_analytics_total_duration", total_time, "ms")

        # Track comprehensive business event
        app_logger.track_business_event(
            event_name="performance_analytics_retrieved",
            properties={
                "user_id": str(current_user.id),
                "campaigns_analyzed": len(campaigns),
                "domains_analyzed": len(domain_stats),
                "time_range_days": time_range,
                "limit": limit
            },
            metrics={
                "total_query_time_ms": total_time,
                "campaign_query_ms": campaign_time,
                "domain_query_ms": domain_time,
                "summary_query_ms": summary_time,
                "total_campaigns": performance_data["summary"]["total_campaigns"],
                "active_campaigns": performance_data["summary"]["active_campaigns"]
            },
        )

        logger.info(
            "Performance analytics retrieved successfully",
            context={
                "user_id": str(current_user.id),
                "campaigns_analyzed": len(campaigns),
                "domains_analyzed": len(domain_stats),
                "total_duration_ms": total_time,
                "time_range": time_range
            }
        )

        return performance_data

    except SQLAlchemyError as e:
        db.rollback()
        
        logger.error(
            "Database error in performance analytics",
            context={
                "user_id": str(current_user.id),
                "time_range": time_range,
                "limit": limit,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )

        app_logger.track_exception(e, handled=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance analytics"
        )

    except Exception as e:
        logger.error(
            "Unexpected error in performance analytics",
            context={
                "user_id": str(current_user.id),
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )

        app_logger.track_exception(e, handled=True)
        
        return {
            "time_range_days": time_range,
            "limit": limit,
            "campaigns": [],
            "domain_statistics": [],
            "summary": {
                "total_campaigns": 0,
                "active_campaigns": 0,
                "completed_campaigns": 0,
                "unique_domains": 0,
                "avg_campaign_success_rate": 0,
                "top_performing_domains": [],
                "most_active_domains": [],
            },
            "error": "Failed to retrieve performance analytics",
            "generated_at": datetime.now(timezone.utc).isoformat()
        }


@router.get("/export")
@log_function("export_analytics_data") 
def export_analytics_data(
    request: Request,
    format: str = Query("json", regex="^(json|csv)$", description="Export format"),
    include_raw_data: bool = Query(False, description="Include raw submission data"),
    time_range: int = Query(30, ge=1, le=365, description="Days to include"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export analytics data in various formats"""
    # Set context variables for structured logging
    user_id_var.set(str(current_user.id))
    
    app_logger = ApplicationInsightsLogger(db)
    app_logger.set_context(user_id=str(current_user.id))

    client_ip = get_client_ip(request)

    logger.info(
        "Analytics export request started",
        context={
            "user_id": str(current_user.id),
            "client_ip": client_ip,
            "format": format,
            "include_raw_data": include_raw_data,
            "time_range": time_range
        }
    )

    app_logger.track_user_action(
        action="export_analytics",
        target="analytics_export",
        properties={
            "format": format,
            "include_raw_data": include_raw_data,
            "time_range": time_range,
            "user_id": str(current_user.id)
        }
    )

    try:
        export_start = time.time()
        
        # Get analytics data using existing endpoints' logic
        # This is a simplified version - you might want to create a dedicated export query
        
        # Get summary data
        summary_query = text("""
            SELECT 
                COUNT(DISTINCT c.id) as campaigns_count,
                COUNT(DISTINCT w.id) as websites_count,
                COUNT(s.id) as total_submissions,
                SUM(CASE WHEN s.success = true THEN 1 ELSE 0 END) as successful_submissions,
                AVG(CASE WHEN s.success = true THEN 100.0 ELSE 0.0 END) as success_rate
            FROM campaigns c
            LEFT JOIN websites w ON w.campaign_id = c.id AND w.user_id = c.user_id
            LEFT JOIN submissions s ON s.campaign_id = c.id AND s.user_id = c.user_id
            WHERE c.user_id = :uid
            AND c.created_at >= NOW() - make_interval(days => :time_range)
        """)
        
        summary_data = db.execute(summary_query, {
            "uid": str(current_user.id),
            "time_range": time_range
        }).mappings().first()

        export_data = {
            "export_metadata": {
                "user_id": str(current_user.id),
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "time_range_days": time_range,
                "format": format,
                "includes_raw_data": include_raw_data
            },
            "summary": dict(summary_data) if summary_data else {},
        }

        if include_raw_data:
            # Add raw submission data if requested
            raw_query = text("""
                SELECT 
                    s.id,
                    s.created_at,
                    s.status,
                    s.success,
                    s.retry_count,
                    c.name as campaign_name,
                    w.domain
                FROM submissions s
                JOIN campaigns c ON s.campaign_id = c.id
                LEFT JOIN websites w ON s.website_id = w.id
                WHERE s.user_id = :uid
                AND s.created_at >= NOW() - make_interval(days => :time_range)
                ORDER BY s.created_at DESC
            """)
            
            raw_data = db.execute(raw_query, {
                "uid": str(current_user.id),
                "time_range": time_range
            }).mappings().all()
            
            export_data["raw_submissions"] = [dict(row) for row in raw_data]

        export_time = (time.time() - export_start) * 1000

        # Track business event
        app_logger.track_business_event(
            event_name="analytics_data_exported",
            properties={
                "user_id": str(current_user.id),
                "format": format,
                "include_raw_data": include_raw_data,
                "time_range": time_range
            },
            metrics={
                "export_time_ms": export_time,
                "data_size_bytes": len(str(export_data))
            }
        )

        logger.info(
            "Analytics export completed successfully",
            context={
                "user_id": str(current_user.id),
                "format": format,
                "export_duration_ms": export_time,
                "data_points": len(export_data.get("raw_submissions", []))
            }
        )

        return export_data

    except Exception as e:
        logger.error(
            "Error in analytics export",
            context={
                "user_id": str(current_user.id),
                "format": format,
                "error_type": type(e).__name__,
                "error_message": str(e)
            }
        )

        app_logger.track_exception(e, handled=True)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export analytics data"
        )