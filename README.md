# Real-Time Stock Sentiment Tracker

A sophisticated AI-powered system that scrapes financial news articles and Reddit discussions to track and analyze sentiment for major stocks. The system uses Named Entity Recognition (NER) to identify company mentions and provides real-time sentiment scoring with multiple aggregation strategies.

## Features

- 📰 **News Scraping**: Collect financial news from Yahoo Finance and MarketWatch using BeautifulSoup
- 💬 **Reddit Integration**: Scrape discussions from r/wallstreetbets, r/stocks, r/investing, and r/StockMarket using PRAW
- 🤖 **AI Sentiment Analysis**: Advanced sentiment scoring using DistilBERT (Hugging Face Transformers)
- 🏢 **Named Entity Recognition**: Track company mentions using spaCy NER
- 📊 **Multiple Aggregation Strategies**: Simple average, weighted average, exponential moving average, and more
- 🗄️ **SQLite Backend**: Persistent storage of historical sentiment scores and documents
- 🌐 **Flask Web Interface**: Interactive dashboard to visualize sentiment trends
- 🎯 **Target up to 15K documents**: Configurable scraping limits for comprehensive analysis

## Architecture

```
Real-Time-Stock-Sentiment-Tracker/
├── app/
│   ├── scrapers/          # Data collection modules
│   │   ├── news_scraper.py     # BeautifulSoup-based news scraper
│   │   └── reddit_scraper.py   # PRAW-based Reddit scraper
│   ├── sentiment/         # Sentiment analysis
│   │   ├── analyzer.py         # Sentiment + NER pipeline
│   │   └── aggregator.py       # Multiple aggregation strategies
│   ├── database/          # Data persistence
│   │   ├── models.py           # SQLAlchemy models
│   │   └── manager.py          # Database operations
│   ├── templates/         # HTML templates
│   ├── config.py          # Configuration management
│   └── routes.py          # Flask API endpoints
├── data/                  # SQLite database storage
├── scrape_and_analyze.py  # CLI tool for data collection
├── run.py                 # Flask application entry point
└── requirements.txt       # Python dependencies
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Timmisetty1/Real-Time-Stock-Sentiment-Tracker.git
cd Real-Time-Stock-Sentiment-Tracker
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```ini
# Reddit API credentials (optional, get from https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=StockSentimentTracker/1.0

# Flask configuration
FLASK_ENV=development
SECRET_KEY=your_secret_key_here

# Target stocks
TARGET_STOCKS=AAPL,GOOGL,MSFT,AMZN,TSLA
```

## Usage

### Step 1: Scrape and Analyze Data

Run the scraper to collect news articles and Reddit posts:

```bash
# Scrape with default settings (1000 news + 500 Reddit posts)
python scrape_and_analyze.py

# Scrape more documents (up to 15K total)
python scrape_and_analyze.py --max-news 10000 --max-reddit 5000

# Scrape only news (skip Reddit)
python scrape_and_analyze.py --no-reddit

# Scrape specific tickers
python scrape_and_analyze.py --tickers AAPL,TSLA,NVDA
```

The scraper will:
1. Collect financial news from Yahoo Finance and MarketWatch
2. Scrape Reddit posts from finance-related subreddits
3. Perform sentiment analysis with NER for company mentions
4. Store results in SQLite database (`data/sentiment.db`)

### Step 2: Start the Flask Application

```bash
python run.py
```

Access the dashboard at: `http://localhost:5000`

## API Endpoints

### GET /api/stats
Get overall statistics including document counts and tracked companies.

**Response:**
```json
{
  "document_count": {
    "total": 1500,
    "news": 1000,
    "reddit": 500
  },
  "tracked_companies": 5,
  "companies": [...]
}
```

### GET /api/sentiment/{ticker}
Get sentiment data for a specific company.

**Parameters:**
- `days` (optional): Number of days to look back (default: 7)

**Response:**
```json
{
  "ticker": "AAPL",
  "aggregated": {
    "avg_sentiment": 0.65,
    "total_documents": 250,
    "positive_count": 180,
    "negative_count": 40,
    "neutral_count": 30
  },
  "history": [...]
}
```

### GET /api/companies
Get list of all tracked companies with sentiment summaries.

### GET /api/recent-documents
Get recent scraped documents.

**Parameters:**
- `limit` (optional): Number of documents to return (default: 50)
- `source` (optional): Filter by source ('news' or 'reddit')

### GET /api/sentiment-trend/{ticker}
Get sentiment trend over time for a company.

**Parameters:**
- `days` (optional): Number of days to analyze (default: 30)

## Sentiment Aggregation Strategies

The system supports multiple aggregation strategies:

1. **Simple Average**: Arithmetic mean of all sentiment scores
2. **Weighted Average**: Weight by confidence scores
3. **Exponential Moving Average (EMA)**: Give more weight to recent sentiment
4. **Volume-Weighted**: Weight by number of mentions
5. **Time-Window Aggregation**: Group by time periods

Example usage in code:

```python
from app.sentiment import SentimentAggregator

# Simple average
avg = SentimentAggregator.simple_average(scores)

# Weighted by confidence
weighted = SentimentAggregator.weighted_average(scores, confidences)

# Exponential moving average
ema = SentimentAggregator.exponential_moving_average(scores, timestamps)
```

## Database Schema

### Documents Table
- `id`: Primary key
- `source`: 'news' or 'reddit'
- `url`: Document URL
- `title`: Document title
- `content`: Full text content
- `author`: Author name
- `published_date`: Publication timestamp
- `scraped_date`: Scraping timestamp

### SentimentScores Table
- `id`: Primary key
- `document_id`: Foreign key to documents
- `company`: Stock ticker
- `sentiment_label`: 'POSITIVE', 'NEGATIVE', or 'NEUTRAL'
- `sentiment_score`: Float score (-1 to 1)
- `confidence`: Confidence level (0 to 1)
- `analyzed_date`: Analysis timestamp

### CompanyMentions Table
- `id`: Primary key
- `document_id`: Foreign key to documents
- `company`: Stock ticker
- `mention_count`: Number of mentions
- `context`: Context around mentions

## Technical Details

### Sentiment Analysis Model
- **Model**: DistilBERT fine-tuned on SST-2 (Stanford Sentiment Treebank)
- **Framework**: Hugging Face Transformers
- **Output**: Sentiment label (POSITIVE/NEGATIVE) with confidence score
- **Normalization**: Scores mapped to [-1, 1] range

### Named Entity Recognition
- **Model**: spaCy `en_core_web_sm`
- **Entities**: ORG (organizations)
- **Pattern Matching**: Ticker symbols ($AAPL, AAPL format)
- **Company Mapping**: Configurable company name → ticker mapping

### Web Scraping
- **News**: BeautifulSoup 4 with requests
- **Reddit**: PRAW (Python Reddit API Wrapper)
- **Rate Limiting**: Built-in delays to respect API limits
- **Error Handling**: Graceful failure with logging

## Configuration

All configuration is managed through `app/config.py` and environment variables:

```python
# Sentiment model
SENTIMENT_MODEL = 'distilbert-base-uncased-finetuned-sst-2-english'

# NER model
NER_MODEL = 'en_core_web_sm'

# Scraping limits
MAX_NEWS_ARTICLES = 15000
MAX_REDDIT_POSTS = 5000

# Target subreddits
REDDIT_SUBREDDITS = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']

# Target stocks
TARGET_STOCKS = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']
```

## Development

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_sentiment.py
```

### Adding New Data Sources

To add a new news source, extend the `NewsScraper` class:

```python
def scrape_new_source(self, ticker):
    # Implementation
    return articles
```

### Adding New Aggregation Strategies

Extend the `SentimentAggregator` class:

```python
@staticmethod
def custom_aggregation(scores):
    # Implementation
    return aggregated_score
```

## Troubleshooting

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### Reddit API Errors
- Verify credentials in `.env`
- Check rate limits
- Ensure Reddit app is configured at https://www.reddit.com/prefs/apps

### Database Locked
- Ensure only one instance is writing
- Check file permissions on `data/` directory

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Acknowledgments

- **BeautifulSoup**: HTML parsing
- **PRAW**: Reddit API wrapper
- **Hugging Face Transformers**: Sentiment analysis models
- **spaCy**: Named entity recognition
- **Flask**: Web framework
- **SQLAlchemy**: Database ORM