from sqlalchemy import Column, String, Boolean, DateTime, Text, UUID, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Settings(Base):
    """User settings model"""

    __tablename__ = "settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    default_message_template = Column(Text, nullable=True)
    captcha_api_key = Column(Text, nullable=True)
    proxy_url = Column(Text, nullable=True)
    auto_submit = Column(Boolean, nullable=True, default=False)

    # Relationships
    user = relationship("User", back_populates="settings")


class Log(Base):
    """General log model"""

    __tablename__ = "logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=True)
    website_id = Column(UUID(as_uuid=True), ForeignKey("websites.id"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=True)
    level = Column(String(20), nullable=True, default="INFO")
    message = Column(Text, nullable=False)
    context = Column(JSON, nullable=True, default=lambda: {})
    timestamp = Column(DateTime(timezone=True), nullable=True, default=func.now())

    # Relationships
    user = relationship("User", back_populates="logs")
    campaign = relationship("Campaign", back_populates="logs")
    website = relationship("Website", back_populates="logs")


class SystemLog(Base):
    """System log model for tracking system events"""

    __tablename__ = "system_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True
    )
    action = Column(String(255), nullable=True)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="system_logs")
