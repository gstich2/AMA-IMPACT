"""Todo schemas for request/response validation."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

from app.models.todo import TodoStatus, TodoPriority


class TodoBase(BaseModel):
    """Base todo schema."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to_user_id: str
    visa_application_id: Optional[str] = None
    case_group_id: Optional[str] = None
    beneficiary_id: Optional[str] = None
    status: TodoStatus = TodoStatus.TODO
    priority: TodoPriority = TodoPriority.MEDIUM
    due_date: Optional[datetime] = None


class TodoCreate(TodoBase):
    """
    Schema for creating a todo.
    
    Auto-population rules:
    - If visa_application_id is provided, case_group_id and beneficiary_id will be auto-filled
    - If case_group_id is provided, beneficiary_id will be auto-filled
    - At least ONE of (visa_application_id, case_group_id, beneficiary_id) should be provided
      for case-related todos, or all can be NULL for general todos
    """
    pass


class TodoUpdate(BaseModel):
    """Schema for updating a todo."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assigned_to_user_id: Optional[str] = None
    visa_application_id: Optional[str] = None
    case_group_id: Optional[str] = None
    beneficiary_id: Optional[str] = None
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None
    due_date: Optional[datetime] = None


class TodoResponse(TodoBase):
    """Schema for todo response with computed metrics."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    created_by_user_id: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    # Computed fields for metrics
    is_overdue: Optional[bool] = None
    days_overdue: Optional[int] = None
    days_to_complete: Optional[int] = None  # How long it took (completed_at - created_at)
    completed_on_time: Optional[bool] = None  # Was it completed before due_date?


class TodoWithDetails(TodoResponse):
    """Todo response with related entity details."""
    # Add nested objects if needed
    assigned_to_name: Optional[str] = None
    created_by_name: Optional[str] = None
    beneficiary_name: Optional[str] = None
    visa_type: Optional[str] = None
    case_type: Optional[str] = None


class TodoStats(BaseModel):
    """Todo statistics for dashboard."""
    total: int
    todo: int
    in_progress: int
    blocked: int
    completed: int
    cancelled: int
    overdue: int
    urgent: int
    high_priority: int
