# Essential schemas based on actual database structure
from .auth import UserLogin, UserRegister, UserResponse, AuthResponse
from .campaign import CampaignCreate, CampaignUpdate, CampaignResponse, CampaignList
from .submission import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionResponse,
    SubmissionList,
)
from .website import WebsiteCreate, WebsiteUpdate, WebsiteResponse
from .user import UserProfileCreate, UserContactProfileCreate, UserProfileResponse
from .analytics import (
    SubmissionStats,
    CampaignAnalytics,
    UserAnalytics,
    SystemAnalytics,
)

__all__ = [
    # Auth schemas (required by app.api.auth)
    "UserLogin",
    "UserRegister",
    "UserResponse",
    "AuthResponse",
    # Campaign schemas
    "CampaignCreate",
    "CampaignUpdate",
    "CampaignResponse",
    "CampaignList",
    # Submission schemas
    "SubmissionCreate",
    "SubmissionUpdate",
    "SubmissionResponse",
    "SubmissionList",
    # Website schemas
    "WebsiteCreate",
    "WebsiteUpdate",
    "WebsiteResponse",
    # User profile schemas
    "UserProfileCreate",
    "UserContactProfileCreate",
    "UserProfileResponse",
    # Analytics schemas
    "SubmissionStats",
    "CampaignAnalytics",
    "UserAnalytics",
    "SystemAnalytics",
]
