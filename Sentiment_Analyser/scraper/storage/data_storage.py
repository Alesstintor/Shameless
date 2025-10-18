"""
Data storage utilities for scraped content.

Provides functionality to save and load data in various formats.
"""

import json
import logging
from pathlib import Path
from typing import Any, List

import pandas as pd

logger = logging.getLogger(__name__)


class DataStorage:
    """Utility class for storing and loading scraped data."""
    
    def __init__(self, base_path: Path):
        """
        Initialize data storage.
        
        Args:
            base_path: Base directory for data storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        
    def save_json(self, data: List[dict], filename: str) -> Path:
        """
        Save data as JSON file.
        
        Args:
            data: List of dictionaries to save
            filename: Output filename (without path)
            
        Returns:
            Path to saved file
        """
        filepath = self.base_path / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Saved {len(data)} records to {filepath}")
        return filepath
    
    def load_json(self, filename: str) -> List[dict]:
        """
        Load data from JSON file.
        
        Args:
            filename: Input filename (without path)
            
        Returns:
            List of dictionaries
        """
        filepath = self.base_path / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        logger.info(f"Loaded {len(data)} records from {filepath}")
        return data
    
    def save_csv(self, data: List[dict], filename: str) -> Path:
        """
        Save data as CSV file.
        
        Args:
            data: List of dictionaries to save
            filename: Output filename (without path)
            
        Returns:
            Path to saved file
        """
        filepath = self.base_path / filename
        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"Saved {len(data)} records to {filepath}")
        return filepath
    
    def load_csv(self, filename: str) -> pd.DataFrame:
        """
        Load data from CSV file.
        
        Args:
            filename: Input filename (without path)
            
        Returns:
            Pandas DataFrame
        """
        filepath = self.base_path / filename
        df = pd.read_csv(filepath)
        
        logger.info(f"Loaded {len(df)} records from {filepath}")
        return df
    
    def save_parquet(self, data: List[dict], filename: str) -> Path:
        """
        Save data as Parquet file (efficient columnar format).
        
        Args:
            data: List of dictionaries to save
            filename: Output filename (without path)
            
        Returns:
            Path to saved file
        """
        filepath = self.base_path / filename
        df = pd.DataFrame(data)
        df.to_parquet(filepath, index=False, compression='snappy')
        
        logger.info(f"Saved {len(data)} records to {filepath}")
        return filepath
    
    def load_parquet(self, filename: str) -> pd.DataFrame:
        """
        Load data from Parquet file.
        
        Args:
            filename: Input filename (without path)
            
        Returns:
            Pandas DataFrame
        """
        filepath = self.base_path / filename
        df = pd.read_parquet(filepath)
        
        logger.info(f"Loaded {len(df)} records from {filepath}")
        return df
    
    def append_json(self, data: List[dict], filename: str) -> Path:
        """
        Append data to existing JSON file or create new one.
        
        Args:
            data: List of dictionaries to append
            filename: Output filename (without path)
            
        Returns:
            Path to file
        """
        filepath = self.base_path / filename
        
        existing_data = []
        if filepath.exists():
            existing_data = self.load_json(filename)
            
        existing_data.extend(data)
        return self.save_json(existing_data, filename)
