"""
Notifications API

Provides endpoints for managing notifications, system announcements,
and automated alerts for visa expirations and task deadlines.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.notification import Notification, NotificationType
from app.schemas.notification import (
    NotificationResponse, NotificationCreate, BulkNotificationCreate,
    SystemAnnouncement, NotificationStats, EmailSendRequest
)
from app.services.notification_service import NotificationService
from app.services.rbac_service import RBACService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False, description="Only return unread notifications"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of notifications to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notifications for the current user.
    
    - **unread_only**: Filter to only unread notifications
    - **limit**: Maximum number of notifications (1-100)
    - **offset**: Pagination offset
    """
    notification_service = NotificationService(db)
    
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        offset=offset
    )
    
    return notifications


@router.get("/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get notification statistics for the current user.
    
    Returns counts of total, read, unread notifications and breakdown by type.
    """
    notification_service = NotificationService(db)
    
    stats = notification_service.get_notification_stats(current_user.id)
    
    return NotificationStats(**stats)


@router.patch("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a specific notification as read.
    
    - **notification_id**: ID of the notification to mark as read
    """
    notification_service = NotificationService(db)
    
    notification = notification_service.mark_as_read(notification_id, current_user.id)
    
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found or access denied"
        )
    
    return {"message": "Notification marked as read", "notification_id": notification_id}


@router.patch("/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark all notifications as read for the current user.
    """
    notification_service = NotificationService(db)
    
    updated_count = notification_service.mark_all_as_read(current_user.id)
    
    return {
        "message": f"Marked {updated_count} notifications as read",
        "updated_count": updated_count
    }


@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a notification for a specific user.
    
    **Requires HR, ADMIN, or PM role to send notifications to other users.**
    Regular users can only send notifications to themselves.
    """
    # Check permissions for sending to other users
    if (notification.user_id != current_user.id and 
        current_user.role not in [UserRole.ADMIN, UserRole.HR, UserRole.PM]):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to send notifications to other users"
        )
    
    # Verify target user exists
    target_user = db.query(User).filter(User.id == notification.user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Target user not found")
    
    notification_service = NotificationService(db)
    
    created_notification = notification_service.create_notification(
        user_id=notification.user_id,
        notification_type=notification.type,
        title=notification.title,
        message=notification.message,
        link=notification.link
    )
    
    return created_notification


@router.post("/bulk", response_model=List[NotificationResponse])
async def create_bulk_notifications(
    bulk_request: BulkNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create notifications for multiple users.
    
    **Requires HR, ADMIN, or PM role.**
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.HR, UserRole.PM]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to send bulk notifications"
        )
    
    # Use RBAC to filter accessible users
    rbac_service = RBACService(db)
    accessible_user_ids = rbac_service.get_accessible_user_ids(
        current_user.id, 
        current_user.role
    )
    
    # Filter requested user IDs to only accessible ones
    valid_user_ids = [
        user_id for user_id in bulk_request.user_ids 
        if user_id in accessible_user_ids
    ]
    
    if not valid_user_ids:
        raise HTTPException(
            status_code=403,
            detail="No accessible users in the provided user ID list"
        )
    
    # Update the bulk request with filtered IDs
    bulk_request.user_ids = valid_user_ids
    
    notification_service = NotificationService(db)
    
    notifications = notification_service.create_bulk_notifications(bulk_request)
    
    return notifications


@router.post("/system-announcement", response_model=List[NotificationResponse])
async def send_system_announcement(
    announcement: SystemAnnouncement,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Send a system-wide announcement to users.
    
    **Requires ADMIN or HR role.**
    
    - **target_roles**: Optional list of roles to target. If empty, sends to all users.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.HR]:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN and HR users can send system announcements"
        )
    
    notification_service = NotificationService(db)
    
    notifications = notification_service.send_system_announcement(announcement)
    
    return notifications


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a specific notification.
    
    Users can only delete their own notifications.
    """
    # Find the notification
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=404,
            detail="Notification not found or access denied"
        )
    
    db.delete(notification)
    db.commit()
    
    return {"message": "Notification deleted successfully", "notification_id": notification_id}


@router.post("/check-expiring-visas")
async def check_expiring_visas(
    days_ahead: int = Query(30, ge=1, le=365, description="Days in advance to check for expiration"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger check for expiring visas and create notifications.
    
    **Requires HR, ADMIN, or PM role.**
    
    - **days_ahead**: Number of days in advance to check (1-365)
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.HR, UserRole.PM]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to trigger visa expiration checks"
        )
    
    def check_visas():
        notification_service = NotificationService(db)
        notifications = notification_service.check_expiring_visas(days_ahead)
        return len(notifications)
    
    # Run in background to avoid blocking
    background_tasks.add_task(check_visas)
    
    return {
        "message": f"Initiated check for visas expiring within {days_ahead} days",
        "status": "processing"
    }


@router.post("/check-overdue-todos")
async def check_overdue_todos(
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger check for overdue todos and create notifications.
    
    **Requires HR, ADMIN, or PM role.**
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.HR, UserRole.PM]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to trigger overdue todo checks"
        )
    
    def check_todos():
        notification_service = NotificationService(db)
        notifications = notification_service.check_overdue_todos()
        return len(notifications)
    
    # Run in background to avoid blocking
    background_tasks.add_task(check_todos)
    
    return {
        "message": "Initiated check for overdue todos",
        "status": "processing"
    }


@router.delete("/cleanup")
async def cleanup_old_notifications(
    days_old: int = Query(90, ge=30, le=365, description="Age in days to consider notifications old"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Clean up old read notifications.
    
    **Requires ADMIN role.**
    
    - **days_old**: Age in days to consider notifications old (30-365)
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only ADMIN users can perform cleanup operations"
        )
    
    notification_service = NotificationService(db)
    
    deleted_count = notification_service.cleanup_old_notifications(days_old)
    
    return {
        "message": f"Cleaned up {deleted_count} old notifications",
        "deleted_count": deleted_count,
        "criteria": f"Read notifications older than {days_old} days"
    }