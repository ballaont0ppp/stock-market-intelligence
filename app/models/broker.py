"""
Broker Model
Represents broker/admin entities
"""
from datetime import datetime
from app import db


class Broker(db.Model):
    """Broker model"""
    __tablename__ = 'brokers'
    
    broker_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True, nullable=False)
    broker_name = db.Column(db.String(255), nullable=False)
    license_number = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    assigned_users_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    def __repr__(self):
        return f'<Broker {self.broker_name}>'
