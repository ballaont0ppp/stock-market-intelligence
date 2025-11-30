"""
Audit Log Model
Tracks all administrative actions for compliance and security
"""
from datetime import datetime
from app import db


class AuditLog(db.Model):
    """Model for audit log entries"""
    
    __tablename__ = 'audit_logs'
    
    # Primary key
    audit_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Admin who performed the action
    admin_id = db.Column(db.Integer, db.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
    
    # Action details
    action_type = db.Column(
        db.Enum('CREATE', 'UPDATE', 'DELETE', 'SUSPEND', 'ACTIVATE', 'ADJUST_BALANCE', 'OTHER', name='audit_action_type'),
        nullable=False
    )
    
    # Entity details
    entity_type = db.Column(
        db.Enum('USER', 'COMPANY', 'BROKER', 'DIVIDEND', 'WALLET', 'OTHER', name='audit_entity_type'),
        nullable=False
    )
    entity_id = db.Column(db.Integer, nullable=True)
    
    # Changes made (JSON format)
    changes = db.Column(db.JSON, nullable=True)
    
    # Additional context
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)  # IPv6 compatible
    
    # Timestamp
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    admin = db.relationship('User', foreign_keys=[admin_id], backref='audit_logs')
    
    # Indexes
    __table_args__ = (
        db.Index('idx_audit_admin_created', 'admin_id', 'created_at'),
        db.Index('idx_audit_entity', 'entity_type', 'entity_id'),
        db.Index('idx_audit_action', 'action_type'),
        db.Index('idx_audit_created', 'created_at'),
    )
    
    def __repr__(self):
        return f'<AuditLog {self.audit_id}: {self.action_type} {self.entity_type}>'
    
    def to_dict(self):
        """Convert audit log to dictionary"""
        return {
            'audit_id': self.audit_id,
            'admin_id': self.admin_id,
            'admin_email': self.admin.email if self.admin else None,
            'action_type': self.action_type,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'changes': self.changes,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
