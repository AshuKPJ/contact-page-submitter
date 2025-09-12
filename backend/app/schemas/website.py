# app/schemas/website.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime


class WebsiteCreate(BaseModel):
    """Schema for creating a website"""

    campaign_id: str
    domain: str = Field(..., max_length=255)
    contact_url: Optional[str] = None

    @validator("domain")
    def validate_domain(cls, v):
        if v:
            # Remove protocol if present
            v = v.replace("http://", "").replace("https://", "").replace("www.", "")
            # Remove trailing slash
            v = v.rstrip("/")
            return v.strip()
        return v

    @validator("contact_url")
    def validate_contact_url(cls, v):
        if v and not v.startswith(("http://", "https://")):
            return f"https://{v}"
        return v


class WebsiteUpdate(BaseModel):
    """Schema for updating a website"""

    domain: Optional[str] = Field(None, max_length=255)
    contact_url: Optional[str] = None
    form_detected: Optional[bool] = None
    form_type: Optional[str] = Field(None, max_length=100)
    form_labels: Optional[List[str]] = None
    form_field_count: Optional[int] = Field(None, ge=0)
    has_captcha: Optional[bool] = None
    captcha_type: Optional[str] = Field(None, max_length=100)
    form_name_variants: Optional[List[str]] = None
    status: Optional[
        Literal["pending", "processing", "completed", "failed", "skipped"]
    ] = None
    failure_reason: Optional[str] = None
    requires_proxy: Optional[bool] = None
    proxy_block_type: Optional[str] = None
    last_proxy_used: Optional[str] = None
    captcha_difficulty: Optional[Literal["easy", "medium", "hard", "very_hard"]] = None
    captcha_solution_time: Optional[int] = Field(None, ge=0)
    captcha_metadata: Optional[Dict[str, Any]] = None
    form_field_types: Optional[Dict[str, Any]] = None
    form_field_options: Optional[Dict[str, Any]] = None
    question_answer_fields: Optional[Dict[str, Any]] = None

    @validator("form_field_count")
    def validate_field_count(cls, v):
        if v is not None and v < 0:
            raise ValueError("Form field count cannot be negative")
        return v

    @validator("captcha_solution_time")
    def validate_solution_time(cls, v):
        if v is not None and v < 0:
            raise ValueError("Captcha solution time cannot be negative")
        return v


class WebsiteResponse(BaseModel):
    """Schema for website response"""

    id: str
    campaign_id: Optional[str] = None
    user_id: Optional[str] = None
    domain: Optional[str] = None
    contact_url: Optional[str] = None
    form_detected: Optional[bool] = False
    form_type: Optional[str] = None
    form_labels: Optional[List[str]] = None
    form_field_count: Optional[int] = None
    has_captcha: Optional[bool] = False
    captcha_type: Optional[str] = None
    form_name_variants: Optional[List[str]] = None
    status: Optional[str] = None
    failure_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: datetime
    requires_proxy: Optional[bool] = False
    proxy_block_type: Optional[str] = None
    last_proxy_used: Optional[str] = None
    captcha_difficulty: Optional[str] = None
    captcha_solution_time: Optional[int] = None
    captcha_metadata: Optional[Dict[str, Any]] = None
    form_field_types: Optional[Dict[str, Any]] = None
    form_field_options: Optional[Dict[str, Any]] = None
    question_answer_fields: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True


class WebsiteList(BaseModel):
    """Schema for paginated website list"""

    websites: List[WebsiteResponse]
    total: int
    page: int = 1
    per_page: int = 10


class WebsiteStats(BaseModel):
    """Schema for website statistics"""

    total_websites: int = 0
    with_forms_detected: int = 0
    with_captcha: int = 0
    successfully_processed: int = 0
    failed_processing: int = 0
    pending_processing: int = 0
    form_detection_rate: float = 0.0
    captcha_encounter_rate: float = 0.0
    success_rate: float = 0.0


class WebsiteFilter(BaseModel):
    """Schema for filtering websites"""

    campaign_id: Optional[str] = None
    status: Optional[
        Literal["pending", "processing", "completed", "failed", "skipped"]
    ] = None
    form_detected: Optional[bool] = None
    has_captcha: Optional[bool] = None
    requires_proxy: Optional[bool] = None
    domain_search: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class WebsiteAnalysis(BaseModel):
    """Schema for website analysis results"""

    website_id: str
    domain: str
    analysis_status: Literal["pending", "in_progress", "completed", "failed"]
    form_analysis: Optional[Dict[str, Any]] = None
    captcha_analysis: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    seo_info: Optional[Dict[str, Any]] = None
    technical_info: Optional[Dict[str, Any]] = None
    analyzed_at: Optional[datetime] = None
    analysis_duration_ms: Optional[int] = None


class WebsiteBulkUpdate(BaseModel):
    """Schema for bulk website updates"""

    website_ids: List[str] = Field(..., min_items=1, max_items=100)
    updates: WebsiteUpdate

    @validator("website_ids")
    def validate_ids(cls, v):
        if len(v) != len(set(v)):
            raise ValueError("Duplicate website IDs found")
        return v


class WebsiteImport(BaseModel):
    """Schema for importing websites"""

    campaign_id: str
    file_type: Literal["csv", "xlsx", "txt"] = "csv"
    domain_column: str = "domain"
    url_column: Optional[str] = "contact_url"
    skip_duplicates: bool = True
    validate_domains: bool = True


class WebsiteExport(BaseModel):
    """Schema for exporting websites"""

    format: Literal["csv", "xlsx", "json"] = "csv"
    filters: Optional[WebsiteFilter] = None
    fields: Optional[List[str]] = None
    include_analysis_data: bool = False
