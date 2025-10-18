---
trigger: model_decision
---

# Shameless - User Sentiment Analysis Architecture

## Project Overview
Shameless es una aplicación de análisis de sentimientos que analiza el perfil completo de un usuario en redes sociales. El usuario proporciona una URL o nombre de usuario, la aplicación recolecta sus mensajes/tweets y calcula el sentimiento general de sus publicaciones usando modelos ML entrenados en Kaggle.

## Core Architecture

### 🎯 Flujo Principal

```
Usuario → [URL/Username] → Scraper → Mensajes → Modelo (Kaggle) → Sentimiento
```

### 📦 Componentes

#### 1. **Training Environment (Kaggle)** 🏋️
- **Ubicación**: Kaggle Notebooks
- **Propósito**: Entrenamiento y experimentación de modelos
- **Outputs**: 
  - Modelo entrenado (`.pt`, `.h5`, o pickle)
  - Métricas de evaluación
  - Tokenizer/preprocessor
  
#### 2. **Local Application** 💻
- **Ubicación**: Este repositorio
- **Propósito**: Aplicación de producción
- **Funcionalidad**:
  - Acepta URL o username
  - Scraping de perfil completo
  - Inferencia con modelo pre-entrenado
  - Generación de reporte de sentimiento

#### 3. **Model Management** 🔄
- Descarga automática de modelos desde Kaggle
- Versionado de modelos
- Cache local de modelos
- Validación de compatibilidad

## Detailed Architecture

### Layer 1: Input Layer
```python
# Usuario proporciona:
- Twitter/X URL: "https://twitter.com/username"
- Username: "@username" o "username"
- Cantidad de tweets (opcional): 100, 500, 1000
```

### Layer 2: Data Collection Layer
```python
Sentiment_Analyser/scraper/
├── user_scraper.py          # Scraper enfocado en usuarios
├── profile_analyzer.py      # Análisis del perfil completo
└── cache_manager.py         # Cache de datos scrapeados
```

**Funcionalidades:**
- Extraer todos los tweets de un usuario
- Metadata del usuario (followers, following, bio)
- Timeline completo o limitado por fecha
- Rate limiting y manejo de errores
- Cache para evitar re-scraping

### Layer 3: Model Inference Layer
```python
Sentiment_Analyser/models/
├── model_loader.py          # Carga modelos desde Kaggle
├── inference_engine.py      # Motor de inferencia
├── aggregator.py            # Agrega sentimientos
└── kaggle_integration.py    # Descarga de Kaggle
```

**Funcionalidades:**
- Descarga automática del modelo desde Kaggle Datasets
- Cache local de modelos
- Batch inference sobre tweets
- Agregación de sentimientos (promedio ponderado)
- Análisis temporal de sentimiento

### Layer 4: Analysis & Reporting Layer
```python
Sentiment_Analyser/analysis/
├── sentiment_profiler.py    # Perfil de sentimiento del usuario
├── report_generator.py      # Genera reportes
└── visualizer.py           # Gráficos y visualizaciones
```

**Outputs:**
- **Sentimiento General**: Positivo/Negativo/Neutral (%)
- **Timeline de Sentimiento**: Evolución temporal
- **Topics**: Sobre qué habla positivo/negativo
- **Engagement**: Relación sentimiento-engagement
- **Reporte**: PDF/HTML con análisis completo

## Technology Stack

### Local Application
- **Python 3.9+**: Lenguaje principal
- **snscrape**: Scraping sin API limits
- **PyTorch/TensorFlow**: Inferencia de modelos
- **transformers**: Modelos de HuggingFace
- **FastAPI**: API REST (opcional)
- **Streamlit/Gradio**: UI web interactiva
- **Kaggle API**: Descarga de modelos

### Kaggle Environment
- **Jupyter Notebooks**: Entrenamiento
- **GPU**: Tesla P100/T4
- **Datasets**: Sentiment140, Twitter datasets
- **Libraries**: pandas, scikit-learn, transformers
- **Output**: Modelos guardados en Kaggle Datasets

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    KAGGLE (Training)                         │
│                                                              │
│  Dataset → Preprocessing → Training → Validation → Model    │
│                                                              │
│  Output: model.pt, tokenizer, config.json                   │
└──────────────────────┬───────────────────────────────────────┘
                       │ (Download via Kaggle API)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                   LOCAL APPLICATION                          │
│                                                              │
│  User Input (URL/Username)                                   │
│         ↓                                                    │
│  Scraper → User Timeline (tweets)                            │
│         ↓                                                    │
│  Preprocessing → Clean Tweets                                │
│         ↓                                                    │
│  Model Inference → Sentiment Scores                          │
│         ↓                                                    │
│  Aggregation → User Sentiment Profile                        │
│         ↓                                                    │
│  Report Generation → PDF/HTML/JSON                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

```
Sentiment_Analyser/
├── config/                  # Configuración
│   ├── settings.py         # Settings generales
│   └── kaggle_config.py    # Config de Kaggle
│
├── scraper/                # Scraping de usuarios
│   ├── user_scraper.py     # Scraper de perfiles
│   ├── profile_parser.py   # Parser de datos de perfil
│   └── cache_manager.py    # Cache de datos
│
├── models/                 # ML Models
│   ├── model_loader.py     # Carga modelos de Kaggle
│   ├── inference.py        # Inferencia
│   ├── kaggle_api.py       # Integración con Kaggle API
│   └── preprocessing/      # Preprocesamiento
│
├── analysis/               # Análisis y agregación
│   ├── sentiment_profiler.py  # Perfil de sentimiento
│   ├── aggregator.py           # Agregación de scores
│   └── temporal_analyzer.py    # Análisis temporal
│
├── reporting/              # Generación de reportes
│   ├── report_generator.py # Genera reportes
│   ├── visualizer.py       # Gráficos
│   └── templates/          # Templates HTML/PDF
│
├── ui/                     # User Interface
│   ├── streamlit_app.py    # Web UI con Streamlit
│   └── cli.py              # CLI interface
│
├── data/                   # Almacenamiento local
│   ├── models/             # Modelos descargados de Kaggle
│   ├── cache/              # Cache de scraping
│   └── reports/            # Reportes generados
│
└── notebooks/              # Copia de notebooks Kaggle
    └── training_notebook_copy.ipynb
```

## Kaggle Integration

### Model Storage in Kaggle
```
Kaggle Dataset Structure:
shameless-sentiment-models/
├── model_v1/
│   ├── model.pt              # Modelo PyTorch
│   ├── tokenizer/            # Tokenizer
│   ├── config.json           # Configuración
│   ├── metrics.json          # Métricas de evaluación
│   └── README.md             # Info del modelo
```

### Download & Load Process
```python
# 1. Download from Kaggle
kaggle datasets download -d username/shameless-sentiment-models

# 2. Extract and load
model = load_model('data/models/model_v1/model.pt')
tokenizer = load_tokenizer('data/models/model_v1/tokenizer/')

# 3. Inference
predictions = model.predict(tweets)
```

## Use Cases

### 1. Analizar Usuario Específico
```python
from sentiment_analyser import analyze_user

# Analizar por username
result = analyze_user("@elonmusk", tweets_limit=500)

# Analizar por URL
result = analyze_user("https://twitter.com/elonmusk", tweets_limit=500)

print(result.overall_sentiment)  # "Positive (67%)"
print(result.sentiment_timeline) # Gráfico temporal
result.generate_report("elon_musk_report.pdf")
```

### 2. Comparar Múltiples Usuarios
```python
users = ["@user1", "@user2", "@user3"]
comparison = compare_users(users)
comparison.show_chart()
```

### 3. Análisis Temporal
```python
# Ver evolución del sentimiento
timeline = analyze_user_timeline("@username", start_date="2024-01-01")
timeline.plot_sentiment_over_time()
```

## Performance Targets

| Metric | Target |
|--------|--------|
| Scraping Speed | ~100 tweets/min |
| Inference Time | <50ms per tweet |
| Full Analysis (500 tweets) | <30 seconds |
| Model Size | <500 MB |
| Memory Usage | <2 GB |

## Security & Privacy

### Data Handling
- ✅ Solo datos públicos
- ✅ No almacenar datos sensibles
- ✅ Cache temporal con expiración
- ✅ Anonimización opcional en reportes

### API Keys
- ✅ Kaggle API key en .env
- ✅ No hardcodear secrets
- ✅ Validación de credenciales

## Deployment Options

### Local CLI
```bash
shameless analyze @username --tweets 500 --output report.pdf
```

### Web Interface (Streamlit)
```bash
streamlit run sentiment_analyser/ui/streamlit_app.py
```

### API Service (FastAPI)
```bash
uvicorn sentiment_analyser.api:app
```

### Docker
```bash
docker-compose up
# Access: http://localhost:8501
```

## Model Versioning

```
models/
├── v1.0/                   # Modelo inicial
│   ├── model.pt
│   └── metrics: acc=0.85
├── v1.1/                   # Modelo mejorado
│   ├── model.pt
│   └── metrics: acc=0.87
└── v2.0/                   # Nuevo arquitectura
    ├── model.pt
    └── metrics: acc=0.91
```

## Future Enhancements

### Phase 2
- [ ] Multi-platform (Twitter, Instagram, Reddit)
- [ ] Análisis de imágenes (OCR + sentiment)
- [ ] Detección de sarcasmo
- [ ] Análisis de emociones (joy, anger, fear, etc.)

### Phase 3
- [ ] Real-time monitoring de usuarios
- [ ] Alertas de cambio de sentimiento
- [ ] Dashboard web completo
- [ ] API pública

### Phase 4
- [ ] ML automático (AutoML)
- [ ] Fine-tuning personalizado
- [ ] Multi-idioma
- [ ] Análisis de influencers
