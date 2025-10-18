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
import requests
import json
from pathlib import Path
from fastapi import Response

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


# --- Simple JSON-backed storage for external API results ---
STORE_PATH = Path(settings.PROCESSED_DATA_DIR) / "users.json"


def read_store() -> dict:
    try:
        if not STORE_PATH.exists():
            return {}
        with STORE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to read store {STORE_PATH}: {e}")
        return {}


def write_store(data: dict):
    try:
        STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STORE_PATH.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to write store {STORE_PATH}: {e}")


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



@app.get("/api/external/user/{handle}")
def proxy_external_user(handle: str, response: Response):
    """
    Proxy to an external REST API that returns the complete sentiment analysis
    for a given handle. The external JSON is stored in
    Sentiment_Analyser/data/processed/users.json under the key `{handle}`.
    """
    if not settings.EXTERNAL_API_URL:
        # If external API URL isn't configured, fall back to using the Bluesky collector
        # so clients can call this endpoint and still get content. Persist the result
        # into the same JSON store for consistency.
        if bluesky_collector:
            try:
                logger.info(f"EXTERNAL_API_URL not set; using Bluesky collector fallback for {handle}")
                posts = list(bluesky_collector.get_user_posts(handle=handle, limit=25))
                posts_serialized = []
                for p in posts:
                    try:
                        if hasattr(p, 'to_dict'):
                            posts_serialized.append(p.to_dict())
                        else:
                            # best-effort serialization
                            posts_serialized.append(json.loads(json.dumps(p, default=str)))
                    except Exception:
                        posts_serialized.append(str(p))

                payload = {
                    "handle": handle,
                    "name": handle,
                    "avatar": None,
                    "posts": posts_serialized,
                }

                # Persist in JSON store under the handle key
                store = read_store()
                store[handle] = payload
                write_store(store)

                response.headers["Content-Type"] = "application/json; charset=utf-8"
                return JSONResponse(content=payload)
            except Exception as e:
                logger.error(f"Bluesky fallback failed for {handle}: {e}")
                raise HTTPException(status_code=500, detail=f"Bluesky fallback failed: {e}")

        raise HTTPException(status_code=500, detail="EXTERNAL_API_URL is not configured in settings.")

    # Build URL - allow the external API to accept either /user/{handle} or /{handle}
    base = settings.EXTERNAL_API_URL.rstrip("/")
    # First try common pattern: /user/{handle}
    candidates = [f"{base}/user/{handle}", f"{base}/{handle}", f"{base}?handle={handle}"]

    headers = {}
    if settings.EXTERNAL_API_KEY:
        headers["Authorization"] = f"Bearer {settings.EXTERNAL_API_KEY}"

    last_err = None
    for url in candidates:
        try:
            logger.info(f"Proxying external request to {url}")
            r = requests.get(url, headers=headers, timeout=settings.EXTERNAL_API_TIMEOUT)
            if r.status_code == 200:
                payload = r.json()

                # Persist in JSON store under the handle key
                store = read_store()
                store[handle] = payload
                write_store(store)

                # Return the payload as-is to the frontend
                response.headers["Content-Type"] = "application/json; charset=utf-8"
                return JSONResponse(content=payload)
            else:
                last_err = f"Status {r.status_code} from {url}"
                logger.warning(last_err)
        except requests.RequestException as e:
            last_err = str(e)
            logger.warning(f"Request to {url} failed: {e}")

    # If we reach here, all candidates failed
    logger.error(f"All external proxy attempts failed for handle={handle}: {last_err}")
    raise HTTPException(status_code=502, detail=f"Failed to fetch external data for '{handle}': {last_err}")


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
