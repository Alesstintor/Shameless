'''
Shared data schemas for scraper outputs.
'''
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Tweet:
    """Generic data class for a social media post (e.g., Tweet or Skeet).
    Kept consistent for downstream compatibility.
    """

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
        """Convert post to dictionary."""
        data = asdict(self)
        data['date'] = self.date.isoformat()
        return data
