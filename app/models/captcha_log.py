from sqlalchemy import Column, String, Integer, DateTime, Text, UUID, ForeignKey, Boolean
import uuid
from app.core.database import Base

class CaptchaLog(Base):
    __tablename__ = "captcha_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=True)
    captcha_type = Column(String(100), nullable=False)
    solved = Column(Boolean, default=False)
    solution_time = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)
