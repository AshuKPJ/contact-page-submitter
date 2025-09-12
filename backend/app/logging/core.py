# app/logging/core.py
"""Core logging functionality"""
import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
from contextvars import ContextVar
from dataclasses import dataclass, asdict

from .config import LoggingConfig
from .formatters import StructuredFormatter, DevelopmentFormatter
from .handlers import DatabaseHandler, BufferHandler
from .rate_limiter import RateLimiter


# Context variables for request tracking
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)
user_id_var: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
campaign_id_var: ContextVar[Optional[str]] = ContextVar("campaign_id", default=None)


@dataclass
class LogContext:
    """Enhanced context for log entries"""

    request_id: Optional[str] = None
    user_id: Optional[str] = None
    campaign_id: Optional[str] = None
    organization_id: Optional[str] = None
    website_id: Optional[str] = None
    session_id: Optional[str] = None
    correlation_id: Optional[str] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


class AppLogger:
    """
    Enhanced application logger with structured logging and multiple backends
    """

    def __init__(self, name: str, config: Optional[LoggingConfig] = None):
        self.name = name
        self.config = config or LoggingConfig()
        self._logger = logging.getLogger(name)
        self._setup_logger()

        # Rate limiting
        if self.config.rate_limit_enabled:
            self.rate_limiter = RateLimiter(
                burst=self.config.rate_limit_burst, rate=self.config.rate_limit_rate
            )
        else:
            self.rate_limiter = None

    def _setup_logger(self):
        """Setup the underlying Python logger"""
        self._logger.setLevel(self.config.level.value)
        self._logger.handlers.clear()

        # Console handler
        if self.config.console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.config.console_level.value)

            if self.config.development_mode:
                console_handler.setFormatter(DevelopmentFormatter())
            else:
                console_handler.setFormatter(StructuredFormatter())

            self._logger.addHandler(console_handler)

        # Database handler
        if self.config.database_enabled:
            db_handler = DatabaseHandler(
                level=self.config.database_level.value,
                batch_size=self.config.database_batch_size,
                flush_interval=self.config.database_flush_interval,
            )
            self._logger.addHandler(db_handler)

        # Buffer handler
        if self.config.buffer_enabled:
            buffer_handler = BufferHandler(
                buffer_size=self.config.buffer_size,
                level=self.config.buffer_level.value,
            )
            self._logger.addHandler(buffer_handler)

    def _should_log(self, level: str) -> bool:
        """Check if we should log based on rate limiting"""
        if not self.rate_limiter:
            return True
        return self.rate_limiter.allow(f"{self.name}:{level}")

    def _build_extra(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Build extra fields for log record"""
        extra = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "logger_name": self.name,
            "request_id": request_id_var.get(),
            "user_id": user_id_var.get(),
            "campaign_id": campaign_id_var.get(),
        }

        if context:
            extra.update(context)

        return {k: v for k, v in extra.items() if v is not None}

    def _log(
        self,
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        """Internal logging method"""
        if not self._should_log(level):
            return

        extra = self._build_extra(context)
        extra.update(kwargs)

        self._logger.log(getattr(logging, level.upper()), message, extra=extra)

    # Public API
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log("DEBUG", message, context, **kwargs)

    def info(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log("INFO", message, context, **kwargs)

    def warning(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log("WARNING", message, context, **kwargs)

    def error(self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs):
        self._log("ERROR", message, context, **kwargs)

    def critical(
        self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ):
        self._log("CRITICAL", message, context, **kwargs)

    # Domain-specific logging methods
    def auth_event(
        self,
        action: str,
        email: str,
        success: bool,
        ip_address: Optional[str] = None,
        **kwargs,
    ):
        """Log authentication events"""
        context = {
            "event_type": "authentication",
            "action": action,
            "email": email,
            "success": success,
            "ip_address": ip_address,
        }
        context.update(kwargs)

        level = "INFO" if success else "WARNING"
        message = f"Auth {action}: {email} - {'SUCCESS' if success else 'FAILED'}"
        self._log(level, message, context)

    def campaign_event(self, action: str, campaign_id: str, **kwargs):
        """Log campaign-related events"""
        context = {
            "event_type": "campaign",
            "action": action,
            "campaign_id": campaign_id,
        }
        context.update(kwargs)

        message = f"Campaign {action}: {campaign_id}"
        self.info(message, context)

    def submission_event(
        self, action: str, submission_id: str, url: str, status: str, **kwargs
    ):
        """Log submission events"""
        context = {
            "event_type": "submission",
            "action": action,
            "submission_id": submission_id,
            "url": url,
            "status": status,
        }
        context.update(kwargs)

        message = f"Submission {action}: {submission_id} - {status}"
        self.info(message, context)

    def performance_metric(self, name: str, value: float, unit: str = "ms", **kwargs):
        """Log performance metrics"""
        context = {
            "event_type": "metric",
            "metric_name": name,
            "metric_value": value,
            "metric_unit": unit,
        }
        context.update(kwargs)

        message = f"Metric {name}: {value}{unit}"
        self.info(message, context)

    def database_operation(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        affected_rows: int = 0,
        success: bool = True,
        **kwargs,
    ):
        """Log database operations"""
        context = {
            "event_type": "database",
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms,
            "affected_rows": affected_rows,
            "success": success,
        }
        context.update(kwargs)

        level = "INFO" if success else "ERROR"
        message = (
            f"DB {operation} on {table}: {duration_ms:.2f}ms, {affected_rows} rows"
        )
        self._log(level, message, context)

    def exception(self, exc: Exception, handled: bool = True, **kwargs):
        """Log exceptions with context"""
        context = {
            "event_type": "exception",
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "handled": handled,
        }
        context.update(kwargs)

        message = f"Exception: {type(exc).__name__}: {str(exc)}"
        self.error(message, context, exc_info=exc if not handled else None)


# Global logger registry
_loggers: Dict[str, AppLogger] = {}
_default_config: Optional[LoggingConfig] = None


def configure_logging(config: LoggingConfig):
    """Configure global logging settings"""
    global _default_config
    _default_config = config


def get_logger(name: str, config: Optional[LoggingConfig] = None) -> AppLogger:
    """Get or create a logger instance"""
    if name not in _loggers:
        effective_config = config or _default_config or LoggingConfig()
        _loggers[name] = AppLogger(name, effective_config)
    return _loggers[name]
