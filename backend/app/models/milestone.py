"""Milestone model for tracking case group and petition progress."""

import enum
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text, Enum, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class MilestoneType(str, enum.Enum):
    """Types of milestones in immigration cases."""
    # Case Group Level Milestones
    CASE_OPENED = "case_opened"
    STRATEGY_MEETING = "strategy_meeting"
    INITIAL_ASSESSMENT = "initial_assessment"
    CASE_CLOSED = "case_closed"
    
    # General Petition Milestones
    DOCUMENTS_REQUESTED = "documents_requested"
    DOCUMENTS_SUBMITTED = "documents_submitted"
    PETITION_DRAFTED = "petition_drafted"
    APPROVED = "approved"
    DENIED = "denied"
    
    # H1B Petition Milestones (I-129)
    LCA_FILED = "lca_filed"
    LCA_APPROVED = "lca_approved"
    H1B_FILED = "h1b_filed"
    H1B_APPROVED = "h1b_approved"
    
    # I-140 (Immigrant Petition) Milestones
    I140_FILED = "i140_filed"
    I140_APPROVED = "i140_approved"
    I140_DENIED = "i140_denied"
    
    # I-485 (Adjustment of Status) Milestones
    I485_FILED = "i485_filed"
    I485_APPROVED = "i485_approved"
    BIOMETRICS_SCHEDULED = "biometrics_scheduled"
    BIOMETRICS_COMPLETED = "biometrics_completed"
    INTERVIEW_SCHEDULED = "interview_scheduled"
    INTERVIEW_COMPLETED = "interview_completed"
    EAD_RECEIVED = "ead_received"
    AP_RECEIVED = "ap_received"
    GREEN_CARD_RECEIVED = "green_card_received"
    
    # PERM (Labor Certification) Milestones
    PWD_FILED = "pwd_filed"
    PWD_APPROVED = "pwd_approved"
    RECRUITMENT_STARTED = "recruitment_started"
    RECRUITMENT_COMPLETED = "recruitment_completed"
    PERM_FILED = "perm_filed"
    PERM_APPROVED = "perm_approved"
    PERM_AUDIT = "perm_audit"
    
    # TN Milestones
    TN_BORDER_APPOINTMENT = "tn_border_appointment"
    TN_APPROVED = "tn_approved"
    
    # EAD (I-765) Milestones
    EAD_FILED = "ead_filed"
    EAD_APPROVED = "ead_approved"
    
    # Advance Parole (I-131) Milestones
    AP_FILED = "ap_filed"
    AP_APPROVED = "ap_approved"
    
    # USCIS General
    FILED_WITH_USCIS = "filed_with_uscis"
    RFE_RECEIVED = "rfe_received"
    RFE_RESPONDED = "rfe_responded"
    NOTICE_OF_INTENT_TO_DENY = "noid_received"
    CASE_TRANSFERRED = "case_transferred"
    
    # Consular Processing
    NVC_CASE_NUMBER_RECEIVED = "nvc_case_received"
    DS260_SUBMITTED = "ds260_submitted"
    INTERVIEW_SCHEDULED_CONSULAR = "interview_scheduled_consular"
    VISA_ISSUED = "visa_issued"
    
    # Other
    OTHER = "other"


class MilestoneStatus(str, enum.Enum):
    """Status of a milestone."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class Milestone(Base):
    """
    Milestone tracking for case groups and petitions.
    
    A milestone can be at:
    - Case group level (e.g., "Case Opened", "Strategy Meeting")
    - Petition level (e.g., "I-140 Filed", "I-485 Approved")
    
    Constraint: Either case_group_id OR petition_id must be set, not both.
    """
    
    __tablename__ = "milestones"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys - ONE of these must be set
    case_group_id = Column(String(36), ForeignKey("case_groups.id"), nullable=True, index=True)
    petition_id = Column(String(36), ForeignKey("petitions.id"), nullable=True, index=True)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Milestone details
    milestone_type = Column(Enum(MilestoneType), nullable=False)
    status = Column(Enum(MilestoneStatus), nullable=False, default=MilestoneStatus.PENDING)
    due_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    title = Column(String(255), nullable=True)  # Custom title if milestone_type is OTHER
    description = Column(Text, nullable=True)  # Additional details
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Constraint: Either case_group_id OR petition_id must be set
    __table_args__ = (
        CheckConstraint(
            '(case_group_id IS NOT NULL AND petition_id IS NULL) OR '
            '(case_group_id IS NULL AND petition_id IS NOT NULL)',
            name='check_milestone_parent'
        ),
    )
    
    # Relationships
    case_group = relationship("CaseGroup", back_populates="milestones")
    petition = relationship("Petition", back_populates="milestones")
    creator = relationship("User")
    
    def __repr__(self):
        parent_type = "CaseGroup" if self.case_group_id else "Petition"
        parent_id = self.case_group_id or self.petition_id
        return f"<Milestone {self.milestone_type} for {parent_type} {parent_id}>"
