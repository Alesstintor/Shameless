'''
Bluesky data collector using the atproto library.
'''

import logging
from typing import Generator, List, Optional

from atproto import Client, models

from Sentiment_Analyser.config import get_settings
from .schemas import Tweet

logger = logging.getLogger(__name__)


class BlueskyCollector:
    """
    Collector for Bluesky data using the atproto SDK.
    """

    def __init__(self):
        """Initialize Bluesky collector and log in."""
        self.settings = get_settings()
        self.client = Client()
        self._logged_in = False

        handle = self.settings.BLUESKY_HANDLE
        password = self.settings.BLUESKY_PASSWORD

        if not (handle and password):
            raise ValueError("Bluesky credentials (BLUESKY_HANDLE, BLUESKY_PASSWORD) must be set.")

        try:
            logger.info(f"Attempting to log in to Bluesky as {handle}...")
            self.client.login(handle, password)
            self._logged_in = True
            logger.info("Bluesky login successful.")
        except Exception as e:
            logger.error(f"Failed to log in to Bluesky: {e}")
            raise

    def _parse_post(self, post_view: models.AppBskyFeedDefs.PostView) -> Tweet:
        """
        Parse an atproto PostView object to our internal Tweet dataclass.
        """
        record = post_view.record
        author = post_view.author

        # Extract hashtags from text or tags attribute
        hashtags = []
        if hasattr(record, 'tags') and record.tags:
            hashtags = list(record.tags)
        elif isinstance(record.text, str):
            hashtags = [word[1:] for word in record.text.split() if word.startswith('#')]

        # Mentions are not a first-class entity in the same way, requires parsing
        # This is a simplified placeholder
        mentions = []

        return Tweet(
            id=post_view.uri.split('/')[-1],  # Extract post ID from URI
            content=record.text,
            user=author.display_name or author.handle,
            username=author.handle,
            date=record.created_at,
            likes=post_view.like_count or 0,
            retweets=post_view.repost_count or 0,
            replies=post_view.reply_count or 0,
            url=f"https://bsky.app/profile/{author.handle}/post/{post_view.uri.split('/')[-1]}",
            hashtags=hashtags,
            mentions=mentions,
            language=getattr(record, 'langs', [None])[0]
        )

    def get_user_posts(
        self, handle: str, limit: int = 25
    ) -> Generator[Tweet, None, None]:
        """
        Get recent posts from a specific Bluesky user.

        Args:
            handle: The user's handle (e.g., 'jay.bsky.team').
            limit: Maximum number of posts to collect.

        Yields:
            Tweet objects.
        """
        if not self._logged_in:
            raise ConnectionError("Client is not logged in. Cannot fetch posts.")

        logger.info(f"Collecting posts for Bluesky user: {handle}")

        try:
            # The official method to get a user's feed is get_author_feed
            response = self.client.app.bsky.feed.get_author_feed(
                actor=handle, limit=limit
            )

            if not response or not response.feed:
                logger.warning(f"Could not find any posts for user {handle}.")
                return

            for feed_item in response.feed:
                # We only care about original posts, not reposts for now
                if feed_item.post:
                    yield self._parse_post(feed_item.post)

        except Exception as e:
            logger.error(f"An error occurred collecting Bluesky posts for {handle}: {e}")
            raise

        logger.info(f"Collection completed for Bluesky user: {handle}.")
