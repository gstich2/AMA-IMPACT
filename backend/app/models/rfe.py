"""RFE Tracking model for managing Requests for Evidence."""

import enum
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class RFEStatus(str, enum.Enum):
    """Status of an RFE (Request for Evidence)."""
    RECEIVED = "received"
    IN_PROGRESS = "in_progress"
    RESPONDED = "responded"
    RESOLVED = "resolved"


class RFEType(str, enum.Enum):
    """Types of RFEs."""
    INITIAL_EVIDENCE = "initial_evidence"
    ADDITIONAL_EVIDENCE = "additional_evidence"
    INTENT_TO_DENY = "intent_to_deny"
    INTENT_TO_REVOKE = "intent_to_revoke"
    OTHER = "other"


class RFETracking(Base):
    """Detailed tracking for RFEs (Requests for Evidence) on visa applications."""
    
    __tablename__ = "rfe_tracking"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    visa_application_id = Column(String(36), ForeignKey("visa_applications.id"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # RFE details
    rfe_type = Column(Enum(RFEType), nullable=False)
    status = Column(Enum(RFEStatus), nullable=False, default=RFEStatus.RECEIVED)
    
    # Important dates
    rfe_received_date = Column(Date, nullable=False)
    rfe_deadline = Column(Date, nullable=False)
    response_submitted_date = Column(Date, nullable=True)
    resolution_date = Column(Date, nullable=True)
    
    # Details
    rfe_subject = Column(String(255), nullable=True)  # Brief subject/title
    description = Column(Text, nullable=True)  # What was requested
    response_summary = Column(Text, nullable=True)  # What was submitted in response
    notes = Column(Text, nullable=True)  # Internal notes and comments
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    visa_application = relationship("VisaApplication", back_populates="rfes")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<RFETracking {self.rfe_type} - {self.status}>"
