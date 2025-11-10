"""Timeline schemas for unified event display."""

from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime, date
from enum import Enum


class TimelineEventType(str, Enum):
    """Types of timeline events."""
    CASE_CREATED = "case_created"
    CASE_UPDATED = "case_updated"
    SUBMITTED_FOR_APPROVAL = "submitted_for_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    STATUS_CHANGED = "status_changed"
    MILESTONE = "milestone"
    TODO_COMPLETED = "todo_completed"


class TimelineEvent(BaseModel):
    """Unified timeline event."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    event_type: TimelineEventType
    timestamp: datetime
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    title: str
    description: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    
    # For milestones
    milestone_type: Optional[str] = None
    milestone_date: Optional[date] = None
    
    # For audit logs
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    
    # For todos
    todo_title: Optional[str] = None
    todo_status: Optional[str] = None


class TimelineResponse(BaseModel):
    """Timeline response with all events."""
    case_group_id: str
    total_events: int
    events: List[TimelineEvent]
