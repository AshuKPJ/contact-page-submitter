# app/api/admin.py - Updated with new logging system
from __future__ import annotations

import time
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.models.user import User
from app.schemas.admin import SystemStatus, UserManagement, AdminResponse
from app.services.admin_service import AdminService

# Import new logging system
from app.logging import get_logger
from app.logging.decorators import log_function, log_exceptions

# Create logger for this module
logger = get_logger("api.admin")

router = APIRouter(redirect_slashes=False)


def get_client_ip(request: Request) -> str:
    """Extract client IP from request headers"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request and request.client:
        return request.client.host
    return "unknown"


def get_user_agent(request: Request) -> str:
    """Extract user agent from request headers"""
    return request.headers.get("user-agent", "unknown")[
        :200
    ]  # Truncate long user agents


@router.get("/system-status", response_model=SystemStatus)
@log_function("admin_get_system_status")
async def get_system_status(
    request: Request,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get system status - admin only"""

    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Log admin access as security event
    logger.auth_event(
        action="admin_access",
        email=admin_user.email,
        success=True,
        ip_address=client_ip,
        context={
            "action_type": "view_system_status",
            "admin_id": str(admin_user.id),
            "user_agent": user_agent,
        },
    )

    try:
        svc = AdminService(db)

        # Time the system status check
        status_start = time.time()
        status_data = svc.get_system_status()
        status_time = (time.time() - status_start) * 1000

        # Log performance metric
        logger.performance_metric(
            "admin_system_status_query_time",
            status_time,
            context={"admin_id": str(admin_user.id)},
        )

        logger.info(
            "System status retrieved successfully",
            context={
                "admin_id": str(admin_user.id),
                "query_time_ms": status_time,
                "status_data_keys": (
                    list(status_data.dict().keys())
                    if hasattr(status_data, "dict")
                    else "unknown"
                ),
            },
        )

        return status_data

    except Exception as e:
        logger.exception(
            e,
            handled=True,
            context={
                "admin_id": str(admin_user.id),
                "action": "get_system_status",
                "client_ip": client_ip,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch system status",
        )


@router.get("/users")
@log_function("admin_list_users")
async def get_all_users(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    active_only: bool = Query(False),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get all users with pagination - admin only"""

    client_ip = get_client_ip(request)

    # Log the admin action
    logger.info(
        f"Admin listing users: page {page}, per_page {per_page}",
        context={
            "event_type": "admin_action",
            "action": "list_users",
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "page": page,
            "per_page": per_page,
            "active_only": active_only,
            "client_ip": client_ip,
        },
    )

    try:
        svc = AdminService(db)

        # Time the query
        query_start = time.time()
        users, total = svc.get_all_users(page, per_page, active_only)
        query_time = (time.time() - query_start) * 1000

        # Log database performance
        logger.database_operation(
            operation="SELECT",
            table="users",
            duration_ms=query_time,
            affected_rows=len(users),
            success=True,
            context={
                "admin_id": str(admin_user.id),
                "pagination": {"page": page, "per_page": per_page},
                "total_results": total,
            },
        )

        logger.info(
            f"User list retrieved: {len(users)} users, {total} total",
            context={
                "admin_id": str(admin_user.id),
                "results_count": len(users),
                "total_count": total,
                "query_time_ms": query_time,
            },
        )

        return {
            "users": users,
            "total": total,
            "page": page,
            "per_page": per_page,
            "query_time_ms": round(query_time, 2),
        }

    except Exception as e:
        logger.exception(
            e,
            handled=True,
            context={
                "admin_id": str(admin_user.id),
                "action": "list_users",
                "page": page,
                "per_page": per_page,
                "client_ip": client_ip,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch users",
        )


@router.post("/manage-user", response_model=AdminResponse)
@log_function("admin_manage_user")
async def manage_user(
    request: Request,
    user_management: UserManagement,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Manage user account - admin only"""

    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Log the critical admin action
    logger.warning(
        f"Admin user management action: {user_management.action}",
        context={
            "event_type": "admin_user_management",
            "action": user_management.action,
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "target_user_id": str(user_management.user_id),
            "client_ip": client_ip,
            "user_agent": user_agent,
        },
    )

    try:
        svc = AdminService(db)

        # Execute management action
        action_start = time.time()
        result = svc.manage_user(admin_user.id, user_management)
        action_time = (time.time() - action_start) * 1000

        # Log successful action
        logger.info(
            f"User management action completed: {user_management.action}",
            context={
                "event_type": "admin_action_success",
                "action": user_management.action,
                "admin_id": str(admin_user.id),
                "target_user_id": str(user_management.user_id),
                "action_time_ms": action_time,
                "result": result.dict() if hasattr(result, "dict") else str(result),
            },
        )

        # Log performance metric
        logger.performance_metric(
            f"admin_user_management_{user_management.action}_time",
            action_time,
            context={
                "admin_id": str(admin_user.id),
                "target_user_id": str(user_management.user_id),
            },
        )

        return result

    except HTTPException:
        # Log HTTP exceptions but let them bubble up
        logger.warning(
            f"User management action failed: {user_management.action}",
            context={
                "event_type": "admin_action_failed",
                "action": user_management.action,
                "admin_id": str(admin_user.id),
                "target_user_id": str(user_management.user_id),
                "error_type": "HTTPException",
            },
        )
        raise
    except Exception as e:
        logger.exception(
            e,
            handled=True,
            context={
                "event_type": "admin_action_error",
                "action": user_management.action,
                "admin_id": str(admin_user.id),
                "target_user_id": str(user_management.user_id),
                "client_ip": client_ip,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to manage user",
        )


@router.get("/metrics")
@log_function("admin_get_metrics")
async def get_system_metrics(
    request: Request,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get detailed system metrics - admin only"""

    client_ip = get_client_ip(request)

    logger.info(
        "Admin accessing system metrics",
        context={
            "event_type": "admin_metrics_access",
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "client_ip": client_ip,
        },
    )

    try:
        svc = AdminService(db)

        metrics_start = time.time()
        metrics = svc.get_system_metrics()
        metrics_time = (time.time() - metrics_start) * 1000

        # Log performance
        logger.performance_metric(
            "admin_metrics_query_time",
            metrics_time,
            context={"admin_id": str(admin_user.id)},
        )

        logger.info(
            "System metrics retrieved successfully",
            context={
                "admin_id": str(admin_user.id),
                "metrics_count": (
                    len(metrics) if isinstance(metrics, (list, dict)) else "unknown"
                ),
                "query_time_ms": metrics_time,
            },
        )

        return metrics

    except Exception as e:
        logger.exception(
            e,
            handled=True,
            context={
                "admin_id": str(admin_user.id),
                "action": "get_system_metrics",
                "client_ip": client_ip,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch metrics",
        )


@router.get("/logs")
@log_exceptions("admin_get_logs")
async def get_system_logs(
    request: Request,
    limit: int = Query(50, ge=1, le=200),
    level: str = Query(None, regex="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get recent system logs - admin only"""

    client_ip = get_client_ip(request)

    # Log admin access to logs (security-sensitive)
    logger.warning(
        "Admin accessing system logs",
        context={
            "event_type": "admin_logs_access",
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "limit": limit,
            "level_filter": level,
            "client_ip": client_ip,
        },
    )

    try:
        svc = AdminService(db)

        logs_start = time.time()
        logs = svc.get_recent_system_logs(limit)
        logs_time = (time.time() - logs_start) * 1000

        # Convert logs to dictionary format if they're model objects
        logs_data = []
        for log in logs:
            if hasattr(log, "__dict__"):
                log_dict = {
                    "id": str(log.id) if hasattr(log, "id") and log.id else None,
                    "user_id": (
                        str(log.user_id)
                        if hasattr(log, "user_id") and log.user_id
                        else None
                    ),
                    "action": log.action if hasattr(log, "action") else None,
                    "details": log.details if hasattr(log, "details") else None,
                    "timestamp": (
                        log.timestamp.isoformat()
                        if hasattr(log, "timestamp") and log.timestamp
                        else None
                    ),
                    "ip_address": (
                        log.ip_address if hasattr(log, "ip_address") else None
                    ),
                    "user_agent": (
                        log.user_agent[:200]
                        if hasattr(log, "user_agent") and log.user_agent
                        else None
                    ),
                    "level": getattr(log, "level", "INFO"),
                }
                logs_data.append(log_dict)
            elif isinstance(log, dict):
                logs_data.append(log)
            else:
                logs_data.append({"raw_log": str(log)})

        # Filter by level if specified
        if level:
            logs_data = [log for log in logs_data if log.get("level") == level]

        logger.info(
            f"System logs retrieved: {len(logs_data)} entries",
            context={
                "admin_id": str(admin_user.id),
                "logs_count": len(logs_data),
                "query_time_ms": logs_time,
                "level_filter": level,
            },
        )

        return {
            "logs": logs_data,
            "count": len(logs_data),
            "limit": limit,
            "level_filter": level,
            "query_time_ms": round(logs_time, 2),
        }

    except Exception as e:
        logger.exception(
            e,
            handled=True,
            context={
                "admin_id": str(admin_user.id),
                "action": "get_system_logs",
                "limit": limit,
                "client_ip": client_ip,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch logs",
        )


@router.post("/audit-trail")
@log_function("admin_create_audit")
async def create_audit_entry(
    request: Request,
    action: str,
    details: str,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Create an audit trail entry - admin only"""

    client_ip = get_client_ip(request)
    user_agent = get_user_agent(request)

    # Validate input
    if not action or not action.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Action is required"
        )

    if not details or not details.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Details are required"
        )

    # Truncate long inputs
    action = action.strip()[:200]
    details = details.strip()[:1000]

    # Log the audit creation (this is meta-logging!)
    logger.warning(
        f"Admin created audit entry: {action}",
        context={
            "event_type": "admin_audit_created",
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "audit_action": action,
            "audit_details": details,
            "client_ip": client_ip,
            "user_agent": user_agent,
        },
    )

    try:
        # Store in database if you have an audit table
        # For now, just log it comprehensively
        logger.info(
            "Audit trail entry created successfully",
            context={
                "event_type": "audit_entry",
                "created_by": str(admin_user.id),
                "created_by_email": admin_user.email,
                "action": action,
                "details": details,
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )

        return {
            "success": True,
            "message": "Audit entry created successfully",
            "audit_id": f"audit_{int(time.time())}_{admin_user.id}",
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.exception(
            e,
            handled=True,
            context={
                "admin_id": str(admin_user.id),
                "action": "create_audit_entry",
                "audit_action": action,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create audit entry",
        )


@router.delete("/logs/clear")
@log_function("admin_clear_logs")
async def clear_system_logs(
    request: Request,
    confirm: bool = Query(False),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Clear system logs - admin only (dangerous operation)"""

    if not confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must confirm log clearing operation with confirm=true",
        )

    client_ip = get_client_ip(request)

    # Log this critical action
    logger.critical(
        "Admin initiated log clearing operation",
        context={
            "event_type": "admin_critical_action",
            "action": "clear_system_logs",
            "admin_id": str(admin_user.id),
            "admin_email": admin_user.email,
            "client_ip": client_ip,
            "confirmed": confirm,
        },
    )

    try:
        # Get buffer handler to clear in-memory logs
        from app.logging.handlers import get_buffer_handler

        buffer_handler = get_buffer_handler()

        if buffer_handler:
            buffer_handler.clear()
            logger.warning("In-memory log buffer cleared by admin")

        # You might also want to clear database logs here
        # Be very careful with this operation!

        logger.warning(
            "System logs cleared successfully",
            context={
                "admin_id": str(admin_user.id),
                "operation": "clear_logs_complete",
            },
        )

        return {
            "success": True,
            "message": "System logs cleared successfully",
            "cleared_by": admin_user.email,
            "timestamp": time.time(),
        }

    except Exception as e:
        logger.exception(
            e,
            handled=True,
            context={
                "admin_id": str(admin_user.id),
                "action": "clear_system_logs",
                "critical_operation": True,
            },
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear logs",
        )
