# app/schemas/admin.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class SystemStatus(BaseModel):
    """Schema for system status"""

    status: Literal["healthy", "degraded", "down"]
    uptime: float
    version: str
    environment: str
    database_status: str
    api_status: str
    redis_status: Optional[str] = None
    background_worker_status: Optional[str] = None
    active_users: int = 0
    total_campaigns: int = 0
    active_submissions: int = 0
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    last_check: datetime = Field(default_factory=datetime.utcnow)


class UserManagement(BaseModel):
    """Schema for user management operations"""

    user_id: str
    action: Literal[
        "activate",
        "deactivate",
        "promote",
        "demote",
        "delete",
        "reset_password",
        "verify",
        "unverify",
    ]
    reason: Optional[str] = Field(None, max_length=500)

    @validator("reason")
    def strip_reason(cls, v):
        if v:
            return v.strip()
        return v


class SystemSettings(BaseModel):
    """Schema for system settings management"""

    rate_limit_per_minute: Optional[int] = Field(None, ge=1, le=10000)
    max_concurrent_submissions: Optional[int] = Field(None, ge=1, le=100)
    submission_delay_seconds: Optional[int] = Field(None, ge=0, le=3600)
    debug_mode: Optional[bool] = None
    maintenance_mode: Optional[bool] = None
    new_user_registration: Optional[bool] = None
    captcha_service_enabled: Optional[bool] = None
    proxy_service_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None
    webhook_notifications: Optional[bool] = None


class AdminAction(BaseModel):
    """Schema for admin action logging"""

    action: str = Field(..., max_length=255)
    target_type: Literal["user", "campaign", "submission", "system", "website", "logs"]
    target_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    performed_by: str
    performed_at: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AdminResponse(BaseModel):
    """Schema for admin operation response"""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemMetrics(BaseModel):
    """Schema for system metrics"""

    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Optional[Dict[str, float]] = None
    database_connections: int = 0
    active_sessions: int = 0
    requests_per_minute: float = 0.0
    error_rate: float = 0.0
    response_time_avg: float = 0.0


class UserListResponse(BaseModel):
    """Schema for admin user list response"""

    users: List[Dict[str, Any]]
    total: int
    page: int = 1
    per_page: int = 20
    filters_applied: Optional[Dict[str, Any]] = None


class AdminUserFilter(BaseModel):
    """Schema for filtering users in admin panel"""

    active_only: Optional[bool] = None
    verified_only: Optional[bool] = None
    role: Optional[Literal["user", "admin", "owner"]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    email_search: Optional[str] = None
    has_campaigns: Optional[bool] = None
    has_submissions: Optional[bool] = None


class SystemLogEntry(BaseModel):
    """Schema for system log entries"""

    id: str
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    message: str
    timestamp: datetime
    user_id: Optional[str] = None
    action: Optional[str] = None
    details: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True


class AuditTrail(BaseModel):
    """Schema for audit trail entries"""

    action: str = Field(..., max_length=255)
    details: str = Field(..., max_length=2000)
    category: Literal[
        "user_management", "system_config", "data_management", "security", "maintenance"
    ] = "system_config"
    severity: Literal["low", "medium", "high", "critical"] = "medium"

    @validator("action", "details")
    def strip_strings(cls, v):
        if v:
            return v.strip()
        return v


class BulkUserAction(BaseModel):
    """Schema for bulk user actions"""

    user_ids: List[str] = Field(..., min_items=1, max_items=100)
    action: Literal["activate", "deactivate", "delete", "verify"]
    reason: Optional[str] = Field(None, max_length=500)

    @validator("user_ids")
    def validate_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Duplicate user IDs found")
        return v


class DatabaseMaintenance(BaseModel):
    """Schema for database maintenance operations"""

    operation: Literal[
        "cleanup_logs", "optimize_indexes", "vacuum", "analyze", "backup"
    ]
    table_name: Optional[str] = None
    days_to_keep: Optional[int] = Field(None, ge=1, le=365)
    dry_run: bool = True


class SystemBackup(BaseModel):
    """Schema for system backup operations"""

    backup_type: Literal["full", "incremental", "tables_only", "logs_only"]
    include_user_data: bool = True
    include_logs: bool = False
    compression: bool = True
    encryption: bool = False
