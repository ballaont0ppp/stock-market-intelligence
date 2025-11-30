"""
Company Model
Represents publicly traded companies
"""
from datetime import datetime
from app import db


class Company(db.Model):
    """Company/Stock model"""
    __tablename__ = 'companies'
    
    company_id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), unique=True, nullable=False, index=True)
    company_name = db.Column(db.String(255), nullable=False)
    sector = db.Column(db.String(100), index=True)
    industry = db.Column(db.String(100))
    market_cap = db.Column(db.BigInteger)
    description = db.Column(db.Text)
    website = db.Column(db.String(255))
    ceo = db.Column(db.String(255))
    employees = db.Column(db.Integer)
    founded_year = db.Column(db.Integer)
    headquarters = db.Column(db.String(255))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    price_history = db.relationship('PriceHistory', backref='company', cascade='all, delete-orphan')
    holdings = db.relationship('Holdings', backref='company')
    orders = db.relationship('Order', backref='company')
    dividends = db.relationship('Dividend', backref='company', cascade='all, delete-orphan')
    sentiment_cache = db.relationship('SentimentCache', backref='company', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Company {self.symbol}>'
