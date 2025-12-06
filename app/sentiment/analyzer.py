"""
Sentiment analyzer with Named Entity Recognition for company mentions.
"""
from transformers import pipeline
import spacy
import re


class SentimentAnalyzer:
    """Sentiment analysis with NER for tracking company mentions."""
    
    def __init__(self, sentiment_model='distilbert-base-uncased-finetuned-sst-2-english'):
        """
        Initialize the sentiment analyzer.
        
        Args:
            sentiment_model: Hugging Face model for sentiment analysis
        """
        print("Loading sentiment analysis model...")
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=sentiment_model,
                truncation=True,
                max_length=512
            )
            print("Sentiment model loaded successfully")
        except Exception as e:
            print(f"Error loading sentiment model: {e}")
            self.sentiment_pipeline = None
        
        print("Loading NER model...")
        try:
            # Try to load spaCy model
            self.nlp = spacy.load('en_core_web_sm')
            print("NER model loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load spaCy model: {e}")
            print("Run: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Company name to ticker mapping (extendable)
        self.company_mappings = {
            'apple': 'AAPL',
            'google': 'GOOGL',
            'alphabet': 'GOOGL',
            'microsoft': 'MSFT',
            'amazon': 'AMZN',
            'tesla': 'TSLA',
            'meta': 'META',
            'facebook': 'META',
            'nvidia': 'NVDA',
            'netflix': 'NFLX',
            'amd': 'AMD',
        }
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment label and score
        """
        if not self.sentiment_pipeline or not text:
            return {
                'label': 'NEUTRAL',
                'score': 0.5,
                'confidence': 0.0
            }
        
        try:
            # Truncate text if too long
            text = text[:512]
            result = self.sentiment_pipeline(text)[0]
            
            # Convert to normalized score (-1 to 1)
            label = result['label'].upper()
            confidence = result['score']
            
            if label == 'POSITIVE':
                sentiment_score = confidence
            elif label == 'NEGATIVE':
                sentiment_score = -confidence
            else:
                sentiment_score = 0.0
            
            return {
                'label': label,
                'score': sentiment_score,
                'confidence': confidence
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'label': 'NEUTRAL',
                'score': 0.0,
                'confidence': 0.0
            }
    
    def extract_company_mentions(self, text, target_tickers=None):
        """
        Extract company mentions using NER and pattern matching.
        
        Args:
            text: Text to analyze
            target_tickers: List of ticker symbols to look for
        
        Returns:
            Dictionary mapping tickers to mention counts and contexts
        """
        mentions = {}
        
        if not text:
            return mentions
        
        text_lower = text.lower()
        
        # Pattern matching for ticker symbols (e.g., $AAPL, AAPL)
        ticker_pattern = r'\$?([A-Z]{2,5})\b'
        found_tickers = re.findall(ticker_pattern, text)
        
        for ticker in found_tickers:
            if target_tickers and ticker in target_tickers:
                if ticker not in mentions:
                    mentions[ticker] = {'count': 0, 'contexts': []}
                mentions[ticker]['count'] += 1
                
                # Extract context (words around the ticker)
                pattern = re.compile(rf'\b\S+\s+\S+\s+\$?{ticker}\b\s+\S+\s+\S+', re.IGNORECASE)
                contexts = pattern.findall(text)
                if contexts:
                    mentions[ticker]['contexts'].extend(contexts[:3])  # Keep up to 3 contexts
        
        # NER for organization names
        if self.nlp:
            try:
                doc = self.nlp(text[:1000])  # Limit text length for NER
                
                for ent in doc.ents:
                    if ent.label_ == 'ORG':
                        org_name = ent.text.lower()
                        
                        # Check if organization maps to a known ticker
                        ticker = self.company_mappings.get(org_name)
                        if ticker and (not target_tickers or ticker in target_tickers):
                            if ticker not in mentions:
                                mentions[ticker] = {'count': 0, 'contexts': []}
                            mentions[ticker]['count'] += 1
                            
                            # Get context
                            start = max(0, ent.start - 5)
                            end = min(len(doc), ent.end + 5)
                            context = doc[start:end].text
                            mentions[ticker]['contexts'].append(context)
            except Exception as e:
                print(f"Error in NER extraction: {e}")
        
        # Also check for company names in text
        for company_name, ticker in self.company_mappings.items():
            if target_tickers and ticker not in target_tickers:
                continue
            
            if company_name in text_lower:
                if ticker not in mentions:
                    mentions[ticker] = {'count': 0, 'contexts': []}
                mentions[ticker]['count'] += text_lower.count(company_name)
        
        return mentions
    
    def analyze_document(self, document, target_tickers=None):
        """
        Perform full analysis on a document.
        
        Args:
            document: Dictionary with 'title' and 'content'
            target_tickers: List of ticker symbols to track
        
        Returns:
            Dictionary with sentiment and company mentions
        """
        # Combine title and content for analysis
        full_text = f"{document.get('title', '')} {document.get('content', '')}"
        
        # Get sentiment
        sentiment = self.analyze_sentiment(full_text)
        
        # Extract company mentions
        mentions = self.extract_company_mentions(full_text, target_tickers)
        
        return {
            'sentiment': sentiment,
            'mentions': mentions,
            'text_length': len(full_text)
        }
    
    def batch_analyze(self, documents, target_tickers=None):
        """
        Analyze multiple documents.
        
        Args:
            documents: List of document dictionaries
            target_tickers: List of ticker symbols to track
        
        Returns:
            List of analysis results
        """
        results = []
        
        for i, doc in enumerate(documents):
            if i % 100 == 0:
                print(f"Analyzing document {i+1}/{len(documents)}...")
            
            result = self.analyze_document(doc, target_tickers)
            result['document'] = doc
            results.append(result)
        
        print(f"Analysis complete: {len(results)} documents processed")
        return results
