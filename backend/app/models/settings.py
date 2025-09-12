# ============================================
# FILE: app/models/settings.py
# ============================================
from __future__ import annotations

import uuid
from sqlalchemy import Column, String, ForeignKey, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base


class Settings(Base):
    __tablename__ = "settings"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Settings
    default_message_template = Column(Text, nullable=True)
    captcha_api_key = Column(Text, nullable=True)
    proxy_url = Column(Text, nullable=True)
    auto_submit = Column(Boolean, nullable=True, default=False)

    # Relationships
    user = relationship("User", back_populates="settings")

    def __repr__(self):
        return f"<Settings {self.user_id}>"
