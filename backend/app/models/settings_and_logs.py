from sqlalchemy import Column, String, Integer, DateTime, Text, UUID, ForeignKey, Boolean
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="system_logs")

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="settings")

class Log(Base):
    __tablename__ = "logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    message = Column(Text, nullable=False)
    level = Column(String(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="logs")
