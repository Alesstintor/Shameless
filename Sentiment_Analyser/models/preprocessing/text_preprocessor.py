"""
Text preprocessing utilities for sentiment analysis.

Provides cleaning, normalization, and tokenization functionality.
"""

import logging
import re
from typing import List, Optional

logger = logging.getLogger(__name__)


class TextPreprocessor:
    """
    Text preprocessing for sentiment analysis.
    
    Handles cleaning, normalization, and tokenization of text data.
    """
    
    def __init__(
        self,
        lowercase: bool = True,
        remove_urls: bool = True,
        remove_mentions: bool = False,
        remove_hashtags: bool = False,
        remove_emojis: bool = False,
        remove_extra_whitespace: bool = True
    ):
        """
        Initialize text preprocessor.
        
        Args:
            lowercase: Convert text to lowercase
            remove_urls: Remove URLs from text
            remove_mentions: Remove @mentions from text
            remove_hashtags: Remove #hashtags from text
            remove_emojis: Remove emojis from text
            remove_extra_whitespace: Remove extra whitespace
        """
        self.lowercase = lowercase
        self.remove_urls = remove_urls
        self.remove_mentions = remove_mentions
        self.remove_hashtags = remove_hashtags
        self.remove_emojis = remove_emojis
        self.remove_extra_whitespace = remove_extra_whitespace
        
        # Regex patterns
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        self.mention_pattern = re.compile(r'@[\w]+')
        self.hashtag_pattern = re.compile(r'#[\w]+')
        self.emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+",
            flags=re.UNICODE
        )
        
    def clean(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
            
        # Remove URLs
        if self.remove_urls:
            text = self.url_pattern.sub('', text)
            
        # Remove mentions
        if self.remove_mentions:
            text = self.mention_pattern.sub('', text)
            
        # Remove hashtags
        if self.remove_hashtags:
            text = self.hashtag_pattern.sub('', text)
            
        # Remove emojis
        if self.remove_emojis:
            text = self.emoji_pattern.sub('', text)
            
        # Convert to lowercase
        if self.lowercase:
            text = text.lower()
            
        # Remove extra whitespace
        if self.remove_extra_whitespace:
            text = ' '.join(text.split())
            
        return text.strip()
    
    def clean_batch(self, texts: List[str]) -> List[str]:
        """
        Clean a batch of texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of cleaned texts
        """
        return [self.clean(text) for text in texts]
    
    def extract_hashtags(self, text: str) -> List[str]:
        """
        Extract hashtags from text.
        
        Args:
            text: Input text
            
        Returns:
            List of hashtags (without #)
        """
        hashtags = self.hashtag_pattern.findall(text)
        return [tag[1:] for tag in hashtags]  # Remove # symbol
    
    def extract_mentions(self, text: str) -> List[str]:
        """
        Extract mentions from text.
        
        Args:
            text: Input text
            
        Returns:
            List of mentions (without @)
        """
        mentions = self.mention_pattern.findall(text)
        return [mention[1:] for mention in mentions]  # Remove @ symbol
    
    def extract_urls(self, text: str) -> List[str]:
        """
        Extract URLs from text.
        
        Args:
            text: Input text
            
        Returns:
            List of URLs
        """
        return self.url_pattern.findall(text)
