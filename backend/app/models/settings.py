# backend/app/models/settings.py
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


class Setting(Base):  # Changed from Settings to Setting to match your import
    __tablename__ = "settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="settings")
