"""
FastAPI application for Shameless Sentiment Analyser.

Provides API endpoints for scraping tweets.
"""

import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from Sentiment_Analyser.config import get_settings
from Sentiment_Analyser.scraper.schemas import Tweet
from Sentiment_Analyser.scraper.collectors.twitter_collector import TwitterCollector
from Sentiment_Analyser.scraper.collectors.bluesky_collector import BlueskyCollector

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

# Initialize FastAPI app
app = FastAPI(
    title="Shameless Sentiment Analyser API",
    description="API for scraping tweets from Twitter/X.",
    version="0.1.0",
)

# Mount the frontend static files (adjust path relative to this file)
app.mount("/static", StaticFiles(directory="./frontend"), name="static")




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


