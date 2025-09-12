from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import get_settings

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Ensures proper cleanup after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    # Import all models to ensure they are registered with Base
    from app.models import (
        User,
        Campaign,
        Submission,
        Website,
        UserProfile,
        SubscriptionPlan,
        Subscription,
        Settings,
        Log,
        SubmissionLog,
        CaptchaLog,
        SystemLog,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized with all tables")

    # Optional: Create default subscription plans if they don't exist
    db = SessionLocal()
    try:
        # Check if plans exist
        existing_plans = db.query(SubscriptionPlan).count()
        if existing_plans == 0:
            # Create default plans
            plans = [
                SubscriptionPlan(
                    name="Free",
                    description="Basic plan for getting started",
                    max_websites=10,
                    max_submissions_per_day=50,
                    price=0.00,
                    features={"basic_support": True, "captcha_solving": False},
                ),
                SubscriptionPlan(
                    name="Pro",
                    description="Professional plan for growing businesses",
                    max_websites=100,
                    max_submissions_per_day=500,
                    price=49.99,
                    features={
                        "priority_support": True,
                        "captcha_solving": True,
                        "proxy_support": True,
                    },
                ),
                SubscriptionPlan(
                    name="Enterprise",
                    description="Unlimited plan for large organizations",
                    max_websites=None,  # Unlimited
                    max_submissions_per_day=None,  # Unlimited
                    price=199.99,
                    features={
                        "dedicated_support": True,
                        "captcha_solving": True,
                        "proxy_support": True,
                        "api_access": True,
                    },
                ),
            ]
            for plan in plans:
                db.add(plan)
            db.commit()
            print("✅ Default subscription plans created")
    except Exception as e:
        print(f"⚠️ Could not create default plans: {e}")
        db.rollback()
    finally:
        db.close()
