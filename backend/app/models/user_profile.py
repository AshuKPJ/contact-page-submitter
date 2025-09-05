# backend/app/models/user_profile.py
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
from datetime import datetime
import uuid

from app.core.database import Base


class UserProfile(Base):
    """User profile model for detailed user information"""

    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)  # Integer to match database
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )  # UUID to match users.id
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone_number = Column(String(50), nullable=True)
    company_name = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    website_url = Column(String(500), nullable=True)
    linkedin_url = Column(String(500), nullable=True)
    industry = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    zip_code = Column(String(20), nullable=True)
    country = Column(String(100), nullable=True)
    region = Column(String(100), nullable=True)
    timezone = Column(String(50), nullable=True)
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=True)
    product_interest = Column(String(255), nullable=True)
    budget_range = Column(String(100), nullable=True)
    referral_source = Column(String(255), nullable=True)
    preferred_contact = Column(String(100), nullable=True)
    best_time_to_contact = Column(String(100), nullable=True)
    contact_source = Column(String(255), nullable=True)
    is_existing_customer = Column(Boolean, nullable=True)
    language = Column(String(50), nullable=True)
    preferred_language = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    form_custom_field_1 = Column(String(500), nullable=True)
    form_custom_field_2 = Column(String(500), nullable=True)
    form_custom_field_3 = Column(String(500), nullable=True)
    dbc_username = Column(String(255), nullable=True)
    dbc_password = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="user_profile")
