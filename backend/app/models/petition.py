import enum
from sqlalchemy import Column, String, Date, DateTime, Enum, Boolean, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class PetitionType(str, enum.Enum):
    """Immigration petition/form types."""
    # Employment-Based Petitions
    I140 = "I140"           # Immigrant Petition for Alien Worker
    I485 = "I485"           # Application to Register Permanent Residence (Adjustment of Status)
    I129 = "I129"           # Petition for Nonimmigrant Worker
    I765 = "I765"           # Application for Employment Authorization (EAD)
    I131 = "I131"           # Application for Travel Document (Advance Parole)
    
    # Labor Certification
    PERM = "PERM"           # Labor Certification (ETA-9089)
    LCA = "LCA"             # Labor Condition Application
    
    # Family-Based
    I130 = "I130"           # Petition for Alien Relative
    I129F = "I129F"         # Petition for Alien Fiancé(e)
    
    # Dependent/Status Change
    I539 = "I539"           # Application to Extend/Change Nonimmigrant Status
    
    # Special Cases
    I360 = "I360"           # Petition for Amerasian, Widow(er), or Special Immigrant (EB4)
    I526 = "I526"           # Immigrant Petition by Standalone Investor (EB5)
    I526E = "I526E"         # Immigrant Petition by Regional Center Investor (EB5)
    
    # Consular Processing
    DS260 = "DS260"         # Immigrant Visa Application
    DS160 = "DS160"         # Nonimmigrant Visa Application
    DS2019 = "DS2019"       # Certificate of Eligibility for Exchange Visitor (J-1)
    
    # Student Visas
    I20 = "I20"             # Certificate of Eligibility for Nonimmigrant Student Status
    I20MN = "I20MN"         # Certificate of Eligibility for Nonimmigrant Student Status (M-1)
    I983 = "I983"           # Training Plan for STEM OPT Students
    
    # Other Forms
    I797 = "I797"           # Notice of Action (Approval Notice)
    I94 = "I94"             # Arrival/Departure Record
    I612 = "I612"           # Application for Waiver of the Foreign Residence Requirement
    I693 = "I693"           # Report of Medical Examination
    I864 = "I864"           # Affidavit of Support
    DS156E = "DS156E"       # Nonimmigrant Treaty Trader/Investor Application
    I589 = "I589"           # Application for Asylum
    
    # TN Visa
    TN_APPLICATION = "TN_APPLICATION"  # TN Application (POE or I-129)


class PetitionStatus(str, enum.Enum):
    """Petition status enumeration."""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    RENEWED = "RENEWED"
    RFE_RECEIVED = "RFE_RECEIVED"
    WITHDRAWN = "WITHDRAWN"


class CaseStatus(str, enum.Enum):
    """Case status for individual petition."""
    UPCOMING = "UPCOMING"      # Future petition, not yet started
    ACTIVE = "ACTIVE"          # Currently working on
    FINALIZED = "FINALIZED"    # Completed (approved or denied)


class PetitionPriority(str, enum.Enum):
    """Petition priority enumeration."""
    CRITICAL = "CRITICAL"
    URGENT = "URGENT"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Petition(Base):
    """Immigration petition/form model for tracking individual filings."""
    
    __tablename__ = "petitions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    beneficiary_id = Column(String(36), ForeignKey("beneficiaries.id"), nullable=False, index=True)
    case_group_id = Column(String(36), ForeignKey("case_groups.id"), nullable=False, index=True)
    dependent_id = Column(String(36), ForeignKey("dependents.id"), nullable=True, index=True)  # NEW: Link to dependent for derivative petitions
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    law_firm_id = Column(String(36), ForeignKey("law_firms.id"), nullable=True)
    responsible_party_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # AMA staff managing this
    
    # Attorney information (text fields, not FK - for flexibility)
    attorney_name = Column(String(255), nullable=True)  # "Jane Attorney"
    attorney_email = Column(String(255), nullable=True)
    attorney_phone = Column(String(50), nullable=True)
    
    # Petition details
    petition_type = Column(Enum(PetitionType), nullable=False, index=True)
    status = Column(Enum(PetitionStatus), nullable=False, default=PetitionStatus.DRAFT)
    case_status = Column(Enum(CaseStatus), nullable=False, default=CaseStatus.ACTIVE, index=True)
    priority = Column(Enum(PetitionPriority), nullable=False, default=PetitionPriority.MEDIUM)
    current_stage = Column(String(100), nullable=True)  # e.g., "I-140 Filed", "RFE Response Submitted"
    
    # Important dates
    filing_date = Column(Date, nullable=True)
    approval_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True, index=True)
    priority_date = Column(Date, nullable=True)  # Important for EB categories
    i94_expiration_date = Column(Date, nullable=True)
    next_action_date = Column(Date, nullable=True)  # When something needs to happen
    
    # USCIS tracking
    receipt_number = Column(String(50), nullable=True)  # e.g., WAC2190012345
    company_case_id = Column(String(50), nullable=True)  # Internal tracking number
    
    # RFE (Request for Evidence) tracking
    rfe_received = Column(Boolean, default=False, nullable=False)
    rfe_received_date = Column(Date, nullable=True)
    rfe_response_date = Column(Date, nullable=True)
    rfe_notes = Column(Text, nullable=True)
    
    # Cost tracking
    filing_fee = Column(String(20), nullable=True)  # Store as string for flexibility (e.g., "$700")
    attorney_fee = Column(String(20), nullable=True)
    premium_processing = Column(Boolean, default=False, nullable=False)
    premium_processing_fee = Column(String(20), nullable=True)
    total_cost = Column(String(20), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_derivative = Column(Boolean, default=False, nullable=False)  # True if for dependent (spouse/child)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    beneficiary = relationship("Beneficiary", foreign_keys=[beneficiary_id], back_populates="petitions")
    case_group = relationship("CaseGroup", foreign_keys=[case_group_id], back_populates="petitions")
    dependent = relationship("Dependent", foreign_keys=[dependent_id], back_populates="petitions")  # NEW
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_petitions", overlaps="responsible_party")
    responsible_party = relationship("User", foreign_keys=[responsible_party_id], overlaps="created_petitions,creator")
    law_firm = relationship("LawFirm", back_populates="petitions")
    milestones = relationship("Milestone", back_populates="petition", cascade="all, delete-orphan")
    rfes = relationship("RFETracking", back_populates="petition", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="petition", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="petition", cascade="all, delete-orphan")
    
    def __repr__(self):
        derivative_marker = " (derivative)" if self.is_derivative else ""
        return f"<Petition {self.petition_type} for Beneficiary {self.beneficiary_id}{derivative_marker}>"
