'''
Bluesky data collector using the atproto library.
'''

import logging
from typing import Generator, List, Optional

from atproto import Client, models
from pydantic import ValidationError

from Sentiment_Analyser.config import get_settings
from ..schemas import Tweet

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
        self, handle: str, limit: int = 10
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

        logger.info(f"🔍 Starting post collection for Bluesky user: {handle} (limit: {limit})")
        posts_collected = 0
        posts_skipped = 0

        try:
            # Use invoke_query with validation disabled to bypass Pydantic validation errors
            # This is necessary because atproto SDK doesn't support video embeds yet
            import httpx
            
            # Build the request URL - use default Bluesky server
            server_url = "https://bsky.social"
            api_url = f"{server_url}/xrpc/app.bsky.feed.getAuthorFeed"
            params_dict = {"actor": handle, "limit": limit}
            
            logger.debug(f"📡 Making HTTP request to: {api_url}")
            logger.debug(f"📋 Request params: {params_dict}")
            
            # Make raw HTTP request to bypass Pydantic validation
            try:
                # Get auth token from logged in client
                headers = {}
                
                # Try to get the session token - atproto stores it in different places depending on version
                access_token = None
                if hasattr(self.client, 'me') and self.client.me:
                    if hasattr(self.client.me, 'accessJwt'):
                        access_token = self.client.me.accessJwt
                    elif hasattr(self.client.me, 'access_jwt'):
                        access_token = self.client.me.access_jwt
                
                # Try alternative ways to get the token
                if not access_token and hasattr(self.client, '_session'):
                    if hasattr(self.client._session, 'access_jwt'):
                        access_token = self.client._session.access_jwt
                    elif hasattr(self.client._session, 'accessJwt'):
                        access_token = self.client._session.accessJwt
                
                if access_token:
                    headers["Authorization"] = f"Bearer {access_token}"
                    logger.debug("🔑 Using authenticated request with token")
                else:
                    logger.error("❌ No authentication token found!")
                    logger.error(f"   Client attributes: {dir(self.client)}")
                    if hasattr(self.client, 'me'):
                        logger.error(f"   Client.me attributes: {dir(self.client.me)}")
                    raise ConnectionError("Cannot make authenticated request - no access token available")
                
                logger.info(f"📤 Sending request to Bluesky API for user: {handle}")
                http_response = httpx.get(api_url, params=params_dict, headers=headers, timeout=30.0)
                
                logger.debug(f"📥 HTTP Response status: {http_response.status_code}")
                http_response.raise_for_status()
                
                raw_data = http_response.json()
                logger.debug(f"📊 Response data keys: {list(raw_data.keys()) if raw_data else 'None'}")
                
                if not raw_data:
                    logger.error(f"❌ Empty response from Bluesky API for user: {handle}")
                    return
                
                if 'feed' not in raw_data:
                    logger.error(f"❌ Response missing 'feed' key for user: {handle}. Keys present: {list(raw_data.keys())}")
                    return
                
                feed_items = raw_data.get('feed', [])
                logger.info(f"📦 Received {len(feed_items)} feed items from API")
                
                if len(feed_items) == 0:
                    logger.warning(f"⚠️ User {handle} has no posts in their feed")
                    return
                
                # Process each feed item manually
                for idx, feed_item_raw in enumerate(feed_items, 1):
                    if 'post' not in feed_item_raw:
                        logger.debug(f"⏭️ Skipping feed item {idx}: no 'post' field")
                        continue
                    
                    try:
                        # Parse the post manually from raw JSON
                        post_data = feed_item_raw['post']
                        record = post_data.get('record', {})
                        author = post_data.get('author', {})
                        
                        # Extract basic post info
                        post_id = post_data.get('uri', '').split('/')[-1]
                        text = record.get('text', '')
                        created_at = record.get('createdAt', '')
                        
                        logger.debug(f"✅ Parsing post {idx}/{len(feed_items)}: {text[:50]}..." if text else f"✅ Parsing post {idx}/{len(feed_items)}")
                        
                        # Extract hashtags
                        hashtags = []
                        if 'tags' in record and record['tags']:
                            hashtags = list(record['tags'])
                        elif isinstance(text, str):
                            hashtags = [word[1:] for word in text.split() if word.startswith('#')]
                        
                        # Create Tweet object
                        tweet = Tweet(
                            id=post_id,
                            content=text,
                            user=author.get('displayName') or author.get('handle', ''),
                            username=author.get('handle', ''),
                            date=created_at,
                            likes=post_data.get('likeCount', 0),
                            retweets=post_data.get('repostCount', 0),
                            replies=post_data.get('replyCount', 0),
                            url=f"https://bsky.app/profile/{author.get('handle', '')}/post/{post_id}",
                            hashtags=hashtags,
                            mentions=[],
                            language=record.get('langs', [None])[0] if 'langs' in record else None
                        )
                        
                        yield tweet
                        posts_collected += 1
                        
                    except (KeyError, AttributeError, Exception) as e:
                        posts_skipped += 1
                        logger.warning(f"⚠️ Skipping post {idx} due to parsing error: {type(e).__name__}: {e}")
                        continue
                        
            except httpx.HTTPStatusError as he:
                status_code = he.response.status_code if hasattr(he, 'response') else 'N/A'
                logger.error(f"❌ HTTP error fetching feed for {handle}: Status {status_code}")
                
                if status_code == 401:
                    logger.error("🔐 Authentication failed (401 Unauthorized)")
                    logger.error("   This means the access token is invalid or expired")
                    logger.error("   Check your Bluesky credentials in .env file")
                    logger.error(f"   Using handle: {self.settings.BLUESKY_HANDLE}")
                elif status_code == 404:
                    logger.error(f"❌ User '{handle}' not found (404)")
                else:
                    logger.error(f"   Response: {he.response.text if hasattr(he, 'response') else 'N/A'}")
                
                return
            except httpx.HTTPError as he:
                logger.error(f"❌ HTTP connection error for {handle}: {he}")
                return
            except Exception as e:
                logger.error(f"❌ Error processing feed data for {handle}: {type(e).__name__}: {e}")
                import traceback
                logger.debug(f"   Traceback: {traceback.format_exc()}")
                return

        except ValidationError as ve:
            logger.error(f"❌ Validation error collecting Bluesky posts for {handle}: {ve}")
            logger.info("💡 This usually happens when posts contain unsupported content types (e.g., videos).")
            if posts_collected > 0:
                logger.info(f"✅ Successfully collected {posts_collected} posts before error.")
            return
        except Exception as e:
            logger.error(f"❌ An error occurred collecting Bluesky posts for {handle}: {type(e).__name__}: {e}")
            if posts_collected > 0:
                logger.info(f"✅ Collected {posts_collected} posts before error occurred.")
            import traceback
            logger.debug(f"   Full traceback: {traceback.format_exc()}")
            raise

        logger.info(f"✅ Collection completed for '{handle}': {posts_collected} posts collected, {posts_skipped} skipped.")
