"""
Social media scraping module using snscrape.

Provides collectors for different platforms and data storage utilities.
"""

from .collectors import TwitterCollector
from .storage import DataStorage

__all__ = ["TwitterCollector", "DataStorage"]
