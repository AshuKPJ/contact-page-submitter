# app/api/activity.py - Updated with comprehensive logging
from __future__ import annotations

import time
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi.responses import StreamingResponse
import csv
import io
import datetime as dt

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_admin_user
from app.models.user import User

# FIXED: Import from existing log_service
from app.services.log_service import LogService as ApplicationInsightsLogger

router = APIRouter(prefix="/api/activity", tags=["activity"], redirect_slashes=False)


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


def _resolve_target_user_id(
    db: Session,
    current_user: User,
    user_id: Optional[str],
    logger: ApplicationInsightsLogger,
) -> str:
    target_user_id = str(current_user.id)
    if user_id and user_id != target_user_id:
        # Admin check
        get_admin_user(db=db, current_user=current_user)

        # Log admin viewing another user's activity
        logger.track_business_event(
            event_name="admin_view_user_activity",
            properties={
                "admin_id": str(current_user.id),
                "target_user_id": user_id,
                "admin_email": current_user.email,
            },
        )

        target_user_id = user_id
    return target_user_id


def _build_filters(
    target_user_id: str,
    *,
    source: Optional[str],
    level: Optional[str],
    action: Optional[str],
    status: Optional[str],
    q: Optional[str],
    date_from: Optional[str],
    date_to: Optional[str],
) -> tuple[str, Dict[str, Any]]:
    # Base WHERE clause for all subqueries
    where_parts = ["user_id = :uid"]
    params: Dict[str, Any] = {"uid": target_user_id}

    if date_from:
        where_parts.append("timestamp >= :date_from")
        params["date_from"] = date_from
    if date_to:
        where_parts.append("timestamp < :date_to")
        params["date_to"] = date_to
    if q:
        where_parts.append(
            "(COALESCE(message,'') ILIKE :q OR COALESCE(details,'') ILIKE :q)"
        )
        params["q"] = f"%{q}%"
    if action:
        where_parts.append("COALESCE(action,'') ILIKE :action")
        params["action"] = f"%{action}%"
    if status:
        where_parts.append("COALESCE(status,'') ILIKE :status")
        params["status"] = f"%{status}%"

    where_clause = " AND ".join(where_parts) if where_parts else "TRUE"

    # App-level filter for level
    app_level_filter = ""
    if level:
        app_level_filter = "AND level = :level"
        params["level"] = level

    # Build the unified query
    base_sql = f"""
        WITH merged AS (
            -- system logs
            SELECT
                'system'::text AS source,
                id::text       AS id,
                user_id::text  AS user_id,
                action         AS title,
                details        AS details,
                NULL::text     AS message,
                NULL::jsonb    AS context,
                NULL::text     AS target_url,
                action         AS action,
                NULL::text     AS status,
                timestamp      AS timestamp
            FROM system_logs
            WHERE {where_clause}

            UNION ALL

            -- app logs
            SELECT
                'app'::text    AS source,
                id::text       AS id,
                user_id::text  AS user_id,
                level          AS title,
                NULL::text     AS details,
                message        AS message,
                COALESCE(context, '{{}}'::jsonb) AS context,
                NULL::text     AS target_url,
                NULL::text     AS action,
                NULL::text     AS status,
                timestamp      AS timestamp
            FROM logs
            WHERE {where_clause}
            {app_level_filter}

            UNION ALL

            -- submission logs
            SELECT
                'submission'::text AS source,
                id::text           AS id,
                user_id::text      AS user_id,
                action             AS title,
                details            AS details,
                NULL::text         AS message,
                NULL::jsonb        AS context,
                COALESCE(target_url,'') AS target_url,
                action             AS action,
                COALESCE(status,'') AS status,
                timestamp          AS timestamp
            FROM submission_logs
            WHERE {where_clause}
        )
        SELECT * FROM merged
    """

    # Optional source filter
    if source in ("system", "app", "submission"):
        base_sql = f"SELECT * FROM ({base_sql}) AS x WHERE source = :source"
        params["source"] = source

    return base_sql, params


@router.get("/stream")
def activity_stream(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # scope
    me: bool = Query(True, description="Limit to my own activity"),
    user_id: Optional[str] = Query(
        None, description="Admin: view a specific user's activity"
    ),
    # filters
    source: Optional[str] = Query(None, pattern="^(system|app|submission)$"),
    level: Optional[str] = Query(None, pattern="^(INFO|WARN|ERROR)$"),
    action: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None, description="Full-text search over message/details"),
    # date range
    date_from: Optional[str] = Query(None, description="ISO timestamp (inclusive)"),
    date_to: Optional[str] = Query(None, description="ISO timestamp (exclusive)"),
    # pagination
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=200),
):
    """Get activity stream with filtering and pagination"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    # Track activity view
    logger.track_user_action(
        action="view_activity_stream",
        target="activity",
        properties={
            "filters": {
                "source": source,
                "level": level,
                "action": action,
                "status": status,
                "has_search": bool(q),
                "date_from": date_from,
                "date_to": date_to,
            },
            "pagination": {"page": page, "page_size": page_size},
            "ip": get_client_ip(request),
        },
    )

    try:
        target_user_id = (
            str(current_user.id)
            if me
            else _resolve_target_user_id(db, current_user, user_id, logger)
        )

        # Build and execute query
        query_start = time.time()
        base_sql, params = _build_filters(
            target_user_id,
            source=source,
            level=level,
            action=action,
            status=status,
            q=q,
            date_from=date_from,
            date_to=date_to,
        )

        # Count query
        count_sql = f"SELECT COUNT(*)::int FROM ({base_sql}) AS c"
        total = db.execute(text(count_sql), params).scalar() or 0

        # Page query
        page_sql = f"{base_sql} ORDER BY timestamp DESC LIMIT :limit OFFSET :offset"
        params.update({"limit": page_size, "offset": (page - 1) * page_size})
        rows = db.execute(text(page_sql), params).mappings().all()

        query_time = (time.time() - query_start) * 1000

        # Track database operation
        logger.track_database_operation(
            operation="SELECT",
            table="logs,system_logs,submission_logs",
            query_time_ms=query_time,
            affected_rows=len(rows),
            success=True,
            query="Activity stream query",
        )

        # Track metrics
        logger.track_metric(
            name="activity_stream_query_performance",
            value=query_time,
            properties={
                "result_count": len(rows),
                "total_count": total,
                "filters_applied": sum(
                    [
                        bool(source),
                        bool(level),
                        bool(action),
                        bool(status),
                        bool(q),
                        bool(date_from),
                        bool(date_to),
                    ]
                ),
            },
        )

        # Track business event
        logger.track_business_event(
            event_name="activity_stream_retrieved",
            properties={
                "user_id": str(current_user.id),
                "target_user_id": target_user_id,
                "is_admin_view": target_user_id != str(current_user.id),
                "filters_used": bool(source or level or action or status or q),
            },
            metrics={
                "query_time_ms": query_time,
                "results_returned": len(rows),
                "total_results": total,
                "page": page,
            },
        )

        return {
            "items": [dict(r) for r in rows],
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size,
        }

    except Exception as e:
        db.rollback()
        logger.track_exception(
            e,
            handled=True,
            properties={
                "endpoint": "/activity/stream",
                "filters": {"source": source, "level": level},
            },
        )

        raise HTTPException(
            status_code=500, detail=f"Failed to fetch activity: {str(e)}"
        )


@router.get("/export")
def export_activity_csv(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # scope
    me: bool = Query(True, description="Limit to my own activity"),
    user_id: Optional[str] = Query(
        None, description="Admin: view a specific user's activity"
    ),
    # filters (same as /stream)
    source: Optional[str] = Query(None, pattern="^(system|app|submission)$"),
    level: Optional[str] = Query(None, pattern="^(INFO|WARN|ERROR)$"),
    action: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    q: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Export activity to CSV file"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    # Track export request
    logger.track_user_action(
        action="export_activity_csv",
        target="activity",
        properties={
            "filters": {
                "source": source,
                "level": level,
                "action": action,
                "status": status,
                "has_search": bool(q),
                "date_from": date_from,
                "date_to": date_to,
            },
            "ip": get_client_ip(request),
        },
    )

    try:
        target_user_id = (
            str(current_user.id)
            if me
            else _resolve_target_user_id(db, current_user, user_id, logger)
        )

        # Build and execute export query
        export_start = time.time()
        base_sql, params = _build_filters(
            target_user_id,
            source=source,
            level=level,
            action=action,
            status=status,
            q=q,
            date_from=date_from,
            date_to=date_to,
        )
        export_sql = f"{base_sql} ORDER BY timestamp DESC"

        rows = db.execute(text(export_sql), params).mappings().all()
        export_query_time = (time.time() - export_start) * 1000

        logger.track_database_operation(
            operation="SELECT",
            table="logs,system_logs,submission_logs",
            query_time_ms=export_query_time,
            affected_rows=len(rows),
            success=True,
            query="Activity export query",
        )

        # Build CSV
        csv_start = time.time()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "source",
                "id",
                "user_id",
                "title",
                "message",
                "details",
                "action",
                "status",
                "target_url",
                "timestamp",
            ]
        )

        for r in rows:
            writer.writerow(
                [
                    r.get("source", ""),
                    r.get("id", ""),
                    r.get("user_id", ""),
                    r.get("title", ""),
                    r.get("message", ""),
                    r.get("details", ""),
                    r.get("action", ""),
                    r.get("status", ""),
                    r.get("target_url", ""),
                    r.get("timestamp", ""),
                ]
            )
        output.seek(0)
        csv_generation_time = (time.time() - csv_start) * 1000

        filename = f"activity_{dt.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}Z.csv"

        # Track export metrics
        logger.track_metric(
            name="activity_export_size",
            value=len(output.getvalue()),
            properties={"row_count": len(rows), "filename": filename},
        )

        # Track business event
        logger.track_business_event(
            event_name="activity_exported",
            properties={
                "user_id": str(current_user.id),
                "target_user_id": target_user_id,
                "export_format": "csv",
                "filename": filename,
            },
            metrics={
                "query_time_ms": export_query_time,
                "csv_generation_ms": csv_generation_time,
                "row_count": len(rows),
                "file_size_bytes": len(output.getvalue()),
            },
        )

        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        db.rollback()
        logger.track_exception(
            e,
            handled=True,
            properties={"endpoint": "/activity/export", "export_format": "csv"},
        )

        raise HTTPException(
            status_code=500, detail=f"Failed to export activity: {str(e)}"
        )


# Activity Stats endpoint
@router.get("/stats")
def activity_stats(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    # scope
    me: bool = Query(True, description="Limit to my own activity"),
    user_id: Optional[str] = Query(
        None, description="Admin: view a specific user's activity"
    ),
    # optional date window (ISO strings)
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
):
    """Get activity statistics"""
    logger = ApplicationInsightsLogger(db)
    logger.set_context(user_id=str(current_user.id))

    target_user_id = (
        str(current_user.id)
        if me
        else _resolve_target_user_id(db, current_user, user_id, logger)
    )

    logger.track_user_action(
        action="view_activity_stats",
        target="activity_stats",
        properties={
            "target_user_id": target_user_id,
            "date_from": date_from,
            "date_to": date_to,
            "ip": get_client_ip(request),
        },
    )

    try:
        # Build base where/time filter
        parts = ["user_id = :uid"]
        params: Dict[str, Any] = {"uid": target_user_id}
        if date_from:
            parts.append("timestamp >= :date_from")
            params["date_from"] = date_from
        if date_to:
            parts.append("timestamp < :date_to")
            params["date_to"] = date_to
        where = " AND ".join(parts)

        # Query stats by source
        stats_start = time.time()

        sql_by_source = f"""
          SELECT 'system' AS source, COUNT(*)::int AS cnt FROM system_logs WHERE {where}
          UNION ALL
          SELECT 'app' AS source, COUNT(*)::int AS cnt FROM logs WHERE {where}
          UNION ALL
          SELECT 'submission' AS source, COUNT(*)::int AS cnt FROM submission_logs WHERE {where}
        """

        sql_by_level = f"""
          SELECT COALESCE(level,'INFO') AS level, COUNT(*)::int AS cnt
          FROM logs
          WHERE {where}
          GROUP BY level
        """

        by_source = {
            r["source"]: r["cnt"]
            for r in db.execute(text(sql_by_source), params).mappings()
        }
        by_level = {
            r["level"]: r["cnt"]
            for r in db.execute(text(sql_by_level), params).mappings()
        }

        stats_time = (time.time() - stats_start) * 1000

        logger.track_database_operation(
            operation="AGGREGATE",
            table="logs,system_logs,submission_logs",
            query_time_ms=stats_time,
            success=True,
            query="Activity statistics aggregation",
        )

        stats_data = {
            "by_source": {
                "system": by_source.get("system", 0),
                "app": by_source.get("app", 0),
                "submission": by_source.get("submission", 0),
            },
            "by_level": {
                "INFO": by_level.get("INFO", 0),
                "WARN": by_level.get("WARN", 0),
                "ERROR": by_level.get("ERROR", 0),
            },
        }

        # Calculate totals
        total_logs = sum(stats_data["by_source"].values())
        error_rate = (
            (stats_data["by_level"]["ERROR"] / total_logs * 100)
            if total_logs > 0
            else 0
        )

        # Track metrics
        logger.track_metric(
            name="activity_stats_query_performance",
            value=stats_time,
            properties={"total_logs": total_logs},
        )

        logger.track_business_event(
            event_name="activity_stats_retrieved",
            properties={
                "user_id": str(current_user.id),
                "target_user_id": target_user_id,
                "date_range": {"from": date_from, "to": date_to},
            },
            metrics={
                "query_time_ms": stats_time,
                "total_logs": total_logs,
                "error_rate_percent": error_rate,
                "system_logs": stats_data["by_source"]["system"],
                "app_logs": stats_data["by_source"]["app"],
                "submission_logs": stats_data["by_source"]["submission"],
            },
        )

        return stats_data

    except Exception as e:
        db.rollback()
        logger.track_exception(e, handled=True)
        return {
            "by_source": {"system": 0, "app": 0, "submission": 0},
            "by_level": {"INFO": 0, "WARN": 0, "ERROR": 0},
        }
