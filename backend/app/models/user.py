# backend/app/models/user.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    UUID,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import Base


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )  # UUID to match database
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # UUID foreign key to match database
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"))

    subscription_status = Column(String)
    subscription_start = Column(DateTime)
    subscription_end = Column(DateTime)
    profile_image_url = Column(String)
    captcha_username = Column(String)
    captcha_password_hash = Column(String)

    # Relationships - Add all missing relationships that other models expect
    user_profile = relationship("UserProfile", back_populates="user", uselist=False)
    subscription_plan = relationship("SubscriptionPlan", back_populates="users")
    subscription = relationship("Subscription", back_populates="user", uselist=False)

    # Add relationships that other models reference
    campaigns = relationship("Campaign", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    websites = relationship("Website", back_populates="user")
    submission_logs = relationship("SubmissionLog", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")
    settings = relationship("Settings", back_populates="user")
    logs = relationship("Log", back_populates="user")
