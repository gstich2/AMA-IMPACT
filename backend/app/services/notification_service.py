"""
Notification Service

Handles creation, management, and delivery of notifications.
Supports both in-app notifications and email alerts.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.notification import Notification, NotificationType, EmailLog, EmailStatus
from app.models.user import User, UserRole
from app.models.petition import Petition, PetitionStatus
from app.models.todo import Todo, TodoStatus
from app.schemas.notification import (
    NotificationCreate, BulkNotificationCreate, SystemAnnouncement
)


class NotificationService:
    """Service for managing notifications and alerts."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self, 
        user_id: str, 
        notification_type: NotificationType,
        title: str, 
        message: str, 
        link: Optional[str] = None
    ) -> Notification:
        """
        Create a single notification for a user.
        
        Args:
            user_id: Target user ID
            notification_type: Type of notification
            title: Notification title
            message: Notification message
            link: Optional link to relevant resource
            
        Returns:
            Created notification
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            link=link
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        return notification
    
    def create_bulk_notifications(self, bulk_request: BulkNotificationCreate) -> List[Notification]:
        """
        Create notifications for multiple users.
        
        Args:
            bulk_request: Bulk notification request
            
        Returns:
            List of created notifications
        """
        notifications = []
        
        for user_id in bulk_request.user_ids:
            notification = Notification(
                user_id=user_id,
                type=bulk_request.type,
                title=bulk_request.title,
                message=bulk_request.message,
                link=bulk_request.link
            )
            notifications.append(notification)
        
        self.db.add_all(notifications)
        self.db.commit()
        
        for notification in notifications:
            self.db.refresh(notification)
        
        return notifications
    
    def send_system_announcement(self, announcement: SystemAnnouncement) -> List[Notification]:
        """
        Send system-wide announcement to users.
        
        Args:
            announcement: System announcement details
            
        Returns:
            List of created notifications
        """
        # Build user query based on target roles
        user_query = self.db.query(User).filter(User.is_active == True)
        
        if announcement.target_roles:
            user_query = user_query.filter(User.role.in_(announcement.target_roles))
        
        users = user_query.all()
        user_ids = [user.id for user in users]
        
        if not user_ids:
            return []
        
        # Create bulk notification
        bulk_request = BulkNotificationCreate(
            user_ids=user_ids,
            type=NotificationType.SYSTEM,
            title=announcement.title,
            message=announcement.message,
            link=None
        )
        
        return self.create_bulk_notifications(bulk_request)
    
    def check_expiring_petitions(self, days_ahead: int = 30) -> List[Notification]:
        """
        Check for expiring petitions and create notifications.
        
        Args:
            days_ahead: Days in advance to notify about expiration
            
        Returns:
            List of created notifications
        """
        cutoff_date = (datetime.utcnow() + timedelta(days=days_ahead)).date()
        today = datetime.utcnow().date()
        
        # Find petitions expiring within the timeframe
        expiring_petitions = self.db.query(Petition).filter(
            and_(
                Petition.expiration_date.isnot(None),
                Petition.expiration_date <= cutoff_date,
                Petition.expiration_date >= today,
                Petition.status.in_([
                    PetitionStatus.APPROVED, PetitionStatus.IN_PROGRESS, PetitionStatus.SUBMITTED
                ])
            )
        ).all()
        
        notifications = []
        
        for petition in expiring_petitions:
            # Check if notification already exists for this petition
            existing = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == petition.beneficiary.user_id,
                    Notification.type == NotificationType.VISA_EXPIRING,
                    Notification.link == f"/petitions/{petition.id}"
                )
            ).first()
            
            if existing:
                continue  # Skip if already notified
            
            days_until_expiry = (petition.expiration_date - today).days
            
            if days_until_expiry < 0:
                # Overdue
                title = f"URGENT: {petition.petition_type} Petition Expired"
                message = f"Your {petition.petition_type} petition expired {abs(days_until_expiry)} days ago. Immediate action required."
                notification_type = NotificationType.OVERDUE
            elif days_until_expiry <= 7:
                # Critical - within a week
                title = f"CRITICAL: {petition.petition_type} Petition Expires in {days_until_expiry} days"
                message = f"Your {petition.petition_type} petition expires on {petition.expiration_date.strftime('%B %d, %Y')}. Please take immediate action."
                notification_type = NotificationType.VISA_EXPIRING
            else:
                # Standard expiration warning
                title = f"{petition.petition_type} Petition Expiring Soon"
                message = f"Your {petition.petition_type} petition expires on {petition.expiration_date.strftime('%B %d, %Y')} ({days_until_expiry} days). Please plan for renewal."
                notification_type = NotificationType.VISA_EXPIRING
            
            notification = self.create_notification(
                user_id=petition.beneficiary.user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                link=f"/petitions/{petition.id}"
            )
            
            notifications.append(notification)
        
        return notifications
    
    def check_overdue_todos(self) -> List[Notification]:
        """
        Check for overdue todos and create notifications.
        
        Returns:
            List of created notifications
        """
        today = datetime.utcnow().date()
        
        # Find overdue todos
        overdue_todos = self.db.query(Todo).filter(
            and_(
                Todo.due_date < today,
                Todo.status.in_([TodoStatus.TODO, TodoStatus.IN_PROGRESS])
            )
        ).all()
        
        notifications = []
        
        for todo in overdue_todos:
            # Check if notification already exists for this todo
            existing = self.db.query(Notification).filter(
                and_(
                    Notification.user_id == todo.assigned_to_user_id,
                    Notification.type == NotificationType.OVERDUE,
                    Notification.link == f"/todos/{todo.id}"
                )
            ).first()
            
            if existing:
                continue  # Skip if already notified
            
            days_overdue = (today - todo.due_date).days
            
            title = f"Overdue Task: {todo.title}"
            message = f"Task '{todo.title}' is {days_overdue} days overdue. Please update or complete."
            
            notification = self.create_notification(
                user_id=todo.assigned_to_user_id,
                notification_type=NotificationType.OVERDUE,
                title=title,
                message=message,
                link=f"/todos/{todo.id}"
            )
            
            notifications.append(notification)
        
        return notifications
    
    def notify_status_change(
        self, 
        user_id: str, 
        resource_type: str,
        resource_id: str,
        old_status: str,
        new_status: str,
        resource_name: str
    ) -> Notification:
        """
        Create notification for status changes.
        
        Args:
            user_id: User to notify
            resource_type: Type of resource (visa, todo, etc.)
            resource_id: ID of the resource
            old_status: Previous status
            new_status: New status
            resource_name: Human-readable resource name
            
        Returns:
            Created notification
        """
        title = f"{resource_type.title()} Status Updated"
        message = f"{resource_name} status changed from '{old_status}' to '{new_status}'"
        link = f"/{resource_type}s/{resource_id}"
        
        return self.create_notification(
            user_id=user_id,
            notification_type=NotificationType.STATUS_CHANGED,
            title=title,
            message=message,
            link=link
        )
    
    def get_user_notifications(
        self, 
        user_id: str, 
        unread_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum number to return
            offset: Offset for pagination
            
        Returns:
            List of notifications
        """
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        return query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
    
    def mark_as_read(self, notification_id: str, user_id: str) -> Optional[Notification]:
        """
        Mark notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for security)
            
        Returns:
            Updated notification or None if not found
        """
        notification = self.db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        ).first()
        
        if notification:
            notification.is_read = True
            self.db.commit()
            self.db.refresh(notification)
        
        return notification
    
    def mark_all_as_read(self, user_id: str) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of notifications updated
        """
        updated = self.db.query(Notification).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).update({Notification.is_read: True})
        
        self.db.commit()
        return updated
    
    def get_notification_stats(self, user_id: str) -> Dict:
        """
        Get notification statistics for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with notification statistics
        """
        total = self.db.query(func.count(Notification.id)).filter(
            Notification.user_id == user_id
        ).scalar()
        
        unread = self.db.query(func.count(Notification.id)).filter(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        ).scalar()
        
        # Count by type
        type_counts = self.db.query(
            Notification.type,
            func.count(Notification.id)
        ).filter(
            Notification.user_id == user_id
        ).group_by(Notification.type).all()
        
        type_stats = {str(type_name): count for type_name, count in type_counts}
        
        return {
            "total_notifications": total or 0,
            "unread_notifications": unread or 0,
            "read_notifications": (total or 0) - (unread or 0),
            "notifications_by_type": type_stats
        }
    
    def cleanup_old_notifications(self, days_old: int = 90) -> int:
        """
        Clean up old read notifications.
        
        Args:
            days_old: Age in days to consider notifications old
            
        Returns:
            Number of notifications deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        deleted = self.db.query(Notification).filter(
            and_(
                Notification.is_read == True,
                Notification.created_at < cutoff_date
            )
        ).delete()
        
        self.db.commit()
        return deleted