"""
Sentiment analysis module with NER for company mentions.
"""
from .analyzer import SentimentAnalyzer
from .aggregator import SentimentAggregator

__all__ = ['SentimentAnalyzer', 'SentimentAggregator']
