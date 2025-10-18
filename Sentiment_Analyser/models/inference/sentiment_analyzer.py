"""
Sentiment analysis inference module.

Provides easy-to-use interface for sentiment prediction using pretrained models.
Supports both HuggingFace models and Kaggle-trained models.
"""

import logging
from typing import Dict, List, Union, Optional

from transformers import pipeline

from ..preprocessing import TextPreprocessor
from ..model_loader import KaggleModelLoader

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Sentiment analyzer using transformer models.
    
    Provides sentiment analysis with preprocessing and batch processing support.
    """
    
    def __init__(
        self,
        model_name: Optional[str] = "distilbert-base-uncased-finetuned-sst-2-english",
        device: str = "cpu",
        preprocess: bool = True,
        use_kaggle_model: bool = False,
        kaggle_model_version: str = "v1.0"
    ):
        """
        Initialize sentiment analyzer.
        
        Args:
            model_name: HuggingFace model name (ignored if use_kaggle_model=True)
            device: Device to run model on ("cpu" or "cuda")
            preprocess: Whether to preprocess text before analysis
            use_kaggle_model: If True, load model trained in Kaggle
            kaggle_model_version: Version of Kaggle model to load
            
        Example:
            # Use HuggingFace model
            >>> analyzer = SentimentAnalyzer()
            
            # Use Kaggle-trained model
            >>> analyzer = SentimentAnalyzer(use_kaggle_model=True, kaggle_model_version="v1.0")
        """
        self.device = device
        self.preprocess_enabled = preprocess
        self.use_kaggle_model = use_kaggle_model
        self.label_mapping = {}
        
        # Load model
        if use_kaggle_model:
            logger.info(f"Loading Kaggle model version: {kaggle_model_version}")
            loader = KaggleModelLoader()
            self.pipeline, config = loader.load_model(kaggle_model_version, device)
            self.model_name = config.get("model_name", kaggle_model_version)
            self.label_mapping = config.get("label_mapping", {})
            logger.info(f"Kaggle model loaded: {self.model_name}")
        else:
            self.model_name = model_name
            logger.info(f"Loading HuggingFace model: {model_name}")
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                device=0 if device == "cuda" else -1
            )
            logger.info("HuggingFace model loaded successfully")
        
        # Initialize preprocessor
        if preprocess:
            self.preprocessor = TextPreprocessor(
                lowercase=True,
                remove_urls=True,
                remove_mentions=False,
                remove_hashtags=False,
                remove_emojis=False
            )
    
    def analyze(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Analyze sentiment of a single text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with sentiment label and score
            
        Example:
            >>> analyzer = SentimentAnalyzer()
            >>> result = analyzer.analyze("I love this!")
            >>> print(result)
            {'label': 'POSITIVE', 'score': 0.9998}
        """
        if not text or not text.strip():
            return {
                'label': 'NEUTRAL',
                'score': 0.0,
                'error': 'Empty text'
            }
        
        # Preprocess if enabled
        if self.preprocess_enabled:
            text = self.preprocessor.clean(text)
        
        try:
            result = self.pipeline(text)[0]
            
            # Map label if using Kaggle model
            sentiment = self._map_label(result['label'])
            
            return {
                'label': result['label'],
                'score': round(result['score'], 4),
                'sentiment': sentiment
            }
        except Exception as e:
            logger.error(f"Error analyzing text: {e}")
            return {
                'label': 'ERROR',
                'score': 0.0,
                'error': str(e)
            }
    
    def analyze_batch(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Analyze sentiment of multiple texts in batch.
        
        Args:
            texts: List of input texts
            batch_size: Batch size for processing
            
        Returns:
            List of dictionaries with sentiment results
        """
        if not texts:
            return []
        
        # Preprocess if enabled
        if self.preprocess_enabled:
            texts = self.preprocessor.clean_batch(texts)
        
        try:
            results = self.pipeline(texts, batch_size=batch_size)
            
            return [
                {
                    'label': result['label'],
                    'score': round(result['score'], 4),
                    'sentiment': self._map_label(result['label'])
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return [
                {'label': 'ERROR', 'score': 0.0, 'error': str(e)}
                for _ in texts
            ]
    
    def _map_label(self, label: str) -> str:
        """
        Map model label to sentiment using configured mapping or normalization.
        
        Args:
            label: Model-specific label
            
        Returns:
            Mapped/normalized label
        """
        # If Kaggle model with mapping, use it
        if self.use_kaggle_model and self.label_mapping:
            # Handle both string and integer keys
            label_key = label.replace('LABEL_', '')
            return self.label_mapping.get(label_key, self._normalize_label(label))
        
        # Otherwise normalize
        return self._normalize_label(label)
    
    def _normalize_label(self, label: str) -> str:
        """
        Normalize label to standard format (positive/negative/neutral).
        
        Args:
            label: Model-specific label
            
        Returns:
            Normalized label
        """
        label_lower = label.lower()
        
        if 'pos' in label_lower or label_lower in ['1', '4', '5', 'label_1']:
            return 'positive'
        elif 'neg' in label_lower or label_lower in ['0', 'label_0']:
            return 'negative'
        else:
            return 'neutral'
    
    def get_detailed_scores(self, text: str) -> Dict[str, float]:
        """
        Get detailed sentiment scores (if model supports it).
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with scores for each sentiment class
        """
        # This is a simplified version - extend for multi-class models
        result = self.analyze(text)
        
        if result['label'] == 'ERROR':
            return {'error': 1.0}
        
        sentiment = result['sentiment']
        score = result['score']
        
        # For binary classification, calculate complement
        scores = {
            sentiment: score,
            'positive' if sentiment == 'negative' else 'negative': 1 - score
        }
        
        return scores
