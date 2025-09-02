from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
import secrets
from functools import lru_cache
import os


class BrowserSettings(BaseSettings):
    """Browser automation settings"""

    headless: bool = True  # Set to False for debugging
    viewport_width: int = 1920
    viewport_height: int = 1080
    page_load_timeout: int = 30000
    element_wait_timeout: int = 10000
    network_idle_timeout: int = 5000
    max_concurrent: int = 1  # Process one at a time for stability
    slow_mo: int = 100  # Milliseconds between actions

    # Anti-detection settings
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    class Config:
        env_prefix = "BROWSER_"
        extra = "ignore"


class Settings(BaseSettings):
    """Main application settings"""

    # Core - Using uppercase to match main.py expectations
    APP_NAME: str = "CPS - Contact Page Submitter"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(
        "development", pattern="^(development|staging|production)$"
    )
    DEBUG: bool = True

    # Security - Using uppercase to match main.py expectations with defaults
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # Database with default for development
    DATABASE_URL: str = Field(default="sqlite:///./contact_submitter.db")

    # CORS - Fixed parsing
    cors_origins: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173"
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    SUBMISSION_DELAY_SECONDS: int = Field(3, ge=1)
    MIN_DELAY_BETWEEN_REQUESTS: float = 1.5
    MAX_DELAY_BETWEEN_REQUESTS: float = 5.0

    # File Upload
    MAX_CSV_SIZE_MB: int = 50
    UPLOAD_FOLDER: str = "./uploads"

    # CAPTCHA Settings - Provide default for development
    CAPTCHA_ENCRYPTION_KEY: str = Field(
        default_factory=lambda: secrets.token_urlsafe(32),
        alias="CAPTCHA_ENCRYPTION_KEY",
    )
    CAPTCHA_DBC_API_URL: str = "http://api.dbcapi.me/api"
    CAPTCHA_SOLVE_TIMEOUT: int = 120
    CAPTCHA_RETRY_ATTEMPTS: int = 3

    # Browser Settings
    browser: BrowserSettings = Field(default_factory=BrowserSettings)

    @property
    def CORS_ORIGINS(self) -> List[str]:
        """Get CORS origins as a list - uppercase for main.py compatibility"""
        origins = []
        if self.cors_origins:
            for origin in self.cors_origins.split(","):
                origin = origin.strip()
                if origin:  # Only add non-empty origins
                    origins.append(origin)

        # Always include localhost and 127.0.0.1 variants in development
        if self.ENVIRONMENT == "development":
            default_origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
            for origin in default_origins:
                if origin not in origins:
                    origins.append(origin)

        return origins

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
        if values.get("ENVIRONMENT") == "production" and (not v or len(v) < 32):
            raise ValueError("SECRET_KEY must be at least 32 characters in production")
        return v

    @validator("CAPTCHA_ENCRYPTION_KEY")
    def validate_captcha_encryption_key(cls, v, values):
        # Only enforce in production, allow defaults in development
        if values.get("ENVIRONMENT") == "production" and (not v or len(v) < 32):
            raise ValueError(
                "CAPTCHA_ENCRYPTION_KEY must be at least 32 characters in production"
            )
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    def validate_config(self):
        """Validate that all required configuration is present"""
        errors = []

        # Check required fields - more lenient for development
        if self.ENVIRONMENT == "production":
            if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                errors.append("SECRET_KEY must be at least 32 characters in production")

            if not self.CAPTCHA_ENCRYPTION_KEY or len(self.CAPTCHA_ENCRYPTION_KEY) < 32:
                errors.append(
                    "CAPTCHA_ENCRYPTION_KEY must be at least 32 characters in production"
                )

            if self.DEBUG:
                errors.append("DEBUG should be False in production")

        # Validate environment
        if self.ENVIRONMENT not in ["development", "staging", "production"]:
            errors.append(
                "ENVIRONMENT must be one of: development, staging, production"
            )

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"- {error}" for error in errors
            )
            raise ValueError(error_msg)

        print(
            f"[CONFIG] Configuration validated successfully for {self.ENVIRONMENT} environment"
        )
        print(f"[CONFIG] CORS origins: {self.CORS_ORIGINS}")
        print(f"[CONFIG] Database URL: {self.DATABASE_URL}")
        print(f"[CONFIG] Browser headless: {self.browser.headless}")
        print(f"[CONFIG] Browser slow_mo: {self.browser.slow_mo}ms")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    settings = Settings()
    # Validate on creation in development to catch issues early
    if settings.ENVIRONMENT == "development":
        try:
            settings.validate_config()
        except ValueError as e:
            print(f"[WARNING] Configuration issues detected: {e}")
    return settings


settings = get_settings()
