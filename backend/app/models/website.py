# ============================================
# FILE: app/models/website.py
# ============================================
from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    ARRAY,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from app.models.base import Base


class Website(Base):
    __tablename__ = "websites"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)

    # Website details
    domain = Column(String(255), nullable=True)
    contact_url = Column(Text, nullable=True)
    status = Column(String(50), nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Form detection
    form_detected = Column(Boolean, nullable=True, default=False)
    form_type = Column(String(100), nullable=True)
    form_labels = Column(ARRAY(Text), nullable=True)
    form_field_count = Column(Integer, nullable=True)
    form_name_variants = Column(ARRAY(Text), nullable=True)
    form_field_types = Column(JSONB, nullable=True)
    form_field_options = Column(JSONB, nullable=True)
    question_answer_fields = Column(JSONB, nullable=True)

    # Captcha information
    has_captcha = Column(Boolean, nullable=True, default=False)
    captcha_type = Column(String(100), nullable=True)
    captcha_difficulty = Column(Text, nullable=True)
    captcha_solution_time = Column(Integer, nullable=True)
    captcha_metadata = Column(JSONB, nullable=True)

    # Proxy information
    requires_proxy = Column(Boolean, nullable=True, default=False)
    proxy_block_type = Column(Text, nullable=True)
    last_proxy_used = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    user = relationship("User", back_populates="websites")
    campaign = relationship("Campaign", back_populates="websites")
    submissions = relationship("Submission", back_populates="website")
    submission_logs = relationship("SubmissionLog", back_populates="website")
    logs = relationship("Log", back_populates="website")

    def __repr__(self):
        return f"<Website {self.domain}>"
