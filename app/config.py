"""
Configuration module for the Stock Sentiment Tracker application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Database settings
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/sentiment.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Reddit API settings
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'StockSentimentTracker/1.0')
    
    # Scraping settings
    NEWS_SOURCES = os.getenv('NEWS_SOURCES', '').split(',')
    TARGET_STOCKS = os.getenv('TARGET_STOCKS', 'AAPL,GOOGL,MSFT,AMZN,TSLA').split(',')
    
    # Sentiment analysis settings
    SENTIMENT_MODEL = 'distilbert-base-uncased-finetuned-sst-2-english'
    NER_MODEL = 'en_core_web_sm'
    
    # Scraping limits
    MAX_NEWS_ARTICLES = 15000
    MAX_REDDIT_POSTS = 5000
    REDDIT_SUBREDDITS = ['wallstreetbets', 'stocks', 'investing', 'StockMarket']
