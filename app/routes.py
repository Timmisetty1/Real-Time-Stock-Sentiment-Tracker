"""
Flask routes for the Stock Sentiment Tracker.
"""
from flask import Blueprint, render_template, jsonify, request
from app.database import DatabaseManager, Document, SentimentScore
from app.config import Config
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)


@main_bp.route('/')
def index():
    """Home page showing dashboard."""
    return render_template('index.html')


@main_bp.route('/company/<ticker>')
def company_detail(ticker):
    """Company detail page."""
    return render_template('company.html', ticker=ticker)


@api_bp.route('/stats')
def get_stats():
    """Get overall statistics."""
    doc_count = DatabaseManager.get_document_count()
    companies = DatabaseManager.get_all_companies_sentiment(days=7)
    
    return jsonify({
        'document_count': doc_count,
        'tracked_companies': len(companies),
        'companies': companies,
        'timestamp': datetime.utcnow().isoformat()
    })


@api_bp.route('/sentiment/<ticker>')
def get_company_sentiment(ticker):
    """Get sentiment data for a specific company."""
    days = request.args.get('days', default=7, type=int)
    
    # Get historical sentiment
    history = DatabaseManager.get_sentiment_history(ticker, days=days)
    
    # Get aggregated sentiment
    aggregated = DatabaseManager.get_aggregated_sentiment(ticker, days=days)
    
    if not aggregated:
        return jsonify({'error': 'No data found for this company'}), 404
    
    # Format history for chart
    history_data = [{
        'date': score.analyzed_date.isoformat(),
        'score': score.sentiment_score,
        'label': score.sentiment_label,
        'confidence': score.confidence
    } for score in history]
    
    return jsonify({
        'ticker': ticker,
        'aggregated': aggregated,
        'history': history_data,
        'timestamp': datetime.utcnow().isoformat()
    })


@api_bp.route('/companies')
def get_companies():
    """Get list of all tracked companies."""
    companies = DatabaseManager.get_all_companies_sentiment(days=30)
    return jsonify({
        'companies': companies,
        'count': len(companies),
        'timestamp': datetime.utcnow().isoformat()
    })


@api_bp.route('/recent-documents')
def get_recent_documents():
    """Get recent documents."""
    limit = request.args.get('limit', default=50, type=int)
    source = request.args.get('source', default=None, type=str)
    
    query = Document.query
    
    if source:
        query = query.filter_by(source=source)
    
    documents = query.order_by(Document.scraped_date.desc()).limit(limit).all()
    
    doc_list = [{
        'id': doc.id,
        'title': doc.title,
        'source': doc.source,
        'url': doc.url,
        'published_date': doc.published_date.isoformat() if doc.published_date else None,
        'scraped_date': doc.scraped_date.isoformat()
    } for doc in documents]
    
    return jsonify({
        'documents': doc_list,
        'count': len(doc_list),
        'timestamp': datetime.utcnow().isoformat()
    })


@api_bp.route('/sentiment-trend/<ticker>')
def get_sentiment_trend(ticker):
    """Get sentiment trend over time."""
    days = request.args.get('days', default=30, type=int)
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    scores = SentimentScore.query.filter(
        SentimentScore.company == ticker,
        SentimentScore.analyzed_date >= cutoff_date
    ).order_by(SentimentScore.analyzed_date).all()
    
    if not scores:
        return jsonify({'error': 'No data found'}), 404
    
    # Group by day
    daily_scores = {}
    for score in scores:
        date_key = score.analyzed_date.date().isoformat()
        if date_key not in daily_scores:
            daily_scores[date_key] = []
        daily_scores[date_key].append(score.sentiment_score)
    
    # Calculate daily averages
    trend_data = [{
        'date': date,
        'avg_sentiment': sum(scores) / len(scores),
        'count': len(scores)
    } for date, scores in sorted(daily_scores.items())]
    
    return jsonify({
        'ticker': ticker,
        'trend': trend_data,
        'timestamp': datetime.utcnow().isoformat()
    })
