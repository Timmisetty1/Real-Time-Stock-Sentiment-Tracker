"""
Database manager for handling database operations.
"""
from datetime import datetime, timedelta
from .models import db, Document, SentimentScore, CompanyMention


class DatabaseManager:
    """Manager class for database operations."""
    
    @staticmethod
    def add_document(source, url, title, content, author=None, published_date=None):
        """Add a new document to the database."""
        try:
            # Check if document already exists
            existing = Document.query.filter_by(url=url).first()
            if existing:
                return existing
            
            document = Document(
                source=source,
                url=url,
                title=title,
                content=content,
                author=author,
                published_date=published_date
            )
            db.session.add(document)
            db.session.commit()
            return document
        except Exception as e:
            db.session.rollback()
            print(f"Error adding document: {e}")
            return None
    
    @staticmethod
    def add_sentiment_score(document_id, company, sentiment_label, sentiment_score, confidence):
        """Add a sentiment score for a document."""
        try:
            score = SentimentScore(
                document_id=document_id,
                company=company,
                sentiment_label=sentiment_label,
                sentiment_score=sentiment_score,
                confidence=confidence
            )
            db.session.add(score)
            db.session.commit()
            return score
        except Exception as e:
            db.session.rollback()
            print(f"Error adding sentiment score: {e}")
            return None
    
    @staticmethod
    def add_company_mention(document_id, company, mention_count=1, context=None):
        """Add a company mention record."""
        try:
            mention = CompanyMention(
                document_id=document_id,
                company=company,
                mention_count=mention_count,
                context=context
            )
            db.session.add(mention)
            db.session.commit()
            return mention
        except Exception as e:
            db.session.rollback()
            print(f"Error adding company mention: {e}")
            return None
    
    @staticmethod
    def get_sentiment_history(company, days=30):
        """Get sentiment history for a company over the last N days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return SentimentScore.query.filter(
            SentimentScore.company == company,
            SentimentScore.analyzed_date >= cutoff_date
        ).order_by(SentimentScore.analyzed_date.desc()).all()
    
    @staticmethod
    def get_aggregated_sentiment(company, days=7):
        """Get aggregated sentiment statistics for a company."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        scores = SentimentScore.query.filter(
            SentimentScore.company == company,
            SentimentScore.analyzed_date >= cutoff_date
        ).all()
        
        if not scores:
            return None
        
        avg_score = sum(s.sentiment_score for s in scores) / len(scores)
        positive_count = sum(1 for s in scores if s.sentiment_label == 'POSITIVE')
        negative_count = sum(1 for s in scores if s.sentiment_label == 'NEGATIVE')
        neutral_count = sum(1 for s in scores if s.sentiment_label == 'NEUTRAL')
        
        return {
            'company': company,
            'avg_sentiment': avg_score,
            'total_documents': len(scores),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'period_days': days
        }
    
    @staticmethod
    def get_all_companies_sentiment(days=7):
        """Get aggregated sentiment for all tracked companies."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        companies = db.session.query(SentimentScore.company).distinct().all()
        results = []
        
        for (company,) in companies:
            agg = DatabaseManager.get_aggregated_sentiment(company, days)
            if agg:
                results.append(agg)
        
        return results
    
    @staticmethod
    def get_document_count():
        """Get total document count by source."""
        return {
            'total': Document.query.count(),
            'news': Document.query.filter_by(source='news').count(),
            'reddit': Document.query.filter_by(source='reddit').count()
        }
