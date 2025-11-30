"""
Sentiment Cache Model
Caches sentiment analysis results
"""
from datetime import datetime
from app import db


class SentimentCache(db.Model):
    """Sentiment analysis cache model"""
    __tablename__ = 'sentiment_cache'
    
    cache_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'), nullable=False, index=True)
    source = db.Column(
        db.Enum('TWITTER', 'NEWS', 'REDDIT', name='sentiment_source_enum'),
        default='TWITTER'
    )
    polarity_score = db.Column(db.Numeric(3, 2), nullable=False)
    positive_count = db.Column(db.Integer, nullable=False)
    negative_count = db.Column(db.Integer, nullable=False)
    neutral_count = db.Column(db.Integer, nullable=False)
    sample_texts = db.Column(db.JSON)
    fetched_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    
    def __repr__(self):
        return f'<SentimentCache company_id={self.company_id} polarity={self.polarity_score}>'
