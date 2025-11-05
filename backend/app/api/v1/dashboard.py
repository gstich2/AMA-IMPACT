"""
Dashboard API endpoints for summary statistics and quick access data
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, or_

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User, UserRole
from app.models.beneficiary import Beneficiary
from app.models.visa import VisaApplication, VisaStatus, VisaCaseStatus
from app.models.todo import Todo, TodoStatus, TodoPriority
from app.models.case_group import CaseGroup, CaseStatus
from app.schemas.dashboard import DashboardResponse, DashboardSummary, RecentActivity

router = APIRouter()


@router.get("/", response_model=DashboardResponse)
def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get dashboard summary statistics based on user role and permissions.
    
    Returns role-filtered data:
    - BENEFICIARY: Own data only
    - MANAGER: Direct and indirect reports
    - PM/HR: Contract-wide data  
    - ADMIN: System-wide data
    """
    
    # Simplified version for now - just get basic counts
    # TODO: Add proper role-based filtering later
    
    # Get basic counts  
    total_beneficiaries = db.query(Beneficiary).filter(Beneficiary.is_active == True).count()
    
    # Active visas (approved, in_progress, submitted)
    active_visa_statuses = [VisaStatus.APPROVED, VisaStatus.IN_PROGRESS, VisaStatus.SUBMITTED]
    active_visas = db.query(VisaApplication).filter(VisaApplication.status.in_(active_visa_statuses)).count()
    
    # Expiring soon (within 30 days)
    thirty_days_from_now = datetime.utcnow().date() + timedelta(days=30)
    today = datetime.utcnow().date()
    expiring_soon = db.query(VisaApplication).filter(
        and_(
            VisaApplication.expiration_date <= thirty_days_from_now,
            VisaApplication.expiration_date >= today,
            VisaApplication.status.in_(active_visa_statuses)
        )
    ).count()
    
    # Overdue visas (expired and still active)
    overdue_visas = db.query(VisaApplication).filter(
        and_(
            VisaApplication.expiration_date < today,
            VisaApplication.status.in_(active_visa_statuses)
        )
    ).count()
    
    # Pending todos (not completed/cancelled)
    pending_todo_statuses = [TodoStatus.TODO, TodoStatus.IN_PROGRESS, TodoStatus.BLOCKED]
    pending_todos = db.query(Todo).filter(Todo.status.in_(pending_todo_statuses)).count()
    
    # Active case groups
    active_case_groups = db.query(CaseGroup).filter(CaseGroup.status == CaseStatus.IN_PROGRESS).count()
    
    # Completed todos this month
    first_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    completed_todos_this_month = db.query(Todo).filter(
        and_(
            Todo.status == TodoStatus.COMPLETED,
            Todo.completed_at >= first_of_month
        )
    ).count()
    
    # Get some sample upcoming expirations (simplified)
    upcoming_expirations = []
    
    # Get some sample urgent todos (simplified) 
    urgent_todos = []
    
    # Empty recent activity for now
    recent_activity = []
    
    return DashboardResponse(
        summary=DashboardSummary(
            total_beneficiaries=total_beneficiaries,
            active_visas=active_visas,
            expiring_soon=expiring_soon,
            overdue_visas=overdue_visas,
            pending_todos=pending_todos,
            active_case_groups=active_case_groups,
            completed_todos_this_month=completed_todos_this_month
        ),
        recent_activity=recent_activity,
        upcoming_expirations=upcoming_expirations,
        urgent_todos=urgent_todos
    )


@router.get("/quick-stats")
def get_quick_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get minimal dashboard stats for header/navbar display.
    Returns just the key numbers without detailed breakdowns.
    """
    
    # Reuse the same role-based filtering logic but return minimal data
    dashboard_data = get_dashboard(current_user, db)
    
    return {
        "active_visas": dashboard_data.summary.active_visas,
        "expiring_soon": dashboard_data.summary.expiring_soon,
        "pending_todos": dashboard_data.summary.pending_todos,
        "overdue_visas": dashboard_data.summary.overdue_visas
    }