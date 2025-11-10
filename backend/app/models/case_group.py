"""Case Group model for grouping related visa applications."""

import enum
import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.visa import VisaPriority


class CaseType(str, enum.Enum):
    """Types of visa cases - multi-step or single applications."""
    # Green Card Cases (Employment-Based)
    EB1 = "eb1"  # EB-1 Extraordinary Ability
    EB2 = "eb2"  # EB-2 Advanced Degree or Exceptional Ability
    EB3 = "eb3"  # EB-3 Skilled Worker or Professional
    EB2_NIW = "eb2_niw"  # EB-2 National Interest Waiver
    
    # PERM Labor Certification
    PERM = "perm"  # PERM Labor Certification Process
    
    # H1B Cases
    H1B_INITIAL = "h1b_initial"  # Initial H1B petition
    H1B_EXTENSION = "h1b_extension"  # H1B extension
    H1B_TRANSFER = "h1b_transfer"  # H1B transfer to new employer
    H1B_AMENDMENT = "h1b_amendment"  # H1B amendment (location/role change)
    
    # Other Nonimmigrant Visas
    L1_INITIAL = "l1_initial"  # L-1 Intracompany Transfer
    L1_EXTENSION = "l1_extension"  # L-1 Extension
    O1 = "o1"  # O-1 Extraordinary Ability
    TN = "tn"  # TN NAFTA Professional
    
    # Student/Training
    F1_OPT = "f1_opt"  # F-1 Optional Practical Training
    F1_STEM_OPT = "f1_stem_opt"  # F-1 STEM OPT Extension
    
    # Family-Based
    FAMILY_BASED = "family_based"  # Family-based immigration
    
    # Other
    SINGLE = "single"  # Single standalone application
    OTHER = "other"  # Other case types


class CaseStatus(str, enum.Enum):
    """Overall status of a case group."""
    PLANNING = "planning"  # Case being planned/prepared
    IN_PROGRESS = "in_progress"  # One or more applications filed
    PENDING = "pending"  # All applications filed, awaiting decisions
    APPROVED = "approved"  # Case successfully completed
    DENIED = "denied"  # Case denied
    WITHDRAWN = "withdrawn"  # Case withdrawn
    ON_HOLD = "on_hold"  # Temporarily paused


class ApprovalStatus(str, enum.Enum):
    """Approval workflow status for case groups."""
    DRAFT = "draft"  # Manager is still preparing the case group
    PENDING_PM_APPROVAL = "pending_pm_approval"  # Submitted to PM for approval
    PM_APPROVED = "pm_approved"  # PM has approved, HR can proceed
    PM_REJECTED = "pm_rejected"  # PM rejected, case is closed


class CaseGroup(Base):
    """
    Case Group model - groups related visa applications into a single case.
    
    Examples:
    - EB2 case with I-140, I-485, EAD, AP applications
    - H1B transfer with withdrawal and new petition
    - PERM process with multiple steps
    - Single standalone applications (default)
    """
    
    __tablename__ = "case_groups"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    beneficiary_id = Column(String(36), ForeignKey("beneficiaries.id"), nullable=False, index=True)
    responsible_party_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # PM/HR managing this case
    created_by_manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # Manager who created this case group
    law_firm_id = Column(String(36), ForeignKey("law_firms.id"), nullable=True)  # Assigned law firm for this case
    
    # Approval workflow
    approval_status = Column(Enum(ApprovalStatus), nullable=False, default=ApprovalStatus.DRAFT, index=True)
    approved_by_pm_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # PM who approved/rejected
    pm_approval_date = Column(DateTime(timezone=True), nullable=True)  # When PM made decision
    pm_approval_notes = Column(Text, nullable=True)  # PM's comments on approval/rejection
    
    # Case identification
    case_type = Column(Enum(CaseType), nullable=False, default=CaseType.SINGLE)
    case_number = Column(String(50), nullable=True, unique=True)  # Internal tracking number (e.g., "EB2-2025-001")
    
    # Status and priority
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.PLANNING)
    priority = Column(Enum(VisaPriority), nullable=False, default=VisaPriority.MEDIUM)
    
    # Key dates
    case_started_date = Column(Date, nullable=True)
    target_completion_date = Column(Date, nullable=True)
    case_completed_date = Column(Date, nullable=True)
    
    # Additional info
    notes = Column(Text, nullable=True)
    attorney_portal_link = Column(String(500), nullable=True)  # Link to law firm's document portal
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    beneficiary = relationship("Beneficiary", back_populates="case_groups")
    applications = relationship("VisaApplication", back_populates="case_group", cascade="all, delete-orphan")
    responsible_party = relationship("User", foreign_keys=[responsible_party_id])
    created_by_manager = relationship("User", foreign_keys=[created_by_manager_id])
    approved_by_pm = relationship("User", foreign_keys=[approved_by_pm_id])
    law_firm = relationship("LawFirm", foreign_keys=[law_firm_id])
    todos = relationship("Todo", back_populates="case_group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CaseGroup {self.case_type} for Beneficiary {self.beneficiary_id}>"
