"""
Audit Log Schemas

Pydantic models for audit trail tracking and reporting.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum

from app.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    """Audit log entry response schema."""
    id: str
    user_id: str
    user_email: str
    user_name: str
    action: AuditAction
    resource_type: str
    resource_id: str
    resource_name: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes_summary: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogCreate(BaseModel):
    """Schema for creating audit log entries."""
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: str
    resource_name: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changes_summary: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class AuditLogFilter(BaseModel):
    """Filtering parameters for audit logs."""
    user_id: Optional[str] = Field(None, description="Filter by user ID")
    user_email: Optional[str] = Field(None, description="Filter by user email")
    action: Optional[AuditAction] = Field(None, description="Filter by action type")
    resource_type: Optional[str] = Field(None, description="Filter by resource type (petition, user, case_group, etc.)")
    resource_id: Optional[str] = Field(None, description="Filter by specific resource ID")
    date_from: Optional[datetime] = Field(None, description="Filter from date (inclusive)")
    date_to: Optional[datetime] = Field(None, description="Filter to date (inclusive)")
    search: Optional[str] = Field(None, description="Search in resource names and changes summary")
    ip_address: Optional[str] = Field(None, description="Filter by IP address")
    
    # Pagination
    limit: int = Field(50, ge=1, le=500, description="Maximum number of results (1-500)")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    
    # Sorting
    sort_by: str = Field("timestamp", description="Sort by field (timestamp, action, resource_type)")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order (asc or desc)")


class AuditLogStats(BaseModel):
    """Audit log statistics schema."""
    total_entries: int
    entries_today: int
    entries_this_week: int
    entries_this_month: int
    
    # Action breakdown
    actions_breakdown: Dict[str, int]
    
    # Resource type breakdown
    resource_types_breakdown: Dict[str, int]
    
    # Top users (by number of actions)
    top_users: List[Dict[str, Any]]
    
    # Recent activity summary
    recent_activity_summary: List[Dict[str, Any]]


class AuditLogExport(BaseModel):
    """Schema for audit log export requests."""
    format: str = Field("csv", pattern="^(csv|json|xlsx)$", description="Export format")
    filters: Optional[AuditLogFilter] = None
    include_fields: Optional[List[str]] = Field(
        None, 
        description="Specific fields to include in export. If None, includes all fields."
    )


class AuditLogBulkResponse(BaseModel):
    """Response schema for bulk audit log operations."""
    total_entries: int
    entries: List[AuditLogResponse]
    has_next_page: bool
    next_offset: Optional[int] = None
    filters_applied: Optional[Dict[str, Any]] = None


class ResourceActivity(BaseModel):
    """Activity summary for a specific resource."""
    resource_type: str
    resource_id: str
    resource_name: Optional[str] = None
    total_actions: int
    last_action: datetime
    last_action_by: str
    actions_breakdown: Dict[str, int]
    recent_actions: List[AuditLogResponse]


class UserActivity(BaseModel):
    """Activity summary for a specific user."""
    user_id: str
    user_email: str
    user_name: str
    total_actions: int
    actions_today: int
    actions_this_week: int
    last_action: Optional[datetime] = None
    actions_breakdown: Dict[str, int]
    resource_types_accessed: List[str]
    recent_actions: List[AuditLogResponse]


class ComplianceReport(BaseModel):
    """Compliance-focused audit report."""
    report_period: str
    total_changes: int
    critical_changes: int
    user_access_events: int
    
    # Security events
    failed_login_attempts: int
    admin_actions: int
    data_exports: int
    
    # Change patterns
    changes_by_day: Dict[str, int]
    changes_by_user_role: Dict[str, int]
    
    # Risk indicators
    after_hours_changes: int
    bulk_changes: int
    privileged_user_changes: int
    
    # Detailed breakdowns
    critical_changes_detail: List[AuditLogResponse]
    admin_actions_detail: List[AuditLogResponse]