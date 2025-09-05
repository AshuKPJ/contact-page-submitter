# backend/app/models/submission_log.py
from sqlalchemy import Column, String, DateTime, Text, UUID, ForeignKey, Enum
from sqlalchemy.orm import relationship
import uuid
import enum
from datetime import datetime

from app.core.database import Base


class SubmissionStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"


class SubmissionLog(Base):
    __tablename__ = "submission_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    submission_id = Column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=True
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )  # UUID to match users.id
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True)
    target_url = Column(String(500), nullable=True)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(Enum(SubmissionStatus), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="submission_logs")
