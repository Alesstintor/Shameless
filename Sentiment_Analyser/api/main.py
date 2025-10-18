"""
FastAPI application for Shameless Sentiment Analyser.

Provides API endpoints for scraping tweets.
"""

import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from Sentiment_Analyser.config import get_settings
from Sentiment_Analyser.scraper.collectors.twitter_collector import TwitterCollector, Tweet

# Initialize logger and settings
logger = logging.getLogger(__name__)
settings = get_settings()

# Create a single, shared instance of the TwitterCollector
# This is more efficient than creating a new one for each request
collector = TwitterCollector()

# Initialize FastAPI app
app = FastAPI(
    title="Shameless Sentiment Analyser API",
    description="API for scraping tweets from Twitter/X.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    """Root endpoint providing basic information about the API."""
    return {
        "message": "Welcome to the Shameless Sentiment Analyser API",
        "documentation": "/docs",
    }


@app.get("/api/scrape/query", response_model=List[Tweet])
async def scrape_by_query(
    q: str = Query(..., description="The search query string."),
    limit: int = Query(100, ge=1, le=1000, description="Number of tweets to return."),
    since: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)."),
    until: Optional[str] = Query(None, description="End date (YYYY-MM-DD)."),
):
    """
    Scrape tweets based on a search query.
    """
    logger.info(f"API call: Scrape by query='{q}' with limit={limit}")
    try:
        tweets_iterator = collector.search(query=q, limit=limit, since=since, until=until)
        tweets = list(tweets_iterator)
        return tweets
    except Exception as e:
        logger.error(f"Error scraping query '{q}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/api/scrape/user/{username}", response_model=List[Tweet])
async def scrape_by_user(
    username: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of tweets to return."),
):
    """
    Scrape tweets from a specific user's timeline.
    """
    logger.info(f"API call: Scrape user='{username}' with limit={limit}")
    try:
        tweets_iterator = collector.get_user_tweets(username=username, limit=limit)
        tweets = list(tweets_iterator)
        if not tweets:
            raise HTTPException(status_code=404, detail=f"User '{username}' not found or has no public tweets.")
        return tweets
    except HTTPException as http_exc:
        # Re-raise HTTPException to avoid catching it as a generic exception
        raise http_exc
    except Exception as e:
        logger.error(f"Error scraping user '{username}': {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

