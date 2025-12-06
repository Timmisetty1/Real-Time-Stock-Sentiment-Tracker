"""
Script to scrape data and perform sentiment analysis.
"""
import sys
import argparse
from app import create_app
from app.config import Config
from app.scrapers import NewsScraper, RedditScraper
from app.sentiment import SentimentAnalyzer, SentimentAggregator
from app.database import DatabaseManager, db
from datetime import datetime


def scrape_data(target_tickers, max_news=10000, max_reddit=5000, use_reddit=True):
    """
    Scrape news articles and Reddit posts.
    
    Args:
        target_tickers: List of stock tickers
        max_news: Maximum news articles to scrape
        max_reddit: Maximum Reddit posts to scrape
        use_reddit: Whether to use Reddit scraper
    
    Returns:
        List of all scraped documents
    """
    all_documents = []
    
    # Scrape news
    print("\n=== Scraping News Articles ===")
    news_scraper = NewsScraper(max_articles=max_news)
    news_articles = news_scraper.scrape_for_tickers(target_tickers)
    all_documents.extend(news_articles)
    
    # Scrape Reddit
    if use_reddit and Config.REDDIT_CLIENT_ID and Config.REDDIT_CLIENT_SECRET:
        print("\n=== Scraping Reddit Posts ===")
        reddit_scraper = RedditScraper(
            client_id=Config.REDDIT_CLIENT_ID,
            client_secret=Config.REDDIT_CLIENT_SECRET,
            user_agent=Config.REDDIT_USER_AGENT,
            max_posts=max_reddit
        )
        
        # Scrape from finance-related subreddits
        reddit_posts = reddit_scraper.scrape_multiple_subreddits(
            Config.REDDIT_SUBREDDITS,
            limit_per_subreddit=max_reddit // len(Config.REDDIT_SUBREDDITS)
        )
        
        # Convert Reddit post format to document format
        for post in reddit_posts:
            all_documents.append({
                'title': post['title'],
                'url': post['url'],
                'content': post['content'],
                'source': 'reddit',
                'author': post['author'],
                'published_date': post.get('created_utc', datetime.utcnow())
            })
    else:
        print("\n=== Skipping Reddit (credentials not configured) ===")
    
    print(f"\n=== Total documents collected: {len(all_documents)} ===")
    return all_documents


def analyze_and_store(documents, target_tickers):
    """
    Analyze sentiment and store in database.
    
    Args:
        documents: List of documents to analyze
        target_tickers: List of stock tickers to track
    """
    print("\n=== Starting Sentiment Analysis ===")
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    # Analyze documents
    results = analyzer.batch_analyze(documents, target_tickers=target_tickers)
    
    print("\n=== Storing Results in Database ===")
    stored_count = 0
    
    for result in results:
        doc_data = result['document']
        
        # Add document to database
        document = DatabaseManager.add_document(
            source=doc_data.get('source', 'news'),
            url=doc_data.get('url', ''),
            title=doc_data.get('title', ''),
            content=doc_data.get('content', ''),
            author=doc_data.get('author'),
            published_date=doc_data.get('published_date')
        )
        
        if not document:
            continue
        
        stored_count += 1
        
        # Store sentiment scores for each mentioned company
        for ticker, mention_data in result['mentions'].items():
            if ticker in target_tickers:
                # Add sentiment score
                DatabaseManager.add_sentiment_score(
                    document_id=document.id,
                    company=ticker,
                    sentiment_label=result['sentiment']['label'],
                    sentiment_score=result['sentiment']['score'],
                    confidence=result['sentiment']['confidence']
                )
                
                # Add company mention
                context = ' | '.join(mention_data.get('contexts', [])[:2])
                DatabaseManager.add_company_mention(
                    document_id=document.id,
                    company=ticker,
                    mention_count=mention_data['count'],
                    context=context[:500] if context else None
                )
        
        if stored_count % 100 == 0:
            print(f"Stored {stored_count} documents...")
    
    print(f"\n=== Successfully stored {stored_count} documents ===")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Stock Sentiment Tracker - Scraper and Analyzer')
    parser.add_argument('--max-news', type=int, default=1000, help='Maximum news articles to scrape')
    parser.add_argument('--max-reddit', type=int, default=500, help='Maximum Reddit posts to scrape')
    parser.add_argument('--no-reddit', action='store_true', help='Skip Reddit scraping')
    parser.add_argument('--tickers', type=str, help='Comma-separated list of tickers (default: from config)')
    
    args = parser.parse_args()
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Get target tickers
        if args.tickers:
            target_tickers = [t.strip().upper() for t in args.tickers.split(',')]
        else:
            target_tickers = Config.TARGET_STOCKS
        
        print("=== Stock Sentiment Tracker ===")
        print(f"Target tickers: {', '.join(target_tickers)}")
        print(f"Max news articles: {args.max_news}")
        print(f"Max Reddit posts: {args.max_reddit}")
        print(f"Reddit enabled: {not args.no_reddit}")
        
        # Scrape data
        documents = scrape_data(
            target_tickers=target_tickers,
            max_news=args.max_news,
            max_reddit=args.max_reddit,
            use_reddit=not args.no_reddit
        )
        
        if not documents:
            print("\nNo documents collected. Exiting.")
            return
        
        # Analyze and store
        analyze_and_store(documents, target_tickers)
        
        # Print summary
        print("\n=== Summary ===")
        doc_count = DatabaseManager.get_document_count()
        print(f"Total documents in database: {doc_count['total']}")
        print(f"  - News articles: {doc_count['news']}")
        print(f"  - Reddit posts: {doc_count['reddit']}")
        
        companies = DatabaseManager.get_all_companies_sentiment(days=7)
        print(f"\nTracked companies: {len(companies)}")
        for company in companies:
            print(f"  - {company['company']}: "
                  f"avg sentiment = {company['avg_sentiment']:.2f}, "
                  f"documents = {company['total_documents']}")
        
        print("\n=== Done! Start the Flask app with: python run.py ===")


if __name__ == '__main__':
    main()
