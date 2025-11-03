from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
import uuid

from app.core.database import Base


class UserSettings(Base):
    """User settings model for preferences."""
    
    __tablename__ = "user_settings"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Settings
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    alert_thresholds = Column(JSON, default={"visa_expiry": [90, 60, 30, 14, 7]})
    timezone = Column(String(50), default="UTC", nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="settings")
    
    def __repr__(self):
        return f"<UserSettings for User {self.user_id}>"
