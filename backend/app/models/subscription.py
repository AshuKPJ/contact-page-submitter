from sqlalchemy import (
    Column,
    String,
    DateTime,
    UUID,
    ForeignKey,
    Integer,
    Numeric,
    JSON,
)
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class SubscriptionPlan(Base):
    """Subscription plan model"""

    __tablename__ = "subscription_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    max_websites = Column(Integer, nullable=True)
    max_submissions_per_day = Column(Integer, nullable=True)
    price = Column(Numeric(10, 2), nullable=True)
    features = Column(JSON, nullable=True)

    # Relationships
    users = relationship("User", foreign_keys="[User.plan_id]", back_populates="plan")
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """User subscription model"""

    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    plan_id = Column(
        UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=True
    )
    status = Column(String(50), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    external_id = Column(String(255), nullable=True)

    # Relationships
    user = relationship("User", back_populates="subscription")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
