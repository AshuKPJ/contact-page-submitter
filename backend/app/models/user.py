# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum, UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid

from app.core.database import Base


class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Foreign keys
    plan_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=True
    )

    # Relationships - fixed to match your actual model class names
    plan = relationship("SubscriptionPlan", back_populates="users")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False)
    user_contact_profile = relationship(
        "UserContactProfile", back_populates="user", uselist=False
    )
    websites = relationship("Website", back_populates="user")
    campaigns = relationship("Campaign", back_populates="user")
    submissions = relationship("Submission", back_populates="user")
    submission_logs = relationship("SubmissionLog", back_populates="user")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    system_logs = relationship("SystemLog", back_populates="user")
    settings = relationship(
        "Settings", back_populates="user"
    )  # Match your Settings class name
    logs = relationship("Log", back_populates="user")
