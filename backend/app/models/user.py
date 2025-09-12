# ============================================
# FILE: app/models/user.py
# ============================================
from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)

    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    profile_image_url = Column(Text, nullable=True)

    # Role and Status
    role = Column(String(20), nullable=True, default="user")
    is_active = Column(Boolean, nullable=True, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    # Subscription
    plan_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=True
    )
    subscription_status = Column(String(50), nullable=True)
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)

    # Captcha credentials
    captcha_username = Column(Text, nullable=True)
    captcha_password_hash = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationships
    campaigns = relationship(
        "Campaign", back_populates="user", cascade="all, delete-orphan"
    )
    submissions = relationship("Submission", back_populates="user")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False)
    websites = relationship("Website", back_populates="user")
    settings = relationship("Settings", back_populates="user", uselist=False)
    subscriptions = relationship("Subscription", back_populates="user")
    logs = relationship("Log", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")
    submission_logs = relationship("SubmissionLog", back_populates="user")
    
    # FIXED: Add the missing subscription_plan relationship
    subscription_plan = relationship("SubscriptionPlan", back_populates="users")

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email.split("@")[0]