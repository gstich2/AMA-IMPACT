"""Law Firm model for visa case management."""

from sqlalchemy import Column, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class LawFirm(Base):
    """Law firm information for visa cases - simplified for tracking purposes."""
    
    __tablename__ = "law_firms"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Firm details
    name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=True)  # Primary contact at firm
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    
    # Performance tracking
    is_preferred_vendor = Column(Boolean, default=False, nullable=False)
    performance_rating = Column(String(20), nullable=True)  # "Excellent", "Good", etc.
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    applications = relationship("VisaApplication", back_populates="law_firm")
    
    def __repr__(self):
        return f"<LawFirm {self.name}>"
