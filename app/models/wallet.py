"""
Wallet Model
Represents user's virtual cash account
"""
from datetime import datetime
from app import db


class Wallet(db.Model):
    """User wallet model"""
    __tablename__ = 'wallets'
    
    wallet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), unique=True, nullable=False, index=True)
    balance = db.Column(db.Numeric(15, 2), default=100000.00, nullable=False)
    currency = db.Column(db.String(3), default='USD')
    total_deposited = db.Column(db.Numeric(15, 2), default=100000.00)
    total_withdrawn = db.Column(db.Numeric(15, 2), default=0.00)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        db.CheckConstraint('balance >= 0', name='check_positive_balance'),
    )
    
    def __repr__(self):
        return f'<Wallet user_id={self.user_id} balance={self.balance}>'
