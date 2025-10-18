"""
Business logic and services for the API.

Contains helper functions for data transformation and processing.
"""

import logging
from typing import Dict, List
from Sentiment_Analyser.scraper.schemas import Tweet

logger = logging.getLogger(__name__)


def extract_top_words_from_posts(posts: List[Tweet], top_n: int = 10, min_length: int = 3) -> List[str]:
    """
    Extract the most frequent words from a list of posts.
    
    Args:
        posts: List of Tweet/Post objects.
        top_n: Number of top words to return.
        min_length: Minimum word length to consider.
        
    Returns:
        List of top N most frequent words.
    """
    word_counts = {}
    
    for post in posts:
        text = post.content if hasattr(post, 'content') else str(post)
        
        # Tokenize and count
        tokens = text.lower().replace('#', '').replace('@', '')
        words = [w for w in tokens.split() if len(w) > min_length and w.isalpha()]
        
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and return top N
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:top_n]]


def generate_summary_from_sentiment(
    total_analyzed: int,
    positive_count: int,
    negative_count: int,
    average_confidence: float
) -> str:
    """
    Generate a human-readable summary from sentiment statistics.
    
    Args:
        total_analyzed: Total number of posts analyzed.
        positive_count: Number of positive posts.
        negative_count: Number of negative posts.
        average_confidence: Average confidence score (0-1).
        
    Returns:
        Summary string in Spanish.
    """
    if total_analyzed == 0:
        return "No se analizaron posts."
    
    # Calculate ratios
    positive_ratio = positive_count / total_analyzed
    negative_ratio = negative_count / total_analyzed
    
    # Determine overall sentiment
    if positive_ratio > 0.7:
        sentiment = "muy positivo"
    elif positive_ratio > 0.55:
        sentiment = "positivo"
    elif negative_ratio > 0.7:
        sentiment = "muy negativo"
    elif negative_ratio > 0.55:
        sentiment = "negativo"
    else:
        sentiment = "neutral"
    
    # Format confidence as percentage
    confidence_pct = average_confidence * 100
    
    return (
        f"Analizados {total_analyzed} posts. "
        f"Sentimiento general: {sentiment}. "
        f"Confianza promedio: {confidence_pct:.1f}%."
    )


def calculate_sentiment_distribution(
    positive_count: int,
    negative_count: int,
    total_count: int
) -> Dict[str, float]:
    """
    Calculate emotion distribution from sentiment counts.
    
    Maps positive/negative sentiments to emotion categories for visualization.
    
    Args:
        positive_count: Number of positive posts.
        negative_count: Number of negative posts.
        total_count: Total number of posts.
        
    Returns:
        Dictionary with emotion categories and their weights (0-1).
    """
    if total_count == 0:
        # Equal distribution if no data
        return {
            'joy': 0.2,
            'surprise': 0.2,
            'sadness': 0.2,
            'anger': 0.2,
            'fear': 0.2
        }
    
    positive_ratio = positive_count / total_count
    negative_ratio = negative_count / total_count
    neutral_ratio = 1 - positive_ratio - negative_ratio
    
    # Map to emotion categories
    return {
        'joy': positive_ratio * 0.6,          # Most positive → Joy
        'surprise': positive_ratio * 0.4,     # Some positive → Surprise
        'sadness': negative_ratio * 0.5,      # Most negative → Sadness
        'anger': negative_ratio * 0.3,        # Some negative → Anger
        'fear': negative_ratio * 0.2 + neutral_ratio  # Remaining → Fear
    }
