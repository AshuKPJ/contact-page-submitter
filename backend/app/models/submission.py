from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    UUID,
    ForeignKey,
    Integer,
    JSON,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Submission(Base):
    """Submission model for tracking individual form submissions"""

    __tablename__ = "submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    submitted_at = Column(DateTime, nullable=True, default=func.current_timestamp())
    url = Column(Text, nullable=True)
    contact_method = Column(String(50), nullable=True)
    email_extracted = Column(String(255), nullable=True)
    success = Column(Boolean, nullable=True)
    response_status = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    form_fields_sent = Column(JSON, nullable=True)
    captcha_encountered = Column(Boolean, nullable=True, default=False)
    captcha_solved = Column(Boolean, nullable=True, default=False)
    retry_count = Column(Integer, nullable=True, default=0)
    processed_at = Column(DateTime, nullable=True)

    # Relationships
    website = relationship("Website", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
    campaign = relationship("Campaign", back_populates="submissions")
    captcha_logs = relationship("CaptchaLog", back_populates="submission")
    submission_logs = relationship("SubmissionLog", back_populates="submission")
