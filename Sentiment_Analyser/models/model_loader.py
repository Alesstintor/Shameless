"""
Model loading utilities for Kaggle-trained models.

Handles loading models trained in Kaggle for local inference.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline
)

logger = logging.getLogger(__name__)


class KaggleModelLoader:
    """
    Load sentiment models trained in Kaggle.
    
    Supports loading models from local cache for inference.
    """
    
    def __init__(self, models_dir: str = "Sentiment_Analyser/data/models"):
        """
        Initialize model loader.
        
        Args:
            models_dir: Directory where models are stored
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Model loader initialized: {self.models_dir}")
        
    def load_model(
        self,
        version: str = "v1.0",
        device: str = "cpu"
    ) -> Tuple[any, Dict]:
        """
        Load a trained model from local storage.
        
        Args:
            version: Model version to load (e.g., "v1.0")
            device: Device to load model on ("cpu" or "cuda")
            
        Returns:
            Tuple of (pipeline, config)
            
        Raises:
            FileNotFoundError: If model not found
            
        Example:
            >>> loader = KaggleModelLoader()
            >>> pipeline, config = loader.load_model("v1.0")
            >>> result = pipeline("I love this!")
        """
        model_path = self.models_dir / version / "model"
        tokenizer_path = self.models_dir / version / "tokenizer"
        config_path = self.models_dir / version / "config.json"
        
        # Check if model exists
        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                f"Please download from Kaggle or train the model first."
            )
        
        logger.info(f"Loading model from {model_path}")
        
        # Load configuration
        config = {}
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
            logger.info(f"Model config loaded: {config.get('model_name', 'unknown')}")
        
        # Load model and tokenizer
        model = AutoModelForSequenceClassification.from_pretrained(model_path)
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        
        # Create pipeline
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model=model,
            tokenizer=tokenizer,
            device=0 if device == "cuda" else -1
        )
        
        logger.info(f"Model loaded successfully on {device}")
        
        return sentiment_pipeline, config
    
    def list_available_models(self) -> list:
        """
        List all available model versions.
        
        Returns:
            List of version strings
        """
        if not self.models_dir.exists():
            return []
        
        models = []
        for version_dir in self.models_dir.iterdir():
            if version_dir.is_dir() and (version_dir / "model").exists():
                models.append(version_dir.name)
        
        return sorted(models)
    
    def get_model_info(self, version: str) -> Optional[Dict]:
        """
        Get information about a specific model version.
        
        Args:
            version: Model version
            
        Returns:
            Dictionary with model info or None if not found
        """
        config_path = self.models_dir / version / "config.json"
        metrics_path = self.models_dir / version / "metrics.json"
        
        if not config_path.exists():
            return None
        
        info = {}
        
        # Load config
        with open(config_path, 'r') as f:
            info['config'] = json.load(f)
        
        # Load metrics if available
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                info['metrics'] = json.load(f)
        
        return info


# Convenience function
def load_model(version: str = "v1.0", device: str = "cpu"):
    """
    Quick load a model.
    
    Args:
        version: Model version
        device: Device ("cpu" or "cuda")
        
    Returns:
        Tuple of (pipeline, config)
    """
    loader = KaggleModelLoader()
    return loader.load_model(version, device)
