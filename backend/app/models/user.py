import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"  # Full system access
    HR = "hr"  # HR staff - can create users, beneficiaries, manage onboarding
    PM = "pm"  # Project Manager - sees everything under org structure + metrics
    MANAGER = "manager"  # Team lead - sees reports under hierarchy (no advanced metrics)
    BENEFICIARY = "beneficiary"  # Foreign national - view own cases only


class User(Base):
    """User model for authentication and authorization."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Authentication
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Identity
    full_name = Column(String(255), nullable=False)
    
    # Authorization
    role = Column(Enum(UserRole), nullable=False, default=UserRole.BENEFICIARY)
    
    # Organizational Structure
    contract_id = Column(String(36), ForeignKey("contracts.id"), nullable=True)
    
    # Department/Organizational unit
    department_id = Column(String(36), ForeignKey("departments.id"), nullable=True, index=True)
    
    # Reporting hierarchy
    reports_to_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Password management
    force_password_change = Column(Boolean, default=False, nullable=False)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    password_change_count = Column(String(50), default="0|", nullable=False)  # Format: "count|last_reset_date"
    invitation_token = Column(String(255), nullable=True)
    invitation_token_expires = Column(DateTime(timezone=True), nullable=True)
    invitation_accepted = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    contract = relationship("Contract", foreign_keys=[contract_id], back_populates="users", lazy="select")
    department = relationship("Department", back_populates="users", foreign_keys=[department_id], lazy="select")
    reports_to = relationship("User", remote_side=[id], backref="direct_reports", lazy="select")
    beneficiary = relationship("Beneficiary", back_populates="user", uselist=False, lazy="select")
    created_visa_applications = relationship("VisaApplication", foreign_keys="VisaApplication.created_by", back_populates="creator", lazy="select")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan", lazy="select")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan", lazy="select")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="select")
    
    def __repr__(self):
        return f"<User {self.email}>"
