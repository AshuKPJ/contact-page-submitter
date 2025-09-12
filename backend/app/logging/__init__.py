# app/logging/__init__.py
"""
Unified logging system for the application.
Provides structured logging with multiple backends and performance optimization.
"""

from .core import (
    AppLogger,
    get_logger,
    configure_logging,
    request_id_var,
    user_id_var,
    campaign_id_var,
)
from .middleware import LoggingMiddleware
from .config import LoggingConfig, LogLevel
from .formatters import StructuredFormatter, DevelopmentFormatter
from .handlers import DatabaseHandler, BufferHandler
from .decorators import log_function, log_exceptions

__all__ = [
    "AppLogger",
    "get_logger",
    "configure_logging",
    "LoggingMiddleware",
    "LoggingConfig",
    "LogLevel",
    "StructuredFormatter",
    "DevelopmentFormatter",
    "DatabaseHandler",
    "BufferHandler",
    "log_function",
    "log_exceptions",
    "request_id_var",
    "user_id_var",
    "campaign_id_var",
]
