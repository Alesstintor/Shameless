---
trigger: model_decision
---

# Shameless - Project Context

## Project Mission
Desarrollar una plataforma robusta de análisis de sentimientos que combine web scraping de redes sociales con técnicas avanzadas de Machine Learning para extraer insights valiosos de datos públicos.

## Target Use Cases

### 1. Brand Monitoring
- Análisis de menciones de marca en tiempo real
- Detección temprana de crisis de reputación
- Tracking de campañas de marketing

### 2. Social Listening
- Tendencias emergentes en redes sociales
- Opinión pública sobre temas específicos
- Análisis de competencia

### 3. Market Research
- Sentimiento del consumidor sobre productos
- Identificación de pain points
- Feedback de características

### 4. Political Analysis
- Análisis de opinión pública
- Detección de polarización
- Tracking de narrativas

## Technical Context

### Why snscrape?
- **No API limits**: A diferencia de la API oficial de Twitter
- **Historical data**: Acceso a tweets antiguos
- **Free**: Sin costes de API
- **Flexible**: Múltiples plataformas soportadas

### ML Model Strategy
1. **Baseline**: Modelos tradicionales (Logistic Regression, SVM)
2. **Advanced**: Transfer learning con BERT/RoBERTa
3. **Production**: Modelo híbrido optimizado para latencia

### Data Pipeline
- **Volume**: ~10K-100K tweets/día
- **Velocity**: Near real-time (batch cada 5 min)
- **Variety**: Text, metadata, user info
- **Veracity**: Filtrado de spam y bots

## Project Phases

### Phase 1: MVP (Current)
- ✅ Project structure
- 🔄 Basic scraper implementation
- 🔄 Simple sentiment model (VADER baseline)
- 🔄 Jupyter notebook for exploration
- ⏳ Basic CLI interface

### Phase 2: Core Features
- Advanced ML models (fine-tuned BERT)
- Data persistence (SQLite → PostgreSQL)
- REST API with FastAPI
- Docker containerization
- Unit and integration tests

### Phase 3: Scale & Polish
- Real-time processing pipeline
- Web dashboard (React/Vue)
- Model monitoring and retraining
- Multi-language support
- Cloud deployment (AWS/GCP)

### Phase 4: Advanced Features
- Entity recognition and extraction
- Topic modeling
- Trend prediction
- Automated reporting
- Multi-platform support (Reddit, News)

## Key Technologies Explained

### snscrape
```python
# Example usage
import snscrape.modules.twitter as sntwitter

query = "bitcoin since:2024-01-01"
for tweet in sntwitter.TwitterSearchScraper(query).get_items():
    print(tweet.content)
```

### Transformers for Sentiment
```python
from transformers import pipeline

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)
result = sentiment_analyzer("I love this product!")
```

### FastAPI Structure
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/analyze")
async def analyze_text(text: str):
    sentiment = model.predict(text)
    return {"sentiment": sentiment}
```

## Data Schema

### Raw Tweet Data
```json
{
  "id": "1234567890",
  "content": "Tweet text here",
  "user": "username",
  "date": "2024-01-01T12:00:00Z",
  "likes": 42,
  "retweets": 10,
  "replies": 5,
  "hashtags": ["tag1", "tag2"],
  "mentions": ["@user1"]
}
```

### Processed Data
```json
{
  "tweet_id": "1234567890",
  "clean_text": "tweet text here",
  "sentiment": "positive",
  "confidence": 0.95,
  "scores": {
    "positive": 0.95,
    "neutral": 0.04,
    "negative": 0.01
  },
  "entities": ["Bitcoin", "Tesla"],
  "language": "en",
  "processed_at": "2024-01-01T12:00:00Z"
}
```

## Model Performance Targets

### Classification Metrics
- **Accuracy**: >85%
- **F1 Score**: >0.83
- **Precision**: >0.85 (minimize false positives)
- **Recall**: >0.80 (catch most sentiments)

### Operational Metrics
- **Inference Time**: <100ms per sample
- **Throughput**: >100 samples/second
- **Uptime**: 99.5%
- **Error Rate**: <1%

## Common Workflows

### 1. Data Collection Workflow
```bash
# Collect tweets
python -m sentiment_analyser.scraper collect --query "python" --limit 1000

# Process raw data
python -m sentiment_analyser.scraper process --input data/raw/tweets.json

# Store in database
python -m sentiment_analyser.scraper store --input data/processed/tweets.json
```

### 2. Model Training Workflow
```bash
# Prepare dataset
python scripts/prepare_dataset.py --source data/processed/ --output data/ml/

# Train model
python -m sentiment_analyser.models.training.train --config config/model_config.yaml

# Evaluate model
python -m sentiment_analyser.models.evaluation.evaluate --model data/models/sentiment_v1/

# Deploy model
python scripts/deploy_model.py --model sentiment_v1 --environment production
```

### 3. Analysis Workflow
```bash
# Launch Jupyter
jupyter lab

# Open notebook: notebooks/exploratory/sentiment_analysis.ipynb
# Run analysis
# Export insights to reports/
```

## Configuration Management

### Config File Structure
```yaml
# config/config.yaml
scraper:
  platform: twitter
  rate_limit: 1  # requests/second
  max_results: 1000
  
model:
  name: "bert-base-uncased"
  max_length: 512
  batch_size: 32
  
database:
  type: postgresql
  host: localhost
  port: 5432
  
api:
  host: 0.0.0.0
  port: 8000
  workers: 4
```

## Error Handling Strategy

### Scraper Errors
- **Rate Limit**: Exponential backoff, max 5 retries
- **Network Error**: Retry with jitter
- **Invalid Data**: Log and skip, continue processing
- **Authentication**: Alert and halt

### ML Errors
- **Model Load Failure**: Fall back to baseline model
- **Prediction Error**: Return neutral sentiment with flag
- **Invalid Input**: Sanitize and retry, or reject
- **OOM**: Reduce batch size dynamically

## Monitoring & Observability

### Key Metrics to Track
- Scraping rate (tweets/min)
- Processing latency (p50, p95, p99)
- Model accuracy drift
- API response times
- Error rates by type
- Resource utilization (CPU, Memory, Disk)

### Alerting Rules
- Error rate >5% → Warning
- Error rate >10% → Critical
- API latency p95 >500ms → Warning
- Model accuracy <80% → Critical
- Disk usage >90% → Warning

## Development Tips

### Quick Start Commands
```bash
# Setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest tests/ -v --cov

# Format code
black . && isort .

# Start API
uvicorn sentiment_analyser.api.main:app --reload

# Run scraper
python -m sentiment_analyser.scraper --help
```

### Debugging
- Use `logging` extensively, not `print()`
- Enable debug mode: `LOG_LEVEL=DEBUG`
- Use `pdb` or `ipdb` for breakpoints
- Check logs in `logs/` directory

### Common Issues
1. **snscrape not working**: Platform may have changed HTML structure, check for updates
2. **Model too slow**: Use smaller model or quantization
3. **Memory issues**: Reduce batch size or use streaming
4. **Database locked**: Check for zombie connections

## Resources & References

### Documentation
- [snscrape GitHub](https://github.com/JustAnotherArchivist/snscrape)
- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [scikit-learn Documentation](https://scikit-learn.org/)

### Datasets for Training
- [Sentiment140](http://help.sentiment140.com/for-students)
- [IMDB Reviews](https://ai.stanford.edu/~amaas/data/sentiment/)
- [Twitter Sentiment](https://www.kaggle.com/datasets/kazanova/sentiment140)

### Pretrained Models
- [nlptown/bert-base-multilingual-uncased-sentiment](https://huggingface.co/nlptown/bert-base-multilingual-uncased-sentiment)
- [cardiffnlp/twitter-roberta-base-sentiment](https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment)
- [distilbert-base-uncased-finetuned-sst-2-english](https://huggingface.co/distilbert-base-uncased-finetuned-sst-2-english)

## Contributing Guidelines

### For Hacktoberfest Contributors
1. Check existing issues or create new one
2. Fork the repository
3. Create feature branch
4. Make changes following our standards
5. Add tests
6. Submit PR with clear description

### Good First Issues
- Add new data sources (Reddit, News)
- Improve preprocessing pipeline
- Add visualization functions
- Write documentation
- Add unit tests
- Performance optimizations

## Project Roadmap

### Q4 2024
- [x] Project initialization
- [ ] Core scraper implementation
- [ ] Baseline ML model
- [ ] Basic API

### Q1 2025
- [ ] Advanced models (BERT fine-tuning)
- [ ] Database integration
- [ ] Docker deployment
- [ ] CI/CD pipeline

### Q2 2025
- [ ] Real-time processing
- [ ] Web dashboard
- [ ] Multi-language support
- [ ] Cloud deployment

### Future
- [ ] Multi-platform support
- [ ] Advanced analytics
- [ ] AutoML integration
- [ ] Enterprise features
