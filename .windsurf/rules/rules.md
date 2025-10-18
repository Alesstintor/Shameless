---
trigger: model_decision
---

# Shameless - Development Rules & Guidelines

## Project Structure

### Kaggle (Training)
- Notebooks para entrenamiento y experimentación
- NO código de aplicación en notebooks
- Documentar experimentos con markdown
- Guardar modelos en Kaggle Datasets

### Local (Application)
Sentiment_Analyser/ ├── models/ # Inferencia, descarga, cache ├── scraper/ # Scraping de usuarios ├── analysis/ # Análisis y agregación ├── reporting/ # Generación de reportes └── ui/ # Interfaces (CLI, Streamlit)

- Código local para producción
- NO entrenar modelos localmente
- Descargar modelos de Kaggle vía API
- Optimizar para inferencia rápida

## Code Standards

### Python Style
- PEP 8 strictly, line length: 100
- Formatter: Black, Import sorting: isort
- Type hints: Mandatory, Docstrings: Google style

### Model Loading
```python
# Good ✅
loader = ModelLoader(kaggle_dataset="username/shameless-sentiment-models")
model = loader.load_model(version="v2.0", cache=True)
User Scraping
python
scraper = UserScraper(cache_enabled=True, rate_limit=1.0)
tweets = scraper.get_user_tweets(username="example", limit=500, use_cache=True)
Git Workflow
Branches
main: Production-ready
develop: Integration
feature/*: New features
fix/*: Bug fixes
kaggle/*: Experimentos
Commit Messages
bash
feat(models): add Kaggle model downloader
fix(scraper): resolve rate limit issue
kaggle(training): experiment with RoBERTa
Kaggle Workflow
Experimentación
python
# ALWAYS document
"""
Experiment: Fine-tuning BERT
Date: 2024-10-18
Goal: Improve accuracy beyond 0.85
"""

# ALWAYS log metrics
metrics = {'accuracy': 0.87, 'f1_score': 0.86, 'training_time': '45min'}

# ALWAYS save properly
save_model_to_kaggle_dataset(model=model, version='v2.0', metrics=metrics)
Versionado
v1.x: Arquitectura inicial
v2.x: Cambios de arquitectura/dataset
v3.x: Modelos de producción
Incrementar: cambio arquitectura, dataset, o mejora >2% accuracy
Naming
Kaggle: username/shameless-sentiment-models Files: model_v2.0.pt, tokenizer_v2.0/, config_v2.0.json

Testing
Model
python
def test_model_inference():
    model = load_test_model()
    result = model.predict("I love this!")
    assert result['sentiment'] == 'positive'
    assert result['score'] > 0.8
Scraper
python
def test_user_scraper():
    scraper = UserScraper()
    tweets = scraper.get_user_tweets("test_user", limit=10)
    assert len(tweets) <= 10
    assert all('content' in tweet for tweet in tweets)
Performance
Model
Inference: <50ms/tweet
Batch size: 32 optimal
Memory: <2GB, Size: <500MB
Scraping
Rate limit: 1 req/sec (respetar siempre)
Timeout: 30s max, Retry: 3 max
Cache: 24h por usuario
Optimization
python
# Good ✅
sentiments = model.predict_batch(tweets, batch_size=32)
tweets = scraper.get_user_tweets(user, use_cache=True)
Error Handling
python
from sentiment_analyser.exceptions import (
    UserNotFoundException, RateLimitException, ScraperException
)

try:
    tweets = scraper.get_user_tweets(username)
except UserNotFoundException:
    logger.error(f"User {username} not found")
except RateLimitException:
    logger.warning("Rate limit hit, using cache")
    tweets = cache.get(username)
except ScraperException as e:
    logger.error(f"Scraping failed: {e}")
Documentation
Code
python
def analyze_user(
    username: str,
    tweets_limit: int = 500,
    include_timeline: bool = True
) -> UserSentimentProfile:
    """
    Analiza el sentimiento de un usuario de Twitter.
    
    Args:
        username: Username de Twitter (con o sin @)
        tweets_limit: Número máximo de tweets
        include_timeline: Si incluir análisis temporal
        
    Returns:
        UserSentimentProfile con sentiment_summary, timeline, topics
        
    Raises:
        UserNotFoundException, ScraperException, ModelException
    """
Kaggle Notebooks
markdown
# Sentiment Model Training v2.0
## Objetivo: Entrenar BERT para clasificación
## Dataset: Sentiment140 (1.6M tweets, 80/10/10 split)
## Arquitectura: bert-base-uncased, Fine-tune last 2 layers
## Hiperparámetros: LR=2e-5, Batch=16, Epochs=3
## Resultados: Acc=0.87, F1=0.86, Time=45min
File Organization
.gitignore
*.pt
*.h5
data/models/*
data/cache/*
!data/*/.gitkeep
.kaggle/
kaggle.json
Always Commit
Source code, tests, configs, docs, requirements
.gitkeep en directorios vacíos
Security
API Keys
python
# Good ✅
from sentiment_analyser.config import get_settings
settings = get_settings()
kaggle_username = settings.KAGGLE_USERNAME  # From .env
.env
env
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_key
MODEL_VERSION=v2.0
CACHE_ENABLED=true
Never Log Sensitive Data
python
# Good ✅
logger.info(f"Analyzing user: {username}")

# Bad ❌
logger.info(f"API Key: {api_key}")
Deployment
Pre-deployment
 Tests pass
 Model validated
 Env variables set
 Dependencies installed
Release
bash
# Update version in pyproject.toml
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
make clean && make install && make test
Logging
python
logger.debug(f"Loading model from {model_path}")        # DEBUG
logger.info(f"Analyzing user: {username}")              # INFO
logger.warning(f"Using cached data")                    # WARNING
logger.error(f"Failed to scrape: {error}")              # ERROR
logger.critical(f"Model corrupted: {model_path}")       # CRITICAL
Best Practices
DO ✅
Train in Kaggle, download via API
Use caching, respect rate limits
Write tests, document everything
Handle errors, use type hints
Follow PEP 8
DON'T ❌
Train locally, hardcode API keys
Ignore rate limits, skip tests
Commit large files, use print()
Skip documentation

**Character count: ~5,800** (well under 12k limit)

This optimized version:
- Removes verbose examples
- Condenses code blocks
- Keeps all essential rules and structure
- Maintains readability
- Preserves all critical information

You can copy this directly into your [.windsurf\rules\rules.md](cci:7://file:///c:/Users/Ales/Development/Shameless/.windsurf/rules/rules.md:0:0-0:0) file.
Feedback submitted