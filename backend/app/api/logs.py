# app/api/logs.py - Updated with comprehensive logging
from __future__ import annotations

import time
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

# FIXED: Import from existing log_service
from app.services.log_service import LogService as ApplicationInsightsLogger

router = APIRouter(prefix="/api/logs", tags=["logs"], redirect_slashes=False)


class AppEvent(BaseModel):
    level: str = Field(default="INFO", pattern="^(INFO|WARN|ERROR)$")
    message: str = Field(min_length=1, max_length=1000)
    campaign_id: Optional[str] = Field(None, max_length=100)
    website_id: Optional[str] = Field(None, max_length=100)
    organization_id: Optional[str] = Field(None, max_length=100)
    context: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "level": "INFO",
                "message": "Campaign started successfully",
                "campaign_id": "12345",
                "context": {"action": "start_campaign"},
            }
        }


class LogResponse(BaseModel):
    status: str
    message: Optional[str] = None


# Rate limiting helper with tracking
class SimpleRateLimiter:
    def __init__(self):
        self.requests = {}
        self.violation_counts = {}

    def allow(
        self, key: str, max_requests: int = 100, window_seconds: int = 60
    ) -> bool:
        import time

        now = time.time()

        if key not in self.requests:
            self.requests[key] = []
            self.violation_counts[key] = 0

        # Clean old requests
        self.requests[key] = [
            req_time
            for req_time in self.requests[key]
            if now - req_time < window_seconds
        ]

        # Check limit
        if len(self.requests[key]) >= max_requests:
            self.violation_counts[key] += 1
            return False

        # Add current request
        self.requests[key].append(now)
        return True

    def get_stats(self, key: str) -> Dict[str, Any]:
        """Get rate limit stats for a key"""
        import time

        now = time.time()

        if key not in self.requests:
            return {"current_requests": 0, "violations": 0}

        # Clean old requests for accurate count
        self.requests[key] = [
            req_time
            for req_time in self.requests[key]
            if now - req_time < 60  # Assuming 60 second window
        ]

        return {
            "current_requests": len(self.requests.get(key, [])),
            "violations": self.violation_counts.get(key, 0),
        }


# Global rate limiter instance
rate_limiter = SimpleRateLimiter()


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request and request.client:
        return request.client.host
    return "unknown"


@router.post("/app", response_model=LogResponse)
def create_app_log(
    request: Request,
    body: AppEvent,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create an application log entry"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(
        user_id=str(current_user.id),
        campaign_id=body.campaign_id,
        organization_id=body.organization_id,
    )

    # Track that a manual log was created
    logger.track_user_action(
        action="create_manual_log",
        target="logs",
        properties={
            "level": body.level,
            "has_campaign": bool(body.campaign_id),
            "has_website": bool(body.website_id),
            "ip": get_client_ip(request),
        },
    )

    # Rate-limit per-user (100 requests per minute)
    key = f"user:{current_user.id}:logs_app"
    if not rate_limiter.allow(key, max_requests=100, window_seconds=60):
        # Track rate limit violation
        stats = rate_limiter.get_stats(key)

        logger.track_business_event(
            event_name="rate_limit_exceeded",
            properties={
                "user_id": str(current_user.id),
                "endpoint": "/logs/app",
                "violation_count": stats["violations"],
            },
            metrics={
                "current_requests": stats["current_requests"],
                "violations": stats["violations"],
            },
        )

        logger.track_metric(
            name="rate_limit_violations",
            value=1,
            properties={"user_id": str(current_user.id), "endpoint": "/logs/app"},
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many log events. Please slow down.",
        )

    try:
        # Validate context if provided
        context = body.context or {}
        if not isinstance(context, dict):
            context = {}

        # Track the creation of the log
        create_start = time.time()

        # Log based on level using our enhanced logger
        if body.level == "INFO":
            logger.track_business_event(
                event_name="user_log_info",
                properties={
                    "message": body.message,
                    "campaign_id": body.campaign_id,
                    "website_id": body.website_id,
                    "custom_context": context,
                },
            )
        elif body.level == "WARN":
            logger.track_business_event(
                event_name="user_log_warning",
                properties={
                    "message": body.message,
                    "campaign_id": body.campaign_id,
                    "website_id": body.website_id,
                    "custom_context": context,
                },
            )
        elif body.level == "ERROR":
            logger.track_business_event(
                event_name="user_log_error",
                properties={
                    "message": body.message,
                    "campaign_id": body.campaign_id,
                    "website_id": body.website_id,
                    "custom_context": context,
                },
            )

        create_time = (time.time() - create_start) * 1000

        # Track performance
        logger.track_metric(
            name="user_log_creation_time",
            value=create_time,
            properties={"level": body.level},
        )

        # Track business event for log creation
        logger.track_business_event(
            event_name="app_log_created",
            properties={
                "user_id": str(current_user.id),
                "log_level": body.level,
                "has_context": bool(context),
            },
            metrics={
                "creation_time_ms": create_time,
                "context_size": len(str(context)),
            },
        )

        return LogResponse(status="ok", message="Log entry created successfully")

    except SQLAlchemyError as e:
        db.rollback()
        logger.track_exception(
            e, handled=True, properties={"endpoint": "/logs/app", "level": body.level}
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create log entry",
        )
    except Exception as e:
        db.rollback()
        logger.track_exception(e, handled=True)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid log data: {str(e)}",
        )


@router.post("/system")
def create_system_log(
    request: Request,
    body: AppEvent,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a system log entry (admin users only)"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    # Check if user is admin
    user_role = getattr(current_user, "role", "user")
    if isinstance(user_role, str):
        role_str = user_role
    else:
        role_str = getattr(user_role, "value", str(user_role))

    if role_str != "admin":
        # Track unauthorized attempt
        logger.track_business_event(
            event_name="unauthorized_system_log_attempt",
            properties={
                "user_id": str(current_user.id),
                "user_role": role_str,
                "ip": get_client_ip(request),
            },
        )

        logger.track_authentication(
            action="system_log_denied",
            email=current_user.email,
            success=False,
            failure_reason="Insufficient privileges",
            ip_address=get_client_ip(request),
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    # Track admin action
    logger.track_business_event(
        event_name="admin_system_log",
        properties={
            "admin_id": str(current_user.id),
            "admin_email": current_user.email,
            "log_level": body.level,
            "ip": get_client_ip(request),
        },
    )

    # Rate-limit per-user
    key = f"user:{current_user.id}:logs_system"
    if not rate_limiter.allow(key, max_requests=50, window_seconds=60):
        stats = rate_limiter.get_stats(key)

        logger.track_business_event(
            event_name="admin_rate_limit_exceeded",
            properties={
                "admin_id": str(current_user.id),
                "endpoint": "/logs/system",
                "violations": stats["violations"],
            },
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many system log events",
        )

    try:
        create_start = time.time()

        # Create system log
        logger.track_business_event(
            event_name=f"system_log_{body.level.lower()}",
            properties={
                "admin_id": str(current_user.id),
                "message": body.message,
                "context": body.context or {},
            },
        )

        create_time = (time.time() - create_start) * 1000

        logger.track_metric(
            name="system_log_creation_time",
            value=create_time,
            properties={"admin_id": str(current_user.id)},
        )

        return LogResponse(status="ok", message="System log entry created")

    except SQLAlchemyError as e:
        db.rollback()
        logger.track_exception(e, handled=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create system log entry",
        )
    except Exception as e:
        db.rollback()
        logger.track_exception(e, handled=True)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid system log data: {str(e)}",
        )


@router.get("/health")
def logs_health_check(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if logging service is operational"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    logger.track_user_action(
        action="check_logs_health",
        target="logs_health",
        properties={"user_id": str(current_user.id), "ip": get_client_ip(request)},
    )

    try:
        # Try to create a test log entry
        health_start = time.time()

        logger.track_business_event(
            event_name="logs_health_check",
            properties={"user_id": str(current_user.id), "test": True},
        )

        health_time = (time.time() - health_start) * 1000

        logger.track_metric(
            name="logs_health_check_time",
            value=health_time,
            properties={"user_id": str(current_user.id)},
        )

        return {
            "status": "healthy",
            "service": "logging",
            "message": "Logging service is operational",
            "response_time_ms": round(health_time, 2),
        }

    except Exception as e:
        db.rollback()
        logger.track_exception(e, handled=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logging service unhealthy: {str(e)}",
        )


@router.get("/rate-limit-status")
def get_rate_limit_status(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current rate limit status for the user"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    logger.track_user_action(
        action="check_rate_limit",
        target="rate_limit_status",
        properties={"user_id": str(current_user.id), "ip": get_client_ip(request)},
    )

    # Get stats for both endpoints
    app_key = f"user:{current_user.id}:logs_app"
    system_key = f"user:{current_user.id}:logs_system"

    app_stats = rate_limiter.get_stats(app_key)
    system_stats = rate_limiter.get_stats(system_key)

    # Check if user is admin
    user_role = getattr(current_user, "role", "user")
    if isinstance(user_role, str):
        role_str = user_role
    else:
        role_str = getattr(user_role, "value", str(user_role))

    is_admin = role_str == "admin"

    response = {
        "user_id": str(current_user.id),
        "app_logs": {
            "current_requests": app_stats["current_requests"],
            "max_requests": 100,
            "window_seconds": 60,
            "remaining": max(0, 100 - app_stats["current_requests"]),
            "violations": app_stats["violations"],
        },
    }

    if is_admin:
        response["system_logs"] = {
            "current_requests": system_stats["current_requests"],
            "max_requests": 50,
            "window_seconds": 60,
            "remaining": max(0, 50 - system_stats["current_requests"]),
            "violations": system_stats["violations"],
        }

    # Track metrics
    logger.track_metric(
        name="rate_limit_check",
        value=app_stats["current_requests"],
        properties={"user_id": str(current_user.id), "endpoint": "app_logs"},
    )

    if app_stats["violations"] > 0:
        logger.track_business_event(
            event_name="rate_limit_status_with_violations",
            properties={
                "user_id": str(current_user.id),
                "app_violations": app_stats["violations"],
                "system_violations": system_stats["violations"] if is_admin else 0,
            },
        )

    return response


@router.post("/bulk")
def create_bulk_logs(
    request: Request,
    logs: list[AppEvent],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create multiple log entries at once (with stricter rate limiting)"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    # Track bulk log request
    logger.track_user_action(
        action="create_bulk_logs",
        target="logs",
        properties={
            "user_id": str(current_user.id),
            "log_count": len(logs),
            "ip": get_client_ip(request),
        },
    )

    # Stricter rate limit for bulk operations
    key = f"user:{current_user.id}:logs_bulk"
    if not rate_limiter.allow(key, max_requests=10, window_seconds=60):
        stats = rate_limiter.get_stats(key)

        logger.track_business_event(
            event_name="bulk_rate_limit_exceeded",
            properties={
                "user_id": str(current_user.id),
                "attempted_logs": len(logs),
                "violations": stats["violations"],
            },
        )

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many bulk log requests",
        )

    # Limit bulk size
    if len(logs) > 50:
        logger.track_business_event(
            event_name="bulk_logs_too_large",
            properties={
                "user_id": str(current_user.id),
                "attempted_count": len(logs),
                "max_allowed": 50,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 logs per bulk request",
        )

    try:
        bulk_start = time.time()
        success_count = 0
        error_count = 0

        # Process each log
        for log_event in logs:
            try:
                # Create log based on level
                if log_event.level == "ERROR":
                    logger.track_business_event(
                        event_name="bulk_user_log_error",
                        properties={
                            "message": log_event.message[
                                :200
                            ],  # Truncate long messages
                            "campaign_id": log_event.campaign_id,
                        },
                    )
                else:
                    logger.track_business_event(
                        event_name=f"bulk_user_log_{log_event.level.lower()}",
                        properties={
                            "message": log_event.message[:200],
                            "campaign_id": log_event.campaign_id,
                        },
                    )
                success_count += 1
            except Exception:
                error_count += 1

        bulk_time = (time.time() - bulk_start) * 1000

        # Track metrics
        logger.track_metric(
            name="bulk_logs_processing_time",
            value=bulk_time,
            properties={"total_logs": len(logs), "success_count": success_count},
        )

        logger.track_business_event(
            event_name="bulk_logs_created",
            properties={
                "user_id": str(current_user.id),
                "total_logs": len(logs),
                "success_count": success_count,
                "error_count": error_count,
            },
            metrics={
                "processing_time_ms": bulk_time,
                "logs_per_second": (
                    len(logs) / (bulk_time / 1000) if bulk_time > 0 else 0
                ),
            },
        )

        return {
            "status": "ok",
            "message": f"Processed {success_count}/{len(logs)} logs successfully",
            "success_count": success_count,
            "error_count": error_count,
        }

    except Exception as e:
        db.rollback()
        logger.track_exception(e, handled=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process bulk logs",
        )
