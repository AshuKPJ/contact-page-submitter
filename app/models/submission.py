from sqlalchemy import Column, String, Integer, DateTime, Text, UUID, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Submission(Base):
    __tablename__ = "submissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True)
    url = Column(String(500), nullable=True)
    contact_method = Column(String(50), nullable=True)
    email_extracted = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")
    success = Column(Boolean, default=False)
    response_status = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    form_fields_sent = Column(Text, nullable=True)  # JSON stored as text
    captcha_encountered = Column(Boolean, default=False)
    captcha_solved = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="submissions")
    user = relationship("User", back_populates="submissions")
    website = relationship("Website", back_populates="submissions")
