"""Dependent model for tracking employee family members (spouse, children)."""

import enum
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class RelationshipType(str, enum.Enum):
    """Relationship type to the primary employee."""
    SPOUSE = "spouse"
    CHILD = "child"
    OTHER = "other"


class Dependent(Base):
    """Dependent (family member) model for tracking visa status of spouse/children."""
    
    __tablename__ = "dependents"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to primary beneficiary (not User)
    beneficiary_id = Column(String(36), ForeignKey("beneficiaries.id"), nullable=False, index=True)
    
    # Basic information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    relationship_type = Column(Enum(RelationshipType), nullable=False)
    
    # Immigration information
    country_of_citizenship = Column(String(100), nullable=True)
    country_of_birth = Column(String(100), nullable=True)
    
    # Current visa status
    current_visa_type = Column(String(50), nullable=True)  # e.g., "H4", "L2", "F2"
    visa_expiration = Column(Date, nullable=True)
    i94_expiration = Column(Date, nullable=True)
    
    # Passport information
    passport_number = Column(String(50), nullable=True)
    passport_country = Column(String(100), nullable=True)
    passport_expiration = Column(Date, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    beneficiary = relationship("Beneficiary", back_populates="dependents")
    petitions = relationship("Petition", back_populates="dependent", cascade="all, delete-orphan")  # NEW: Derivative petitions
    
    def __repr__(self):
        return f"<Dependent {self.first_name} {self.last_name} ({self.relationship_type})>"
