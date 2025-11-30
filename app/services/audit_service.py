"""
Audit Service
Handles audit logging for administrative actions
"""
import logging
from datetime import datetime
from flask import request
from app import db
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging"""
    
    @staticmethod
    def log_action(admin_id, action_type, entity_type, entity_id=None, changes=None, description=None):
        """
        Log an administrative action
        
        Args:
            admin_id: ID of the admin user performing the action
            action_type: Type of action (CREATE, UPDATE, DELETE, SUSPEND, ACTIVATE, ADJUST_BALANCE, OTHER)
            entity_type: Type of entity (USER, COMPANY, BROKER, DIVIDEND, WALLET, OTHER)
            entity_id: ID of the entity being acted upon (optional)
            changes: Dictionary of changes made (optional)
            description: Additional description (optional)
        
        Returns:
            AuditLog: Created audit log entry
        """
        try:
            # Get IP address from request context
            ip_address = None
            if request:
                ip_address = request.remote_addr or request.environ.get('HTTP_X_FORWARDED_FOR', None)
            
            # Create audit log entry
            audit_log = AuditLog(
                admin_id=admin_id,
                action_type=action_type,
                entity_type=entity_type,
                entity_id=entity_id,
                changes=changes,
                description=description,
                ip_address=ip_address,
                created_at=datetime.utcnow()
            )
            
            db.session.add(audit_log)
            db.session.commit()
            
            logger.info(
                f"Audit log created: admin_id={admin_id}, action={action_type}, "
                f"entity={entity_type}:{entity_id}, ip={ip_address}"
            )
            
            return audit_log
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create audit log: {str(e)}", exc_info=True)
            # Don't raise exception - audit logging failure shouldn't break the main operation
            return None
    
    @staticmethod
    def get_audit_logs(filters=None, page=1, per_page=50):
        """
        Get audit logs with optional filtering and pagination
        
        Args:
            filters: Dictionary with filter criteria
                - admin_id: Filter by admin user
                - action_type: Filter by action type
                - entity_type: Filter by entity type
                - entity_id: Filter by entity ID
                - date_from: Filter by start date
                - date_to: Filter by end date
            page: Page number (default 1)
            per_page: Items per page (default 50)
        
        Returns:
            dict: Paginated audit logs data
        """
        try:
            query = AuditLog.query
            
            # Apply filters
            if filters:
                if filters.get('admin_id'):
                    query = query.filter(AuditLog.admin_id == filters['admin_id'])
                
                if filters.get('action_type'):
                    query = query.filter(AuditLog.action_type == filters['action_type'])
                
                if filters.get('entity_type'):
                    query = query.filter(AuditLog.entity_type == filters['entity_type'])
                
                if filters.get('entity_id'):
                    query = query.filter(AuditLog.entity_id == filters['entity_id'])
                
                if filters.get('date_from'):
                    query = query.filter(AuditLog.created_at >= filters['date_from'])
                
                if filters.get('date_to'):
                    query = query.filter(AuditLog.created_at <= filters['date_to'])
            
            # Order by creation date (newest first)
            query = query.order_by(AuditLog.created_at.desc())
            
            # Paginate
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return {
                'audit_logs': pagination.items,
                'total': pagination.total,
                'page': pagination.page,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
            
        except Exception as e:
            logger.error(f"Error getting audit logs: {str(e)}")
            raise Exception(f"Failed to retrieve audit logs: {str(e)}")
    
    @staticmethod
    def get_entity_audit_trail(entity_type, entity_id):
        """
        Get complete audit trail for a specific entity
        
        Args:
            entity_type: Type of entity (USER, COMPANY, BROKER, etc.)
            entity_id: ID of the entity
        
        Returns:
            list: List of audit log entries for the entity
        """
        try:
            audit_logs = AuditLog.query.filter_by(
                entity_type=entity_type,
                entity_id=entity_id
            ).order_by(AuditLog.created_at.desc()).all()
            
            return audit_logs
            
        except Exception as e:
            logger.error(f"Error getting entity audit trail: {str(e)}")
            raise Exception(f"Failed to retrieve entity audit trail: {str(e)}")
    
    @staticmethod
    def get_admin_activity(admin_id, days=30):
        """
        Get recent activity for a specific admin
        
        Args:
            admin_id: ID of the admin user
            days: Number of days to look back (default 30)
        
        Returns:
            list: List of audit log entries for the admin
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            audit_logs = AuditLog.query.filter(
                AuditLog.admin_id == admin_id,
                AuditLog.created_at >= cutoff_date
            ).order_by(AuditLog.created_at.desc()).all()
            
            return audit_logs
            
        except Exception as e:
            logger.error(f"Error getting admin activity: {str(e)}")
            raise Exception(f"Failed to retrieve admin activity: {str(e)}")
