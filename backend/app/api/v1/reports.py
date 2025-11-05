"""
Reports API

Comprehensive reporting and analytics endpoints for system insights,
compliance tracking, and executive dashboards.
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.schemas.reports import (
    ReportRequest, ReportResponse, VisaStatusReport, UserActivityReport,
    ComplianceReport, ExecutiveSummary, ReportFormat, ReportPeriod,
    ReportList, DashboardWidget
)
from app.services.reports_service import ReportsService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/types")
async def get_available_report_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of available report types based on user role.
    
    Returns different report types depending on user permissions:
    - **Beneficiaries**: Basic personal reports
    - **Managers/PMs**: Team and departmental reports  
    - **HR/Admin**: All reports including compliance and financial
    """
    reports_service = ReportsService(db)
    
    available_types = reports_service.get_available_report_types(current_user.role)
    
    return {
        "available_reports": available_types,
        "user_role": str(current_user.role),
        "total_types": len(available_types)
    }


@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate a comprehensive system report.
    
    **Supported Report Types:**
    - `visa_status`: Visa applications status and analytics
    - `user_activity`: User engagement and activity patterns
    - `executive_summary`: High-level dashboard summary
    - `compliance`: Audit and compliance report (HR/Admin only)
    - `performance`: System performance metrics (HR/Admin only)
    - `financial`: Cost analysis and budget tracking (HR/Admin only)
    
    **Access Control:**
    Reports are filtered based on user role and accessible data scope.
    """
    reports_service = ReportsService(db)
    
    # Validate report type access
    available_types = reports_service.get_available_report_types(current_user.role)
    if request.report_type not in available_types:
        raise HTTPException(
            status_code=403,
            detail=f"Report type '{request.report_type}' not available for role {current_user.role}"
        )
    
    # Generate report ID
    report_id = str(uuid.uuid4())
    
    # For small reports, generate inline
    if request.format == ReportFormat.JSON and not request.include_details:
        try:
            if request.report_type == "visa_status":
                report_data = reports_service.generate_visa_status_report(
                    request, current_user.id, current_user.role
                )
            elif request.report_type == "user_activity":
                report_data = reports_service.generate_user_activity_report(
                    request, current_user.id, current_user.role
                )
            elif request.report_type == "executive_summary":
                report_data = reports_service.generate_executive_summary(
                    current_user.id, current_user.role
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Report type '{request.report_type}' not implemented"
                )
            
            return ReportResponse(
                report_id=report_id,
                report_type=request.report_type,
                status="completed",
                format=request.format,
                requested_at=datetime.utcnow(),
                requested_by=current_user.email,
                generated_at=datetime.utcnow(),
                report_data=report_data,
                generation_time_ms=100,  # Would be measured in real implementation
                record_count=getattr(report_data, 'total_applications', 0) if hasattr(report_data, 'total_applications') else 0
            )
            
        except Exception as e:
            return ReportResponse(
                report_id=report_id,
                report_type=request.report_type,
                status="failed",
                format=request.format,
                requested_at=datetime.utcnow(),
                requested_by=current_user.email,
                error_message=str(e)
            )
    
    # For large reports, generate in background
    def generate_background_report():
        # This would implement actual file generation and storage
        # For now, return a placeholder response
        return f"report_{report_id}.{request.format.value}"
    
    background_tasks.add_task(generate_background_report)
    
    return ReportResponse(
        report_id=report_id,
        report_type=request.report_type,
        status="generating",
        format=request.format,
        requested_at=datetime.utcnow(),
        requested_by=current_user.email,
        file_url=f"/api/v1/reports/{report_id}/download",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )


@router.get("/visa-status", response_model=VisaStatusReport)
async def get_visa_status_report(
    period: ReportPeriod = Query(ReportPeriod.MONTHLY, description="Report period"),
    start_date: Optional[date] = Query(None, description="Custom start date (for custom period)"),
    end_date: Optional[date] = Query(None, description="Custom end date (for custom period)"),
    department_ids: Optional[str] = Query(None, description="Comma-separated department IDs"),
    visa_types: Optional[str] = Query(None, description="Comma-separated visa types"),
    include_details: bool = Query(False, description="Include detailed application records"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate detailed visa status report with analytics.
    
    Provides comprehensive visa application statistics including:
    - Status breakdown and trends
    - Processing time analytics
    - Expiration tracking
    - Department and visa type analysis
    
    Data is filtered based on user's role and accessible scope.
    """
    reports_service = ReportsService(db)
    
    # Parse comma-separated filters
    dept_list = department_ids.split(',') if department_ids else None
    visa_list = visa_types.split(',') if visa_types else None
    
    request = ReportRequest(
        report_type="visa_status",
        period=period,
        start_date=start_date,
        end_date=end_date,
        department_ids=dept_list,
        visa_types=visa_list,
        include_details=include_details
    )
    
    return reports_service.generate_visa_status_report(
        request, current_user.id, current_user.role
    )


@router.get("/user-activity", response_model=UserActivityReport)
async def get_user_activity_report(
    period: ReportPeriod = Query(ReportPeriod.MONTHLY, description="Report period"),
    start_date: Optional[date] = Query(None, description="Custom start date"),
    end_date: Optional[date] = Query(None, description="Custom end date"),
    department_ids: Optional[str] = Query(None, description="Filter by departments"),
    user_roles: Optional[str] = Query(None, description="Filter by user roles"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate user activity and engagement report.
    
    Analyzes user behavior patterns including:
    - Login frequency and patterns
    - Feature usage statistics
    - Most active users
    - Engagement trends
    
    **Access Control:**
    - Beneficiaries see only their own activity
    - Managers see team member activity
    - HR/Admin see all user activity
    """
    reports_service = ReportsService(db)
    
    # Parse filters
    dept_list = department_ids.split(',') if department_ids else None
    role_list = user_roles.split(',') if user_roles else None
    
    request = ReportRequest(
        report_type="user_activity",
        period=period,
        start_date=start_date,
        end_date=end_date,
        department_ids=dept_list,
        user_roles=role_list
    )
    
    return reports_service.generate_user_activity_report(
        request, current_user.id, current_user.role
    )


@router.get("/executive-summary", response_model=ExecutiveSummary)
async def get_executive_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate executive dashboard summary with key metrics.
    
    Provides high-level overview including:
    - Key performance indicators
    - Monthly growth trends  
    - Critical alerts and recommendations
    - Interactive dashboard widgets
    
    Perfect for executive dashboards and management reporting.
    """
    reports_service = ReportsService(db)
    
    return reports_service.generate_executive_summary(
        current_user.id, current_user.role
    )


@router.get("/dashboard/widgets")
async def get_dashboard_widgets(
    widget_types: Optional[str] = Query(None, description="Comma-separated widget types"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard widgets for real-time monitoring.
    
    Returns configurable widgets for dashboard display:
    - Metric widgets (KPI values)
    - Chart widgets (trends and breakdowns)
    - Alert widgets (critical notifications)
    - Table widgets (recent activity)
    """
    reports_service = ReportsService(db)
    
    # Get executive summary to extract widgets
    summary = reports_service.generate_executive_summary(
        current_user.id, current_user.role
    )
    
    widgets = summary.widgets
    
    # Filter by requested widget types
    if widget_types:
        requested_types = widget_types.split(',')
        widgets = [w for w in widgets if w.widget_type in requested_types]
    
    return {
        "widgets": widgets,
        "total_widgets": len(widgets),
        "last_updated": datetime.utcnow(),
        "refresh_interval": 300  # 5 minutes
    }


@router.get("/{report_id}/status", response_model=ReportResponse)
async def get_report_status(
    report_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of a background report generation.
    
    Returns current status and download information for async reports.
    """
    # In a real implementation, this would check a database or cache
    # for the report generation status
    
    return ReportResponse(
        report_id=report_id,
        report_type="visa_status",  # Would be retrieved from storage
        status="completed",
        format=ReportFormat.CSV,
        requested_at=datetime.utcnow() - timedelta(minutes=5),
        requested_by=current_user.email,
        generated_at=datetime.utcnow() - timedelta(minutes=2),
        file_url=f"/api/v1/reports/{report_id}/download",
        file_size_mb=2.3,
        expires_at=datetime.utcnow() + timedelta(days=7),
        generation_time_ms=120000,
        record_count=1250
    )


@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download a generated report file.
    
    Supports CSV, Excel, and PDF formats based on the original request.
    Files are automatically cleaned up after expiration.
    """
    # In a real implementation, this would:
    # 1. Validate report ownership/access
    # 2. Check if file exists and hasn't expired
    # 3. Return file using FileResponse
    
    raise HTTPException(
        status_code=501,
        detail="Report download not implemented in this demo"
    )


@router.get("/analytics/trends")
async def get_analytics_trends(
    metric: str = Query(..., description="Metric to analyze (applications, users, processing_time)"),
    period_days: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    granularity: str = Query("daily", pattern="^(daily|weekly|monthly)$", description="Data granularity"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get trend analysis for key metrics.
    
    Provides time-series data for dashboard charts and analytics.
    
    **Supported Metrics:**
    - `applications`: Visa application counts over time
    - `users`: User registration and activity trends  
    - `processing_time`: Average processing time trends
    - `completion_rate`: Application completion rates
    """
    if current_user.role == UserRole.BENEFICIARY:
        raise HTTPException(
            status_code=403,
            detail="Analytics trends not available for beneficiary users"
        )
    
    # Generate sample trend data (in real implementation, would query database)
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=period_days)
    
    trend_data = []
    current_date = start_date
    
    while current_date <= end_date:
        if granularity == "daily":
            increment = timedelta(days=1)
        elif granularity == "weekly":
            increment = timedelta(weeks=1)
        else:  # monthly
            increment = timedelta(days=30)
        
        # Generate sample values based on metric type
        if metric == "applications":
            value = 25 + (current_date.day % 10)  # Sample data
        elif metric == "users":
            value = 5 + (current_date.day % 3)
        elif metric == "processing_time":
            value = 35.5 + (current_date.day % 15)
        else:
            value = 85.2 + (current_date.day % 20)
        
        trend_data.append({
            "date": current_date.isoformat(),
            "value": value,
            "metric": metric
        })
        
        current_date += increment
    
    return {
        "metric": metric,
        "period_days": period_days,
        "granularity": granularity,
        "data_points": len(trend_data),
        "trend_data": trend_data,
        "generated_at": datetime.utcnow()
    }


@router.delete("/cleanup")
async def cleanup_old_reports(
    days_old: int = Query(30, ge=7, le=365, description="Age in days to consider reports old"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up old generated report files.
    
    **Requires ADMIN role.**
    
    Removes expired report files to manage storage space.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN users can perform report cleanup"
        )
    
    # In real implementation, would clean up file storage
    cleaned_count = 15  # Sample count
    
    return {
        "message": f"Cleaned up reports older than {days_old} days",
        "files_removed": cleaned_count,
        "storage_freed_mb": cleaned_count * 2.1
    }