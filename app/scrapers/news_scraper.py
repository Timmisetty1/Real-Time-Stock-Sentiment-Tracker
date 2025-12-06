"""
News scraper module using BeautifulSoup for financial news articles.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random


class NewsScraper:
    """Scraper for financial news articles."""
    
    def __init__(self, max_articles=10000):
        """
        Initialize the news scraper.
        
        Args:
            max_articles: Maximum number of articles to scrape
        """
        self.max_articles = max_articles
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.articles = []
    
    def scrape_yahoo_finance(self, ticker):
        """
        Scrape news articles from Yahoo Finance for a specific ticker.
        
        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL')
        
        Returns:
            List of article dictionaries
        """
        articles = []
        try:
            url = f'https://finance.yahoo.com/quote/{ticker}/news'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles - Yahoo Finance structure
            news_items = soup.find_all('li', class_='js-stream-content')[:50]
            
            for item in news_items:
                try:
                    title_elem = item.find('h3') or item.find('a')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.find('a')['href'] if title_elem.find('a') else None
                    
                    if link and not link.startswith('http'):
                        link = f'https://finance.yahoo.com{link}'
                    
                    # Try to get summary
                    summary_elem = item.find('p')
                    content = summary_elem.get_text(strip=True) if summary_elem else title
                    
                    if title and link:
                        articles.append({
                            'title': title,
                            'url': link,
                            'content': content,
                            'source': 'yahoo_finance',
                            'ticker': ticker,
                            'published_date': datetime.utcnow()
                        })
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"Error scraping Yahoo Finance for {ticker}: {e}")
        
        return articles
    
    def scrape_marketwatch(self, query):
        """
        Scrape news articles from MarketWatch.
        
        Args:
            query: Search query (e.g., stock ticker or company name)
        
        Returns:
            List of article dictionaries
        """
        articles = []
        try:
            url = f'https://www.marketwatch.com/search?q={query}&ts=0&tab=All%20News'
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find news articles
            news_items = soup.find_all('div', class_='article__content')[:50]
            
            for item in news_items:
                try:
                    title_elem = item.find('a', class_='link')
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    link = title_elem.get('href', '')
                    
                    # Get summary
                    summary_elem = item.find('p', class_='article__summary')
                    content = summary_elem.get_text(strip=True) if summary_elem else title
                    
                    if title and link:
                        articles.append({
                            'title': title,
                            'url': link,
                            'content': content,
                            'source': 'marketwatch',
                            'ticker': query,
                            'published_date': datetime.utcnow()
                        })
                except Exception as e:
                    print(f"Error parsing article: {e}")
                    continue
            
            # Add delay
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"Error scraping MarketWatch for {query}: {e}")
        
        return articles
    
    def scrape_generic_news_site(self, url, ticker=None):
        """
        Generic scraper for news websites.
        
        Args:
            url: URL of the news site
            ticker: Associated stock ticker
        
        Returns:
            List of article dictionaries
        """
        articles = []
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common article patterns
            article_tags = soup.find_all(['article', 'div'], class_=lambda x: x and any(
                keyword in str(x).lower() for keyword in ['article', 'post', 'news', 'story']
            ))[:50]
            
            for article in article_tags:
                try:
                    # Try to find title
                    title_elem = article.find(['h1', 'h2', 'h3', 'h4'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Try to find link
                    link_elem = article.find('a', href=True)
                    link = link_elem['href'] if link_elem else url
                    
                    if not link.startswith('http'):
                        from urllib.parse import urljoin
                        link = urljoin(url, link)
                    
                    # Try to get content
                    content_elem = article.find('p')
                    content = content_elem.get_text(strip=True) if content_elem else title
                    
                    if title and link:
                        articles.append({
                            'title': title,
                            'url': link,
                            'content': content,
                            'source': 'generic',
                            'ticker': ticker,
                            'published_date': datetime.utcnow()
                        })
                except Exception as e:
                    continue
            
            time.sleep(random.uniform(1, 2))
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        
        return articles
    
    def scrape_for_tickers(self, tickers):
        """
        Scrape news for multiple stock tickers.
        
        Args:
            tickers: List of stock ticker symbols
        
        Returns:
            List of all scraped articles
        """
        all_articles = []
        
        for ticker in tickers:
            if len(all_articles) >= self.max_articles:
                break
            
            print(f"Scraping news for {ticker}...")
            
            # Scrape from Yahoo Finance
            yahoo_articles = self.scrape_yahoo_finance(ticker)
            all_articles.extend(yahoo_articles)
            print(f"  Found {len(yahoo_articles)} articles from Yahoo Finance")
            
            # Scrape from MarketWatch
            mw_articles = self.scrape_marketwatch(ticker)
            all_articles.extend(mw_articles)
            print(f"  Found {len(mw_articles)} articles from MarketWatch")
            
            # Rate limiting
            time.sleep(random.uniform(2, 4))
        
        self.articles = all_articles[:self.max_articles]
        print(f"\nTotal articles scraped: {len(self.articles)}")
        return self.articles
    
    def get_articles(self):
        """Get all scraped articles."""
        return self.articles
