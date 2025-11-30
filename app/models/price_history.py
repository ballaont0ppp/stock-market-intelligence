"""
Price History Model
Stores historical stock prices
"""
from datetime import datetime
from app import db


class PriceHistory(db.Model):
    """Stock price history model"""
    __tablename__ = 'price_history'
    
    price_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    open = db.Column(db.Numeric(10, 2), nullable=False)
    high = db.Column(db.Numeric(10, 2), nullable=False)
    low = db.Column(db.Numeric(10, 2), nullable=False)
    close = db.Column(db.Numeric(10, 2), nullable=False)
    adjusted_close = db.Column(db.Numeric(10, 2), nullable=False)
    volume = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('company_id', 'date', name='unique_company_date'),
    )
    
    def __repr__(self):
        return f'<PriceHistory company_id={self.company_id} date={self.date} close={self.close}>'
