"""Case Group model for grouping related petitions into immigration pathways."""

import enum
import uuid
from sqlalchemy import Column, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base
from app.models.petition import PetitionPriority


class PathwayType(str, enum.Enum):
    """Immigration pathway types (case group types) - represents the overall immigration strategy."""
    # Green Card Pathways (Employment-Based)
    EB1_EA = "EB1_EA"  # EB-1A Extraordinary Ability
    EB1_OR = "EB1_OR"  # EB-1B Outstanding Researcher
    EB1_MN = "EB1_MN"  # EB-1C Multinational Manager/Executive
    EB2_PERM = "EB2_PERM"  # EB-2 with PERM Labor Certification
    EB2_NIW = "EB2_NIW"  # EB-2 National Interest Waiver (no PERM required)
    EB3_PERM = "EB3_PERM"  # EB-3 with PERM Labor Certification
    EB4 = "EB4"  # EB-4 Special Immigrant
    EB5 = "EB5"  # EB-5 Investor
    
    # H1B Pathways
    H1B_INITIAL = "H1B_INITIAL"  # Initial H1B petition
    H1B_EXTENSION = "H1B_EXTENSION"  # H1B extension
    H1B_TRANSFER = "H1B_TRANSFER"  # H1B transfer to new employer
    H1B_AMENDMENT = "H1B_AMENDMENT"  # H1B amendment (location/role change)
    
    # L1 Pathways
    L1A = "L1A"  # L-1A Intracompany Transferee Executive/Manager
    L1B = "L1B"  # L-1B Intracompany Transferee Specialized Knowledge
    L1_EXTENSION = "L1_EXTENSION"  # L-1 Extension
    
    # Other Nonimmigrant Pathways
    O1A = "O1A"  # O-1A Extraordinary Ability (Arts/Sciences/Business)
    O1B = "O1B"  # O-1B Extraordinary Ability (Arts/Motion Pictures/TV)
    TN = "TN"  # TN NAFTA/USMCA Professional
    E1 = "E1"  # E-1 Treaty Trader
    E2 = "E2"  # E-2 Treaty Investor
    
    # Student/Training Pathways
    F1_OPT = "F1_OPT"  # F-1 Optional Practical Training
    F1_STEM_OPT = "F1_STEM_OPT"  # F-1 STEM OPT Extension
    F1_INITIAL = "F1_INITIAL"  # F-1 Student Visa Initial
    J1 = "J1"  # J-1 Exchange Visitor
    M1 = "M1"  # M-1 Vocational Student
    
    # Family-Based Pathways
    MARRIAGE_BASED = "MARRIAGE_BASED"  # Marriage-based immigration (I-130/I-485)
    K1_FIANCE = "K1_FIANCE"  # K-1 Fiancé(e) Visa
    FAMILY_PREFERENCE = "FAMILY_PREFERENCE"  # Family preference categories
    
    # Other
    R1_RELIGIOUS = "R1_RELIGIOUS"  # R-1 Religious Worker
    ASYLUM = "ASYLUM"  # Asylum application
    U_VISA = "U_VISA"  # U Visa (Crime Victims)
    T_VISA = "T_VISA"  # T Visa (Trafficking Victims)


class CaseStatus(str, enum.Enum):
    """Overall status of a case group."""
    PLANNING = "PLANNING"  # Case being planned/prepared
    IN_PROGRESS = "IN_PROGRESS"  # One or more applications filed
    PENDING = "PENDING"  # All applications filed, awaiting decisions
    APPROVED = "APPROVED"  # Case successfully completed
    DENIED = "DENIED"  # Case denied
    WITHDRAWN = "WITHDRAWN"  # Case withdrawn
    ON_HOLD = "ON_HOLD"  # Temporarily paused


class ApprovalStatus(str, enum.Enum):
    """Approval workflow status for case groups."""
    DRAFT = "DRAFT"  # Manager is still preparing the case group
    PENDING_PM_APPROVAL = "PENDING_PM_APPROVAL"  # Submitted to PM for approval
    PM_APPROVED = "PM_APPROVED"  # PM has approved, HR can proceed
    PM_REJECTED = "PM_REJECTED"  # PM rejected, case is closed


class CaseGroup(Base):
    """
    Case Group model - represents an immigration pathway with multiple petitions.
    
    Examples:
    - EB2-NIW pathway with I-140, I-485, I-765 (EAD), I-131 (AP) petitions
    - H1B pathway with LCA and I-129 petition
    - Family-based pathway with I-130 and I-485 petitions
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
    pathway_type = Column(Enum(PathwayType), nullable=False)  # RENAMED from case_type
    case_number = Column(String(50), nullable=True, unique=True)  # Internal tracking number (e.g., "EB2-2025-001")
    
    # Status and priority
    status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.PLANNING)
    priority = Column(Enum(PetitionPriority), nullable=False, default=PetitionPriority.MEDIUM)
    
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
    petitions = relationship("Petition", back_populates="case_group", cascade="all, delete-orphan")  # RENAMED from applications
    responsible_party = relationship("User", foreign_keys=[responsible_party_id])
    created_by_manager = relationship("User", foreign_keys=[created_by_manager_id])
    approved_by_pm = relationship("User", foreign_keys=[approved_by_pm_id])
    law_firm = relationship("LawFirm", foreign_keys=[law_firm_id])
    todos = relationship("Todo", back_populates="case_group", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="case_group", cascade="all, delete-orphan")  # NEW: Case-level milestones
    
    def __repr__(self):
        return f"<CaseGroup {self.pathway_type} for Beneficiary {self.beneficiary_id}>"
