"""
User database management for sentiment analysis results.

Stores and retrieves user analysis data in JSON format.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class UserDatabase:
    """Manages storage and retrieval of user sentiment analysis results."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the user database.
        
        Args:
            db_path: Path to the database directory. Defaults to 'db/' in project root.
        """
        if db_path is None:
            db_path = Path("db")
        
        self.db_path = Path(db_path)
        self.db_file = self.db_path / "users.json"
        
        # Ensure directory exists
        self.db_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"UserDatabase initialized at {self.db_file}")
    
    def read_all(self) -> List[Dict]:
        """
        Read all users from the database.
        
        Returns:
            List of user analysis dictionaries, ordered by most recent first.
        """
        try:
            if not self.db_file.exists():
                logger.debug("Database file does not exist, returning empty list")
                return []
            
            with self.db_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Ensure it's a list
                if isinstance(data, list):
                    return data
                
                # Legacy format: dict with handles as keys
                if isinstance(data, dict):
                    logger.warning("Converting legacy dict format to list")
                    return list(data.values())
                
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse database JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Failed to read users database: {e}")
            return []
    
    def write_all(self, users: List[Dict]):
        """
        Write complete users list to the database.
        
        Args:
            users: List of user analysis dictionaries to write.
        """
        try:
            self.db_path.mkdir(parents=True, exist_ok=True)
            with self.db_file.open("w", encoding="utf-8") as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            logger.debug(f"Wrote {len(users)} users to database")
        except Exception as e:
            logger.error(f"Failed to write users database: {e}")
            raise
    
    def save_analysis(self, analysis: Dict, max_users: int = 10):
        """
        Save a user analysis to the database.
        
        Automatically manages the database by:
        - Removing duplicate entries for the same handle
        - Adding timestamp if not present
        - Keeping only the most recent N users
        
        Args:
            analysis: User analysis dictionary to save.
            max_users: Maximum number of users to keep (default: 10).
        """
        try:
            users = self.read_all()
            
            # Get handle for deduplication
            handle = analysis.get('user_handle', '')
            if not handle:
                logger.warning("Analysis missing user_handle, cannot save")
                return
            
            # Remove existing entry for this handle
            users = [u for u in users if u.get('user_handle') != handle]
            
            # Add timestamp if not present
            if 'analyzed_at' not in analysis:
                analysis['analyzed_at'] = datetime.now().isoformat()
            
            # Add to front (most recent first)
            users.insert(0, analysis)
            
            # Keep only last N users
            users = users[:max_users]
            
            self.write_all(users)
            logger.info(f"Saved analysis for '{handle}' to database ({len(users)} total users)")
        except Exception as e:
            logger.error(f"Failed to save user analysis: {e}")
            raise
    
    def get_by_handle(self, handle: str) -> Optional[Dict]:
        """
        Get analysis for a specific user handle.
        
        Args:
            handle: User handle to search for.
            
        Returns:
            User analysis dictionary if found, None otherwise.
        """
        users = self.read_all()
        for user in users:
            if user.get('user_handle') == handle:
                return user
        return None
    
    def delete_by_handle(self, handle: str) -> bool:
        """
        Delete analysis for a specific user handle.
        
        Args:
            handle: User handle to delete.
            
        Returns:
            True if deleted, False if not found.
        """
        users = self.read_all()
        initial_count = len(users)
        users = [u for u in users if u.get('user_handle') != handle]
        
        if len(users) < initial_count:
            self.write_all(users)
            logger.info(f"Deleted analysis for '{handle}'")
            return True
        
        return False
    
    def clear_all(self):
        """Clear all entries from the database."""
        self.write_all([])
        logger.info("Cleared all entries from database")
    
    def get_count(self) -> int:
        """Get the number of stored analyses."""
        return len(self.read_all())
