from sqlalchemy import Column, String, Integer, DateTime, Text, UUID, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class SubmissionLog(Base):
    __tablename__ = "submission_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True)
    target_url = Column(String(500), nullable=True)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    status = Column(String(50), nullable=True)
    timestamp = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="submission_logs")
