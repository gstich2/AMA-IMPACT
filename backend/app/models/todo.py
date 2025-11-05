"""
Todo model for task tracking
"""
import enum
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class TodoStatus(str, enum.Enum):
    """Todo status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TodoPriority(str, enum.Enum):
    """Todo priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Todo(Base):
    """
    Todo/Task model for tracking action items.
    
    Denormalized design: If visa_application_id is set, case_group_id and beneficiary_id
    are automatically populated for faster queries. If case_group_id is set, beneficiary_id
    is populated. This allows efficient filtering at any level.
    """
    
    __tablename__ = "todos"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Core fields
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # User assignments
    assigned_to_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    created_by_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Hierarchical associations (denormalized for query performance)
    # All three can be NULL for general todos not tied to a specific case
    # If visa_application_id is set, case_group_id and beneficiary_id are auto-populated
    # If case_group_id is set, beneficiary_id is auto-populated
    visa_application_id = Column(String(36), ForeignKey("visa_applications.id"), nullable=True, index=True)
    case_group_id = Column(String(36), ForeignKey("case_groups.id"), nullable=True, index=True)
    beneficiary_id = Column(String(36), ForeignKey("beneficiaries.id"), nullable=True, index=True)
    
    # Status and priority
    status = Column(Enum(TodoStatus), nullable=False, default=TodoStatus.TODO, index=True)
    priority = Column(Enum(TodoPriority), nullable=False, default=TodoPriority.MEDIUM, index=True)
    
    # Timing
    due_date = Column(DateTime(timezone=True), nullable=True, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    assigned_to = relationship("User", foreign_keys=[assigned_to_user_id], backref="assigned_todos", lazy="select")
    created_by = relationship("User", foreign_keys=[created_by_user_id], backref="created_todos", lazy="select")
    visa_application = relationship("VisaApplication", back_populates="todos", lazy="select")
    case_group = relationship("CaseGroup", back_populates="todos", lazy="select")
    beneficiary = relationship("Beneficiary", back_populates="todos", lazy="select")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_todos_assigned_status', 'assigned_to_user_id', 'status'),
        Index('ix_todos_assigned_priority', 'assigned_to_user_id', 'priority'),
        Index('ix_todos_beneficiary_status', 'beneficiary_id', 'status'),
        Index('ix_todos_due_date_status', 'due_date', 'status'),
    )
    
    def __repr__(self):
        return f"<Todo {self.title} ({self.status})>"
