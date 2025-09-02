from sqlalchemy import Column, String, Integer, DateTime, Text, UUID, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    status = Column(String(50), default="draft")
    total_urls = Column(Integer, default=0)
    submitted_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    submissions = relationship("Submission", back_populates="campaign", cascade="all, delete-orphan")
