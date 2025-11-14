"""
Reports Schemas

Pydantic models for various system reports and analytics.
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List, Union
from pydantic import BaseModel, Field
from enum import Enum


class ReportFormat(str, Enum):
    """Supported report export formats."""
    JSON = "json"
    CSV = "csv" 
    XLSX = "xlsx"
    PDF = "pdf"


class ReportPeriod(str, Enum):
    """Predefined report periods."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class PetitionStatusReport(BaseModel):
    """Visa application status report."""
    report_title: str
    report_period: str
    generated_at: datetime
    generated_by: str
    
    # Summary statistics
    total_applications: int
    active_applications: int
    completed_applications: int
    cancelled_applications: int
    
    # Status breakdown
    status_breakdown: Dict[str, int]
    
    # Visa type breakdown
    visa_type_breakdown: Dict[str, int]
    
    # Department breakdown
    department_breakdown: Dict[str, int]
    
    # Timeline metrics
    average_processing_time_days: Optional[float] = None
    median_processing_time_days: Optional[float] = None
    
    # Expiration tracking
    expiring_within_30_days: int
    expiring_within_60_days: int
    expiring_within_90_days: int
    expired_visas: int
    
    # Trend data (last 12 periods)
    trend_data: List[Dict[str, Any]]
    
    # Detailed records (optional for exports)
    detailed_records: Optional[List[Dict[str, Any]]] = None


class UserActivityReport(BaseModel):
    """User activity and engagement report."""
    report_title: str
    report_period: str
    generated_at: datetime
    generated_by: str
    
    # User statistics
    total_users: int
    active_users: int
    inactive_users: int
    new_users_this_period: int
    
    # Role breakdown
    users_by_role: Dict[str, int]
    
    # Department breakdown
    users_by_department: Dict[str, int]
    
    # Activity metrics
    total_logins: int
    unique_daily_users: int
    average_session_time_minutes: Optional[float] = None
    
    # Most active users
    top_active_users: List[Dict[str, Any]]
    
    # Login patterns
    login_patterns_by_day: Dict[str, int]
    login_patterns_by_hour: Dict[str, int]
    
    # Feature usage
    feature_usage_stats: Dict[str, int]
    
    # Detailed user activity (optional)
    detailed_user_activity: Optional[List[Dict[str, Any]]] = None


class ComplianceReport(BaseModel):
    """Compliance and audit report."""
    report_title: str
    report_period: str
    generated_at: datetime
    generated_by: str
    
    # Audit metrics
    total_audit_events: int
    critical_changes: int
    security_events: int
    failed_access_attempts: int
    
    # Access control metrics
    privileged_operations: int
    after_hours_changes: int
    weekend_changes: int
    
    # Data handling
    data_exports: int
    data_deletions: int
    sensitive_data_access: int
    
    # Compliance violations
    policy_violations: int
    unauthorized_access_attempts: int
    
    # Risk indicators
    high_risk_activities: List[Dict[str, Any]]
    suspicious_patterns: List[Dict[str, Any]]
    
    # Remediation actions
    actions_required: List[Dict[str, Any]]
    recommendations: List[str]


class PerformanceReport(BaseModel):
    """System performance and metrics report."""
    report_title: str
    report_period: str
    generated_at: datetime
    generated_by: str
    
    # Application metrics
    total_requests: int
    average_response_time_ms: float
    error_rate_percentage: float
    uptime_percentage: float
    
    # Database metrics
    total_records: int
    database_size_mb: float
    query_performance_ms: Dict[str, float]
    
    # User experience metrics
    page_load_times: Dict[str, float]
    feature_usage_frequency: Dict[str, int]
    user_satisfaction_score: Optional[float] = None
    
    # Resource utilization
    peak_concurrent_users: int
    average_concurrent_users: int
    storage_usage_breakdown: Dict[str, float]
    
    # Performance trends
    performance_trends: List[Dict[str, Any]]
    
    # Alerts and issues
    performance_alerts: List[Dict[str, Any]]
    resolved_issues: List[Dict[str, Any]]


class FinancialReport(BaseModel):
    """Financial and cost analysis report."""
    report_title: str
    report_period: str
    generated_at: datetime
    generated_by: str
    
    # Visa processing costs
    total_visa_processing_costs: float
    average_cost_per_application: float
    cost_by_visa_type: Dict[str, float]
    cost_by_department: Dict[str, float]
    
    # Legal fees
    total_legal_fees: float
    legal_fees_by_firm: Dict[str, float]
    legal_fees_by_case_type: Dict[str, float]
    
    # Administrative costs
    administrative_overhead: float
    technology_costs: float
    personnel_costs: float
    
    # Cost trends
    cost_trends_monthly: List[Dict[str, Any]]
    
    # Budget analysis
    budget_allocated: Optional[float] = None
    budget_used: Optional[float] = None
    budget_remaining: Optional[float] = None
    variance_analysis: Optional[Dict[str, float]] = None
    
    # ROI metrics
    time_savings_hours: Optional[float] = None
    cost_savings_amount: Optional[float] = None
    efficiency_improvements: Optional[Dict[str, float]] = None


class ReportRequest(BaseModel):
    """Base request schema for generating reports."""
    report_type: str = Field(..., description="Type of report to generate")
    start_date: Optional[date] = Field(None, description="Report start date")
    end_date: Optional[date] = Field(None, description="Report end date")
    period: ReportPeriod = Field(ReportPeriod.MONTHLY, description="Predefined period")
    format: ReportFormat = Field(ReportFormat.JSON, description="Output format")
    
    # Filters
    department_ids: Optional[List[str]] = Field(None, description="Filter by departments")
    user_roles: Optional[List[str]] = Field(None, description="Filter by user roles")
    visa_types: Optional[List[str]] = Field(None, description="Filter by visa types")
    
    # Options
    include_details: bool = Field(False, description="Include detailed records")
    include_charts: bool = Field(True, description="Include chart data")
    exclude_test_data: bool = Field(True, description="Exclude test/demo data")


class ReportResponse(BaseModel):
    """Response schema for report generation."""
    report_id: str
    report_type: str
    status: str  # "generating", "completed", "failed"
    format: ReportFormat
    
    # Metadata
    requested_at: datetime
    requested_by: str
    generated_at: Optional[datetime] = None
    
    # Report data (inline for small reports)
    report_data: Optional[Union[PetitionStatusReport, UserActivityReport, ComplianceReport, PerformanceReport, FinancialReport]] = None
    
    # File info (for large reports)
    file_url: Optional[str] = None
    file_size_mb: Optional[float] = None
    expires_at: Optional[datetime] = None
    
    # Generation info
    generation_time_ms: Optional[int] = None
    record_count: Optional[int] = None
    error_message: Optional[str] = None


class ReportList(BaseModel):
    """List of available reports."""
    reports: List[ReportResponse]
    total_reports: int
    available_report_types: List[str]


class ReportSchedule(BaseModel):
    """Scheduled report configuration."""
    id: str
    report_type: str
    name: str
    description: Optional[str] = None
    
    # Schedule settings
    frequency: str  # "daily", "weekly", "monthly"
    schedule_time: str  # "HH:MM" format
    timezone: str = "UTC"
    
    # Recipients
    recipients: List[str]  # Email addresses
    
    # Configuration
    filters: Dict[str, Any]
    format: ReportFormat
    include_details: bool
    
    # Status
    is_active: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_by: str
    created_at: datetime


class DashboardWidget(BaseModel):
    """Dashboard widget data."""
    widget_id: str
    widget_type: str  # "chart", "metric", "table", "alert"
    title: str
    description: Optional[str] = None
    
    # Data
    data: Dict[str, Any]
    
    # Display options
    chart_type: Optional[str] = None  # "bar", "line", "pie", "gauge"
    color_scheme: Optional[str] = None
    size: str = "medium"  # "small", "medium", "large"
    
    # Refresh settings
    auto_refresh: bool = True
    refresh_interval_minutes: int = 15
    last_updated: datetime


class ExecutiveSummary(BaseModel):
    """Executive summary dashboard."""
    summary_date: date
    generated_at: datetime
    
    # Key metrics
    total_petitions: int
    petitions_this_month: int
    month_over_month_growth: float
    
    # Status overview
    pending_approvals: int
    expiring_soon: int
    overdue_items: int
    
    # Performance indicators
    average_processing_time: float
    system_uptime: float
    user_satisfaction: Optional[float] = None
    
    # Financial overview
    monthly_costs: Optional[float] = None
    budget_utilization: Optional[float] = None
    
    # Alerts and recommendations
    critical_alerts: List[str]
    recommendations: List[str]
    
    # Widgets for dashboard
    widgets: List[DashboardWidget]