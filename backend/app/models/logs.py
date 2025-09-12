# ============================================
# FILE: app/models/logs.py
# ============================================
from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    Float,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.models.base import Base


class Log(Base):
    __tablename__ = "logs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True)

    # Log details
    level = Column(String(20), nullable=True)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    context = Column(JSONB, nullable=True)

    # Timestamp
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="logs")
    campaign = relationship("Campaign", back_populates="logs")
    website = relationship("Website", back_populates="logs")

    def __repr__(self):
        return f"<Log {self.level}: {self.message[:50]}>"


class SubmissionLog(Base):
    __tablename__ = "submission_logs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True)
    submission_id = Column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=True
    )

    # Log details
    target_url = Column(String, nullable=False)
    status = Column(String, nullable=True)
    action = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)

    # Timestamps
    processed_at = Column(DateTime, nullable=True)
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="submission_logs")
    campaign = relationship("Campaign", back_populates="submission_logs")
    website = relationship("Website", back_populates="submission_logs")
    submission = relationship("Submission", back_populates="submission_logs")

    def __repr__(self):
        return f"<SubmissionLog {self.target_url}>"


class CaptchaLog(Base):
    __tablename__ = "captcha_logs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    submission_id = Column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=True
    )

    # Captcha details
    captcha_type = Column(String(100), nullable=True)
    solved = Column(Boolean, nullable=True, default=False)
    solve_time = Column(Float, nullable=True)  # DOUBLE PRECISION in PostgreSQL
    dbc_balance = Column(Float, nullable=True)  # DOUBLE PRECISION in PostgreSQL
    error = Column(Text, nullable=True)

    # Timestamp
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)

    # Relationships
    submission = relationship("Submission", back_populates="captcha_logs")

    def __repr__(self):
        return f"<CaptchaLog {self.captcha_type}: {self.solved}>"


class SystemLog(Base):
    __tablename__ = "system_logs"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Log details
    action = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    timestamp = Column(DateTime, nullable=True, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="system_logs")

    def __repr__(self):
        return f"<SystemLog {self.action}>"
