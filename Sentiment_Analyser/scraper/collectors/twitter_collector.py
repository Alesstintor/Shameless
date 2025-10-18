"""
Twitter data collector using twikit.

Provides functionality to scrape tweets using cookie-based authentication.
"""

import logging
import asyncio
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import AsyncGenerator, List, Optional

from twikit import Client
from twikit.errors import TwitterException

from Sentiment_Analyser.config import get_settings

logger = logging.getLogger(__name__)


@dataclass
class Tweet:
    """Data class representing a scraped tweet. Kept consistent for downstream compatibility."""

    id: str
    content: str
    user: str
    username: str
    date: datetime
    likes: int
    retweets: int
    replies: int
    url: str
    hashtags: List[str]
    mentions: List[str]
    language: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert tweet to dictionary."""
        data = asdict(self)
        data["date"] = self.date.isoformat()
        return data


class TwitterCollector:
    """
    Collector for Twitter data using twikit.
    Handles authentication and provides async methods for data collection.
    """

    def __init__(self):
        """Initialize Twitter collector with twikit client."""
        self.settings = get_settings()
        self.client = Client("en-US")
        self._logged_in = False

    async def _login_if_needed(self):
        """Logs in to the client using credentials from settings if not already logged in."""
        if self._logged_in:
            return

        username = self.settings.TWITTER_USERNAME
        email = self.settings.TWITTER_EMAIL
        password = self.settings.TWITTER_PASSWORD

        if not (username and email and password):
            raise ValueError(
                "Twitter credentials (TWITTER_USERNAME, TWITTER_EMAIL, TWITTER_PASSWORD) are not fully set in settings."
            )

        try:
            logger.info(f"Attempting to log in to Twitter as '{username}'...")
            await self.client.login(
                auth_info_1=username,
                auth_info_2=email,
                password=password
            )
            self._logged_in = True
            logger.info("Successfully logged in.")
        except TwitterException as e:
            logger.error(f"Failed to log in with credentials: {e}")
            raise

    def _parse_tweet(self, twikit_tweet) -> Tweet:
        """
        Parse a twikit tweet object to our internal Tweet dataclass.

        Args:
            twikit_tweet: Raw tweet object from twikit.

        Returns:
            Parsed Tweet object.
        """
        user_mentions = [
            mention["screen_name"] for mention in twikit_tweet.user_mentions
        ]
        # The URL can be constructed from the username and tweet id
        tweet_url = f"https://twitter.com/{twikit_tweet.user.screen_name}/status/{twikit_tweet.id}"

        return Tweet(
            id=twikit_tweet.id,
            content=twikit_tweet.text,
            user=twikit_tweet.user.name,
            username=twikit_tweet.user.screen_name,
            date=twikit_tweet.created_at,
            likes=twikit_tweet.favorite_count,
            retweets=twikit_tweet.retweet_count,
            replies=twikit_tweet.reply_count,
            url=tweet_url,
            hashtags=twikit_tweet.hashtags,
            mentions=user_mentions,
            language=twikit_tweet.lang,
        )

    async def search(
        self,
        query: str,
        limit: int = 100,
        since: Optional[
            str
        ] = None,  # Note: twikit search doesn't directly support date ranges
        until: Optional[str] = None,
    ) -> AsyncGenerator[Tweet, None]:
        """
        Search for tweets matching the query.

        Args:
            query: Search query.
            limit: Maximum number of tweets to collect.

        Yields:
            Tweet objects.
        """
        await self._login_if_needed()
        logger.info(f"Starting tweet search with query: '{query}'")

        count = 0
        try:
            async for tweet_obj in self.client.search_tweet(query, "Latest"):
                if count >= limit:
                    break
                yield self._parse_tweet(tweet_obj)
                count += 1
        except TwitterException as e:
            logger.error(f"An error occurred during tweet search: {e}")
            raise

        logger.info(f"Search completed. Total tweets collected: {count}")

    async def get_user_tweets(
        self, username: str, limit: int = 100
    ) -> AsyncGenerator[Tweet, None]:
        """
        Get tweets from a specific user.

        Args:
            username: Twitter username (without @).
            limit: Maximum number of tweets to collect.

        Yields:
            Tweet objects.
        """
        await self._login_if_needed()
        logger.info(f"Collecting tweets from user: @{username}")

        try:
            # First, get the user ID from the screen name
            user = await self.client.get_user_by_screen_name(username)
            if not user:
                raise ValueError(f"User with username '{username}' not found.")

            count = 0
            async for tweet_obj in self.client.get_user_tweets(user.id, "Tweets"):
                if count >= limit:
                    break
                yield self._parse_tweet(tweet_obj)
                count += 1
        except TwitterException as e:
            logger.error(f"An error occurred collecting user tweets: {e}")
            raise

        logger.info(f"Collection completed for @{username}. Total tweets: {count}")
