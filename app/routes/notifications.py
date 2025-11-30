"""
Notifications Routes Blueprint
Handles notification viewing and management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.services.notification_service import NotificationService

bp = Blueprint('notifications', __name__, url_prefix='/notifications')


@bp.route('/')
@login_required
def index():
    """
    Display all notifications for the current user with pagination and filters
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    notification_type = request.args.get('type', '')
    read_status = request.args.get('status', '')  # 'read', 'unread', or ''
    
    notification_service = NotificationService()
    
    # Determine if we should filter by read status
    unread_only = (read_status == 'unread')
    
    # Get notifications
    offset = (page - 1) * per_page
    
    if notification_type:
        # Filter by type
        notifications = notification_service.get_notifications_by_type(
            user_id=current_user.user_id,
            notification_type=notification_type,
            limit=per_page
        )
        # Apply read status filter if needed
        if read_status == 'read':
            notifications = [n for n in notifications if n.is_read]
        elif read_status == 'unread':
            notifications = [n for n in notifications if not n.is_read]
        total = len(notifications)
    else:
        # Get all notifications with pagination
        all_notifications = notification_service.get_user_notifications(
            user_id=current_user.user_id,
            unread_only=unread_only
        )
        
        # Apply read status filter if needed (and not already filtered by unread_only)
        if read_status == 'read':
            all_notifications = [n for n in all_notifications if n.is_read]
        
        total = len(all_notifications)
        notifications = all_notifications[offset:offset + per_page]
    
    # Get unread count
    unread_count = notification_service.get_unread_count(current_user.user_id)
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    
    return render_template(
        'notifications/index.html',
        notifications=notifications,
        unread_count=unread_count,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
        notification_type=notification_type,
        read_status=read_status
    )


@bp.route('/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """
    Mark all notifications as read for the current user
    """
    notification_service = NotificationService()
    count = notification_service.mark_all_as_read(current_user.user_id)
    
    flash(f'Marked {count} notifications as read', 'success')
    return redirect(url_for('notifications.index'))


@bp.route('/delete-all-read', methods=['POST'])
@login_required
def delete_all_read():
    """
    Delete all read notifications for the current user
    """
    notification_service = NotificationService()
    count = notification_service.delete_all_read(current_user.user_id)
    
    flash(f'Deleted {count} read notifications', 'success')
    return redirect(url_for('notifications.index'))


@bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_read(notification_id):
    """
    Mark a specific notification as read
    """
    from app.models.notification import Notification
    
    # Verify notification belongs to current user
    notification = Notification.query.get(notification_id)
    if not notification or notification.user_id != current_user.user_id:
        flash('Notification not found', 'error')
        return redirect(url_for('notifications.index'))
    
    notification_service = NotificationService()
    notification_service.mark_as_read(notification_id)
    
    return redirect(url_for('notifications.index'))


@bp.route('/<int:notification_id>/delete', methods=['POST'])
@login_required
def delete(notification_id):
    """
    Delete a specific notification
    """
    from app.models.notification import Notification
    
    # Verify notification belongs to current user
    notification = Notification.query.get(notification_id)
    if not notification or notification.user_id != current_user.user_id:
        flash('Notification not found', 'error')
        return redirect(url_for('notifications.index'))
    
    notification_service = NotificationService()
    notification_service.delete_notification(notification_id)
    
    flash('Notification deleted', 'success')
    return redirect(url_for('notifications.index'))
