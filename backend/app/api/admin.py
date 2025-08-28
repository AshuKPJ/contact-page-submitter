from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_admin_user
from app.models.user import User
from app.schemas.admin import SystemStatus, UserManagement, AdminResponse
from app.services.admin_service import AdminService

router = APIRouter()


@router.get("/system-status", response_model=SystemStatus)
async def get_system_status(
    admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)
):
    """Get system status (admin only)"""
    admin_service = AdminService(db)
    status = admin_service.get_system_status()
    return status


@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    active_only: bool = Query(False),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get all users (admin only)"""
    admin_service = AdminService(db)
    users, total = admin_service.get_all_users(page, per_page, active_only)
    return {"users": users, "total": total, "page": page, "per_page": per_page}


@router.post("/manage-user", response_model=AdminResponse)
async def manage_user(
    user_management: UserManagement,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Perform user management actions (admin only)"""
    admin_service = AdminService(db)
    result = admin_service.manage_user(admin_user.id, user_management)
    return result


@router.get("/metrics")
async def get_system_metrics(
    admin_user: User = Depends(get_admin_user), db: Session = Depends(get_db)
):
    """Get detailed system metrics (admin only)"""
    admin_service = AdminService(db)
    metrics = admin_service.get_system_metrics()
    return metrics


@router.get("/logs")
async def get_system_logs(
    limit: int = Query(50, ge=1, le=200),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """Get recent system logs (admin only)"""
    admin_service = AdminService(db)
    logs = admin_service.get_recent_system_logs(limit)
    return {"logs": logs}
