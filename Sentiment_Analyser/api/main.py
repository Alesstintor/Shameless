"""
FastAPI application for Shameless Sentiment Analyser.

Provides API endpoints for scraping tweets and analyzing sentiment.
"""

import logging
from typing import List, Optional
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from Sentiment_Analyser.config import get_settings
from Sentiment_Analyser.scraper.schemas import Tweet
from Sentiment_Analyser.scraper.collectors.twitter_collector import TwitterCollector
from Sentiment_Analyser.scraper.collectors.bluesky_collector import BlueskyCollector
from Sentiment_Analyser.models import SentimentAnalyzer

# Initialize logger and settings
logger = logging.getLogger(__name__)
settings = get_settings()

# --- Initialize Collectors ---

# Initialize Twitter Collector
try:
    twitter_collector = TwitterCollector()
except ValueError:
    twitter_collector = None
    logger.warning("Twitter credentials not set. The /api/twitter/ endpoints will be disabled.")

# Initialize Bluesky Collector
try:
    bluesky_collector = BlueskyCollector()
except ValueError:
    bluesky_collector = None
    logger.warning("Bluesky credentials not set. The /api/bluesky/ endpoint will be disabled.")

# Initialize Sentiment Analyzer with Kaggle model
try:
    sentiment_analyzer = SentimentAnalyzer(
        use_kaggle_model=True,
        kaggle_model_version="v1.0",
        device="cpu",
        preprocess=True
    )
    logger.info("Kaggle sentiment model loaded successfully")
except Exception as e:
    sentiment_analyzer = None
    logger.warning(f"Kaggle model not loaded: {e}. Sentiment analysis will be disabled.")

# Initialize FastAPI app
app = FastAPI(
    title="Shameless Sentiment Analyser API",
    description="API for scraping tweets from Twitter/X and analyzing sentiment.",
    version="0.1.0",
)

# Mount the frontend static files (adjust path relative to this file)
app.mount("/static", StaticFiles(directory="./frontend"), name="static")


# --- Response Models ---

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


@app.get("/")
def read_root():
    """Serve the frontend index.html if available, otherwise return API root info."""
    index_path = "./frontend/index.html"
    try:
        return FileResponse(index_path)
    except Exception:
        return {
            "message": "Welcome to the Shameless Sentiment Analyser API",
            "documentation": "/docs",
        }


@app.get("/api/twitter/search", response_model=List[Tweet])
def scrape_twitter_query(
    q: str = Query(..., description="The search query string."),
    limit: int = Query(25, ge=10, le=100, description="Number of tweets to return (10-100)."),
):
    """
    Scrape recent tweets from Twitter based on a search query (last 7 days).
    """
    if not twitter_collector:
        raise HTTPException(status_code=503, detail="Twitter integration is not configured on the server.")
    
    logger.info(f"API call: Scrape Twitter query='{q}' with limit={limit}")
    try:
        tweets_iterator = twitter_collector.search(query=q, limit=limit)
        tweets = list(tweets_iterator)
        return tweets
    except Exception as e:
        logger.error(f"Error scraping Twitter query '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/api/twitter/user/{username}", response_model=List[Tweet])
def scrape_twitter_user(
    username: str,
    limit: int = Query(25, ge=5, le=100, description="Number of tweets to return (5-100)."),
):
    """
    Scrape recent tweets from a specific Twitter user's timeline.
    """
    if not twitter_collector:
        raise HTTPException(status_code=503, detail="Twitter integration is not configured on the server.")

    logger.info(f"API call: Scrape Twitter user='{username}' with limit={limit}")
    try:
        tweets_iterator = twitter_collector.get_user_tweets(username=username, limit=limit)
        tweets = list(tweets_iterator)
        if not tweets:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found or has no public tweets.")
        return tweets
    except HTTPException as http_exc:
        # Re-raise HTTPException to avoid catching it as a generic exception
        raise http_exc
    except Exception as e:
        logger.error(f"Error scraping Twitter user '{username}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


# --- Bluesky Endpoints ---

@app.get("/api/bluesky/user/{handle}", response_model=List[Tweet])
def scrape_bluesky_user(
    handle: str,
    limit: int = Query(25, ge=1, le=100, description="Number of posts to return (1-100)."),
):
    """
    Scrape recent posts from a specific Bluesky user's timeline.
    """
    if not bluesky_collector:
        raise HTTPException(status_code=503, detail="Bluesky integration is not configured on the server.")

    logger.info(f"API call: Scrape Bluesky user='{handle}' with limit={limit}")
    try:
        posts_iterator = bluesky_collector.get_user_posts(handle=handle, limit=limit)
        posts = list(posts_iterator)
        if not posts:
            raise HTTPException(status_code=404, detail=f"User '{handle}' not found or has no public posts.")
        return posts
    except Exception as e:
        logger.error(f"Error scraping Bluesky user '{handle}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


# --- Sentiment Analysis Endpoints ---

@app.get("/api/analyze/twitter/user/{username}", response_model=List[TweetWithSentiment])
def analyze_twitter_user_sentiment(
    username: str,
    limit: int = Query(25, ge=5, le=100, description="Number of tweets to analyze (5-100)."),
):
    """
    Scrape tweets from a Twitter user and analyze sentiment using Kaggle-trained model.
    Returns tweets with sentiment (positive/negative) and confidence score.
    """
    if not twitter_collector:
        raise HTTPException(status_code=503, detail="Twitter integration is not configured on the server.")
    
    if not sentiment_analyzer:
        raise HTTPException(status_code=503, detail="Sentiment analysis model is not available.")
    
    logger.info(f"API call: Analyze Twitter user='{username}' sentiment with limit={limit}")
    
    try:
        # Scrape tweets
        tweets_iterator = twitter_collector.get_user_tweets(username=username, limit=limit)
        tweets = list(tweets_iterator)
        
        if not tweets:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found or has no public tweets.")
        
        # Analyze sentiment for each tweet
        analyzed_tweets = []
        for tweet in tweets:
            # Use 'content' attribute from Tweet schema
            result = sentiment_analyzer.analyze(tweet.content)
            
            analyzed_tweet = TweetWithSentiment(
                id=tweet.id,
                text=tweet.content,
                author=tweet.username,
                created_at=tweet.date.isoformat() if hasattr(tweet.date, 'isoformat') else str(tweet.date),
                url=tweet.url,
                sentiment=result.get('sentiment', 'unknown'),
                confidence=result.get('score', 0.0),
                label=result.get('label', 'UNKNOWN')
            )
            analyzed_tweets.append(analyzed_tweet)
        
        logger.info(f"Successfully analyzed {len(analyzed_tweets)} tweets from @{username}")
        return analyzed_tweets
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error analyzing Twitter user '{username}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/api/analyze/bluesky/user/{handle}", response_model=SentimentAnalysisResult)
def analyze_bluesky_user_sentiment(
    handle: str,
    limit: int = Query(25, ge=1, le=100, description="Number of posts to analyze (1-100)."),
):
    """
    Scrape posts from a Bluesky user and analyze sentiment using Kaggle-trained model.
    Returns posts with sentiment analysis, including most positive and most negative posts.
    """
    if not bluesky_collector:
        raise HTTPException(status_code=503, detail="Bluesky integration is not configured on the server.")
    
    if not sentiment_analyzer:
        raise HTTPException(status_code=503, detail="Sentiment analysis model is not available.")
    
    logger.info(f"API call: Analyze Bluesky user='{handle}' sentiment with limit={limit}")
    
    try:
        # Get user profile information
        try:
            from atproto import models
            profile_params = models.AppBskyActorGetProfile.Params(actor=handle)
            profile = bluesky_collector.client.app.bsky.actor.get_profile(profile_params)
            user_name = profile.display_name or profile.handle
            user_handle = profile.handle
            user_avatar = profile.avatar if hasattr(profile, 'avatar') else None
        except Exception as e:
            logger.warning(f"Could not fetch user profile: {e}")
            user_name = handle
            user_handle = handle
            user_avatar = None
        
        # Scrape posts
        posts_iterator = bluesky_collector.get_user_posts(handle=handle, limit=limit)
        posts = list(posts_iterator)
        
        if not posts:
            raise HTTPException(status_code=404, detail=f"User '{handle}' not found or has no public posts.")
        
        # Analyze sentiment for each post
        analyzed_posts = []
        positive_count = 0
        negative_count = 0
        total_confidence = 0
        
        for post in posts:
            # Use 'content' attribute from Tweet schema
            result = sentiment_analyzer.analyze(post.content)
            
            analyzed_post = TweetWithSentiment(
                id=post.id,
                text=post.content,
                author=post.username,
                created_at=post.date.isoformat() if hasattr(post.date, 'isoformat') else str(post.date),
                url=post.url,
                sentiment=result.get('sentiment', 'unknown'),
                confidence=result.get('score', 0.0),
                label=result.get('label', 'UNKNOWN')
            )
            analyzed_posts.append(analyzed_post)
            
            # Count sentiments
            if analyzed_post.sentiment == 'positive':
                positive_count += 1
            elif analyzed_post.sentiment == 'negative':
                negative_count += 1
            
            total_confidence += analyzed_post.confidence
        
        # Find most positive and most negative
        positive_posts = [p for p in analyzed_posts if p.sentiment == 'positive']
        negative_posts = [p for p in analyzed_posts if p.sentiment == 'negative']
        
        most_positive = max(positive_posts, key=lambda x: x.confidence) if positive_posts else analyzed_posts[0]
        most_negative = min(negative_posts, key=lambda x: x.confidence) if negative_posts else analyzed_posts[0]
        
        # Calculate average confidence
        avg_confidence = total_confidence / len(analyzed_posts) if analyzed_posts else 0.0
        
        result = SentimentAnalysisResult(
            user_name=user_name,
            user_handle=user_handle,
            user_avatar=user_avatar,
            posts=analyzed_posts,
            total_analyzed=len(analyzed_posts),
            positive_count=positive_count,
            negative_count=negative_count,
            average_confidence=avg_confidence,
            most_positive=most_positive,
            most_negative=most_negative
        )
        
        logger.info(f"Successfully analyzed {len(analyzed_posts)} posts from {handle}")
        return result
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"Error analyzing Bluesky user '{handle}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
