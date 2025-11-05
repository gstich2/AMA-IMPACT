"""
Reports Service

Comprehensive reporting and analytics service for system insights.
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, extract, case
import uuid
import statistics

from app.models.visa import VisaApplication, VisaStatus, VisaType
from app.models.user import User, UserRole
from app.models.beneficiary import Beneficiary
from app.models.department import Department
from app.models.audit import AuditLog, AuditAction
from app.models.todo import Todo, TodoStatus
from app.schemas.reports import (
    VisaStatusReport, UserActivityReport, ComplianceReport,
    PerformanceReport, ReportRequest, ReportResponse, 
    ExecutiveSummary, DashboardWidget, ReportPeriod
)
from app.services.rbac_service import RBACService


class ReportsService:
    """Service for generating comprehensive system reports and analytics."""
    
    def __init__(self, db: Session):
        self.db = db
        self.rbac_service = RBACService(db)
    
    def _get_date_range(self, period: ReportPeriod, start_date: Optional[date], end_date: Optional[date]) -> Tuple[datetime, datetime]:
        """Get date range based on period or custom dates."""
        now = datetime.utcnow()
        
        if period == ReportPeriod.CUSTOM and start_date and end_date:
            return (
                datetime.combine(start_date, datetime.min.time()),
                datetime.combine(end_date, datetime.max.time())
            )
        
        if period == ReportPeriod.DAILY:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
        elif period == ReportPeriod.WEEKLY:
            days_since_monday = now.weekday()
            start = (now - timedelta(days=days_since_monday)).replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=7)
        elif period == ReportPeriod.MONTHLY:
            start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = start + timedelta(days=32)
            end = next_month.replace(day=1)
        elif period == ReportPeriod.QUARTERLY:
            quarter = (now.month - 1) // 3 + 1
            start = datetime(now.year, (quarter - 1) * 3 + 1, 1)
            end = datetime(now.year, quarter * 3 + 1, 1) if quarter < 4 else datetime(now.year + 1, 1, 1)
        else:  # YEARLY
            start = datetime(now.year, 1, 1)
            end = datetime(now.year + 1, 1, 1)
        
        return start, end
    
    def _apply_rbac_filters(self, query, current_user_id: str, current_user_role: UserRole):
        """Apply role-based access control filters to queries."""
        if current_user_role == UserRole.BENEFICIARY:
            # Beneficiaries only see their own data
            if hasattr(query.column_descriptions[0]['type'], 'beneficiary'):
                query = query.join(Beneficiary).filter(Beneficiary.user_id == current_user_id)
            elif hasattr(query.column_descriptions[0]['type'], 'user_id'):
                query = query.filter(query.column_descriptions[0]['type'].user_id == current_user_id)
        
        elif current_user_role in [UserRole.MANAGER, UserRole.PM]:
            # Apply hierarchical filtering
            accessible_user_ids = self.rbac_service.get_accessible_user_ids(
                current_user_id, current_user_role
            )
            if hasattr(query.column_descriptions[0]['type'], 'beneficiary'):
                query = query.join(Beneficiary).filter(Beneficiary.user_id.in_(accessible_user_ids))
            elif hasattr(query.column_descriptions[0]['type'], 'user_id'):
                query = query.filter(query.column_descriptions[0]['type'].user_id.in_(accessible_user_ids))
        
        # HR and ADMIN see all data (no additional filtering)
        return query
    
    def generate_visa_status_report(
        self, 
        request: ReportRequest,
        current_user_id: str,
        current_user_role: UserRole
    ) -> VisaStatusReport:
        """Generate comprehensive visa status report."""
        start_date, end_date = self._get_date_range(request.period, request.start_date, request.end_date)
        
        # Base query
        base_query = self.db.query(VisaApplication)
        base_query = self._apply_rbac_filters(base_query, current_user_id, current_user_role)
        
        # Apply date filter
        if request.period != ReportPeriod.YEARLY:  # For yearly, include all historical data
            base_query = base_query.filter(
                VisaApplication.created_at.between(start_date, end_date)
            )
        
        # Apply additional filters
        if request.department_ids:
            base_query = base_query.join(Beneficiary).join(User).filter(
                User.department_id.in_(request.department_ids)
            )
        
        if request.visa_types:
            base_query = base_query.filter(VisaApplication.visa_type.in_(request.visa_types))
        
        # Get all applications in scope
        all_applications = base_query.all()
        total_applications = len(all_applications)
        
        # Status breakdown
        status_counts = {}
        active_count = completed_count = cancelled_count = 0
        
        for app in all_applications:
            status_str = str(app.status)
            status_counts[status_str] = status_counts.get(status_str, 0) + 1
            
            if app.status in [VisaStatus.IN_PROGRESS, VisaStatus.SUBMITTED, VisaStatus.UNDER_REVIEW]:
                active_count += 1
            elif app.status in [VisaStatus.APPROVED]:
                completed_count += 1
            elif app.status in [VisaStatus.DENIED, VisaStatus.CANCELLED]:
                cancelled_count += 1
        
        # Visa type breakdown
        visa_type_counts = {}
        for app in all_applications:
            visa_type_str = str(app.visa_type)
            visa_type_counts[visa_type_str] = visa_type_counts.get(visa_type_str, 0) + 1
        
        # Department breakdown
        dept_query = self.db.query(
            Department.name,
            func.count(VisaApplication.id).label('count')
        ).join(User, Department.id == User.department_id)\
         .join(Beneficiary, User.id == Beneficiary.user_id)\
         .join(VisaApplication, Beneficiary.id == VisaApplication.beneficiary_id)
        
        if request.period != ReportPeriod.YEARLY:
            dept_query = dept_query.filter(
                VisaApplication.created_at.between(start_date, end_date)
            )
        
        department_breakdown = {}
        for dept_name, count in dept_query.group_by(Department.name).all():
            department_breakdown[dept_name] = count
        
        # Processing time analysis (for approved applications)
        approved_apps = [app for app in all_applications if app.status == VisaStatus.APPROVED and app.approval_date]
        processing_times = []
        for app in approved_apps:
            if app.approval_date and app.created_at:
                days = (app.approval_date.date() - app.created_at.date()).days
                processing_times.append(days)
        
        avg_processing_time = statistics.mean(processing_times) if processing_times else None
        median_processing_time = statistics.median(processing_times) if processing_times else None
        
        # Expiration analysis
        today = date.today()
        expiring_30 = expiring_60 = expiring_90 = expired = 0
        
        for app in all_applications:
            if app.expiration_date:
                days_to_expiry = (app.expiration_date - today).days
                if days_to_expiry < 0:
                    expired += 1
                elif days_to_expiry <= 30:
                    expiring_30 += 1
                elif days_to_expiry <= 60:
                    expiring_60 += 1
                elif days_to_expiry <= 90:
                    expiring_90 += 1
        
        # Trend data (last 12 periods)
        trend_data = []
        for i in range(12):
            period_start = start_date - timedelta(days=30 * i)  # Approximate monthly periods
            period_end = start_date - timedelta(days=30 * (i-1)) if i > 0 else end_date
            
            period_count = base_query.filter(
                VisaApplication.created_at.between(period_start, period_end)
            ).count()
            
            trend_data.append({
                "period": period_start.strftime("%Y-%m"),
                "applications": period_count
            })
        
        trend_data.reverse()  # Chronological order
        
        # Detailed records (if requested)
        detailed_records = None
        if request.include_details:
            detailed_records = []
            for app in all_applications[:1000]:  # Limit to 1000 records
                detailed_records.append({
                    "id": app.id,
                    "beneficiary_name": app.beneficiary.full_name,
                    "visa_type": str(app.visa_type),
                    "status": str(app.status),
                    "created_at": app.created_at.isoformat(),
                    "expiration_date": app.expiration_date.isoformat() if app.expiration_date else None,
                    "priority": str(app.priority),
                    "company_case_id": app.company_case_id
                })
        
        return VisaStatusReport(
            report_title=f"Visa Status Report - {request.period.value.title()}",
            report_period=f"{start_date.date()} to {end_date.date()}",
            generated_at=datetime.utcnow(),
            generated_by=current_user_id,
            total_applications=total_applications,
            active_applications=active_count,
            completed_applications=completed_count,
            cancelled_applications=cancelled_count,
            status_breakdown=status_counts,
            visa_type_breakdown=visa_type_counts,
            department_breakdown=department_breakdown,
            average_processing_time_days=avg_processing_time,
            median_processing_time_days=median_processing_time,
            expiring_within_30_days=expiring_30,
            expiring_within_60_days=expiring_60,
            expiring_within_90_days=expiring_90,
            expired_visas=expired,
            trend_data=trend_data,
            detailed_records=detailed_records
        )
    
    def generate_user_activity_report(
        self,
        request: ReportRequest,
        current_user_id: str,
        current_user_role: UserRole
    ) -> UserActivityReport:
        """Generate user activity and engagement report."""
        start_date, end_date = self._get_date_range(request.period, request.start_date, request.end_date)
        
        # Base user query
        users_query = self.db.query(User).filter(User.is_active == True)
        
        if current_user_role in [UserRole.MANAGER, UserRole.PM]:
            accessible_user_ids = self.rbac_service.get_accessible_user_ids(
                current_user_id, current_user_role
            )
            users_query = users_query.filter(User.id.in_(accessible_user_ids))
        elif current_user_role == UserRole.BENEFICIARY:
            users_query = users_query.filter(User.id == current_user_id)
        
        # Apply filters
        if request.department_ids:
            users_query = users_query.filter(User.department_id.in_(request.department_ids))
        
        if request.user_roles:
            users_query = users_query.filter(User.role.in_(request.user_roles))
        
        all_users = users_query.all()
        total_users = len(all_users)
        
        # New users in period
        new_users = users_query.filter(
            User.created_at.between(start_date, end_date)
        ).count()
        
        # Role breakdown
        role_breakdown = {}
        for user in all_users:
            role_str = str(user.role)
            role_breakdown[role_str] = role_breakdown.get(role_str, 0) + 1
        
        # Department breakdown
        dept_breakdown = {}
        for user in all_users:
            if user.department:
                dept_name = user.department.name
                dept_breakdown[dept_name] = dept_breakdown.get(dept_name, 0) + 1
        
        # Activity metrics from audit logs
        audit_query = self.db.query(AuditLog).filter(
            AuditLog.timestamp.between(start_date, end_date)
        )
        
        if current_user_role != UserRole.ADMIN and current_user_role != UserRole.HR:
            accessible_user_ids = [user.id for user in all_users]
            audit_query = audit_query.filter(AuditLog.user_id.in_(accessible_user_ids))
        
        # Login metrics
        login_logs = audit_query.filter(AuditLog.action == AuditAction.LOGIN).all()
        total_logins = len(login_logs)
        unique_daily_users = len(set(log.user_id for log in login_logs))
        
        # Top active users
        user_activity = {}
        for log in audit_query.all():
            if log.user_id not in user_activity:
                user_activity[log.user_id] = {"count": 0, "user_name": log.user_name}
            user_activity[log.user_id]["count"] += 1
        
        top_active_users = []
        for user_id, data in sorted(user_activity.items(), key=lambda x: x[1]["count"], reverse=True)[:10]:
            top_active_users.append({
                "user_id": user_id,
                "user_name": data["user_name"],
                "activity_count": data["count"]
            })
        
        # Login patterns
        login_by_day = {}
        login_by_hour = {}
        for log in login_logs:
            day_name = log.timestamp.strftime("%A")
            hour = log.timestamp.hour
            
            login_by_day[day_name] = login_by_day.get(day_name, 0) + 1
            login_by_hour[str(hour)] = login_by_hour.get(str(hour), 0) + 1
        
        # Feature usage (based on resource types accessed)
        feature_usage = {}
        for log in audit_query.all():
            resource = log.resource_type
            feature_usage[resource] = feature_usage.get(resource, 0) + 1
        
        return UserActivityReport(
            report_title=f"User Activity Report - {request.period.value.title()}",
            report_period=f"{start_date.date()} to {end_date.date()}",
            generated_at=datetime.utcnow(),
            generated_by=current_user_id,
            total_users=total_users,
            active_users=unique_daily_users,
            inactive_users=total_users - unique_daily_users,
            new_users_this_period=new_users,
            users_by_role=role_breakdown,
            users_by_department=dept_breakdown,
            total_logins=total_logins,
            unique_daily_users=unique_daily_users,
            top_active_users=top_active_users,
            login_patterns_by_day=login_by_day,
            login_patterns_by_hour=login_by_hour,
            feature_usage_stats=feature_usage
        )
    
    def generate_executive_summary(
        self,
        current_user_id: str,
        current_user_role: UserRole
    ) -> ExecutiveSummary:
        """Generate executive dashboard summary."""
        today = date.today()
        this_month_start = today.replace(day=1)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # Base queries with RBAC
        visa_query = self.db.query(VisaApplication)
        visa_query = self._apply_rbac_filters(visa_query, current_user_id, current_user_role)
        
        # Key metrics
        total_visas = visa_query.count()
        this_month_visas = visa_query.filter(
            VisaApplication.created_at >= datetime.combine(this_month_start, datetime.min.time())
        ).count()
        
        last_month_visas = visa_query.filter(
            and_(
                VisaApplication.created_at >= datetime.combine(last_month_start, datetime.min.time()),
                VisaApplication.created_at < datetime.combine(this_month_start, datetime.min.time())
            )
        ).count()
        
        # Month-over-month growth
        mom_growth = ((this_month_visas - last_month_visas) / max(last_month_visas, 1)) * 100
        
        # Status overview
        pending_approvals = visa_query.filter(
            VisaApplication.status.in_([VisaStatus.SUBMITTED, VisaStatus.UNDER_REVIEW])
        ).count()
        
        expiring_soon = visa_query.filter(
            and_(
                VisaApplication.expiration_date.isnot(None),
                VisaApplication.expiration_date <= today + timedelta(days=30),
                VisaApplication.expiration_date >= today
            )
        ).count()
        
        # Overdue items (todos)
        overdue_todos = self.db.query(Todo).filter(
            and_(
                Todo.due_date < today,
                Todo.status != TodoStatus.COMPLETED
            )
        ).count()
        
        # Performance metrics
        approved_visas = visa_query.filter(VisaApplication.status == VisaStatus.APPROVED).all()
        processing_times = []
        for visa in approved_visas:
            if visa.approval_date and visa.created_at:
                days = (visa.approval_date.date() - visa.created_at.date()).days
                processing_times.append(days)
        
        avg_processing = statistics.mean(processing_times) if processing_times else 0
        
        # Alerts and recommendations
        alerts = []
        recommendations = []
        
        if expiring_soon > 0:
            alerts.append(f"{expiring_soon} visas expiring within 30 days")
        
        if overdue_todos > 0:
            alerts.append(f"{overdue_todos} overdue tasks require attention")
        
        if mom_growth < -10:
            recommendations.append("Investigate decline in visa applications")
        
        if avg_processing > 45:
            recommendations.append("Review processing workflow for efficiency improvements")
        
        # Create dashboard widgets
        widgets = [
            DashboardWidget(
                widget_id="total_applications",
                widget_type="metric",
                title="Total Applications",
                data={"value": total_visas, "trend": "up" if mom_growth > 0 else "down"},
                size="medium",
                last_updated=datetime.utcnow()
            ),
            DashboardWidget(
                widget_id="monthly_growth",
                widget_type="chart",
                title="Monthly Growth",
                chart_type="line",
                data={
                    "current_month": this_month_visas,
                    "last_month": last_month_visas,
                    "growth_rate": round(mom_growth, 2)
                },
                size="large",
                last_updated=datetime.utcnow()
            ),
            DashboardWidget(
                widget_id="status_overview",
                widget_type="chart",
                title="Status Overview",
                chart_type="pie",
                data={
                    "pending": pending_approvals,
                    "expiring_soon": expiring_soon,
                    "overdue": overdue_todos
                },
                size="medium",
                last_updated=datetime.utcnow()
            )
        ]
        
        return ExecutiveSummary(
            summary_date=today,
            generated_at=datetime.utcnow(),
            total_visa_applications=total_visas,
            applications_this_month=this_month_visas,
            month_over_month_growth=round(mom_growth, 2),
            pending_approvals=pending_approvals,
            expiring_soon=expiring_soon,
            overdue_items=overdue_todos,
            average_processing_time=round(avg_processing, 1),
            system_uptime=99.5,  # Would be calculated from monitoring data
            critical_alerts=alerts,
            recommendations=recommendations,
            widgets=widgets
        )
    
    def get_available_report_types(self, current_user_role: UserRole) -> List[str]:
        """Get list of available report types based on user role."""
        base_reports = [
            "visa_status",
            "user_activity", 
            "executive_summary"
        ]
        
        if current_user_role in [UserRole.HR, UserRole.ADMIN]:
            base_reports.extend([
                "compliance",
                "performance", 
                "financial"
            ])
        
        if current_user_role in [UserRole.PM, UserRole.MANAGER]:
            base_reports.extend([
                "department_performance"
            ])
        
        return sorted(base_reports)