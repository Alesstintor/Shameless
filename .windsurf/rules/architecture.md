---
trigger: model_decision
---

# Shameless - Sentiment Analysis Architecture

## Project Overview
Shameless es un proyecto de análisis de sentimientos que combina scraping de redes sociales con machine learning para analizar y clasificar el sentimiento de contenido textual.

## Core Components

### 1. Data Collection Layer (`Sentiment_Analyser/scraper/`)
- **SNScrape Integration**: Módulo para recolección de datos de Twitter/X
- **Data Pipeline**: Sistema de procesamiento y limpieza de datos
- **Storage Manager**: Gestión de datos raw y procesados

### 2. Machine Learning Layer (`Sentiment_Analyser/models/`)
- **Preprocessing**: Tokenización, normalización, feature extraction
- **Model Training**: Entrenamiento de modelos de clasificación de sentimientos
- **Model Inference**: Predicción en tiempo real
- **Model Registry**: Versionado y gestión de modelos

### 3. Analysis Layer (`Sentiment_Analyser/notebooks/`)
- **Exploratory Analysis**: Notebooks Jupyter para análisis exploratorio
- **Model Development**: Experimentación y desarrollo de modelos
- **Visualization**: Dashboards y visualizaciones de resultados

### 4. API Layer (`Sentiment_Analyser/api/`)
- **REST API**: Endpoints para acceso a funcionalidad
- **Webhooks**: Integración con servicios externos
- **Authentication**: Sistema de autenticación y autorización

## Data Flow

```
[Twitter/X] 
    ↓ (snscrape)
[Raw Data Collection]
    ↓ (preprocessing)
[Clean Dataset]
    ↓ (feature engineering)
[ML Pipeline]
    ↓ (training/inference)
[Sentiment Predictions]
    ↓ (visualization)
[Reports & Dashboards]
```

## Technology Stack

### Core Technologies
- **Python 3.9+**: Lenguaje principal
- **snscrape**: Scraping de redes sociales
- **scikit-learn**: Machine learning tradicional
- **transformers**: Modelos de lenguaje pre-entrenados (BERT, RoBERTa)
- **pandas/numpy**: Manipulación de datos
- **Jupyter**: Notebooks interactivos

### ML/NLP Stack
- **NLTK/spaCy**: Procesamiento de lenguaje natural
- **TensorFlow/PyTorch**: Deep learning frameworks
- **Hugging Face**: Modelos pre-entrenados
- **MLflow**: Tracking de experimentos

### Data & Storage
- **SQLite/PostgreSQL**: Base de datos
- **Redis**: Caché y colas
- **MinIO/S3**: Almacenamiento de objetos

### Monitoring & Deployment
- **FastAPI**: Framework web
- **Docker**: Containerización
- **Prometheus/Grafana**: Monitoreo
- **DVC**: Versionado de datos

## Module Structure

```
Sentiment_Analyser/
├── config/              # Configuración centralizada
├── scraper/            # Módulos de scraping
│   ├── collectors/     # Diferentes scrapers
│   ├── parsers/        # Parsing de datos
│   └── storage/        # Persistencia
├── data/               # Datasets
│   ├── raw/           # Datos sin procesar
│   ├── processed/     # Datos procesados
│   └── models/        # Modelos guardados
├── models/            # Código ML
│   ├── preprocessing/ # Limpieza y feature engineering
│   ├── training/      # Scripts de entrenamiento
│   ├── inference/     # Predicción
│   └── evaluation/    # Métricas y evaluación
├── notebooks/         # Jupyter notebooks
│   ├── exploratory/   # Análisis exploratorio
│   ├── experiments/   # Experimentos ML
│   └── reports/       # Reportes finales
├── api/               # API REST
│   ├── routes/        # Endpoints
│   ├── middleware/    # Middleware
│   └── schemas/       # Validación de datos
├── utils/             # Utilidades compartidas
├── tests/             # Tests unitarios e integración
└── scripts/           # Scripts de automatización
```

## Design Patterns

### 1. Repository Pattern
- Abstracción de acceso a datos
- Facilita testing con mocks
- Separación de lógica de negocio y persistencia

### 2. Factory Pattern
- Creación dinámica de scrapers
- Instanciación de modelos ML
- Configuración de pipelines

### 3. Pipeline Pattern
- Procesamiento de datos en etapas
- Transformaciones encadenadas
- Flujo claro de datos

### 4. Strategy Pattern
- Múltiples algoritmos de clasificación
- Intercambiabilidad de modelos
- A/B testing de estrategias

## Best Practices

### Code Quality
- **Type Hints**: Uso obligatorio de typing
- **Docstrings**: Google style docstrings
- **Linting**: Black, flake8, mypy
- **Testing**: pytest con cobertura >80%

### ML Best Practices
- **Reproducibilidad**: Seeds fijos, versionado de datos
- **Validation**: Cross-validation, train/test split
- **Metrics**: Múltiples métricas (accuracy, F1, precision, recall)
- **Explainability**: SHAP values, feature importance

### Data Management
- **Versionado**: DVC para datasets y modelos
- **Backups**: Automáticos y regulares
- **Privacy**: Anonimización de datos sensibles
- **Compliance**: GDPR compliance

## Security Considerations

- **API Keys**: Nunca en código, usar .env
- **Rate Limiting**: Protección contra abuse
- **Input Validation**: Sanitización de entradas
- **Data Encryption**: En tránsito y en reposo

## Scalability

### Horizontal Scaling
- Stateless API design
- Task queues (Celery/RQ)
- Load balancing

### Vertical Scaling
- Batch processing
- Model optimization
- Caching strategies

## Performance Targets

- **Scraping**: 1000+ tweets/min
- **Inference**: <100ms latency
- **Batch Processing**: 10k+ samples/min
- **API Response**: <200ms p95

## Future Enhancements

1. **Multi-language Support**: Análisis en múltiples idiomas
2. **Real-time Processing**: Stream processing con Kafka
3. **Advanced Models**: Fine-tuning de LLMs
4. **Web Dashboard**: Interface visual interactiva
5. **AutoML**: Optimización automática de hiperparámetros
