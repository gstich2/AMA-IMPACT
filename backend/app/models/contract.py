import enum
from sqlalchemy import Column, String, Date, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class ContractStatus(str, enum.Enum):
    """Contract status enumeration."""
    ACTIVE = "active"
    ARCHIVED = "archived"


class Contract(Base):
    """Contract model representing company projects."""
    
    __tablename__ = "contracts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    code = Column(String(50), unique=True, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    status = Column(Enum(ContractStatus), nullable=False, default=ContractStatus.ACTIVE)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("User", back_populates="contract")
    departments = relationship("Department", back_populates="contract", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Contract {self.code}>"
