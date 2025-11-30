"""
Notification Model
Represents user notifications
"""
from datetime import datetime
from app import db


class Notification(db.Model):
    """User notification model"""
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    notification_type = db.Column(
        db.Enum('TRANSACTION', 'DIVIDEND', 'PRICE_ALERT', 'SYSTEM', name='notification_type_enum'),
        nullable=False
    )
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    read_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Notification {self.notification_id} {self.notification_type}>'
