"""
Example: Using Kaggle-trained models in local application.

This demonstrates how to use models trained in Kaggle with the Shameless application.
"""

from sentiment_analyser.models import SentimentAnalyzer, KaggleModelLoader


def example_basic_usage():
    """Basic usage with Kaggle model."""
    print("="*80)
    print("Example 1: Basic Usage with Kaggle Model")
    print("="*80)
    
    # Initialize with Kaggle model
    analyzer = SentimentAnalyzer(
        use_kaggle_model=True,
        kaggle_model_version="v1.0"
    )
    
    # Analyze single text
    text = "I absolutely love this product!"
    result = analyzer.analyze(text)
    
    print(f"\nText: {text}")
    print(f"Sentiment: {result['sentiment']}")
    print(f"Confidence: {result['score']:.4f}")


def example_batch_processing():
    """Process multiple texts (data-agnostic)."""
    print("\n" + "="*80)
    print("Example 2: Batch Processing (1..n texts)")
    print("="*80)
    
    analyzer = SentimentAnalyzer(use_kaggle_model=True)
    
    # Works with ANY text source - tweets, reviews, comments, etc.
    texts = [
        "Great service and fast delivery!",
        "Terrible experience, very disappointed",
        "It's okay, nothing special",
        "Absolutely fantastic, highly recommend!",
        "Worst product ever, waste of money",
        "Pretty good, worth the price"
    ]
    
    results = analyzer.analyze_batch(texts, batch_size=8)
    
    print(f"\nAnalyzed {len(texts)} texts:")
    for text, result in zip(texts, results):
        print(f"\n{text[:50]}...")
        print(f"  → {result['sentiment']} (confidence: {result['score']:.2%})")


def example_multi_source():
    """Demonstrate data-agnostic nature - works with any source."""
    print("\n" + "="*80)
    print("Example 3: Multi-Source Analysis (Data-Agnostic)")
    print("="*80)
    
    analyzer = SentimentAnalyzer(use_kaggle_model=True)
    
    # Different text sources - all work the same!
    sources = {
        "Tweet": "@user Just got the new product and loving it! #awesome",
        "Review": "Excellent quality. Exceeded my expectations. Will buy again.",
        "Comment": "Not happy with customer service response time.",
        "Feedback": "Amazing experience from start to finish!",
        "Post": "Disappointed with the packaging quality"
    }
    
    print("\nAnalyzing texts from different sources:")
    for source_type, text in sources.items():
        result = analyzer.analyze(text)
        print(f"\n[{source_type}]")
        print(f"Text: {text[:60]}...")
        print(f"Result: {result['sentiment']} ({result['score']:.2%})")


def example_model_info():
    """Get information about available models."""
    print("\n" + "="*80)
    print("Example 4: Model Information")
    print("="*80)
    
    loader = KaggleModelLoader()
    
    # List available models
    models = loader.list_available_models()
    print(f"\nAvailable models: {models}")
    
    # Get detailed info about a model
    if models:
        version = models[0]
        info = loader.get_model_info(version)
        
        if info:
            print(f"\nModel {version} details:")
            print(f"  Base model: {info['config'].get('model_name', 'N/A')}")
            print(f"  Training date: {info['config'].get('training_date', 'N/A')}")
            print(f"  Epochs: {info['config'].get('epochs', 'N/A')}")
            
            if 'metrics' in info:
                print(f"\nPerformance:")
                print(f"  Accuracy: {info['metrics'].get('test_accuracy', 0):.4f}")
                print(f"  F1 Score: {info['metrics'].get('test_f1', 0):.4f}")


def example_comparison():
    """Compare HuggingFace model vs Kaggle model."""
    print("\n" + "="*80)
    print("Example 5: Model Comparison")
    print("="*80)
    
    text = "This is an amazing product, highly recommended!"
    
    # HuggingFace model
    hf_analyzer = SentimentAnalyzer(use_kaggle_model=False)
    hf_result = hf_analyzer.analyze(text)
    
    # Kaggle model (if available)
    try:
        kaggle_analyzer = SentimentAnalyzer(use_kaggle_model=True)
        kaggle_result = kaggle_analyzer.analyze(text)
        
        print(f"\nText: {text}\n")
        print("HuggingFace Model:")
        print(f"  Sentiment: {hf_result['sentiment']}")
        print(f"  Confidence: {hf_result['score']:.4f}")
        print("\nKaggle Model:")
        print(f"  Sentiment: {kaggle_result['sentiment']}")
        print(f"  Confidence: {kaggle_result['score']:.4f}")
        
    except FileNotFoundError:
        print("\nKaggle model not found. Download it first:")
        print("  kaggle datasets download user/shameless-sentiment-models")


if __name__ == "__main__":
    print("\n🎭 Shameless - Kaggle Model Usage Examples\n")
    
    try:
        example_basic_usage()
        example_batch_processing()
        example_multi_source()
        example_model_info()
        example_comparison()
        
        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("="*80)
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nTo use Kaggle models:")
        print("1. Train model in Kaggle (use sentiment_analysis.ipynb)")
        print("2. Create Kaggle Dataset with trained model")
        print("3. Download to data/models/v1.0/")
        print("\nSee KAGGLE_WORKFLOW.md for detailed instructions.")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
