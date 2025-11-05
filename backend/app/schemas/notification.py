"""
Notification schemas for request/response models
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.notification import NotificationType, EmailStatus


class NotificationBase(BaseModel):
    """Base notification schema."""
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    link: Optional[str] = Field(None, max_length=500)


class NotificationCreate(NotificationBase):
    """Create notification schema."""
    user_id: str = Field(..., description="User ID to send notification to")


class NotificationUpdate(BaseModel):
    """Update notification schema."""
    is_read: bool = Field(..., description="Mark notification as read/unread")


class NotificationResponse(NotificationBase):
    """Notification response schema."""
    id: str
    user_id: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationSummary(BaseModel):
    """Notification summary for dashboard."""
    total_unread: int
    recent_notifications: List[NotificationResponse]


class BulkNotificationCreate(BaseModel):
    """Create notifications for multiple users."""
    user_ids: List[str] = Field(..., min_items=1, description="List of user IDs")
    type: NotificationType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    link: Optional[str] = Field(None, max_length=500)


class NotificationStats(BaseModel):
    """Notification statistics."""
    total_notifications: int
    unread_notifications: int
    read_notifications: int
    notifications_by_type: dict
    recent_activity: List[NotificationResponse]


# Email schemas
class EmailLogResponse(BaseModel):
    """Email log response schema."""
    id: str
    recipient_email: str
    subject: str
    body: str
    status: EmailStatus
    error_message: Optional[str]
    visa_application_id: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class EmailSendRequest(BaseModel):
    """Request to send email."""
    recipient_email: str = Field(..., description="Email address to send to")
    subject: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1)
    visa_application_id: Optional[str] = None


class NotificationPreferences(BaseModel):
    """User notification preferences."""
    email_notifications_enabled: bool = True
    visa_expiration_alerts: bool = True
    status_change_alerts: bool = True
    overdue_alerts: bool = True
    system_announcements: bool = True
    days_before_expiration: int = Field(30, ge=1, le=365, description="Days before expiration to send alert")


class SystemAnnouncement(BaseModel):
    """System-wide announcement."""
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    priority: str = Field("normal", pattern="^(low|normal|high|critical)$")
    target_roles: Optional[List[str]] = Field(None, description="Roles to send to (empty = all users)")
    expires_at: Optional[datetime] = Field(None, description="When announcement expires")