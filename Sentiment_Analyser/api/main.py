"""
FastAPI application for Shameless Sentiment Analyser.

Provides API endpoints for scraping tweets and analyzing sentiment.
"""

import logging
from typing import List

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from Sentiment_Analyser.config import get_settings
from Sentiment_Analyser.scraper.schemas import Tweet
from Sentiment_Analyser.scraper.collectors.twitter_collector import TwitterCollector
from Sentiment_Analyser.scraper.collectors.bluesky_collector import BlueskyCollector
from Sentiment_Analyser.models import SentimentAnalyzer
from Sentiment_Analyser.storage import UserDatabase
from Sentiment_Analyser.api.schemas import TweetWithSentiment, SentimentAnalysisResult
from Sentiment_Analyser.deepseek import DeepSeekAnalyzer

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
        kaggle_model_version=settings.MODEL_VERSION,
        device=settings.MODEL_DEVICE,
        preprocess=True
    )
    logger.info(f"Kaggle sentiment model loaded successfully (version: {settings.MODEL_VERSION}, device: {settings.MODEL_DEVICE})")
except Exception as e:
    sentiment_analyzer = None
    logger.warning(f"Kaggle model not loaded: {e}. Sentiment analysis will be disabled.")

# Initialize DeepSeek Analyzer
try:
    deepseek_analyzer = DeepSeekAnalyzer()
    if deepseek_analyzer.is_available():
        logger.info("✅ DeepSeek personality analyzer initialized successfully")
    else:
        logger.info("⚠️ DeepSeek API token not configured. Personality analysis disabled.")
except Exception as e:
    deepseek_analyzer = None
    logger.warning(f"DeepSeek analyzer initialization failed: {e}")

# Initialize FastAPI app
app = FastAPI(
    title="Shameless Sentiment Analyser API",
    description="API for scraping tweets from Twitter/X and analyzing sentiment.",
    version="0.1.0",
)

# Mount the frontend static files (adjust path relative to this file)
app.mount("/static", StaticFiles(directory="./frontend"), name="static")

# Initialize User Database
user_db = UserDatabase()


# --- Background Tasks ---

def generate_personality_analysis_task(handle: str):
    """
    Background task to generate personality analysis and update database.
    
    This runs asynchronously after the main analysis is complete.
    """
    try:
        if not deepseek_analyzer or not deepseek_analyzer.is_available():
            logger.info(f"⏭️ Skipping personality analysis for {handle} - DeepSeek not configured")
            return
        
        logger.info(f"🧠 Background: Starting personality analysis for {handle}")
        
        # Get analysis from database
        user_data = user_db.get_by_handle(handle)
        if not user_data:
            logger.warning(f"⚠️ Background: User data not found for {handle}")
            return
        
        posts = user_data.get('posts', [])
        user_name = user_data.get('user_name', handle)
        
        if not posts:
            logger.warning(f"⚠️ Background: No posts found for {handle}")
            return
        
        # Generate personality analysis
        personality_analysis = deepseek_analyzer.analyze_personality(posts, user_name)
        
        if personality_analysis:
            # Update database with personality analysis
            user_data['personality_analysis'] = personality_analysis
            user_db.save_analysis(user_data)
            logger.info(f"✅ Background: Personality analysis saved for {handle}")
        else:
            logger.warning(f"⚠️ Background: DeepSeek returned no analysis for {handle}")
            
    except Exception as e:
        logger.error(f"❌ Background: Error generating personality analysis for {handle}: {e}")
        import traceback
        logger.debug(f"   Traceback: {traceback.format_exc()}")


# --- Root Endpoint ---

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
        logger.error("❌ Bluesky collector not initialized - credentials missing")
        raise HTTPException(status_code=503, detail="Bluesky integration is not configured on the server.")

    logger.info(f"📥 API endpoint called: GET /api/bluesky/user/{handle} (limit={limit})")
    
    try:
        logger.info(f"🔄 Starting post collection from Bluesky for user: {handle}")
        posts_iterator = bluesky_collector.get_user_posts(handle=handle, limit=limit)
        posts = list(posts_iterator)
        
        logger.info(f"📊 Collection result: {len(posts)} posts retrieved")
        
        if not posts:
            logger.warning(f"⚠️ No posts found for user '{handle}' - returning 404")
            raise HTTPException(status_code=404, detail=f"User '{handle}' not found or has no public posts.")
        
        logger.info(f"✅ Successfully returning {len(posts)} posts for user: {handle}")
        return posts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error scraping Bluesky user '{handle}': {type(e).__name__}: {e}")
        import traceback
        logger.debug(f"   Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")



@app.get("/api/users")
def get_saved_users():
    """
    Get list of all saved analyzed users from database.
    Returns the last 10 analyzed users in reverse chronological order.
    """
    users = user_db.read_all()
    return JSONResponse(content=users)


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
    background_tasks: BackgroundTasks,
    limit: int = Query(25, ge=1, le=100, description="Number of posts to analyze (1-100)."),
):
    """
    Scrape posts from a Bluesky user and analyze sentiment using Kaggle-trained model.
    Returns posts with sentiment analysis, including most positive and most negative posts.
    """
    if not bluesky_collector:
        logger.error("❌ Bluesky collector not initialized - credentials missing")
        raise HTTPException(status_code=503, detail="Bluesky integration is not configured on the server.")
    
    if not sentiment_analyzer:
        logger.error("❌ Sentiment analyzer not initialized - model not loaded")
        raise HTTPException(status_code=503, detail="Sentiment analysis model is not available.")
    
    logger.info(f"🎯 API endpoint called: POST /api/analyze/bluesky/user/{handle} (limit={limit})")
    
    try:
        # Get user profile information
        logger.info(f"👤 Fetching profile information for: {handle}")
        try:
            from atproto import models
            profile_params = models.AppBskyActorGetProfile.Params(actor=handle)
            profile = bluesky_collector.client.app.bsky.actor.get_profile(profile_params)
            user_name = profile.display_name or profile.handle
            user_handle = profile.handle
            user_avatar = profile.avatar if hasattr(profile, 'avatar') else None
            logger.info(f"✅ Profile found: {user_name} (@{user_handle})")
        except Exception as e:
            logger.warning(f"⚠️ Could not fetch user profile for '{handle}': {type(e).__name__}: {e}")
            logger.info("💡 Continuing with handle as fallback name")
            user_name = handle
            user_handle = handle
            user_avatar = None
        
        # Scrape posts
        logger.info(f"📥 Starting to collect posts for '{handle}' (limit: {limit})")
        posts_iterator = bluesky_collector.get_user_posts(handle=handle, limit=limit)
        posts = list(posts_iterator)
        
        logger.info(f"📦 Post collection completed: {len(posts)} posts retrieved")
        
        if not posts:
            logger.warning(f"⚠️ No posts found for user '{handle}' - returning 404")
            raise HTTPException(status_code=404, detail=f"User '{handle}' not found or has no public posts.")
        
        # Analyze sentiment for each post
        logger.info(f"🤖 Starting sentiment analysis for {len(posts)} posts...")
        analyzed_posts = []
        positive_count = 0
        negative_count = 0
        total_confidence = 0
        
        for idx, post in enumerate(posts, 1):
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
            
            if idx % 5 == 0:
                logger.debug(f"   Analyzed {idx}/{len(posts)} posts...")
        
        logger.info(f"✅ Sentiment analysis completed: {positive_count} positive, {negative_count} negative")
        
        # Find most positive and most negative
        positive_posts = [p for p in analyzed_posts if p.sentiment == 'positive']
        negative_posts = [p for p in analyzed_posts if p.sentiment == 'negative']
        
        most_positive = max(positive_posts, key=lambda x: x.confidence) if positive_posts else analyzed_posts[0]
        most_negative = min(negative_posts, key=lambda x: x.confidence) if negative_posts else analyzed_posts[0]
        
        # Calculate average confidence
        avg_confidence = total_confidence / len(analyzed_posts) if analyzed_posts else 0.0
        
        logger.info(f"📊 Creating analysis result summary (avg confidence: {avg_confidence:.2%})")
        
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
        
        # Save to database
        logger.info(f"💾 Saving analysis to database for user: {handle}")
        user_db.save_analysis(result.dict())
        logger.info(f"✅ Analysis saved successfully")
        
        # Launch background task to generate personality analysis
        background_tasks.add_task(generate_personality_analysis_task, handle)
        logger.info(f"🚀 Launched background task for personality analysis of {handle}")
        
        logger.info(f"🎉 Analysis complete for '{handle}': {len(analyzed_posts)} posts, {positive_count}+ / {negative_count}-")
        return result
        
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Unexpected error analyzing Bluesky user '{handle}': {type(e).__name__}: {e}")
        import traceback
        logger.debug(f"   Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/api/personality/{handle}")
def get_personality_analysis(handle: str):
    """
    Get personality analysis for a user if it exists in the database.
    
    The personality analysis is generated automatically in the background
    when a user is analyzed. This endpoint just retrieves it if available.
    
    Returns:
        JSON with personality_analysis or null if not yet generated.
    """
    logger.info(f"📖 API endpoint called: GET /api/personality/{handle}")
    
    try:
        # Get analysis from database
        user_data = user_db.get_by_handle(handle)
        
        if not user_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No analysis found for '{handle}'."
            )
        
        personality_analysis = user_data.get('personality_analysis', None)
        
        return JSONResponse(content={
            "handle": handle,
            "personality_analysis": personality_analysis,
            "is_available": personality_analysis is not None
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving personality analysis for '{handle}': {e}")
        raise HTTPException(status_code=500, detail=str(e))
