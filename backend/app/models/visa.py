import enum
from sqlalchemy import Column, String, Date, DateTime, Enum, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class VisaTypeEnum(str, enum.Enum):
    """Visa type enumeration."""
    H1B = "H1B"
    L1 = "L1"
    O1 = "O1"
    TN = "TN"
    EB1A = "EB1A"
    EB1B = "EB1B"
    EB2 = "EB2"
    EB2NIW = "EB2NIW"
    PERM = "PERM"
    OPT = "OPT"
    EAD = "EAD"
    GREEN_CARD = "GREEN_CARD"


class VisaStatus(str, enum.Enum):
    """Visa application status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    RENEWED = "renewed"


class VisaCaseStatus(str, enum.Enum):
    """Visa case status enumeration."""
    UPCOMING = "upcoming"  # Future case, not yet started
    ACTIVE = "active"      # Currently working on
    FINALIZED = "finalized"  # Completed (approved or denied)


class VisaPriority(str, enum.Enum):
    """Visa application priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class VisaApplication(Base):
    """Visa application model for tracking employee visas."""
    
    __tablename__ = "visa_applications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    beneficiary_id = Column(String(36), ForeignKey("beneficiaries.id"), nullable=False, index=True)
    case_group_id = Column(String(36), ForeignKey("case_groups.id"), nullable=True, index=True)  # Optional: group related applications
    visa_type_id = Column(String(36), ForeignKey("visa_types.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    law_firm_id = Column(String(36), ForeignKey("law_firms.id"), nullable=True)
    responsible_party_id = Column(String(36), ForeignKey("users.id"), nullable=True)  # AMA staff managing this
    
    # Attorney information (text fields, not FK - for flexibility)
    attorney_name = Column(String(255), nullable=True)  # "Jane Attorney"
    attorney_email = Column(String(255), nullable=True)
    attorney_phone = Column(String(50), nullable=True)
    
    # Visa details
    visa_type = Column(Enum(VisaTypeEnum), nullable=False)
    petition_type = Column(String(50), nullable=True)  # e.g., "I-140", "I-129", "I-485"
    status = Column(Enum(VisaStatus), nullable=False, default=VisaStatus.DRAFT)
    case_status = Column(Enum(VisaCaseStatus), nullable=False, default=VisaCaseStatus.ACTIVE, index=True)
    priority = Column(Enum(VisaPriority), nullable=False, default=VisaPriority.MEDIUM)
    current_stage = Column(String(100), nullable=True)  # e.g., "I-140 Filed", "RFE Response Submitted"
    
    # Important dates
    filing_date = Column(Date, nullable=True)
    approval_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True, index=True)
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
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    beneficiary = relationship("Beneficiary", foreign_keys=[beneficiary_id], back_populates="visa_applications")
    case_group = relationship("CaseGroup", foreign_keys=[case_group_id], back_populates="applications")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_visa_applications", overlaps="responsible_party")
    responsible_party = relationship("User", foreign_keys=[responsible_party_id], overlaps="created_visa_applications,creator")
    visa_type_info = relationship("VisaType", back_populates="applications")
    law_firm = relationship("LawFirm", back_populates="applications")
    milestones = relationship("ApplicationMilestone", back_populates="visa_application", cascade="all, delete-orphan")
    rfes = relationship("RFETracking", back_populates="visa_application", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="visa_application", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="visa_application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VisaApplication {self.visa_type} for Beneficiary {self.beneficiary_id}>"


class VisaType(Base):
    """Visa type definition model."""
    
    __tablename__ = "visa_types"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    default_renewal_lead_days = Column(String(10), nullable=False, default="180")  # Store as string for flexibility
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    applications = relationship("VisaApplication", back_populates="visa_type_info")
    
    def __repr__(self):
        return f"<VisaType {self.code}>"
