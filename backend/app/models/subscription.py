# backend/app/models/subscription.py
from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Integer
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Subscription(Base):
    """User subscription model"""

    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False, unique=True
    )  # Changed from UUID to Integer
    plan_id = Column(
        Integer, ForeignKey("subscription_plans.id"), nullable=False
    )  # Changed from UUID to Integer
    status = Column(String(50), nullable=False, default="active")
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    external_id = Column(String(255), nullable=True)  # For payment provider IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
