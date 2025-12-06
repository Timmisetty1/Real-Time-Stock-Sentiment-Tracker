"""
Database models for the Stock Sentiment Tracker.
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Document(db.Model):
    """Model for storing scraped documents (news articles and Reddit posts)."""
    
    __tablename__ = 'documents'
    
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(50), nullable=False)  # 'news' or 'reddit'
    url = db.Column(db.String(500), unique=True, nullable=False)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(200))
    published_date = db.Column(db.DateTime)
    scraped_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sentiment_scores = db.relationship('SentimentScore', backref='document', lazy=True, cascade='all, delete-orphan')
    company_mentions = db.relationship('CompanyMention', backref='document', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Document {self.id}: {self.title[:50]}...>'


class SentimentScore(db.Model):
    """Model for storing sentiment scores."""
    
    __tablename__ = 'sentiment_scores'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    company = db.Column(db.String(10), nullable=False)  # Stock ticker
    sentiment_label = db.Column(db.String(20), nullable=False)  # 'POSITIVE', 'NEGATIVE', 'NEUTRAL'
    sentiment_score = db.Column(db.Float, nullable=False)  # -1 to 1
    confidence = db.Column(db.Float, nullable=False)  # 0 to 1
    analyzed_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index for faster queries
    __table_args__ = (
        db.Index('idx_company_date', 'company', 'analyzed_date'),
    )
    
    def __repr__(self):
        return f'<SentimentScore {self.company}: {self.sentiment_label} ({self.sentiment_score:.2f})>'


class CompanyMention(db.Model):
    """Model for tracking company mentions in documents."""
    
    __tablename__ = 'company_mentions'
    
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    company = db.Column(db.String(10), nullable=False)  # Stock ticker
    mention_count = db.Column(db.Integer, default=1)
    context = db.Column(db.Text)  # Context around the mention
    
    def __repr__(self):
        return f'<CompanyMention {self.company}: {self.mention_count} times>'
