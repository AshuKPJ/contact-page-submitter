from sqlalchemy import Column, String, Boolean, DateTime, Text, UUID, ForeignKey, Float
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class CaptchaLog(Base):
    """CAPTCHA log model for tracking CAPTCHA solving attempts"""

    __tablename__ = "captcha_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_id = Column(
        UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=True
    )
    captcha_type = Column(String(100), nullable=True)
    solved = Column(Boolean, nullable=True)
    solve_time = Column(Float, nullable=True)
    dbc_balance = Column(Float, nullable=True)
    error = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=True)

    # Relationships
    submission = relationship("Submission", back_populates="captcha_logs")
