"""
Dashboard response schemas
"""
from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel
from app.models.visa import VisaStatus
from app.models.todo import TodoStatus, TodoPriority


class DashboardSummary(BaseModel):
    """Summary statistics for dashboard overview."""
    total_beneficiaries: int
    active_visas: int
    expiring_soon: int  # Within 30 days
    overdue_visas: int
    pending_todos: int
    active_case_groups: int
    completed_todos_this_month: int


class RecentActivity(BaseModel):
    """Recent activity item for dashboard feed."""
    id: str
    type: str  # "visa_approved", "todo_completed", "case_group_created", etc.
    description: str
    timestamp: datetime
    user_name: str


class UpcomingExpiration(BaseModel):
    """Upcoming visa expiration for dashboard alert."""
    id: str
    beneficiary_name: str
    visa_type: str
    expiration_date: date
    days_remaining: int
    status: VisaStatus


class UrgentTodo(BaseModel):
    """Urgent todo item for dashboard attention."""
    id: str
    title: str
    priority: TodoPriority
    due_date: Optional[datetime]
    assignee_name: str
    is_overdue: bool
    days_overdue: Optional[int]
    status: TodoStatus


class DashboardResponse(BaseModel):
    """Complete dashboard response with all sections."""
    summary: DashboardSummary
    recent_activity: List[RecentActivity]
    upcoming_expirations: List[UpcomingExpiration]
    urgent_todos: List[UrgentTodo]


class QuickStatsResponse(BaseModel):
    """Minimal stats for header/navbar display."""
    active_visas: int
    expiring_soon: int
    pending_todos: int
    overdue_visas: int