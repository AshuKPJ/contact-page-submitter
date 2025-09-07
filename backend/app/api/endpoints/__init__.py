# ============================================================================
# app/api/endpoints/__init__.py
# ============================================================================
"""
API Endpoints Package
Exports all routers for use in main application
"""

from .auth import router as auth_router
from .users import router as users_router
from .campaigns import router as campaigns_router
from .submissions import router as submissions_router
from .analytics import router as analytics_router
from .admin import router as admin_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "users_router",
    "campaigns_router",
    "submissions_router",
    "analytics_router",
    "admin_router",
    "health_router",
]
