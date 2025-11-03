import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    HR = "hr"
    PROGRAM_MANAGER = "program_manager"
    TECH_LEAD = "tech_lead"
    STAFF = "staff"


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.STAFF)
    
    # Contract association
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=True)
    
    # Reporting hierarchy
    reports_to_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    contract = relationship("Contract", back_populates="users")
    reports_to = relationship("User", remote_side=[id], backref="direct_reports")
    visa_applications = relationship("VisaApplication", back_populates="user", cascade="all, delete-orphan")
    created_visa_applications = relationship("VisaApplication", foreign_keys="VisaApplication.created_by", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"
