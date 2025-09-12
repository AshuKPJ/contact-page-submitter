# app/schemas/submission.py - Complete submission schemas matching database

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from enum import Enum


class SubmissionStatus(str, Enum):
    """Submission status enum matching database values"""

    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SubmissionBase(BaseModel):
    """Base submission schema"""

    url: str = Field(..., description="Target URL for submission")
    website_id: Optional[uuid.UUID] = Field(None, description="Associated website ID")
    campaign_id: Optional[uuid.UUID] = Field(None, description="Associated campaign ID")
    contact_method: Optional[str] = Field("form", description="Contact method used")
    status: Optional[str] = Field("pending", description="Submission status")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError("URL cannot be empty")
        return v.strip()

    class Config:
        from_attributes = True  # Pydantic v2 uses from_attributes instead of orm_mode
        use_enum_values = True


class SubmissionCreate(SubmissionBase):
    """Schema for creating a submission"""

    pass


class SubmissionUpdate(BaseModel):
    """Schema for updating a submission"""

    url: Optional[str] = None
    status: Optional[str] = None
    contact_method: Optional[str] = None
    error_message: Optional[str] = None
    email_extracted: Optional[str] = None
    success: Optional[bool] = None
    retry_count: Optional[int] = None
    response_status: Optional[int] = None
    captcha_encountered: Optional[bool] = None
    captcha_solved: Optional[bool] = None
    form_fields_sent: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class SubmissionResponse(BaseModel):
    """Schema for submission response - matches database fields"""

    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    campaign_id: Optional[uuid.UUID]
    website_id: Optional[uuid.UUID]
    url: Optional[str]
    status: str
    contact_method: Optional[str]
    email_extracted: Optional[str]
    error_message: Optional[str]
    success: Optional[bool]
    retry_count: Optional[int] = 0
    response_status: Optional[int]
    form_fields_sent: Optional[Dict[str, Any]]
    captcha_encountered: Optional[bool]
    captcha_solved: Optional[bool]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            uuid.UUID: lambda v: str(v) if v else None,
        }


class SubmissionBulkCreate(BaseModel):
    """Schema for bulk submission creation"""

    campaign_id: str = Field(..., description="Campaign ID for bulk submissions")
    urls: List[str] = Field(..., description="List of URLs to submit")

    @field_validator("urls")
    @classmethod
    def validate_urls(cls, v):
        if not v:
            raise ValueError("At least one URL is required")
        if len(v) > 1000:
            raise ValueError("Maximum 1000 URLs allowed per bulk operation")
        return v

    class Config:
        json_schema_extra = (
            {  # Pydantic v2 uses json_schema_extra instead of schema_extra
                "example": {
                    "campaign_id": "123e4567-e89b-12d3-a456-426614174000",
                    "urls": [
                        "https://example.com/contact",
                        "https://another-site.com/contact-us",
                        "https://third-site.com/get-in-touch",
                    ],
                }
            }
        )


class SubmissionStatistics(BaseModel):
    """Schema for submission statistics"""

    total: int = Field(0, description="Total number of submissions")
    successful: int = Field(0, description="Number of successful submissions")
    failed: int = Field(0, description="Number of failed submissions")
    pending: int = Field(0, description="Number of pending submissions")
    processing: int = Field(0, description="Number of processing submissions")
    success_rate: float = Field(0.0, description="Success rate percentage")
    email_fallback: int = Field(0, description="Number of email fallback submissions")
    avg_processing_time: float = Field(
        0.0, description="Average processing time in seconds"
    )
    retries_used: int = Field(0, description="Number of submissions that used retries")
    daily_average: Optional[float] = Field(
        None, description="Daily average submissions"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "successful": 120,
                "failed": 20,
                "pending": 10,
                "processing": 0,
                "success_rate": 85.7,
                "email_fallback": 15,
                "avg_processing_time": 3.5,
                "retries_used": 5,
                "daily_average": 21.4,
            }
        }


class SubmissionExportRequest(BaseModel):
    """Schema for submission export request"""

    format: str = Field(
        "csv", pattern="^(csv|json|excel)$", description="Export format"
    )
    campaign_id: Optional[str] = Field(None, description="Filter by campaign ID")
    status: Optional[str] = Field(None, description="Filter by status")
    date_from: Optional[datetime] = Field(None, description="Start date filter")
    date_to: Optional[datetime] = Field(None, description="End date filter")


class SubmissionExportResponse(BaseModel):
    """Schema for submission export response"""

    data: List[Dict[str, Any]]
    total_records: int
    format: str
    exported_at: str

    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "url": "https://example.com",
                        "status": "success",
                        "created_at": "2024-01-15T10:30:00Z",
                    }
                ],
                "total_records": 1,
                "format": "csv",
                "exported_at": "2024-01-15T12:00:00Z",
            }
        }


class SubmissionListResponse(BaseModel):
    """Schema for paginated submission list response"""

    submissions: List[SubmissionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    class Config:
        json_schema_extra = {
            "example": {
                "submissions": [],
                "total": 100,
                "page": 1,
                "per_page": 10,
                "total_pages": 10,
            }
        }


class SubmissionRetryRequest(BaseModel):
    """Schema for retry failed submissions request"""

    max_retries: int = Field(
        3, ge=1, le=10, description="Maximum number of retry attempts"
    )

    class Config:
        json_schema_extra = {"example": {"max_retries": 3}}


class SubmissionRetryResponse(BaseModel):
    """Schema for retry operation response"""

    retried_count: int
    skipped_count: int
    total_failed: int
    message: str

    class Config:
        json_schema_extra = {
            "example": {
                "retried_count": 5,
                "skipped_count": 2,
                "total_failed": 7,
                "message": "Retried 5 failed submissions",
            }
        }


class SubmissionLogEntry(BaseModel):
    """Schema for submission log entry - matches submission_logs table"""

    id: uuid.UUID
    submission_id: Optional[uuid.UUID]
    campaign_id: uuid.UUID
    user_id: Optional[uuid.UUID]
    website_id: Optional[uuid.UUID]
    target_url: str
    action: Optional[str]
    details: Optional[str]
    status: Optional[str]
    timestamp: Optional[datetime]
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            uuid.UUID: lambda v: str(v) if v else None,
        }


class SubmissionFilter(BaseModel):
    """Schema for filtering submissions"""

    status: Optional[str] = None
    campaign_id: Optional[str] = None
    website_id: Optional[str] = None
    search: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    success: Optional[bool] = None
    has_error: Optional[bool] = None
    captcha_encountered: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "campaign_id": "123e4567-e89b-12d3-a456-426614174000",
                "date_from": "2024-01-01T00:00:00Z",
                "date_to": "2024-01-31T23:59:59Z",
            }
        }


class SubmissionSummary(BaseModel):
    """Schema for submission summary"""

    id: uuid.UUID
    url: str
    status: str
    success: Optional[bool]
    created_at: datetime
    processed_at: Optional[datetime]
    error_message: Optional[str]

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            uuid.UUID: lambda v: str(v) if v else None,
        }


# Aliases for backward compatibility
SubmissionList = SubmissionListResponse


# Export all schemas
__all__ = [
    "SubmissionStatus",
    "SubmissionBase",
    "SubmissionCreate",
    "SubmissionUpdate",
    "SubmissionResponse",
    "SubmissionBulkCreate",
    "SubmissionStatistics",
    "SubmissionExportRequest",
    "SubmissionExportResponse",
    "SubmissionListResponse",
    "SubmissionList",  # Alias
    "SubmissionRetryRequest",
    "SubmissionRetryResponse",
    "SubmissionLogEntry",
    "SubmissionFilter",
    "SubmissionSummary",
]
