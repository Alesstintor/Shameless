"""
Response schemas for the API.

Defines Pydantic models for API responses.
"""

from typing import List, Optional
from pydantic import BaseModel


class TweetWithSentiment(BaseModel):
    """Tweet/Post with sentiment analysis results."""
    id: str
    text: str
    author: str
    created_at: str
    url: str
    sentiment: str
    confidence: float
    label: str


class SentimentAnalysisResult(BaseModel):
    """Complete sentiment analysis result with summary."""
    user_name: str
    user_handle: str
    user_avatar: Optional[str]
    posts: List[TweetWithSentiment]
    total_analyzed: int
    positive_count: int
    negative_count: int
    average_confidence: float
    most_positive: TweetWithSentiment
    most_negative: TweetWithSentiment
