"""Application Milestone model for tracking visa case progress."""

import enum
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class MilestoneType(str, enum.Enum):
    """Types of milestones in a visa application process."""
    CASE_OPENED = "case_opened"
    DOCUMENTS_REQUESTED = "documents_requested"
    DOCUMENTS_SUBMITTED = "documents_submitted"
    FILED_WITH_USCIS = "filed_with_uscis"
    RFE_RECEIVED = "rfe_received"
    RFE_RESPONDED = "rfe_responded"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    APPROVED = "approved"
    DENIED = "denied"
    CASE_CLOSED = "case_closed"
    OTHER = "other"


class ApplicationMilestone(Base):
    """Milestone tracking for visa applications to show case timeline."""
    
    __tablename__ = "application_milestones"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    visa_application_id = Column(String(36), ForeignKey("visa_applications.id"), nullable=False, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Milestone details
    milestone_type = Column(Enum(MilestoneType), nullable=False)
    milestone_date = Column(Date, nullable=False)
    title = Column(String(255), nullable=True)  # Custom title if milestone_type is OTHER
    description = Column(Text, nullable=True)  # Additional details
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    visa_application = relationship("VisaApplication", back_populates="milestones")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<ApplicationMilestone {self.milestone_type} on {self.milestone_date}>"
