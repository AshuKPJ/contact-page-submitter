# app/models/campaign.py
"""Campaign model with proper enum handling."""

from __future__ import annotations

import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    Enum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class CampaignStatus(str, enum.Enum):
    """Campaign status enum."""

    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Campaign(Base):
    __tablename__ = "campaigns"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Campaign details
    name = Column(String(255), nullable=True)
    message = Column(Text, nullable=True)

    # FIX: Use Enum type instead of String
    status = Column(Enum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT)

    # File management
    csv_filename = Column(String(255), nullable=True)
    file_name = Column(String(255), nullable=True)

    # Configuration
    proxy = Column(String(255), nullable=True)
    use_captcha = Column(Boolean, nullable=True, default=False)

    # Statistics
    total_urls = Column(Integer, nullable=True, default=0)
    total_websites = Column(Integer, nullable=True, default=0)
    processed = Column(Integer, nullable=True, default=0)
    submitted_count = Column(Integer, nullable=True, default=0)
    successful = Column(Integer, nullable=True, default=0)
    failed = Column(Integer, nullable=True, default=0)
    failed_count = Column(Integer, nullable=True, default=0)
    email_fallback = Column(Integer, nullable=True, default=0)
    no_form = Column(Integer, nullable=True, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="campaigns")
    submissions = relationship(
        "Submission", back_populates="campaign", cascade="all, delete-orphan"
    )
    websites = relationship("Website", back_populates="campaign")
    submission_logs = relationship("SubmissionLog", back_populates="campaign")
    logs = relationship("Log", back_populates="campaign")

    def __repr__(self):
        return f"<Campaign {self.name}>"
