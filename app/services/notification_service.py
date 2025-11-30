"""
Notification Service
Handles creation, retrieval, and management of user notifications
"""
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy import and_
from app import db
from app.models.notification import Notification
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing user notifications"""
    
    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str
    ) -> Notification:
        """
        Create a new notification for a user
        
        Args:
            user_id: ID of the user to notify
            notification_type: Type of notification (TRANSACTION, DIVIDEND, PRICE_ALERT, SYSTEM)
            title: Notification title
            message: Notification message
            
        Returns:
            Created Notification object
            
        Raises:
            ValueError: If user_id is invalid or notification_type is not valid
        """
        try:
            # Validate user exists
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")
            
            # Validate notification type
            valid_types = ['TRANSACTION', 'DIVIDEND', 'PRICE_ALERT', 'SYSTEM']
            if notification_type not in valid_types:
                raise ValueError(f"Invalid notification type: {notification_type}. Must be one of {valid_types}")
            
            # Create notification
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                is_read=False,
                created_at=datetime.utcnow()
            )
            
            db.session.add(notification)
            db.session.commit()
            
            logger.info(f"Created notification {notification.notification_id} for user {user_id}")
            return notification
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating notification for user {user_id}: {str(e)}")
            raise
    
    def get_user_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Notification]:
        """
        Get notifications for a user
        
        Args:
            user_id: ID of the user
            unread_only: If True, only return unread notifications
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip (for pagination)
            
        Returns:
            List of Notification objects
        """
        try:
            query = Notification.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(is_read=False)
            
            # Order by most recent first
            query = query.order_by(Notification.created_at.desc())
            
            # Apply pagination
            if offset > 0:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            notifications = query.all()
            logger.debug(f"Retrieved {len(notifications)} notifications for user {user_id}")
            return notifications
            
        except Exception as e:
            logger.error(f"Error retrieving notifications for user {user_id}: {str(e)}")
            raise
    
    def get_unread_count(self, user_id: int) -> int:
        """
        Get count of unread notifications for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Count of unread notifications
        """
        try:
            count = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).count()
            return count
        except Exception as e:
            logger.error(f"Error getting unread count for user {user_id}: {str(e)}")
            return 0
    
    def mark_as_read(self, notification_id: int) -> bool:
        """
        Mark a notification as read
        
        Args:
            notification_id: ID of the notification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.query.get(notification_id)
            if not notification:
                logger.warning(f"Notification {notification_id} not found")
                return False
            
            if not notification.is_read:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Marked notification {notification_id} as read")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error marking notification {notification_id} as read: {str(e)}")
            return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """
        Mark all notifications as read for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of notifications marked as read
        """
        try:
            # Get all unread notifications for the user
            unread_notifications = Notification.query.filter_by(
                user_id=user_id,
                is_read=False
            ).all()
            
            count = len(unread_notifications)
            
            if count > 0:
                # Mark all as read
                for notification in unread_notifications:
                    notification.is_read = True
                    notification.read_at = datetime.utcnow()
                
                db.session.commit()
                logger.info(f"Marked {count} notifications as read for user {user_id}")
            
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error marking all notifications as read for user {user_id}: {str(e)}")
            return 0
    
    def delete_notification(self, notification_id: int) -> bool:
        """
        Delete a notification
        
        Args:
            notification_id: ID of the notification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            notification = Notification.query.get(notification_id)
            if not notification:
                logger.warning(f"Notification {notification_id} not found")
                return False
            
            db.session.delete(notification)
            db.session.commit()
            logger.info(f"Deleted notification {notification_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting notification {notification_id}: {str(e)}")
            return False
    
    def delete_all_read(self, user_id: int) -> int:
        """
        Delete all read notifications for a user
        
        Args:
            user_id: ID of the user
            
        Returns:
            Number of notifications deleted
        """
        try:
            # Get all read notifications for the user
            read_notifications = Notification.query.filter_by(
                user_id=user_id,
                is_read=True
            ).all()
            
            count = len(read_notifications)
            
            if count > 0:
                for notification in read_notifications:
                    db.session.delete(notification)
                
                db.session.commit()
                logger.info(f"Deleted {count} read notifications for user {user_id}")
            
            return count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting read notifications for user {user_id}: {str(e)}")
            return 0
    
    def get_notifications_by_type(
        self,
        user_id: int,
        notification_type: str,
        limit: Optional[int] = None
    ) -> List[Notification]:
        """
        Get notifications of a specific type for a user
        
        Args:
            user_id: ID of the user
            notification_type: Type of notification to filter by
            limit: Maximum number of notifications to return
            
        Returns:
            List of Notification objects
        """
        try:
            query = Notification.query.filter_by(
                user_id=user_id,
                notification_type=notification_type
            ).order_by(Notification.created_at.desc())
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error retrieving {notification_type} notifications for user {user_id}: {str(e)}")
            return []
