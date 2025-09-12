"""
Services module for Contact Page Submitter application.
"""

# Import services with proper error handling
try:
    from .auth_service import AuthService
except ImportError as e:
    print(f"Warning: Could not import AuthService: {e}")
    AuthService = None

try:
    from .browser_automation_service import BrowserAutomationService
except ImportError as e:
    print(f"Warning: Could not import BrowserAutomationService: {e}")
    BrowserAutomationService = None

try:
    from .browser_service import BrowserService
except ImportError as e:
    print(f"Warning: Could not import BrowserService: {e}")
    BrowserService = None

try:
    from .campaign_service import CampaignService
except ImportError as e:
    print(f"Warning: Could not import CampaignService: {e}")
    CampaignService = None

try:
    from .captcha_service import CaptchaService
except ImportError as e:
    print(f"Warning: Could not import CaptchaService: {e}")
    CaptchaService = None

try:
    from .form_service import FormService
except ImportError as e:
    print(f"Warning: Could not import FormService: {e}")
    FormService = None

try:
    from .log_service import LogService
except ImportError as e:
    print(f"Warning: Could not import LogService: {e}")
    LogService = None

# Export all available services
__all__ = [
    "AuthService",
    "BrowserAutomationService",
    "BrowserService",
    "CampaignService",
    "CaptchaService",
    "FormService",
    "LogService",
]
