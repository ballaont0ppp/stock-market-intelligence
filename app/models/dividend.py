"""
Dividend Models
Represents dividend announcements and payments
"""
from datetime import datetime
from app import db


class Dividend(db.Model):
    """Dividend announcement model"""
    __tablename__ = 'dividends'
    
    dividend_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False, index=True)
    dividend_per_share = db.Column(db.Numeric(10, 4), nullable=False)
    payment_date = db.Column(db.Date, nullable=False, index=True)
    record_date = db.Column(db.Date, nullable=False)
    ex_dividend_date = db.Column(db.Date, nullable=False)
    announcement_date = db.Column(db.Date)
    dividend_type = db.Column(
        db.Enum('REGULAR', 'SPECIAL', name='dividend_type_enum'),
        default='REGULAR'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    payments = db.relationship('DividendPayment', backref='dividend', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.CheckConstraint('dividend_per_share > 0', name='check_positive_dividend'),
        db.CheckConstraint('payment_date > record_date', name='check_payment_after_record'),
        db.CheckConstraint('record_date > ex_dividend_date', name='check_record_after_ex'),
    )
    
    def __repr__(self):
        return f'<Dividend {self.dividend_id} ${self.dividend_per_share} on {self.payment_date}>'


class DividendPayment(db.Model):
    """Dividend payment to user model"""
    __tablename__ = 'dividend_payments'
    
    payment_id = db.Column(db.Integer, primary_key=True)
    dividend_id = db.Column(db.Integer, db.ForeignKey('dividends.dividend_id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    holding_id = db.Column(db.Integer, db.ForeignKey('holdings.holding_id'), nullable=False)
    shares_owned = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.transaction_id'), nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DividendPayment {self.payment_id} ${self.amount_paid}>'
