"""
Audit Log API

Provides endpoints for audit trail tracking, compliance reporting,
and system activity monitoring.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.audit import AuditAction
from app.schemas.audit import (
    AuditLogResponse, AuditLogFilter, AuditLogStats, 
    AuditLogBulkResponse, ResourceActivity, UserActivity, 
    ComplianceReport
)
from app.services.audit_service import AuditLogService

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/", response_model=AuditLogBulkResponse)
async def get_audit_logs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    user_email: Optional[str] = Query(None, description="Filter by user email"),
    action: Optional[AuditAction] = Query(None, description="Filter by action type"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    resource_id: Optional[str] = Query(None, description="Filter by specific resource ID"),
    date_from: Optional[datetime] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[datetime] = Query(None, description="Filter to date (ISO format)"),
    search: Optional[str] = Query(None, description="Search in resource names and changes"),
    ip_address: Optional[str] = Query(None, description="Filter by IP address"),
    limit: int = Query(50, ge=1, le=500, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    sort_by: str = Query("timestamp", description="Sort by field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit logs with comprehensive filtering and role-based access control.
    
    - **Beneficiaries**: Can only see their own audit logs
    - **Managers**: Can see logs for users in their reporting hierarchy
    - **PMs**: Can see logs for users in their contracts
    - **HR/Admin**: Can see all audit logs
    
    Supports filtering by user, action, resource, date range, and text search.
    """
    filters = AuditLogFilter(
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        date_from=date_from,
        date_to=date_to,
        search=search,
        ip_address=ip_address,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    audit_service = AuditLogService(db)
    
    audit_logs, total_count = audit_service.get_audit_logs(
        filters, current_user.id, current_user.role
    )
    
    has_next_page = (offset + limit) < total_count
    next_offset = offset + limit if has_next_page else None
    
    return AuditLogBulkResponse(
        total_entries=total_count,
        entries=audit_logs,
        has_next_page=has_next_page,
        next_offset=next_offset,
        filters_applied={
            "user_id": user_id,
            "action": str(action) if action else None,
            "resource_type": resource_type,
            "date_range": f"{date_from} to {date_to}" if date_from and date_to else None,
            "search": search
        }
    )


@router.get("/stats", response_model=AuditLogStats)
async def get_audit_log_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get audit log statistics and activity summaries.
    
    Returns counts, breakdowns by action/resource type, top users, and recent activity.
    Access is role-based - users see statistics for data they have access to.
    """
    audit_service = AuditLogService(db)
    
    stats = audit_service.get_audit_log_stats(current_user.id, current_user.role)
    
    return AuditLogStats(**stats)


@router.get("/resource/{resource_type}/{resource_id}", response_model=ResourceActivity)
async def get_resource_activity(
    resource_type: str,
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete activity history for a specific resource.
    
    - **resource_type**: Type of resource (visa_application, user, contract, etc.)
    - **resource_id**: Unique ID of the resource
    
    Returns activity summary, action breakdown, and recent changes.
    Access is controlled based on user's permissions to the resource.
    """
    audit_service = AuditLogService(db)
    
    activity = audit_service.get_resource_activity(
        resource_type, resource_id, current_user.id, current_user.role
    )
    
    if not activity:
        raise HTTPException(
            status_code=404,
            detail="Resource not found or access denied"
        )
    
    return activity


@router.get("/user/{user_id}", response_model=UserActivity)
async def get_user_activity(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get complete activity summary for a specific user.
    
    - **user_id**: Target user ID
    
    Returns user's action counts, resource access patterns, and recent activity.
    
    **Access Control**:
    - Beneficiaries can only see their own activity
    - Managers can see activity for users in their hierarchy
    - PMs can see activity for users in their contracts
    - HR/Admin can see all user activity
    """
    audit_service = AuditLogService(db)
    
    activity = audit_service.get_user_activity(
        user_id, current_user.id, current_user.role
    )
    
    if not activity:
        raise HTTPException(
            status_code=404,
            detail="User not found or access denied"
        )
    
    return activity


@router.get("/compliance-report", response_model=ComplianceReport)
async def generate_compliance_report(
    start_date: datetime = Query(..., description="Report start date (ISO format)"),
    end_date: datetime = Query(..., description="Report end date (ISO format)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate comprehensive compliance and security audit report.
    
    **Requires HR or ADMIN role.**
    
    - **start_date**: Beginning of report period
    - **end_date**: End of report period
    
    Returns detailed compliance metrics including:
    - Critical system changes
    - Security events and failed logins
    - After-hours and privileged user activity
    - Risk indicators and patterns
    - Detailed records for critical events
    """
    if current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Only HR and ADMIN users can generate compliance reports"
        )
    
    if end_date <= start_date:
        raise HTTPException(
            status_code=400,
            detail="End date must be after start date"
        )
    
    # Limit report period to 1 year for performance
    if (end_date - start_date).days > 365:
        raise HTTPException(
            status_code=400,
            detail="Report period cannot exceed 365 days"
        )
    
    audit_service = AuditLogService(db)
    
    try:
        report = audit_service.generate_compliance_report(
            start_date, end_date, current_user.role
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/cleanup")
async def cleanup_old_audit_logs(
    days_old: int = Query(365, ge=90, le=2555, description="Age in days to consider logs old"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up old audit logs to manage database size.
    
    **Requires ADMIN role.**
    
    - **days_old**: Age in days to consider logs old (90-2555 days)
    
    Runs as background task to avoid blocking. Use with caution as this permanently
    removes audit trail data older than the specified period.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN users can perform audit log cleanup"
        )
    
    def cleanup_logs():
        audit_service = AuditLogService(db)
        deleted_count = audit_service.cleanup_old_logs(days_old)
        return deleted_count
    
    # Run cleanup in background
    background_tasks.add_task(cleanup_logs)
    
    return {
        "message": f"Initiated cleanup of audit logs older than {days_old} days",
        "status": "processing",
        "warning": "This operation permanently removes audit trail data"
    }


# Additional endpoints for specific audit scenarios

@router.get("/security-events")
async def get_security_events(
    days_back: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get security-related audit events from recent period.
    
    **Requires HR or ADMIN role.**
    
    Returns failed logins, admin actions, privilege escalations, and other security events.
    """
    if current_user.role not in [UserRole.HR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=403,
            detail="Only HR and ADMIN users can view security events"
        )
    
    audit_service = AuditLogService(db)
    
    start_date = datetime.utcnow() - timedelta(days=days_back)
    end_date = datetime.utcnow()
    
    filters = AuditLogFilter(
        date_from=start_date,
        date_to=end_date,
        limit=200,
        sort_by="timestamp",
        sort_order="desc"
    )
    
    # Get logs for security-related actions
    security_actions = [
        AuditAction.LOGIN_FAILED,
        AuditAction.DELETE,  # Deletions are security-sensitive
        AuditAction.EXPORT   # Data exports are security-sensitive
    ]
    
    security_logs = []
    for action in security_actions:
        filters.action = action
        logs, _ = audit_service.get_audit_logs(
            filters, current_user.id, current_user.role
        )
        security_logs.extend(logs)
    
    # Sort by timestamp descending
    security_logs.sort(key=lambda x: x.timestamp, reverse=True)
    
    return {
        "period": f"Last {days_back} days",
        "total_events": len(security_logs),
        "events": security_logs[:100]  # Return top 100 most recent
    }


@router.get("/changes-summary")
async def get_changes_summary(
    resource_type: Optional[str] = Query(None, description="Filter by resource type"),
    days_back: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get summary of recent system changes.
    
    Returns overview of CREATE, UPDATE, DELETE actions by resource type and user.
    Useful for monitoring system activity patterns.
    """
    if current_user.role == UserRole.BENEFICIARY:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view system changes summary"
        )
    
    audit_service = AuditLogService(db)
    
    start_date = datetime.utcnow() - timedelta(days=days_back)
    
    filters = AuditLogFilter(
        resource_type=resource_type,
        date_from=start_date,
        limit=1000,
        sort_by="timestamp",
        sort_order="desc"
    )
    
    logs, total_count = audit_service.get_audit_logs(
        filters, current_user.id, current_user.role
    )
    
    # Summarize by action type
    action_summary = {}
    for log in logs:
        action_str = str(log.action)
        if action_str not in action_summary:
            action_summary[action_str] = 0
        action_summary[action_str] += 1
    
    # Summarize by resource type
    resource_summary = {}
    for log in logs:
        if log.resource_type not in resource_summary:
            resource_summary[log.resource_type] = 0
        resource_summary[log.resource_type] += 1
    
    return {
        "period": f"Last {days_back} days",
        "total_changes": total_count,
        "filtered_resource_type": resource_type,
        "changes_by_action": action_summary,
        "changes_by_resource_type": resource_summary,
        "recent_changes": logs[:20]  # Most recent 20 changes
    }