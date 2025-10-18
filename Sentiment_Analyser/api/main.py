"""
FastAPI application for Shameless Sentiment Analyser.

Provides API endpoints for scraping tweets.
"""

import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
import json
from pathlib import Path
import requests
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


    # Directory where external analysis JSONs will be stored
    STORED_EXTERNAL_DIR: Path = settings.PROCESSED_DATA_DIR / "external_stored"
    STORED_EXTERNAL_DIR.mkdir(parents=True, exist_ok=True)


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


# --- External analysis fetch & storage endpoints ---


@app.get("/api/external/fetch/{handle}")
def fetch_and_store_external(handle: str, force: bool = Query(False, description="If true, re-fetch from external API even if a stored file exists")):
    """Fetch analysis from the configured external REST API for `handle` and persist it to disk.

    Returns the fetched (or existing) JSON content.
    """
    base = settings.EXTERNAL_ANALYSIS_API_BASE
    if not base:
        raise HTTPException(status_code=503, detail="EXTERNAL_ANALYSIS_API_BASE is not configured on the server.")

    # Build target URL: assume the external API expects the handle appended to the base URL
    url = f"{base.rstrip('/')}/{handle}"
    logger.info(f"Fetching external analysis for '{handle}' from {url}")

    target_file = STORED_EXTERNAL_DIR / f"{handle}.json"
    # If already stored and no force, return stored copy
    if target_file.exists() and not force:
        try:
            with open(target_file, 'r', encoding='utf-8') as fh:
                return json.load(fh)
        except Exception as e:
            logger.warning(f"Could not read existing stored file for {handle}: {e}")

    # Fetch from external API
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.HTTPError as e:
        logger.error(f"External API returned HTTP error for {handle}: {e}")
        raise HTTPException(status_code=502, detail=f"External API error: {e}")
    except Exception as e:
        logger.error(f"Error fetching external API for {handle}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch external API: {e}")

    # Persist to disk (atomic write)
    try:
        tmp_path = target_file.with_suffix('.json.tmp')
        with open(tmp_path, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        tmp_path.replace(target_file)
    except Exception as e:
        logger.error(f"Failed to persist external analysis for {handle}: {e}")
        # we still return the fetched data even if persisting failed
    return data


@app.get("/api/stored_users")
def list_stored_users():
    """Return a list of all stored external analysis JSONs (parsed).

    Each item is the parsed JSON saved for a handle. Results are ordered by modification time (newest first).
    """
    out = []
    try:
        files = sorted(STORED_EXTERNAL_DIR.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
        for p in files:
            try:
                with open(p, 'r', encoding='utf-8') as fh:
                    out.append(json.load(fh))
            except Exception as e:
                logger.warning(f"Skipping stored file {p} due to read error: {e}")
    except Exception as e:
        logger.error(f"Error listing stored external files: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list stored users: {e}")
    return out


@app.get("/api/stored_user/{handle}")
def get_stored_user(handle: str):
    """Return the stored JSON for a specific handle, if available."""
    target_file = STORED_EXTERNAL_DIR / f"{handle}.json"
    if not target_file.exists():
        raise HTTPException(status_code=404, detail=f"No stored data for '{handle}'. Use /api/external/fetch/{handle} to fetch it.")
    try:
        with open(target_file, 'r', encoding='utf-8') as fh:
            return json.load(fh)
    except Exception as e:
        logger.error(f"Failed to read stored file for {handle}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read stored data for '{handle}': {e}")


