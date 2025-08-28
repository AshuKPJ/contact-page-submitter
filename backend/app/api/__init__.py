# Import all API routers
from . import auth
from . import users
from . import campaigns
from . import submissions
from . import analytics
from . import admin
from . import health

__all__ = ["auth", "users", "campaigns", "submissions", "analytics", "admin", "health"]
