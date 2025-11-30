"""
Holdings Model
Represents user's stock holdings
"""
from datetime import datetime
from app import db


class Holdings(db.Model):
    """User stock holdings model"""
    __tablename__ = 'holdings'
    
    holding_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    average_purchase_price = db.Column(db.Numeric(10, 2), nullable=False)
    total_invested = db.Column(db.Numeric(15, 2), nullable=False)
    first_purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    dividend_payments = db.relationship('DividendPayment', backref='holding', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'company_id', name='unique_user_company'),
        db.CheckConstraint('quantity > 0', name='check_positive_quantity'),
    )
    
    def __repr__(self):
        return f'<Holdings user_id={self.user_id} company_id={self.company_id} qty={self.quantity}>'
