# app/core/config.py

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App Configuration
    APP_NAME: str = Field(default="Contact Page Submitter API", env="APP_NAME")
    VERSION: str = Field(default="1.0.0", env="VERSION")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")  # Added from your .env
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")

    # Security Configuration
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    JWT_ALGORITHM: str = Field(
        default="HS256", env="JWT_ALGORITHM"
    )  # Added from your .env
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    JWT_EXPIRATION_HOURS: int = Field(
        default=24, env="JWT_EXPIRATION_HOURS"
    )  # Added from your .env

    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ],
        env="CORS_ORIGINS",
    )

    # Browser Configuration
    BROWSER_HEADLESS: bool = Field(default=True, env="BROWSER_HEADLESS")
    BROWSER_SLOW_MO: int = Field(default=100, env="BROWSER_SLOW_MO")

    # Captcha Configuration - Added from your .env
    CAPTCHA_ENCRYPTION_KEY: str = Field(default="", env="CAPTCHA_ENCRYPTION_KEY")
    CAPTCHA_DBC_API_URL: str = Field(
        default="http://api.dbcapi.me/api", env="CAPTCHA_DBC_API_URL"
    )
    CAPTCHA_SOLVE_TIMEOUT: int = Field(default=120, env="CAPTCHA_SOLVE_TIMEOUT")

    # Rate Limiting - Added from your .env
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    SUBMISSION_DELAY_SECONDS: int = Field(default=3, env="SUBMISSION_DELAY_SECONDS")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT"
    )
    LOG_FILE: str = Field(default="cps.log", env="LOG_FILE")  # Added from your .env

    # Redis Configuration (if needed)
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")

    # Email Configuration - Updated with your .env variables
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: Optional[int] = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_USER: str = Field(
        default="your-email@gmail.com", env="SMTP_USER"
    )  # Added from your .env
    SMTP_FROM_EMAIL: str = Field(
        default="noreply@cps-platform.com", env="SMTP_FROM_EMAIL"
    )  # Added from your .env

    # File Upload Configuration - Updated with your .env variables
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, env="MAX_FILE_SIZE")  # 10MB
    UPLOAD_DIRECTORY: str = Field(default="uploads", env="UPLOAD_DIRECTORY")
    MAX_CSV_SIZE_MB: int = Field(
        default=50, env="MAX_CSV_SIZE_MB"
    )  # Added from your .env
    ALLOWED_FILE_EXTENSIONS: str = Field(
        default=".csv,.txt", env="ALLOWED_FILE_EXTENSIONS"
    )  # Added from your .env
    UPLOAD_FOLDER: str = Field(
        default="./uploads", env="UPLOAD_FOLDER"
    )  # Added from your .env

    # Submission Configuration - Added from your .env
    MAX_CONCURRENT_SUBMISSIONS: int = Field(default=5, env="MAX_CONCURRENT_SUBMISSIONS")
    FORM_TIMEOUT_SECONDS: int = Field(default=30, env="FORM_TIMEOUT_SECONDS")
    EMAIL_EXTRACTION_TIMEOUT: int = Field(default=15, env="EMAIL_EXTRACTION_TIMEOUT")
    MAX_RETRIES_PER_URL: int = Field(default=2, env="MAX_RETRIES_PER_URL")
    MIN_DELAY_BETWEEN_REQUESTS: float = Field(
        default=1.5, env="MIN_DELAY_BETWEEN_REQUESTS"
    )
    MAX_DELAY_BETWEEN_REQUESTS: float = Field(
        default=5.0, env="MAX_DELAY_BETWEEN_REQUESTS"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow extra fields to prevent validation errors
        extra = "ignore"  # This will ignore any extra environment variables

    def validate_configuration(self):
        """Validate critical configuration settings"""
        errors = []

        if not self.SECRET_KEY:
            errors.append("SECRET_KEY is required")

        if not self.DATABASE_URL:
            errors.append("DATABASE_URL is required")

        if len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY should be at least 32 characters long")

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        print(
            f"[CONFIG] Configuration validated successfully for {self.ENVIRONMENT} environment"
        )
        print(f"[CONFIG] CORS origins: {self.CORS_ORIGINS}")
        print(f"[CONFIG] Database URL: {self.DATABASE_URL}")
        print(f"[CONFIG] Browser headless: {self.BROWSER_HEADLESS}")
        print(f"[CONFIG] Browser slow_mo: {self.BROWSER_SLOW_MO}ms")

        return True


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get settings instance (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.validate_configuration()
    return _settings


# IMPORTANT: For backward compatibility with existing imports
# This allows both patterns to work:
# - from app.core.config import settings
# - from app.core.config import get_settings
settings = get_settings()
