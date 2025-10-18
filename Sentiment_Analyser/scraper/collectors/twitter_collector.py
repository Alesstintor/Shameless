"""
Twitter data collector using snscrape.

Provides functionality to scrape tweets based on queries with rate limiting
and error handling.
"""

import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Generator, List, Optional

import snscrape.modules.twitter as sntwitter

logger = logging.getLogger(__name__)


@dataclass
class Tweet:
    """Data class representing a scraped tweet."""
    
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
        data['date'] = self.date.isoformat()
        return data


class TwitterCollector:
    """
    Collector for Twitter data using snscrape.
    
    Provides rate limiting, error handling, and data normalization.
    """
    
    def __init__(
        self,
        rate_limit: float = 1.0,
        max_retries: int = 3,
        timeout: int = 30
    ):
        """
        Initialize Twitter collector.
        
        Args:
            rate_limit: Maximum requests per second
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.timeout = timeout
        self._last_request_time = 0.0
        
    def _rate_limit_sleep(self):
        """Sleep to respect rate limiting."""
        elapsed = time.time() - self._last_request_time
        sleep_time = (1.0 / self.rate_limit) - elapsed
        
        if sleep_time > 0:
            time.sleep(sleep_time)
            
        self._last_request_time = time.time()
    
    def _parse_tweet(self, tweet_obj) -> Tweet:
        """
        Parse snscrape tweet object to our Tweet dataclass.
        
        Args:
            tweet_obj: Raw tweet object from snscrape
            
        Returns:
            Parsed Tweet object
        """
        return Tweet(
            id=str(tweet_obj.id),
            content=tweet_obj.rawContent,
            user=tweet_obj.user.displayname,
            username=tweet_obj.user.username,
            date=tweet_obj.date,
            likes=tweet_obj.likeCount or 0,
            retweets=tweet_obj.retweetCount or 0,
            replies=tweet_obj.replyCount or 0,
            url=tweet_obj.url,
            hashtags=tweet_obj.hashtags or [],
            mentions=[m.username for m in (tweet_obj.mentionedUsers or [])],
            language=tweet_obj.lang
        )
    
    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        since: Optional[str] = None,
        until: Optional[str] = None
    ) -> Generator[Tweet, None, None]:
        """
        Search for tweets matching the query.
        
        Args:
            query: Search query (supports Twitter advanced search syntax)
            limit: Maximum number of tweets to collect
            since: Start date in YYYY-MM-DD format
            until: End date in YYYY-MM-DD format
            
        Yields:
            Tweet objects
            
        Example:
            >>> collector = TwitterCollector()
            >>> for tweet in collector.search("python", limit=100):
            ...     print(tweet.content)
        """
        # Build query with date filters
        full_query = query
        if since:
            full_query += f" since:{since}"
        if until:
            full_query += f" until:{until}"
            
        logger.info(f"Starting tweet collection with query: {full_query}")
        
        scraper = sntwitter.TwitterSearchScraper(full_query)
        count = 0
        
        try:
            for tweet_obj in scraper.get_items():
                self._rate_limit_sleep()
                
                try:
                    tweet = self._parse_tweet(tweet_obj)
                    yield tweet
                    
                    count += 1
                    if count % 100 == 0:
                        logger.info(f"Collected {count} tweets")
                    
                    if limit and count >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error parsing tweet: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error during tweet collection: {e}")
            raise
            
        logger.info(f"Collection completed. Total tweets: {count}")
    
    def get_user_tweets(
        self,
        username: str,
        limit: Optional[int] = None
    ) -> Generator[Tweet, None, None]:
        """
        Get tweets from a specific user.
        
        Args:
            username: Twitter username (without @)
            limit: Maximum number of tweets to collect
            
        Yields:
            Tweet objects
        """
        logger.info(f"Collecting tweets from user: @{username}")
        
        scraper = sntwitter.TwitterUserScraper(username)
        count = 0
        
        try:
            for tweet_obj in scraper.get_items():
                self._rate_limit_sleep()
                
                try:
                    tweet = self._parse_tweet(tweet_obj)
                    yield tweet
                    
                    count += 1
                    if limit and count >= limit:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error parsing tweet: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error collecting user tweets: {e}")
            raise
            
        logger.info(f"Collected {count} tweets from @{username}")
    
    def get_hashtag_tweets(
        self,
        hashtag: str,
        limit: Optional[int] = None
    ) -> Generator[Tweet, None, None]:
        """
        Get tweets for a specific hashtag.
        
        Args:
            hashtag: Hashtag to search (without #)
            limit: Maximum number of tweets to collect
            
        Yields:
            Tweet objects
        """
        query = f"#{hashtag}"
        yield from self.search(query, limit=limit)
