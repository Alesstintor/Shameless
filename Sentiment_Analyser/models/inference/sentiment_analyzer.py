"""
Sentiment analysis inference module.

Provides easy-to-use interface for sentiment prediction using pretrained models.
"""

import logging
from typing import Dict, List, Union

from transformers import pipeline

from ..preprocessing import TextPreprocessor

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Sentiment analyzer using transformer models.
    
    Provides sentiment analysis with preprocessing and batch processing support.
    """
    
    def __init__(
        self,
        model_name: str = "distilbert-base-uncased-finetuned-sst-2-english",
        device: str = "cpu",
        preprocess: bool = True
    ):
        """
        Initialize sentiment analyzer.
        
        Args:
            model_name: HuggingFace model name
            device: Device to run model on ("cpu" or "cuda")
            preprocess: Whether to preprocess text before analysis
        """
        self.model_name = model_name
        self.device = device
        self.preprocess_enabled = preprocess
        
        logger.info(f"Loading model: {model_name}")
        self.pipeline = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=0 if device == "cuda" else -1
        )
        
        if preprocess:
            self.preprocessor = TextPreprocessor(
                lowercase=True,
                remove_urls=True,
                remove_mentions=False,
                remove_hashtags=False,
                remove_emojis=False
            )
        
        logger.info("Model loaded successfully")
    
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
            
            return {
                'label': result['label'],
                'score': round(result['score'], 4),
                'sentiment': self._normalize_label(result['label'])
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
                    'sentiment': self._normalize_label(result['label'])
                }
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error in batch analysis: {e}")
            return [
                {'label': 'ERROR', 'score': 0.0, 'error': str(e)}
                for _ in texts
            ]
    
    def _normalize_label(self, label: str) -> str:
        """
        Normalize label to standard format (positive/negative/neutral).
        
        Args:
            label: Model-specific label
            
        Returns:
            Normalized label
        """
        label_lower = label.lower()
        
        if 'pos' in label_lower or label_lower in ['1', '4', '5']:
            return 'positive'
        elif 'neg' in label_lower or label_lower in ['0', '1']:
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
