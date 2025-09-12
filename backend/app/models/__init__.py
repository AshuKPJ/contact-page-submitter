# app/models/__init__.py
"""
Database models for Contact Page Submitter application.
Import all models here to ensure they are registered with SQLAlchemy Base.
"""

from app.models.user import User
from app.models.campaign import Campaign
from app.models.submission import Submission
from app.models.website import Website
from app.models.user_profile import UserProfile
from app.models.subscription import SubscriptionPlan, Subscription
from app.models.logs import Log, SubmissionLog, CaptchaLog, SystemLog
from app.models.settings import Settings

# Export all models for easy access
__all__ = [
    "User",
    "Campaign",
    "Submission",
    "Website",
    "UserProfile",
    "SubscriptionPlan",
    "Subscription",
    "Settings",
    "Log",
    "SubmissionLog",
    "CaptchaLog",
    "SystemLog",
]
