# backend/app/models/website.py
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Text,
    UUID,
    ForeignKey,
    Boolean,
)
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from app.core.database import Base


class Website(Base):
    __tablename__ = "websites"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )  # UUID to match users.id
    domain = Column(String(255), nullable=False)
    contact_url = Column(String(500), nullable=True)
    form_detected = Column(Boolean, default=False)
    form_type = Column(String(100), nullable=True)
    form_labels = Column(Text, nullable=True)  # JSON stored as text
    form_field_count = Column(Integer, nullable=True)
    has_captcha = Column(Boolean, default=False)
    captcha_type = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True)
    failure_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="websites")
    user = relationship("User", back_populates="websites")
    submissions = relationship("Submission", back_populates="website")
