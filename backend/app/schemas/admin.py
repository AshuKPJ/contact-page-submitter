from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class SystemStatus(BaseModel):
    """Schema for system status"""

    status: Literal["healthy", "degraded", "down"]
    uptime: float
    version: str
    environment: str
    database_status: str
    redis_status: Optional[str] = None


class UserManagement(BaseModel):
    """Schema for user management operations"""

    user_id: str
    action: Literal["activate", "deactivate", "promote", "demote", "delete"]
    reason: Optional[str] = None


class SystemSettings(BaseModel):
    """Schema for system settings management"""

    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=1000)
    max_concurrent_submissions: Optional[int] = Field(None, ge=1, le=50)
    submission_delay_seconds: Optional[int] = Field(None, ge=1, le=300)
    debug_mode: Optional[bool] = None


class AdminAction(BaseModel):
    """Schema for admin action logging"""

    action: str
    target_type: Literal["user", "campaign", "submission", "system"]
    target_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    performed_by: str
    performed_at: datetime = Field(default_factory=datetime.utcnow)


class AdminResponse(BaseModel):
    """Schema for admin operation response"""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
