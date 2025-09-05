# app/models/__init__.py

# Core models
from .user_profile import UserProfile  # both exist
from .user import User, UserRole
from .subscription_plan import SubscriptionPlan
from .website import Website
from .submission import Submission, SubmissionStatus
from .submission_log import SubmissionLog
from .settings_and_logs import SystemLog, Settings, Log

# Optional modules: import only if present
try:
    from .campaign import Campaign, CampaignStatus  # keep if you have campaign.py

    HAS_CAMPAIGN = True
except Exception:
    HAS_CAMPAIGN = False

try:
    from .captcha_log import CaptchaLog  # keep if you have captcha_log.py

    HAS_CAPTCHA_LOG = True
except Exception:
    HAS_CAPTCHA_LOG = False

try:
    from .subscription import Subscription  # exists in your tree

    HAS_SUBSCRIPTION = True
except Exception:
    HAS_SUBSCRIPTION = False

__all__ = [
    "User",
    "UserRole",
    "UserProfile",
    "Submission",
    "SubmissionStatus",
    "SubmissionLog",
    "SystemLog",
    "Settings",
    "Log",
    "Website",
    "SubscriptionPlan",
]

if HAS_SUBSCRIPTION:
    __all__.append("Subscription")
if HAS_CAMPAIGN:
    __all__ += ["Campaign", "CampaignStatus"]
if HAS_CAPTCHA_LOG:
    __all__.append("CaptchaLog")
