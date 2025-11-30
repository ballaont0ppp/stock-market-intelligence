"""
User Model
Represents registered users with authentication and profile information
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(db.Model, UserMixin):
    """User account model"""
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    risk_tolerance = db.Column(
        db.Enum('conservative', 'moderate', 'aggressive', name='risk_tolerance_enum'),
        default='moderate'
    )
    investment_goals = db.Column(db.Text)
    preferred_sectors = db.Column(db.JSON)
    notification_preferences = db.Column(db.JSON)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    account_status = db.Column(
        db.Enum('active', 'suspended', name='account_status_enum'),
        default='active'
    )
    
    # Relationships
    wallet = db.relationship('Wallet', backref='user', uselist=False, cascade='all, delete-orphan')
    holdings = db.relationship('Holdings', backref='user', cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', cascade='all, delete-orphan')
    broker = db.relationship('Broker', backref='user', uselist=False, cascade='all, delete-orphan')
    dividend_payments = db.relationship('DividendPayment', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password using bcrypt"""
        from app import bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against hash using bcrypt"""
        from app import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return user ID as string for Flask-Login"""
        return str(self.user_id)
    
    def __repr__(self):
        return f'<User {self.email}>'
