from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import secrets
from functools import lru_cache
import os


class BrowserSettings(BaseSettings):
    """Browser automation settings"""

    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    page_load_timeout: int = 30000
    element_wait_timeout: int = 10000
    network_idle_timeout: int = 5000
    max_concurrent: int = Field(5, ge=1, le=10)
    restart_after: int = 100

    class Config:
        env_prefix = "BROWSER_"
        extra = "ignore"


class Settings(BaseSettings):
    """Main application settings"""

    # Core - Using uppercase to match main.py expectations
    APP_NAME: str = "Contact Page Submitter"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(
        "development", pattern="^(development|staging|production)$"
    )
    DEBUG: bool = False

    # Security - Using uppercase to match main.py expectations
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Database
    DATABASE_URL: str

    # CORS - Use alias to map from CORS_ORIGINS env var to cors_origins field
    cors_origins: str = Field(default="http://localhost:3000", alias="CORS_ORIGINS")

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    SUBMISSION_DELAY_SECONDS: int = Field(3, ge=1)
    MIN_DELAY_BETWEEN_REQUESTS: float = 1.5
    MAX_DELAY_BETWEEN_REQUESTS: float = 5.0

    # File Upload
    MAX_CSV_SIZE_MB: int = 50
    UPLOAD_FOLDER: str = "./uploads"

    # CAPTCHA Settings - Moved directly to main settings
    CAPTCHA_ENCRYPTION_KEY: str = Field(alias="CAPTCHA_ENCRYPTION_KEY")
    CAPTCHA_DBC_API_URL: str = "http://api.dbcapi.me/api"
    CAPTCHA_SOLVE_TIMEOUT: int = 120
    CAPTCHA_RETRY_ATTEMPTS: int = 3

    # Browser Settings
    browser: BrowserSettings = Field(default_factory=BrowserSettings)

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins as a list - uppercase for main.py compatibility"""
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    # Add lowercase properties for backwards compatibility
    @property
    def app_name(self) -> str:
        return self.APP_NAME

    @property
    def app_version(self) -> str:
        return self.APP_VERSION

    @property
    def secret_key(self) -> str:
        return self.SECRET_KEY

    @property
    def database_url(self) -> str:
        return self.DATABASE_URL

    @property
    def debug(self) -> bool:
        return self.DEBUG

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v, values):
        if values.get("ENVIRONMENT") == "production" and v == "change-me":
            raise ValueError("SECRET_KEY must be changed in production")
        return v

    @validator("CAPTCHA_ENCRYPTION_KEY")
    def validate_captcha_encryption_key(cls, v):
        if not v or v == "change-me":
            raise ValueError(
                "CAPTCHA_ENCRYPTION_KEY must be set in environment variables"
            )
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def validate_config(self):
        """Validate that all required configuration is present"""
        errors = []

        # Check required fields
        if not self.SECRET_KEY or self.SECRET_KEY == "change-me":
            errors.append("SECRET_KEY must be set and not be 'change-me'")

        if not self.DATABASE_URL:
            errors.append("DATABASE_URL must be set")

        if (
            not self.CAPTCHA_ENCRYPTION_KEY
            or self.CAPTCHA_ENCRYPTION_KEY == "change-me"
        ):
            errors.append("CAPTCHA_ENCRYPTION_KEY must be set and not be 'change-me'")

        # Validate environment
        if self.ENVIRONMENT not in ["development", "staging", "production"]:
            errors.append(
                "ENVIRONMENT must be one of: development, staging, production"
            )

        # Production-specific validations
        if self.ENVIRONMENT == "production":
            if self.DEBUG:
                errors.append("DEBUG should be False in production")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"- {error}" for error in errors
            )
            raise ValueError(error_msg)

        print(
            f"[CONFIG] Configuration validated successfully for {self.ENVIRONMENT} environment"
        )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
