from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    Text,
    UUID,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Campaign(Base):
    """Campaign model for managing form submission campaigns"""

    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    name = Column(String(255), nullable=True)
    csv_filename = Column(String(255), nullable=True)
    started_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=True)
    message = Column(Text, nullable=True)
    proxy = Column(String(255), nullable=True)
    use_captcha = Column(Boolean, nullable=True, default=True)
    total_urls = Column(Integer, nullable=True, default=0)
    submitted_count = Column(Integer, nullable=True, default=0)
    failed_count = Column(Integer, nullable=True, default=0)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="campaigns")
    websites = relationship("Website", back_populates="campaign")
    submissions = relationship("Submission", back_populates="campaign")
    logs = relationship("Log", back_populates="campaign")
    submission_logs = relationship("SubmissionLog", back_populates="campaign")
