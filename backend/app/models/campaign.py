# backend/app/models/campaign.py
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    UUID,
    ForeignKey,
    Boolean,
    Enum,
)
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from app.core.database import Base  # Fixed import path


class CampaignStatus(enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)
    total_urls = Column(Integer, default=0)
    submitted_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="campaigns")
    submissions = relationship(
        "Submission", back_populates="campaign", cascade="all, delete-orphan"
    )
    websites = relationship(
        "Website", back_populates="campaign"
    )  # Added this relationship
