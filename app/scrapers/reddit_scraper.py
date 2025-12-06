"""
Reddit scraper module using PRAW for Reddit discussions.
"""
import praw
from datetime import datetime
import time


class RedditScraper:
    """Scraper for Reddit discussions."""
    
    def __init__(self, client_id, client_secret, user_agent, max_posts=5000):
        """
        Initialize the Reddit scraper.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string
            max_posts: Maximum number of posts to scrape
        """
        self.max_posts = max_posts
        self.posts = []
        
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            self.is_authenticated = True
        except Exception as e:
            print(f"Warning: Could not authenticate with Reddit API: {e}")
            print("Reddit scraping will be disabled.")
            self.is_authenticated = False
    
    def scrape_subreddit(self, subreddit_name, limit=100, time_filter='week'):
        """
        Scrape posts from a specific subreddit.
        
        Args:
            subreddit_name: Name of the subreddit
            limit: Number of posts to scrape
            time_filter: Time filter ('hour', 'day', 'week', 'month', 'year', 'all')
        
        Returns:
            List of post dictionaries
        """
        if not self.is_authenticated:
            return []
        
        posts = []
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Get hot posts
            for submission in subreddit.hot(limit=limit // 2):
                try:
                    post_data = {
                        'title': submission.title,
                        'url': f'https://reddit.com{submission.permalink}',
                        'content': submission.selftext or submission.title,
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'created_utc': datetime.fromtimestamp(submission.created_utc),
                        'subreddit': subreddit_name,
                        'source': 'reddit'
                    }
                    posts.append(post_data)
                except Exception as e:
                    print(f"Error processing submission: {e}")
                    continue
            
            # Get top posts
            for submission in subreddit.top(time_filter=time_filter, limit=limit // 2):
                try:
                    post_data = {
                        'title': submission.title,
                        'url': f'https://reddit.com{submission.permalink}',
                        'content': submission.selftext or submission.title,
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'created_utc': datetime.fromtimestamp(submission.created_utc),
                        'subreddit': subreddit_name,
                        'source': 'reddit'
                    }
                    posts.append(post_data)
                except Exception as e:
                    print(f"Error processing submission: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping subreddit {subreddit_name}: {e}")
        
        return posts
    
    def search_reddit(self, query, subreddit_name=None, limit=100):
        """
        Search Reddit for posts matching a query.
        
        Args:
            query: Search query
            subreddit_name: Specific subreddit to search (None for all)
            limit: Number of results
        
        Returns:
            List of post dictionaries
        """
        if not self.is_authenticated:
            return []
        
        posts = []
        try:
            if subreddit_name:
                subreddit = self.reddit.subreddit(subreddit_name)
            else:
                subreddit = self.reddit.subreddit('all')
            
            for submission in subreddit.search(query, limit=limit, sort='relevance'):
                try:
                    post_data = {
                        'title': submission.title,
                        'url': f'https://reddit.com{submission.permalink}',
                        'content': submission.selftext or submission.title,
                        'author': str(submission.author) if submission.author else '[deleted]',
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'created_utc': datetime.fromtimestamp(submission.created_utc),
                        'subreddit': str(submission.subreddit),
                        'source': 'reddit',
                        'query': query
                    }
                    posts.append(post_data)
                except Exception as e:
                    print(f"Error processing submission: {e}")
                    continue
        
        except Exception as e:
            print(f"Error searching Reddit for '{query}': {e}")
        
        return posts
    
    def scrape_multiple_subreddits(self, subreddit_list, limit_per_subreddit=100):
        """
        Scrape posts from multiple subreddits.
        
        Args:
            subreddit_list: List of subreddit names
            limit_per_subreddit: Number of posts per subreddit
        
        Returns:
            List of all posts
        """
        all_posts = []
        
        for subreddit in subreddit_list:
            if len(all_posts) >= self.max_posts:
                break
            
            print(f"Scraping r/{subreddit}...")
            posts = self.scrape_subreddit(subreddit, limit=limit_per_subreddit)
            all_posts.extend(posts)
            print(f"  Found {len(posts)} posts")
            
            # Rate limiting
            time.sleep(2)
        
        self.posts = all_posts[:self.max_posts]
        print(f"\nTotal Reddit posts scraped: {len(self.posts)}")
        return self.posts
    
    def scrape_for_tickers(self, tickers, subreddit_list):
        """
        Search for posts mentioning specific stock tickers.
        
        Args:
            tickers: List of stock ticker symbols
            subreddit_list: List of subreddits to search
        
        Returns:
            List of posts mentioning the tickers
        """
        all_posts = []
        
        for ticker in tickers:
            if len(all_posts) >= self.max_posts:
                break
            
            print(f"Searching Reddit for ${ticker}...")
            
            for subreddit in subreddit_list:
                if len(all_posts) >= self.max_posts:
                    break
                
                # Search for ticker with $ prefix (common on Reddit)
                posts = self.search_reddit(f'${ticker}', subreddit, limit=50)
                all_posts.extend(posts)
                
                time.sleep(1)
        
        self.posts = all_posts[:self.max_posts]
        print(f"\nTotal ticker-related posts: {len(self.posts)}")
        return self.posts
    
    def get_posts(self):
        """Get all scraped posts."""
        return self.posts
