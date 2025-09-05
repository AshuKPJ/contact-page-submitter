# backend/app/models/subscription_plan.py
from sqlalchemy import Column, String, DateTime, Integer, Numeric, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(
        Integer, primary_key=True, index=True
    )  # Changed from UUID to Integer to match database
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    max_websites = Column(Integer, nullable=True)
    max_submissions_per_day = Column(Integer, nullable=True)
    max_campaigns = Column(Integer, default=1)
    price = Column(Numeric(10, 2), nullable=False, default=0.0)
    currency = Column(String(3), default="USD")
    features = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="subscription_plan")
    subscriptions = relationship("Subscription", back_populates="plan")
