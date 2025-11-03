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
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    visa_type_id = Column(String(36), ForeignKey("visa_types.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Visa details
    visa_type = Column(Enum(VisaTypeEnum), nullable=False)
    status = Column(Enum(VisaStatus), nullable=False, default=VisaStatus.DRAFT)
    case_status = Column(Enum(VisaCaseStatus), nullable=False, default=VisaCaseStatus.ACTIVE, index=True)
    priority = Column(Enum(VisaPriority), nullable=False, default=VisaPriority.MEDIUM)
    
    # Important dates
    filing_date = Column(Date, nullable=True)
    approval_date = Column(Date, nullable=True)
    expiration_date = Column(Date, nullable=True, index=True)
    i94_expiration_date = Column(Date, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="visa_applications", overlaps="created_visa_applications,creator")
    creator = relationship("User", foreign_keys=[created_by], back_populates="created_visa_applications", overlaps="visa_applications,user")
    visa_type_info = relationship("VisaType", back_populates="applications")
    email_logs = relationship("EmailLog", back_populates="visa_application", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VisaApplication {self.visa_type} for User {self.user_id}>"


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
