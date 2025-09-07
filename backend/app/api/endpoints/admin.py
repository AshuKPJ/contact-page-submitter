# ============================================================================
# app/api/endpoints/admin.py - FIXED
# ============================================================================
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/system-status")
async def get_system_status(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get system status (admin only)"""
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Test database
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except:
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "uptime": 0,
        "version": "1.0.0",
        "environment": "production",
        "database_status": db_status,
        "redis_status": None,
    }


@router.get("/users")
async def get_all_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all users (admin only)"""
    if current_user.role not in ["admin", "owner"]:
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        offset = (page - 1) * per_page
        users = db.query(User).offset(offset).limit(per_page).all()
        total = db.query(User).count()

        user_list = []
        for u in users:
            user_list.append(
                {
                    "id": str(u.id),
                    "email": u.email,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "role": u.role,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None,
                }
            )

        return {"users": user_list, "total": total, "page": page, "per_page": per_page}
    except Exception as e:
        print(f"[ADMIN ERROR] Failed to get users: {str(e)}")
        return {"users": [], "total": 0, "page": page, "per_page": per_page}
