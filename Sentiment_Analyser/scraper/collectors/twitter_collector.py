'''
Twitter data collector using tweepy and the official Twitter API v2.

Provides functionality to fetch tweets using developer credentials.
'''

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Generator, List, Optional

import tweepy

from Sentiment_Analyser.config import get_settings

logger = logging.getLogger(__name__)


from .schemas import Tweet


class TwitterCollector:
    """
    Collector for Twitter data using tweepy.
    Handles authentication with Twitter API v2 credentials.
    """
    
    def __init__(self):
        """Initialize Twitter collector with tweepy client."""
        settings = get_settings()
        api_key = settings.TWITTER_API_KEY
        api_secret = settings.TWITTER_API_KEY_SECRET
        access_token = settings.TWITTER_ACCESS_TOKEN
        access_token_secret = settings.TWITTER_ACCESS_TOKEN_SECRET

        if not all([api_key, api_secret, access_token, access_token_secret]):
            raise ValueError("All Twitter API credentials must be set in settings.")

        try:
            logger.info("Authenticating with Twitter API v2...")
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            logger.info("Successfully authenticated.")
        except Exception as e:
            logger.error(f"Failed to authenticate with tweepy: {e}")
            raise

    def _parse_tweet(self, tweepy_tweet: tweepy.Tweet, users: dict) -> Tweet:
        """
        Parse a tweepy.Tweet object to our internal Tweet dataclass.

        Args:
            tweepy_tweet: Raw tweet object from tweepy.
            users: A dictionary mapping user IDs to user objects from the response includes.

        Returns:
            Parsed Tweet object.
        """
        author_info = users.get(tweepy_tweet.author_id, {})
        entities = tweepy_tweet.entities or {}
        hashtags = [tag['tag'] for tag in entities.get('hashtags', [])]
        mentions = [mention['username'] for mention in entities.get('mentions', [])]
        
        # Construct URL
        username = author_info.get('username', 'unknown')
        tweet_url = f"https://twitter.com/{username}/status/{tweepy_tweet.id}"

        return Tweet(
            id=str(tweepy_tweet.id),
            content=tweepy_tweet.text,
            user=author_info.get('name', 'Unknown User'),
            username=username,
            date=tweepy_tweet.created_at,
            likes=tweepy_tweet.public_metrics.get('like_count', 0),
            retweets=tweepy_tweet.public_metrics.get('retweet_count', 0),
            replies=tweepy_tweet.public_metrics.get('reply_count', 0),
            url=tweet_url,
            hashtags=hashtags,
            mentions=mentions,
            language=tweepy_tweet.lang
        )

    def search(
        self, query: str, limit: int = 100
    ) -> Generator[Tweet, None, None]:
        """
        Search for recent tweets matching the query (last 7 days for free tier).

        Args:
            query: Search query.
            limit: Maximum number of tweets to collect (10-100).

        Yields:
            Tweet objects.
        """
        logger.info(f"Starting tweet search with query: '{query}'")
        limit = max(10, min(100, limit))  # API v2 requires limit between 10 and 100

        try:
            response = self.client.search_recent_tweets(
                query=query,
                max_results=limit,
                tweet_fields=['created_at', 'public_metrics', 'lang', 'entities'],
                expansions=['author_id']
            )

            if not response.data:
                logger.warning("Search returned no tweets.")
                return

            users = {user["id"]: user for user in response.includes.get('users', [])}
            for tweet_obj in response.data:
                yield self._parse_tweet(tweet_obj, users)

        except tweepy.errors.TweepyException as e:
            logger.error(f"An error occurred during tweet search: {e}")
            raise

        logger.info(f"Search completed.")

    def get_user_tweets(
        self, username: str, limit: int = 100
    ) -> Generator[Tweet, None, None]:
        """
        Get recent tweets from a specific user.

        Args:
            username: Twitter username (without @).
            limit: Maximum number of tweets to collect (5-100).

        Yields:
            Tweet objects.
        """
        logger.info(f"Collecting tweets from user: @{username}")
        limit = max(5, min(100, limit))  # API v2 requires limit between 5 and 100

        try:
            user_response = self.client.get_user(username=username)
            if not user_response.data:
                raise ValueError(f"User with username '{username}' not found.")
            user_id = user_response.data.id

            response = self.client.get_users_tweets(
                id=user_id,
                max_results=limit,
                tweet_fields=['created_at', 'public_metrics', 'lang', 'entities'],
                expansions=['author_id']
            )

            if not response.data:
                logger.warning(f"User @{username} has no recent tweets.")
                return

            users = {user["id"]: user for user in response.includes.get('users', [])}
            for tweet_obj in response.data:
                yield self._parse_tweet(tweet_obj, users)

        except tweepy.errors.TweepyException as e:
            logger.error(f"An error occurred collecting user tweets: {e}")
            raise

        logger.info(f"Collection completed for @{username}.")
