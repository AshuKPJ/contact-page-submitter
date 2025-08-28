from sqlalchemy import Column, String, DateTime, Text, UUID, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class SubmissionLog(Base):
    """Submission log model for tracking submission events"""

    __tablename__ = "submission_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    website_id = Column(
        UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True, index=True
    )
    submission_id = Column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=True, index=True
    )
    target_url = Column(String, nullable=False)
    status = Column(String, nullable=True)
    action = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=True, default=func.current_timestamp())
    processed_at = Column(DateTime(timezone=True), nullable=True, default=func.now())

    # Relationships
    campaign = relationship("Campaign", back_populates="submission_logs")
    user = relationship("User", back_populates="submission_logs")
    website = relationship("Website", back_populates="submission_logs")
    submission = relationship("Submission", back_populates="submission_logs")
