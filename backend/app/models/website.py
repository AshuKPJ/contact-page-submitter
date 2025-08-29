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
    # Remove ARRAY import - not compatible with SQLite
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Website(Base):
    """Website model for tracking website analysis and form detection"""

    __tablename__ = "websites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    domain = Column(String(255), nullable=True)
    contact_url = Column(Text, nullable=True)
    form_detected = Column(Boolean, nullable=True, default=False)
    form_type = Column(String(100), nullable=True)

    # Changed from ARRAY to JSON for SQLite compatibility
    form_labels = Column(JSON, nullable=True, default=list)  # Was ARRAY(String)
    form_field_count = Column(Integer, nullable=True)
    has_captcha = Column(Boolean, nullable=True, default=False)
    captcha_type = Column(String(100), nullable=True)

    # Changed from ARRAY to JSON
    form_name_variants = Column(JSON, nullable=True, default=list)  # Was ARRAY(String)

    status = Column(String(50), nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True, default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    requires_proxy = Column(Boolean, nullable=True, default=False)
    proxy_block_type = Column(Text, nullable=True)
    last_proxy_used = Column(Text, nullable=True)
    captcha_difficulty = Column(Text, nullable=True)
    captcha_solution_time = Column(Integer, nullable=True)
    captcha_metadata = Column(JSON, nullable=True)
    form_field_types = Column(JSON, nullable=True, default=lambda: {})
    form_field_options = Column(JSON, nullable=True, default=lambda: {})
    question_answer_fields = Column(JSON, nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="websites")
    user = relationship("User", back_populates="websites")
    submissions = relationship("Submission", back_populates="website")
    submission_logs = relationship("SubmissionLog", back_populates="website")
    logs = relationship("Log", back_populates="website")
