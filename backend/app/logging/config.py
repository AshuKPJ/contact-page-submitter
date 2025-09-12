# app/logging/config.py
"""Logging configuration - simplified without Pydantic dependency"""
import os
from enum import Enum
from typing import Dict, Any, Optional


class LogLevel(str, Enum):
    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class LoggingConfig:
    """Configuration for logging system"""

    def __init__(self, **kwargs):
        # Default values
        self.level: LogLevel = LogLevel.INFO
        self.format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Console logging
        self.console_enabled: bool = True
        self.console_level: LogLevel = LogLevel.INFO

        # Database logging
        self.database_enabled: bool = True
        self.database_level: LogLevel = LogLevel.INFO
        self.database_batch_size: int = 50
        self.database_flush_interval: int = 5  # seconds

        # Buffer settings
        self.buffer_enabled: bool = True
        self.buffer_size: int = 1000
        self.buffer_level: LogLevel = LogLevel.DEBUG

        # Performance settings
        self.async_logging: bool = True
        self.rate_limit_enabled: bool = True
        self.rate_limit_burst: int = 100
        self.rate_limit_rate: float = 10.0  # events per second

        # Development settings
        self.development_mode: bool = False
        self.request_logging: bool = True

        # Load from environment variables with LOG_ prefix
        self._load_from_env()

        # Override with any provided kwargs
        for key, value in kwargs.items():
            if hasattr(self, key):
                # Convert string values to appropriate types
                if key.endswith("_enabled") or key in [
                    "development_mode",
                    "request_logging",
                    "async_logging",
                    "rate_limit_enabled",
                ]:
                    value = str(value).lower() in ("true", "1", "yes", "on")
                elif key in [
                    "database_batch_size",
                    "database_flush_interval",
                    "buffer_size",
                    "rate_limit_burst",
                ]:
                    value = int(value) if isinstance(value, str) else value
                elif key in ["rate_limit_rate"]:
                    value = float(value) if isinstance(value, str) else value
                elif key in [
                    "level",
                    "console_level",
                    "database_level",
                    "buffer_level",
                ]:
                    if isinstance(value, str):
                        value = LogLevel(value.upper())

                setattr(self, key, value)

    def _load_from_env(self):
        """Load configuration from environment variables with LOG_ prefix"""
        env_mappings = {
            "LOG_LEVEL": ("level", lambda x: LogLevel(x.upper())),
            "LOG_FORMAT": ("format", str),
            "LOG_CONSOLE_ENABLED": (
                "console_enabled",
                lambda x: x.lower() in ("true", "1", "yes", "on"),
            ),
            "LOG_CONSOLE_LEVEL": ("console_level", lambda x: LogLevel(x.upper())),
            "LOG_DATABASE_ENABLED": (
                "database_enabled",
                lambda x: x.lower() in ("true", "1", "yes", "on"),
            ),
            "LOG_DATABASE_LEVEL": ("database_level", lambda x: LogLevel(x.upper())),
            "LOG_DATABASE_BATCH_SIZE": ("database_batch_size", int),
            "LOG_DATABASE_FLUSH_INTERVAL": ("database_flush_interval", int),
            "LOG_BUFFER_ENABLED": (
                "buffer_enabled",
                lambda x: x.lower() in ("true", "1", "yes", "on"),
            ),
            "LOG_BUFFER_SIZE": ("buffer_size", int),
            "LOG_BUFFER_LEVEL": ("buffer_level", lambda x: LogLevel(x.upper())),
            "LOG_ASYNC_LOGGING": (
                "async_logging",
                lambda x: x.lower() in ("true", "1", "yes", "on"),
            ),
            "LOG_RATE_LIMIT_ENABLED": (
                "rate_limit_enabled",
                lambda x: x.lower() in ("true", "1", "yes", "on"),
            ),
            "LOG_RATE_LIMIT_BURST": ("rate_limit_burst", int),
            "LOG_RATE_LIMIT_RATE": ("rate_limit_rate", float),
            "LOG_DEVELOPMENT_MODE": (
                "development_mode",
                lambda x: x.lower() in ("true", "1", "yes", "on"),
            ),
            "LOG_REQUEST_LOGGING": (
                "request_logging",
                lambda x: x.lower() in ("true", "1", "yes", "on"),
            ),
        }

        for env_key, (attr_name, converter) in env_mappings.items():
            if env_key in os.environ:
                try:
                    value = converter(os.environ[env_key])
                    setattr(self, attr_name, value)
                except (ValueError, TypeError) as e:
                    print(
                        f"Warning: Invalid value for {env_key}: {os.environ[env_key]}. Using default."
                    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            key: value.value if isinstance(value, LogLevel) else value
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    def __repr__(self) -> str:
        items = [f"{k}={v}" for k, v in self.to_dict().items()]
        return f"LoggingConfig({', '.join(items)})"
