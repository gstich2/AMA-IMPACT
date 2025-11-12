"""Beneficiary model for tracking foreign nationals with visa cases."""

from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Beneficiary(Base):
    """
    Beneficiary model for foreign nationals who have visa cases.
    
    Beneficiaries may or may not have User accounts:
    - Current employees: Have both User and Beneficiary
    - Future hires: Beneficiary only (no User yet)
    - Contractors: May have User + Beneficiary if need system access
    """
    
    __tablename__ = "beneficiaries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Link to User (nullable - future hires don't have User accounts yet)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, unique=True, index=True)
    
    # Basic Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    
    # Immigration Information
    country_of_citizenship = Column(String(100), nullable=True)
    country_of_birth = Column(String(100), nullable=True)
    passport_country = Column(String(100), nullable=True)  # For dual citizens
    passport_expiration = Column(Date, nullable=True)  # For renewal warnings
    
    # Current Visa Status
    current_visa_type = Column(String(50), nullable=True)  # H1B, TN, L1, etc.
    current_visa_expiration = Column(Date, nullable=True)
    i94_expiration = Column(Date, nullable=True)
    
    # Employment Information (for visa petitions/USCIS documents)
    job_title = Column(String(255), nullable=True)
    employment_start_date = Column(Date, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="beneficiary", uselist=False)
    petitions = relationship("Petition", back_populates="beneficiary", cascade="all, delete-orphan")
    dependents = relationship("Dependent", back_populates="beneficiary", cascade="all, delete-orphan")
    case_groups = relationship("CaseGroup", back_populates="beneficiary", cascade="all, delete-orphan")
    todos = relationship("Todo", back_populates="beneficiary", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Beneficiary {self.first_name} {self.last_name}>"
    
    @property
    def full_name(self):
        """Full name for display."""
        return f"{self.first_name} {self.last_name}"
