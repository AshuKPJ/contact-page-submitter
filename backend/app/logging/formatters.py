# app/logging/formatters.py
"""Custom formatters for structured logging"""
import json
import logging
from datetime import datetime
from typing import Dict, Any


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured JSON logs"""

    def format(self, record: logging.LogRecord) -> str:
        # Base log data
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields from record
        if hasattr(record, "__dict__"):
            for key, value in record.__dict__.items():
                if key not in log_data and not key.startswith("_"):
                    # Skip standard logging fields
                    if key not in [
                        "name",
                        "msg",
                        "args",
                        "levelname",
                        "levelno",
                        "pathname",
                        "filename",
                        "module",
                        "lineno",
                        "funcName",
                        "created",
                        "msecs",
                        "relativeCreated",
                        "thread",
                        "threadName",
                        "processName",
                        "process",
                        "exc_info",
                        "exc_text",
                        "stack_info",
                    ]:
                        log_data[key] = value

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str, separators=(",", ":"))


class DevelopmentFormatter(logging.Formatter):
    """Human-readable formatter for development"""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        # Add context info if available
        context_parts = []

        if hasattr(record, "request_id") and record.request_id:
            context_parts.append(f"req:{record.request_id[:8]}")

        if hasattr(record, "user_id") and record.user_id:
            context_parts.append(f"user:{record.user_id[:8]}")

        if hasattr(record, "campaign_id") and record.campaign_id:
            context_parts.append(f"campaign:{record.campaign_id[:8]}")

        base_message = super().format(record)

        if context_parts:
            return f"{base_message} [{' | '.join(context_parts)}]"

        return base_message
