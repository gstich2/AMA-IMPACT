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
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    beneficiary = relationship("Beneficiary", back_populates="case_groups")
    applications = relationship("VisaApplication", back_populates="case_group", cascade="all, delete-orphan")
    responsible_party = relationship("User", foreign_keys=[responsible_party_id])
    todos = relationship("Todo", back_populates="case_group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CaseGroup {self.case_type} for Beneficiary {self.beneficiary_id}>"
