# ============================================
# FILE: app/models/user_profile.py
# ============================================
from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, DateTime, Integer, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    # Primary key (Integer, not UUID)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Basic contact information
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)

    # Company information
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    website_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    industry = Column(String(255), nullable=True)

    # Location information
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)

    # Message defaults
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=True)

    # Business information
    product_interest = Column(String(255), nullable=True)
    budget_range = Column(String(100), nullable=True)
    referral_source = Column(String(255), nullable=True)

    # Contact preferences
    preferred_contact = Column(String(100), nullable=True)
    best_time_to_contact = Column(String(100), nullable=True)
    contact_source = Column(String(255), nullable=True)
    is_existing_customer = Column(Boolean, nullable=True, default=False)

    # Language preferences
    language = Column(String(50), nullable=True)
    preferred_language = Column(String(50), nullable=True)

    # Additional fields
    notes = Column(Text, nullable=True)
    form_custom_field_1 = Column(String(500), nullable=True)
    form_custom_field_2 = Column(String(500), nullable=True)
    form_custom_field_3 = Column(String(500), nullable=True)

    # DeathByCaptcha credentials
    dbc_username = Column(String(255), nullable=True)
    dbc_password = Column(String(255), nullable=True)

    # Timestamps
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_profile")

    def __repr__(self):
        return f"<UserProfile {self.user_id}>"
