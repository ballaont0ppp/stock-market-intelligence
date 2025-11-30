"""
Job Log Model
Tracks background job execution
"""
from datetime import datetime
from app import db


class JobLog(db.Model):
    """Background job execution log model"""
    __tablename__ = 'job_logs'
    
    job_id = db.Column(db.Integer, primary_key=True)
    job_name = db.Column(db.String(100), nullable=False, index=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)
    status = db.Column(
        db.Enum('RUNNING', 'SUCCESS', 'FAILED', 'PARTIAL', name='job_status_enum'),
        default='RUNNING'
    )
    stocks_processed = db.Column(db.Integer, default=0)
    stocks_failed = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    
    def complete(self, status='SUCCESS', stocks_processed=0, stocks_failed=0, error_message=None):
        """Mark job as complete"""
        self.completed_at = datetime.utcnow()
        self.status = status
        self.stocks_processed = stocks_processed
        self.stocks_failed = stocks_failed
        self.error_message = error_message
        db.session.commit()
    
    @classmethod
    def create(cls, job_name):
        """Create a new job log entry"""
        job_log = cls(job_name=job_name, status='RUNNING')
        db.session.add(job_log)
        db.session.commit()
        return job_log
    
    def __repr__(self):
        return f'<JobLog {self.job_name} {self.status}>'
