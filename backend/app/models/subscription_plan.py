from sqlalchemy import Column, String, Integer, DateTime, Numeric, UUID, Boolean
import uuid
from app.core.database import Base

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    features = Column(String(500), nullable=True)
    max_submissions = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False)

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.id"), nullable=False)
    status = Column(String(50), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="subscription")
