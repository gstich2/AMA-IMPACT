"""
Audit Log Service

Provides comprehensive audit trail tracking and analysis functionality.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func, text, extract
import json

from app.models.audit import AuditLog, AuditAction
from app.models.user import User, UserRole
from app.schemas.audit import (
    AuditLogCreate, AuditLogFilter, ResourceActivity, 
    UserActivity, ComplianceReport
)
from app.services.rbac_service import RBACService


class AuditLogService:
    """Service for managing audit logs and compliance reporting."""
    
    def __init__(self, db: Session):
        self.db = db
        self.rbac_service = RBACService(db)
    
    def create_audit_log(self, audit_data: AuditLogCreate) -> AuditLog:
        """
        Create a new audit log entry.
        
        Args:
            audit_data: Audit log creation data
            
        Returns:
            Created audit log entry
        """
        # Get user information for the audit log
        user = self.db.query(User).filter(User.id == audit_data.user_id).first()
        
        audit_log = AuditLog(
            user_id=audit_data.user_id,
            action=audit_data.action,
            resource_type=audit_data.resource_type,
            resource_id=audit_data.resource_id,
            old_value=audit_data.old_values,
            new_value=audit_data.new_values,
            ip_address=audit_data.ip_address
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log
    
    def get_audit_logs(
        self, 
        filters: AuditLogFilter,
        current_user_id: str,
        current_user_role: UserRole
    ) -> Tuple[List[AuditLog], int]:
        """
        Get audit logs with filtering and role-based access control.
        
        Args:
            filters: Filter parameters
            current_user_id: Current user ID for access control
            current_user_role: Current user role for access control
            
        Returns:
            Tuple of (audit_logs, total_count)
        """
        query = self.db.query(AuditLog)
        
        # Apply role-based filtering
        if current_user_role == UserRole.BENEFICIARY:
            query = query.filter(AuditLog.user_id == current_user_id)
        elif current_user_role in [UserRole.MANAGER, UserRole.PM]:
            accessible_user_ids = self.rbac_service.get_accessible_user_ids(
                current_user_id, current_user_role
            )
            query = query.filter(AuditLog.user_id.in_(accessible_user_ids))
        
        # Apply filters
        if filters.user_id:
            query = query.filter(AuditLog.user_id == filters.user_id)
        
        if filters.action:
            query = query.filter(AuditLog.action == filters.action)
        
        if filters.resource_type:
            query = query.filter(AuditLog.resource_type == filters.resource_type)
        
        if filters.resource_id:
            query = query.filter(AuditLog.resource_id == filters.resource_id)
        
        if filters.date_from:
            query = query.filter(AuditLog.created_at >= filters.date_from)
        
        if filters.date_to:
            query = query.filter(AuditLog.created_at <= filters.date_to)
        
        if filters.ip_address:
            query = query.filter(AuditLog.ip_address == filters.ip_address)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting  
        if filters.sort_by == "action":
            sort_field = AuditLog.action
        elif filters.sort_by == "resource_type":
            sort_field = AuditLog.resource_type
        else:
            sort_field = AuditLog.created_at
        
        if filters.sort_order == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        
        # Apply pagination
        audit_logs = query.offset(filters.offset).limit(filters.limit).all()
        
        return audit_logs, total_count
    
    def get_audit_log_stats(
        self,
        current_user_id: str,
        current_user_role: UserRole
    ) -> Dict[str, Any]:
        """
        Get audit log statistics with role-based filtering.
        
        Args:
            current_user_id: Current user ID for access control
            current_user_role: Current user role for access control
            
        Returns:
            Dictionary with audit statistics
        """
        base_query = self.db.query(AuditLog)
        
        # Apply role-based filtering
        if current_user_role == UserRole.BENEFICIARY:
            base_query = base_query.filter(AuditLog.user_id == current_user_id)
        elif current_user_role in [UserRole.MANAGER, UserRole.PM]:
            accessible_user_ids = self.rbac_service.get_accessible_user_ids(
                current_user_id, current_user_role
            )
            base_query = base_query.filter(AuditLog.user_id.in_(accessible_user_ids))
        
        now = datetime.utcnow()
        today = now.date()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Basic counts
        total_entries = base_query.count()
        entries_today = base_query.filter(
            func.date(AuditLog.timestamp) == today
        ).count()
        entries_this_week = base_query.filter(
            AuditLog.timestamp >= week_ago
        ).count()
        entries_this_month = base_query.filter(
            AuditLog.timestamp >= month_ago
        ).count()
        
        # Action breakdown
        actions_breakdown = {}
        action_counts = base_query.with_entities(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action).all()
        
        for action, count in action_counts:
            actions_breakdown[str(action)] = count
        
        # Resource type breakdown
        resource_types_breakdown = {}
        resource_counts = base_query.with_entities(
            AuditLog.resource_type,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.resource_type).all()
        
        for resource_type, count in resource_counts:
            resource_types_breakdown[resource_type] = count
        
        # Top users (last 30 days)
        top_users_query = base_query.filter(
            AuditLog.timestamp >= month_ago
        ).with_entities(
            AuditLog.user_id,
            AuditLog.user_name,
            AuditLog.user_email,
            func.count(AuditLog.id).label('action_count')
        ).group_by(
            AuditLog.user_id, AuditLog.user_name, AuditLog.user_email
        ).order_by(desc('action_count')).limit(10)
        
        top_users = []
        for user_id, user_name, user_email, count in top_users_query:
            top_users.append({
                "user_id": user_id,
                "user_name": user_name,
                "user_email": user_email,
                "action_count": count
            })
        
        # Recent activity summary (last 24 hours)
        recent_query = base_query.filter(
            AuditLog.timestamp >= (now - timedelta(days=1))
        ).order_by(desc(AuditLog.timestamp)).limit(20)
        
        recent_activity = []
        for log in recent_query:
            recent_activity.append({
                "timestamp": log.timestamp,
                "user_name": log.user_name,
                "action": str(log.action),
                "resource_type": log.resource_type,
                "resource_name": log.resource_name,
                "changes_summary": log.changes_summary
            })
        
        return {
            "total_entries": total_entries,
            "entries_today": entries_today,
            "entries_this_week": entries_this_week,
            "entries_this_month": entries_this_month,
            "actions_breakdown": actions_breakdown,
            "resource_types_breakdown": resource_types_breakdown,
            "top_users": top_users,
            "recent_activity_summary": recent_activity
        }
    
    def get_resource_activity(
        self, 
        resource_type: str, 
        resource_id: str,
        current_user_id: str,
        current_user_role: UserRole
    ) -> Optional[ResourceActivity]:
        """
        Get activity summary for a specific resource.
        
        Args:
            resource_type: Type of resource
            resource_id: ID of resource
            current_user_id: Current user ID for access control
            current_user_role: Current user role for access control
            
        Returns:
            Resource activity summary or None if not found/no access
        """
        base_query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id
            )
        )
        
        # Apply role-based filtering
        if current_user_role == UserRole.BENEFICIARY:
            base_query = base_query.filter(AuditLog.user_id == current_user_id)
        elif current_user_role in [UserRole.MANAGER, UserRole.PM]:
            accessible_user_ids = self.rbac_service.get_accessible_user_ids(
                current_user_id, current_user_role
            )
            base_query = base_query.filter(AuditLog.user_id.in_(accessible_user_ids))
        
        # Check if any logs exist for this resource
        if base_query.count() == 0:
            return None
        
        # Get basic stats
        total_actions = base_query.count()
        last_log = base_query.order_by(desc(AuditLog.timestamp)).first()
        
        # Actions breakdown
        actions_breakdown = {}
        action_counts = base_query.with_entities(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action).all()
        
        for action, count in action_counts:
            actions_breakdown[str(action)] = count
        
        # Recent actions (last 20)
        recent_actions = base_query.order_by(
            desc(AuditLog.timestamp)
        ).limit(20).all()
        
        return ResourceActivity(
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=last_log.resource_name,
            total_actions=total_actions,
            last_action=last_log.timestamp,
            last_action_by=last_log.user_name,
            actions_breakdown=actions_breakdown,
            recent_actions=recent_actions
        )
    
    def get_user_activity(
        self,
        target_user_id: str,
        current_user_id: str,
        current_user_role: UserRole
    ) -> Optional[UserActivity]:
        """
        Get activity summary for a specific user.
        
        Args:
            target_user_id: User to get activity for
            current_user_id: Current user ID for access control
            current_user_role: Current user role for access control
            
        Returns:
            User activity summary or None if no access
        """
        # Check if current user can access target user's audit logs
        if current_user_role == UserRole.BENEFICIARY and target_user_id != current_user_id:
            return None
        
        if current_user_role in [UserRole.MANAGER, UserRole.PM]:
            accessible_user_ids = self.rbac_service.get_accessible_user_ids(
                current_user_id, current_user_role
            )
            if target_user_id not in accessible_user_ids:
                return None
        
        # Get target user info
        target_user = self.db.query(User).filter(User.id == target_user_id).first()
        if not target_user:
            return None
        
        base_query = self.db.query(AuditLog).filter(AuditLog.user_id == target_user_id)
        
        now = datetime.utcnow()
        today = now.date()
        week_ago = now - timedelta(days=7)
        
        # Basic counts
        total_actions = base_query.count()
        actions_today = base_query.filter(
            func.date(AuditLog.timestamp) == today
        ).count()
        actions_this_week = base_query.filter(
            AuditLog.timestamp >= week_ago
        ).count()
        
        # Last action
        last_log = base_query.order_by(desc(AuditLog.timestamp)).first()
        last_action = last_log.timestamp if last_log else None
        
        # Actions breakdown
        actions_breakdown = {}
        action_counts = base_query.with_entities(
            AuditLog.action,
            func.count(AuditLog.id).label('count')
        ).group_by(AuditLog.action).all()
        
        for action, count in action_counts:
            actions_breakdown[str(action)] = count
        
        # Resource types accessed
        resource_types = base_query.with_entities(
            AuditLog.resource_type
        ).distinct().all()
        resource_types_accessed = [rt[0] for rt in resource_types]
        
        # Recent actions (last 20)
        recent_actions = base_query.order_by(
            desc(AuditLog.timestamp)
        ).limit(20).all()
        
        return UserActivity(
            user_id=target_user_id,
            user_email=target_user.email,
            user_name=target_user.full_name,
            total_actions=total_actions,
            actions_today=actions_today,
            actions_this_week=actions_this_week,
            last_action=last_action,
            actions_breakdown=actions_breakdown,
            resource_types_accessed=resource_types_accessed,
            recent_actions=recent_actions
        )
    
    def generate_compliance_report(
        self,
        start_date: datetime,
        end_date: datetime,
        current_user_role: UserRole
    ) -> ComplianceReport:
        """
        Generate compliance-focused audit report.
        
        Args:
            start_date: Report start date
            end_date: Report end date
            current_user_role: Current user role for access control
            
        Returns:
            Compliance report
        """
        base_query = self.db.query(AuditLog).filter(
            and_(
                AuditLog.timestamp >= start_date,
                AuditLog.timestamp <= end_date
            )
        )
        
        # Only HR and ADMIN can generate full compliance reports
        if current_user_role not in [UserRole.HR, UserRole.ADMIN]:
            raise ValueError("Insufficient permissions for compliance reporting")
        
        # Basic counts
        total_changes = base_query.count()
        
        # Critical changes (CREATE, DELETE actions)
        critical_changes = base_query.filter(
            AuditLog.action.in_([AuditAction.CREATE, AuditAction.DELETE])
        ).count()
        
        # User access events (LOGIN actions)
        user_access_events = base_query.filter(
            AuditLog.action == AuditAction.LOGIN
        ).count()
        
        # Security-related metrics
        failed_login_attempts = base_query.filter(
            AuditLog.action == AuditAction.LOGIN_FAILED
        ).count()
        
        admin_actions = base_query.join(User).filter(
            User.role == UserRole.ADMIN
        ).count()
        
        data_exports = base_query.filter(
            AuditLog.action == AuditAction.EXPORT
        ).count()
        
        # Changes by day
        changes_by_day = {}
        daily_counts = base_query.with_entities(
            func.date(AuditLog.timestamp).label('date'),
            func.count(AuditLog.id).label('count')
        ).group_by(func.date(AuditLog.timestamp)).all()
        
        for date, count in daily_counts:
            changes_by_day[str(date)] = count
        
        # Changes by user role
        changes_by_user_role = {}
        role_counts = base_query.join(User).with_entities(
            User.role,
            func.count(AuditLog.id).label('count')
        ).group_by(User.role).all()
        
        for role, count in role_counts:
            changes_by_user_role[str(role)] = count
        
        # Risk indicators
        # After hours changes (before 8 AM or after 6 PM)
        after_hours_changes = base_query.filter(
            or_(
                extract('hour', AuditLog.timestamp) < 8,
                extract('hour', AuditLog.timestamp) > 18
            )
        ).count()
        
        # Bulk changes (more than 10 actions by same user in 1 hour)
        bulk_changes = 0  # This would require more complex SQL
        
        # Privileged user changes
        privileged_user_changes = base_query.join(User).filter(
            User.role.in_([UserRole.ADMIN, UserRole.HR])
        ).count()
        
        # Get detailed records for critical sections
        critical_changes_detail = base_query.filter(
            AuditLog.action.in_([AuditAction.CREATE, AuditAction.DELETE])
        ).order_by(desc(AuditLog.timestamp)).limit(50).all()
        
        admin_actions_detail = base_query.join(User).filter(
            User.role == UserRole.ADMIN
        ).order_by(desc(AuditLog.timestamp)).limit(50).all()
        
        return ComplianceReport(
            report_period=f"{start_date.date()} to {end_date.date()}",
            total_changes=total_changes,
            critical_changes=critical_changes,
            user_access_events=user_access_events,
            failed_login_attempts=failed_login_attempts,
            admin_actions=admin_actions,
            data_exports=data_exports,
            changes_by_day=changes_by_day,
            changes_by_user_role=changes_by_user_role,
            after_hours_changes=after_hours_changes,
            bulk_changes=bulk_changes,
            privileged_user_changes=privileged_user_changes,
            critical_changes_detail=critical_changes_detail,
            admin_actions_detail=admin_actions_detail
        )
    
    def cleanup_old_logs(self, days_old: int = 365) -> int:
        """
        Clean up old audit logs.
        
        Args:
            days_old: Age in days to consider logs old
            
        Returns:
            Number of logs deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted = self.db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).delete()
        
        self.db.commit()
        return deleted