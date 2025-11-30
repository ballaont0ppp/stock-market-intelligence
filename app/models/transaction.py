"""
Transaction Model
Represents all financial transactions
"""
from datetime import datetime
from app import db


class Transaction(db.Model):
    """Transaction history model"""
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    transaction_type = db.Column(
        db.Enum('BUY', 'SELL', 'DIVIDEND', 'DEPOSIT', 'WITHDRAWAL', 'FEE', name='transaction_type_enum'),
        nullable=False,
        index=True
    )
    order_id = db.Column(db.Integer, db.ForeignKey('orders.order_id'))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'))
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    balance_before = db.Column(db.Numeric(15, 2), nullable=False)
    balance_after = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Transaction {self.transaction_id} {self.transaction_type} {self.amount}>'
