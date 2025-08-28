from sqlalchemy import Column, String, Boolean, DateTime, Text, UUID, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """User model for authentication and basic info"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)
    plan_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=True
    )
    subscription_status = Column(String(50), nullable=True)
    subscription_start = Column(DateTime, nullable=True)
    subscription_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=True, default=func.current_timestamp())
    profile_image_url = Column(Text, nullable=True)
    role = Column(String(20), nullable=True, default="user")
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    captcha_username = Column(Text, nullable=True)
    captcha_password_hash = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)

    # Relationships
    plan = relationship("SubscriptionPlan", foreign_keys=[plan_id])
    campaigns = relationship("Campaign", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    websites = relationship("Website", back_populates="user")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False)
    user_contact_profile = relationship(
        "UserContactProfile", back_populates="user", uselist=False
    )
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    logs = relationship("Log", back_populates="user")
    system_logs = relationship("SystemLog", back_populates="user")
    settings = relationship("Settings", back_populates="user", uselist=False)
    submission_logs = relationship("SubmissionLog", back_populates="user")
