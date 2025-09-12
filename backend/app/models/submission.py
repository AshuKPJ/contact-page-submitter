# app/models/submission.py
from __future__ import annotations

import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


# Python enum for use in code
class SubmissionStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class Submission(Base):
    __tablename__ = "submissions"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True)

    # Submission details
    url = Column(Text, nullable=True)
    status = Column(
        String(50), nullable=False, default="pending"
    )  # VARCHAR(50) in your DB
    success = Column(Boolean, nullable=True, default=False)

    # Response details
    response_status = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    contact_method = Column(String(50), nullable=True)
    email_extracted = Column(String(255), nullable=True)

    # Form data
    form_fields_sent = Column(JSONB, nullable=True)

    # Captcha handling
    captcha_encountered = Column(Boolean, nullable=True, default=False)
    captcha_solved = Column(Boolean, nullable=True, default=False)

    # Processing details
    retry_count = Column(Integer, nullable=True, default=0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    submitted_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="submissions")
    campaign = relationship("Campaign", back_populates="submissions")
    website = relationship("Website", back_populates="submissions")
    captcha_logs = relationship("CaptchaLog", back_populates="submission")
    submission_logs = relationship("SubmissionLog", back_populates="submission")

    def __repr__(self):
        return f"<Submission {self.url}>"
