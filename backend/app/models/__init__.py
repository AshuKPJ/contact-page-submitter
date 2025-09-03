# backend/app/models/__init__.py

# Simple fix: Import only from files that exist and avoid duplicates

# Core models
from .user_profile import UserContactProfile, UserProfile
from .user import User, UserRole

# Choose ONE source for SubscriptionPlan - use standalone file
from .subscription_plan import SubscriptionPlan

# Other models
from .website import Website
from .campaign import Campaign, CampaignStatus
from .submission import Submission, SubmissionStatus
from .submission_log import (
    SubmissionLog,
)  # Make sure Log class is deleted from this file
from .captcha_log import CaptchaLog

# Use your existing combined settings and logs file
from .settings_and_logs import SystemLog, Settings, Log

# Import Subscription class (separate from SubscriptionPlan)
try:
    from .subscription import Subscription

    HAS_SUBSCRIPTION = True
except ImportError:
    HAS_SUBSCRIPTION = False

# Export models
__all__ = [
    "User",
    "UserRole",
    "UserProfile",
    "UserContactProfile",
    "Campaign",
    "CampaignStatus",
    "Submission",
    "SubmissionLog",
    "SubmissionStatus",
    "CaptchaLog",
    "Log",
    "SystemLog",
    "Settings",
    "Website",
    "SubscriptionPlan",
]

# Add Subscription to exports if it exists
if HAS_SUBSCRIPTION:
    __all__.append("Subscription")
