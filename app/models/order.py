"""
Order Model
Represents buy/sell orders
"""
from datetime import datetime
from app import db


class Order(db.Model):
    """Stock order model"""
    __tablename__ = 'orders'
    
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False, index=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False, index=True)
    order_type = db.Column(db.Enum('BUY', 'SELL', name='order_type_enum'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_share = db.Column(db.Numeric(10, 2), nullable=False)
    commission_fee = db.Column(db.Numeric(10, 2), nullable=False)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    order_status = db.Column(
        db.Enum('PENDING', 'COMPLETED', 'FAILED', 'CANCELLED', name='order_status_enum'),
        default='PENDING',
        index=True
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    executed_at = db.Column(db.DateTime)
    failure_reason = db.Column(db.Text)
    realized_gain_loss = db.Column(db.Numeric(15, 2))
    
    # Relationships
    transactions = db.relationship('Transaction', backref='order')
    
    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_positive_order_quantity'),
    )
    
    def __repr__(self):
        return f'<Order {self.order_id} {self.order_type} {self.quantity} shares>'
