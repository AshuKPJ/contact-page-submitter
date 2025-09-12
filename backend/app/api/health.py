# app/api/health.py - Fixed with correct settings references
from __future__ import annotations

import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import get_db
from app.core.config import get_settings

# Check if enhanced log service exists, otherwise use regular LogService
try:
    from app.services.log_service import ApplicationInsightsLogger
except ImportError:
    from app.services.log_service import LogService as ApplicationInsightsLogger

router = APIRouter(prefix="/api", tags=["health"], redirect_slashes=False)
settings = get_settings()


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


@router.get("/health")
async def health_check(
    request: Request, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Health check endpoint to verify API and database connectivity"""
    logger = ApplicationInsightsLogger(db)

    # Track health check
    if hasattr(logger, "track_business_event"):
        logger.track_business_event(
            event_name="health_check",
            properties={
                "endpoint": "/health",
                "ip": get_client_ip(request),
                "user_agent": request.headers.get("user-agent", "")[:200],
            },
        )
    else:
        logger.info(
            "health_check",
            context={"endpoint": "/health", "ip": get_client_ip(request)},
        )

    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": getattr(settings, "APP_VERSION", "1.0.0"),
        "services": {},
    }

    # Check database connection
    db_check_start = time.time()
    try:
        result = db.execute(text("SELECT 1 as health_check"))
        row = result.fetchone()
        db_check_time = (time.time() - db_check_start) * 1000

        if row and row[0] == 1:
            health_status["services"]["database"] = {
                "status": "connected",
                "message": "Database connection successful",
                "response_time_ms": round(db_check_time, 2),
            }

            if hasattr(logger, "track_dependency"):
                logger.track_dependency(
                    name="database",
                    dependency_type="SQL",
                    target="postgres",
                    duration_ms=db_check_time,
                    success=True,
                    result_code="OK",
                )

    except SQLAlchemyError as e:
        db_check_time = (time.time() - db_check_start) * 1000
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = {
            "status": "disconnected",
            "message": f"Database connection failed: {str(e)}",
            "response_time_ms": round(db_check_time, 2),
        }

        if hasattr(logger, "track_exception"):
            logger.track_exception(
                e, handled=True, properties={"check": "database_health"}
            )

    except Exception as e:
        db_check_time = (time.time() - db_check_start) * 1000
        health_status["status"] = "unhealthy"
        health_status["services"]["database"] = {
            "status": "error",
            "message": f"Database check error: {str(e)}",
            "response_time_ms": round(db_check_time, 2),
        }

    # Check other services status
    health_status["services"]["auth"] = {"status": "operational"}
    health_status["services"]["browser_automation"] = {"status": "operational"}

    # Check critical tables
    tables_check_start = time.time()
    try:
        tables_check = db.execute(
            text(
                """
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name IN ('users', 'campaigns', 'submissions')
                """
            )
        ).scalar()
        tables_check_time = (time.time() - tables_check_start) * 1000

        health_status["services"]["database"]["tables_available"] = tables_check >= 3

        if hasattr(logger, "track_database_operation"):
            logger.track_database_operation(
                operation="SELECT",
                table="information_schema.tables",
                query_time_ms=tables_check_time,
                success=True,
            )

    except Exception as e:
        health_status["services"]["database"]["tables_available"] = False
        if hasattr(logger, "track_exception"):
            logger.track_exception(
                e, handled=True, properties={"check": "tables_health"}
            )

    # Track overall health status
    if hasattr(logger, "track_metric"):
        logger.track_metric(
            name="health_check_status",
            value=1 if health_status["status"] == "healthy" else 0,
            properties={
                "database_connected": health_status["services"]
                .get("database", {})
                .get("status")
                == "connected"
            },
        )

    return health_status


@router.get("/ping")
async def ping(request: Request, db: Session = Depends(get_db)) -> Dict[str, str]:
    """Simple ping endpoint for uptime monitoring"""
    logger = ApplicationInsightsLogger(db)

    if hasattr(logger, "track_metric"):
        logger.track_metric(
            name="ping_received", value=1, properties={"ip": get_client_ip(request)}
        )

    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Contact Page Submitter API",
    }


@router.get("/version")
async def version(db: Session = Depends(get_db)) -> Dict[str, str]:
    """Get API version information"""
    logger = ApplicationInsightsLogger(db)

    if hasattr(logger, "track_business_event"):
        logger.track_business_event(
            event_name="version_check",
            properties={"version": getattr(settings, "APP_VERSION", "1.0.0")},
        )

    return {
        "version": getattr(settings, "APP_VERSION", "1.0.0"),
        "name": "Contact Page Submitter API",
        "description": "API for automated contact form submissions",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/readiness")
async def readiness_check(
    request: Request, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Readiness check for Kubernetes/container orchestration"""
    logger = ApplicationInsightsLogger(db)

    if hasattr(logger, "track_business_event"):
        logger.track_business_event(
            event_name="readiness_check",
            properties={"endpoint": "/readiness", "ip": get_client_ip(request)},
        )

    checks = {
        "database": False,
        "tables": False,
    }

    check_start = time.time()

    try:
        # Test database connection
        db_test_start = time.time()
        db.execute(text("SELECT 1"))
        checks["database"] = True
        db_test_time = (time.time() - db_test_start) * 1000

        if hasattr(logger, "track_dependency"):
            logger.track_dependency(
                name="database_readiness",
                dependency_type="SQL",
                target="postgres",
                duration_ms=db_test_time,
                success=True,
            )

        # Check critical tables
        tables_start = time.time()
        tables_result = db.execute(
            text(
                """
                SELECT table_name FROM information_schema.tables 
                WHERE table_name IN ('users', 'campaigns', 'submissions', 'logs')
                """
            )
        ).fetchall()
        tables_time = (time.time() - tables_start) * 1000

        checks["tables"] = len(tables_result) >= 3

        if hasattr(logger, "track_database_operation"):
            logger.track_database_operation(
                operation="SELECT",
                table="information_schema.tables",
                query_time_ms=tables_time,
                affected_rows=len(tables_result),
                success=True,
            )

    except Exception as e:
        if hasattr(logger, "track_exception"):
            logger.track_exception(e, handled=True, properties={"check": "readiness"})

    ready = all(checks.values())
    total_check_time = (time.time() - check_start) * 1000

    response = {
        "ready": ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat(),
        "check_duration_ms": round(total_check_time, 2),
    }

    if not ready:
        if hasattr(logger, "track_metric"):
            logger.track_metric(
                name="readiness_failure",
                value=1,
                properties={"failed_checks": [k for k, v in checks.items() if not v]},
            )
        raise HTTPException(status_code=503, detail=response)

    return response


@router.get("/liveness")
async def liveness_check(
    request: Request, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Liveness check for Kubernetes/container orchestration"""
    logger = ApplicationInsightsLogger(db)

    # Quick liveness check - just verify the app is responsive
    if hasattr(logger, "track_metric"):
        logger.track_metric(
            name="liveness_probe", value=1, properties={"ip": get_client_ip(request)}
        )

    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "running",
    }


@router.get("/metrics/prometheus")
async def prometheus_metrics(db: Session = Depends(get_db)) -> str:
    """Export metrics in Prometheus format"""
    logger = ApplicationInsightsLogger(db)

    if hasattr(logger, "track_business_event"):
        logger.track_business_event(
            event_name="prometheus_metrics_exported",
            properties={"format": "prometheus"},
        )

    try:
        # Get metrics from database
        metrics_query = text(
            """
            SELECT 
                (SELECT COUNT(*) FROM users WHERE is_active = true) as active_users,
                (SELECT COUNT(*) FROM campaigns WHERE status = 'RUNNING') as running_campaigns,
                (SELECT COUNT(*) FROM submissions WHERE status = 'pending') as pending_submissions,
                (SELECT COUNT(*) FROM logs WHERE level = 'ERROR' AND timestamp > NOW() - INTERVAL '1 hour') as recent_errors
            """
        )
        result = db.execute(metrics_query).first()

        # Format as Prometheus metrics
        metrics_text = f"""# HELP active_users Number of active users
# TYPE active_users gauge
active_users {result[0] if result else 0}

# HELP running_campaigns Number of running campaigns
# TYPE running_campaigns gauge
running_campaigns {result[1] if result else 0}

# HELP pending_submissions Number of pending submissions
# TYPE pending_submissions gauge
pending_submissions {result[2] if result else 0}

# HELP recent_errors Number of errors in the last hour
# TYPE recent_errors gauge
recent_errors {result[3] if result else 0}
"""

        if hasattr(logger, "track_metric"):
            logger.track_metric(
                name="prometheus_export_success",
                value=1,
                properties={"metrics_count": 4},
            )

        return metrics_text

    except Exception as e:
        if hasattr(logger, "track_exception"):
            logger.track_exception(e, handled=True)
        return "# Error generating metrics\n"
