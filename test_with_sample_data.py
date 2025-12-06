"""
Test script with sample data to demonstrate the system functionality.
"""
from app import create_app
from app.sentiment import SentimentAnalyzer
from app.database import DatabaseManager
from datetime import datetime, timedelta
import random

# Sample financial news and Reddit posts
sample_documents = [
    {
        'title': 'Apple Reports Record-Breaking Q4 Earnings',
        'content': 'Apple Inc. announced outstanding fourth-quarter earnings today, surpassing analyst expectations. The tech giant reported revenue of $94.5 billion, driven by strong iPhone sales and services growth. CEO Tim Cook expressed confidence in the company\'s future prospects.',
        'url': 'https://example.com/apple-earnings-q4',
        'source': 'news',
        'author': 'John Smith',
        'published_date': datetime.utcnow() - timedelta(hours=2)
    },
    {
        'title': 'Tesla Unveils New Battery Technology',
        'content': 'Tesla has announced a revolutionary new battery technology that could extend vehicle range by 40%. Elon Musk called it a game-changer for the electric vehicle industry. The stock surged on the news.',
        'url': 'https://example.com/tesla-battery',
        'source': 'news',
        'author': 'Jane Doe',
        'published_date': datetime.utcnow() - timedelta(hours=5)
    },
    {
        'title': 'Google\'s AI Breakthrough Impresses Analysts',
        'content': 'Alphabet\'s Google division unveiled significant advances in artificial intelligence capabilities. The new AI model demonstrates unprecedented accuracy and efficiency. Industry experts predict this will strengthen Google\'s market position.',
        'url': 'https://example.com/google-ai',
        'source': 'news',
        'author': 'Tech Reporter',
        'published_date': datetime.utcnow() - timedelta(hours=8)
    },
    {
        'title': 'Microsoft Azure Growth Continues Strong Momentum',
        'content': 'Microsoft Corporation reported robust Azure cloud computing revenue growth this quarter. The cloud segment showed 30% year-over-year increase. Microsoft\'s stock reached new all-time highs on the positive results.',
        'url': 'https://example.com/msft-azure',
        'source': 'news',
        'author': 'Business Weekly',
        'published_date': datetime.utcnow() - timedelta(hours=12)
    },
    {
        'title': 'Amazon Prime Day Sets New Sales Records',
        'content': 'Amazon announced that this year\'s Prime Day event broke all previous sales records. The company saw unprecedented customer engagement and transaction volumes. Analysts are bullish on Amazon\'s retail prospects.',
        'url': 'https://example.com/amazon-prime-day',
        'source': 'news',
        'author': 'Retail News',
        'published_date': datetime.utcnow() - timedelta(hours=15)
    },
    {
        'title': '$AAPL looking strong today! 🚀',
        'content': 'Apple is killing it with the new iPhone launch. Sales numbers are insane. Thinking of buying more shares. What do you all think? AAPL to the moon!',
        'url': 'https://reddit.com/r/wallstreetbets/post1',
        'source': 'reddit',
        'author': 'bullish_trader',
        'published_date': datetime.utcnow() - timedelta(hours=3)
    },
    {
        'title': 'Concerns about TSLA production delays',
        'content': 'Reports suggest Tesla may face production delays at its new factory. Some investors are worried about the impact on quarterly deliveries. Anyone else concerned about their TSLA position?',
        'url': 'https://reddit.com/r/stocks/post2',
        'source': 'reddit',
        'author': 'concerned_investor',
        'published_date': datetime.utcnow() - timedelta(hours=6)
    },
    {
        'title': 'GOOGL AI products are impressive',
        'content': 'Just tried the new Google AI features. Absolutely blown away by the capabilities. Google is really ahead in the AI race. Bullish on GOOGL long term.',
        'url': 'https://reddit.com/r/investing/post3',
        'source': 'reddit',
        'author': 'tech_enthusiast',
        'published_date': datetime.utcnow() - timedelta(hours=10)
    },
    {
        'title': 'MSFT continues to dominate enterprise market',
        'content': 'Microsoft just won another massive enterprise contract. Their Azure + Office 365 combo is unstoppable. MSFT is a solid hold in any portfolio.',
        'url': 'https://reddit.com/r/stocks/post4',
        'source': 'reddit',
        'author': 'enterprise_watcher',
        'published_date': datetime.utcnow() - timedelta(hours=14)
    },
    {
        'title': 'Amazon facing increased competition',
        'content': 'Not sure about AMZN anymore. Competition in retail and cloud is heating up. Profit margins getting squeezed. Anyone else thinking of trimming their position?',
        'url': 'https://reddit.com/r/investing/post5',
        'source': 'reddit',
        'author': 'value_investor',
        'published_date': datetime.utcnow() - timedelta(hours=18)
    },
    # Additional documents for more realistic data
    {
        'title': 'Apple Stock Price Target Raised by Major Bank',
        'content': 'Goldman Sachs has raised its price target for Apple stock to $220, citing strong fundamentals and innovation pipeline. The analysts are particularly optimistic about Apple\'s services segment and wearables business.',
        'url': 'https://example.com/aapl-target',
        'source': 'news',
        'author': 'Financial Times',
        'published_date': datetime.utcnow() - timedelta(days=1)
    },
    {
        'title': 'Tesla Faces Regulatory Challenges in Europe',
        'content': 'Tesla is encountering new regulatory hurdles in the European market. The company needs to address concerns about autopilot safety features. This could impact near-term sales in the region.',
        'url': 'https://example.com/tesla-europe',
        'source': 'news',
        'author': 'Auto Industry News',
        'published_date': datetime.utcnow() - timedelta(days=1, hours=3)
    },
    {
        'title': 'Google Cloud Wins Major Government Contract',
        'content': 'Alphabet\'s Google Cloud division has secured a significant government contract worth billions. This validates Google\'s cloud strategy and strengthens its position against AWS and Azure.',
        'url': 'https://example.com/google-cloud-contract',
        'source': 'news',
        'author': 'Cloud Computing Today',
        'published_date': datetime.utcnow() - timedelta(days=2)
    },
    {
        'title': 'Microsoft Teams Hits 500 Million Users',
        'content': 'Microsoft Teams has reached the milestone of 500 million monthly active users. The collaboration platform continues to see strong adoption in enterprise and education sectors.',
        'url': 'https://example.com/msft-teams',
        'source': 'news',
        'author': 'Business Tech',
        'published_date': datetime.utcnow() - timedelta(days=2, hours=6)
    },
    {
        'title': 'Amazon Web Services Announces Price Cuts',
        'content': 'AWS has announced significant price reductions across multiple services. While this may pressure margins, it could help Amazon maintain its cloud market share leadership position.',
        'url': 'https://example.com/aws-pricing',
        'source': 'news',
        'author': 'Cloud Report',
        'published_date': datetime.utcnow() - timedelta(days=3)
    }
]

def main():
    """Generate sample data and populate database."""
    print("=== Stock Sentiment Tracker - Sample Data Test ===\n")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        print("Loading sentiment analysis model...")
        analyzer = SentimentAnalyzer()
        
        target_tickers = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
        
        print(f"Processing {len(sample_documents)} sample documents...\n")
        
        # Analyze documents
        results = analyzer.batch_analyze(sample_documents, target_tickers=target_tickers)
        
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
            
            print(f"Stored: {doc_data['title'][:60]}...")
        
        print(f"\n=== Successfully stored {stored_count} documents ===\n")
        
        # Print summary
        print("=== Summary ===")
        doc_count = DatabaseManager.get_document_count()
        print(f"Total documents in database: {doc_count['total']}")
        print(f"  - News articles: {doc_count['news']}")
        print(f"  - Reddit posts: {doc_count['reddit']}")
        
        companies = DatabaseManager.get_all_companies_sentiment(days=7)
        print(f"\nTracked companies: {len(companies)}")
        for company in sorted(companies, key=lambda x: x['company']):
            sentiment = company['avg_sentiment']
            label = 'POSITIVE' if sentiment > 0.2 else 'NEGATIVE' if sentiment < -0.2 else 'NEUTRAL'
            print(f"  - {company['company']}: "
                  f"avg sentiment = {company['avg_sentiment']:+.2f} ({label}), "
                  f"documents = {company['total_documents']}, "
                  f"pos={company['positive_count']}, "
                  f"neg={company['negative_count']}")
        
        print("\n=== Test Complete! ===")
        print("Flask app is running at http://localhost:5000")
        print("Try these API endpoints:")
        print("  - http://localhost:5000/api/stats")
        print("  - http://localhost:5000/api/companies")
        print("  - http://localhost:5000/api/sentiment/AAPL")
        print("  - http://localhost:5000/api/recent-documents")


if __name__ == '__main__':
    main()
