"""
Sentiment aggregation strategies for combining multiple sentiment scores.
"""
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict


class SentimentAggregator:
    """Different aggregation strategies for sentiment scores."""
    
    @staticmethod
    def simple_average(scores):
        """
        Simple average of sentiment scores.
        
        Args:
            scores: List of sentiment score values
        
        Returns:
            Average score
        """
        if not scores:
            return 0.0
        return sum(scores) / len(scores)
    
    @staticmethod
    def weighted_average(scores, weights):
        """
        Weighted average based on confidence or other weights.
        
        Args:
            scores: List of sentiment scores
            weights: List of weights (e.g., confidence scores)
        
        Returns:
            Weighted average score
        """
        if not scores or not weights or len(scores) != len(weights):
            return 0.0
        
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        
        weighted_sum = sum(s * w for s, w in zip(scores, weights))
        return weighted_sum / total_weight
    
    @staticmethod
    def exponential_moving_average(scores, timestamps, decay_rate=0.1):
        """
        Exponential moving average giving more weight to recent scores.
        
        Args:
            scores: List of sentiment scores
            timestamps: List of timestamps
            decay_rate: Decay rate for older scores
        
        Returns:
            EMA score
        """
        if not scores or not timestamps:
            return 0.0
        
        # Sort by timestamp
        sorted_data = sorted(zip(timestamps, scores), key=lambda x: x[0])
        
        if len(sorted_data) == 1:
            return sorted_data[0][1]
        
        # Calculate time differences from most recent
        latest_time = sorted_data[-1][0]
        
        weighted_scores = []
        weights = []
        
        for timestamp, score in sorted_data:
            if isinstance(timestamp, datetime):
                time_diff = (latest_time - timestamp).total_seconds() / 3600  # Hours
            else:
                time_diff = 0
            
            weight = np.exp(-decay_rate * time_diff)
            weighted_scores.append(score * weight)
            weights.append(weight)
        
        total_weight = sum(weights)
        if total_weight == 0:
            return 0.0
        
        return sum(weighted_scores) / total_weight
    
    @staticmethod
    def mode_based(sentiment_labels):
        """
        Most common sentiment label.
        
        Args:
            sentiment_labels: List of sentiment labels ('POSITIVE', 'NEGATIVE', 'NEUTRAL')
        
        Returns:
            Most common label
        """
        if not sentiment_labels:
            return 'NEUTRAL'
        
        from collections import Counter
        counts = Counter(sentiment_labels)
        return counts.most_common(1)[0][0]
    
    @staticmethod
    def volume_weighted(scores, volumes):
        """
        Volume-weighted sentiment (e.g., weighted by number of mentions).
        
        Args:
            scores: List of sentiment scores
            volumes: List of volumes (e.g., mention counts)
        
        Returns:
            Volume-weighted score
        """
        return SentimentAggregator.weighted_average(scores, volumes)
    
    @staticmethod
    def aggregate_by_time_window(sentiment_data, window_hours=24):
        """
        Aggregate sentiment scores within time windows.
        
        Args:
            sentiment_data: List of dicts with 'score', 'timestamp', 'company'
            window_hours: Size of time window in hours
        
        Returns:
            Dictionary of aggregated scores by company
        """
        company_windows = defaultdict(lambda: defaultdict(list))
        
        for data in sentiment_data:
            company = data.get('company')
            score = data.get('score', 0)
            timestamp = data.get('timestamp', datetime.utcnow())
            
            if not company:
                continue
            
            # Determine which window this belongs to
            if isinstance(timestamp, datetime):
                window_key = timestamp.replace(minute=0, second=0, microsecond=0)
                window_key = window_key.replace(hour=(timestamp.hour // window_hours) * window_hours)
            else:
                window_key = 'default'
            
            company_windows[company][window_key].append(score)
        
        # Aggregate each window
        results = {}
        for company, windows in company_windows.items():
            results[company] = {}
            for window_key, scores in windows.items():
                results[company][window_key] = {
                    'average': SentimentAggregator.simple_average(scores),
                    'count': len(scores),
                    'positive_ratio': sum(1 for s in scores if s > 0) / len(scores) if scores else 0
                }
        
        return results
    
    @staticmethod
    def calculate_momentum(scores, timestamps):
        """
        Calculate sentiment momentum (trend direction).
        
        Args:
            scores: List of sentiment scores
            timestamps: List of timestamps
        
        Returns:
            Momentum value (positive = improving, negative = declining)
        """
        if len(scores) < 2:
            return 0.0
        
        # Sort by timestamp
        sorted_data = sorted(zip(timestamps, scores), key=lambda x: x[0])
        
        # Calculate simple linear trend
        x = list(range(len(sorted_data)))
        y = [s for _, s in sorted_data]
        
        # Simple linear regression slope
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi ** 2 for xi in x)
        
        denominator = (n * sum_x2 - sum_x ** 2)
        if denominator == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope
    
    @staticmethod
    def aggregate_with_strategy(analysis_results, strategy='weighted', company=None):
        """
        Aggregate sentiment results using specified strategy.
        
        Args:
            analysis_results: List of analysis results from SentimentAnalyzer
            strategy: Aggregation strategy ('simple', 'weighted', 'ema')
            company: Specific company ticker to aggregate for
        
        Returns:
            Aggregated sentiment score
        """
        # Filter for specific company if provided
        if company:
            relevant_results = [
                r for r in analysis_results
                if company in r.get('mentions', {})
            ]
        else:
            relevant_results = analysis_results
        
        if not relevant_results:
            return 0.0
        
        scores = [r['sentiment']['score'] for r in relevant_results]
        
        if strategy == 'simple':
            return SentimentAggregator.simple_average(scores)
        
        elif strategy == 'weighted':
            confidences = [r['sentiment']['confidence'] for r in relevant_results]
            return SentimentAggregator.weighted_average(scores, confidences)
        
        elif strategy == 'ema':
            timestamps = [
                r['document'].get('published_date') or 
                r['document'].get('created_utc') or 
                datetime.utcnow()
                for r in relevant_results
            ]
            return SentimentAggregator.exponential_moving_average(scores, timestamps)
        
        else:
            return SentimentAggregator.simple_average(scores)
