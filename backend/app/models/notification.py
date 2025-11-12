import enum
from sqlalchemy import Column, String, DateTime, Enum, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class NotificationType(str, enum.Enum):
    """Notification type enumeration."""
    VISA_EXPIRING = "visa_expiring"
    STATUS_CHANGED = "status_changed"
    OVERDUE = "overdue"
    SYSTEM = "system"


class Notification(Base):
    """In-app notification model."""
    
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    link = Column(String(500), nullable=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.type} for User {self.user_id}>"


class EmailStatus(str, enum.Enum):
    """Email status enumeration."""
    QUEUED = "queued"
    SENT = "sent"
    FAILED = "failed"


class EmailLog(Base):
    """Email log model for tracking sent emails."""
    
    __tablename__ = "email_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recipient_email = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(Enum(EmailStatus), nullable=False, default=EmailStatus.QUEUED)
    error_message = Column(Text, nullable=True)
    petition_id = Column(String(36), ForeignKey("petitions.id"), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    petition = relationship("Petition", back_populates="email_logs")
    
    def __repr__(self):
        return f"<EmailLog {self.status} to {self.recipient_email}>"
