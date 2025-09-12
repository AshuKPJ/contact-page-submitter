# app/schemas/analytics.py
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List, Literal, Union
from datetime import datetime, date


class SubmissionStats(BaseModel):
    """Schema for submission statistics"""

    total_submissions: int = 0
    successful_submissions: int = 0
    failed_submissions: int = 0
    pending_submissions: int = 0
    processing_submissions: int = 0
    success_rate: float = 0.0
    completion_rate: float = 0.0
    average_retry_count: float = 0.0
    captcha_encounter_rate: float = 0.0
    captcha_solve_rate: float = 0.0


class CampaignAnalytics(BaseModel):
    """Schema for campaign analytics"""

    campaign_id: str
    campaign_name: str
    status: str
    total_urls: int = 0
    submitted_count: int = 0
    failed_count: int = 0
    successful_count: int = 0
    processed_count: int = 0
    no_form_count: int = 0
    email_fallback_count: int = 0
    success_rate: float = 0.0
    completion_rate: float = 0.0
    captcha_encounters: int = 0
    captcha_solve_rate: float = 0.0
    average_processing_time: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


class UserAnalytics(BaseModel):
    """Schema for user analytics"""

    user_id: str
    email: str
    total_campaigns: int = 0
    active_campaigns: int = 0
    completed_campaigns: int = 0
    total_submissions: int = 0
    total_websites: int = 0
    submission_stats: SubmissionStats
    last_campaign_date: Optional[datetime] = None
    last_submission_date: Optional[datetime] = None
    account_age_days: int = 0
    average_campaign_size: float = 0.0


class SystemAnalytics(BaseModel):
    """Schema for system-wide analytics"""

    total_users: int = 0
    active_users: int = 0
    verified_users: int = 0
    total_campaigns: int = 0
    active_campaigns: int = 0
    running_campaigns: int = 0
    completed_campaigns: int = 0
    total_websites: int = 0
    total_submissions: int = 0
    submission_stats: SubmissionStats
    top_performing_campaigns: List[CampaignAnalytics] = []
    daily_activity: Optional[Dict[str, int]] = None
    resource_usage: Optional[Dict[str, float]] = None


class TimeSeriesData(BaseModel):
    """Schema for time series analytics data"""

    date: Union[date, datetime, str]
    value: Union[int, float]
    label: Optional[str] = None
    category: Optional[str] = None

    @validator("date")
    def validate_date(cls, v):
        if isinstance(v, str):
            try:
                # Try to parse ISO format
                return datetime.fromisoformat(v.replace("Z", "+00:00")).date()
            except ValueError:
                # Try date format
                return datetime.strptime(v, "%Y-%m-%d").date()
        elif isinstance(v, datetime):
            return v.date()
        return v


class DailyStats(BaseModel):
    """Schema for daily statistics"""

    days: int = 30
    series: List[TimeSeriesData] = []
    summary: Optional[Dict[str, Union[int, float]]] = None


class PerformanceAnalytics(BaseModel):
    """Schema for performance analytics"""

    campaigns: List[CampaignAnalytics] = []
    domain_statistics: List[Dict[str, Any]] = []
    metrics: Dict[str, Any] = {}
    trends: Optional[Dict[str, List[TimeSeriesData]]] = None
    benchmarks: Optional[Dict[str, float]] = None


class AnalyticsFilter(BaseModel):
    """Schema for analytics filtering"""

    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    user_id: Optional[str] = None
    campaign_id: Optional[str] = None
    status: Optional[Literal["pending", "processing", "success", "failed"]] = None
    include_inactive: bool = False
    group_by: Optional[
        Literal["day", "week", "month", "campaign", "user", "domain"]
    ] = None
    limit: Optional[int] = Field(None, ge=1, le=1000)


class CampaignComparisonAnalytics(BaseModel):
    """Schema for comparing multiple campaigns"""

    campaigns: List[CampaignAnalytics]
    comparison_metrics: Dict[str, Any]
    best_performing: Optional[CampaignAnalytics] = None
    worst_performing: Optional[CampaignAnalytics] = None
    average_metrics: Dict[str, float]


class DomainAnalytics(BaseModel):
    """Schema for domain-specific analytics"""

    domain: str
    total_attempts: int = 0
    successful_attempts: int = 0
    failed_attempts: int = 0
    success_rate: float = 0.0
    average_retry_count: float = 0.0
    captcha_encounter_rate: float = 0.0
    form_detection_rate: float = 0.0
    last_attempt: Optional[datetime] = None
    common_failure_reasons: List[Dict[str, Any]] = []


class ConversionFunnelAnalytics(BaseModel):
    """Schema for conversion funnel analytics"""

    stage_1_urls_loaded: int = 0
    stage_2_forms_detected: int = 0
    stage_3_forms_submitted: int = 0
    stage_4_successful_submissions: int = 0
    conversion_rates: Dict[str, float] = {}
    drop_off_points: List[Dict[str, Any]] = []


class CaptchaAnalytics(BaseModel):
    """Schema for captcha-specific analytics"""

    total_captchas_encountered: int = 0
    total_captchas_solved: int = 0
    solve_rate: float = 0.0
    average_solve_time: Optional[float] = None
    captcha_types: Dict[str, int] = {}
    difficulty_distribution: Dict[str, int] = {}
    cost_analysis: Optional[Dict[str, float]] = None


class UserEngagementAnalytics(BaseModel):
    """Schema for user engagement analytics"""

    daily_active_users: int = 0
    weekly_active_users: int = 0
    monthly_active_users: int = 0
    new_users: int = 0
    returning_users: int = 0
    user_retention_rate: float = 0.0
    average_session_duration: Optional[float] = None
    bounce_rate: float = 0.0


class RealtimeAnalytics(BaseModel):
    """Schema for real-time analytics"""

    active_campaigns: int = 0
    submissions_in_progress: int = 0
    submissions_last_hour: int = 0
    success_rate_last_hour: float = 0.0
    errors_last_hour: int = 0
    system_load: Optional[Dict[str, float]] = None
    active_users: int = 0


class AnalyticsExport(BaseModel):
    """Schema for exporting analytics data"""

    export_type: Literal["summary", "detailed", "raw_data", "charts"]
    format: Literal["csv", "xlsx", "json", "pdf"] = "csv"
    date_range: Optional[Dict[str, datetime]] = None
    filters: Optional[AnalyticsFilter] = None
    include_charts: bool = False
    include_raw_data: bool = False


class CustomAnalyticsQuery(BaseModel):
    """Schema for custom analytics queries"""

    query_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    metrics: List[str] = Field(..., min_items=1)
    dimensions: List[str] = []
    filters: Optional[Dict[str, Any]] = None
    date_range: Optional[Dict[str, datetime]] = None
    aggregation: Literal["sum", "avg", "count", "min", "max"] = "sum"
    group_by: Optional[str] = None


class AnalyticsDashboard(BaseModel):
    """Schema for analytics dashboard configuration"""

    dashboard_name: str = Field(..., max_length=255)
    user_id: str
    widgets: List[Dict[str, Any]] = []
    layout: Dict[str, Any] = {}
    refresh_interval: Optional[int] = Field(None, ge=30, le=3600)  # seconds
    is_public: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AnalyticsAlert(BaseModel):
    """Schema for analytics alerts and notifications"""

    alert_name: str = Field(..., max_length=255)
    metric: str
    condition: Literal["greater_than", "less_than", "equals", "not_equals"]
    threshold: float
    is_active: bool = True
    notification_channels: List[Literal["email", "webhook", "in_app"]] = []
    frequency: Literal["immediate", "hourly", "daily", "weekly"] = "immediate"
