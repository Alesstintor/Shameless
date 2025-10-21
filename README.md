# 🎭 Shameless - User Sentiment Profiler

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hacktoberfest 2025](https://img.shields.io/badge/Hacktoberfest-2025-orange.svg)](https://hacktoberfest.com/)
[![Kaggle Model](https://img.shields.io/badge/Kaggle-Model-20BEFF.svg)](https://www.kaggle.com/models/aleselmaquinas/shameless-sentiment-analyzer)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0-009688.svg)](https://fastapi.tiangolo.com/)
[![Bluesky](https://img.shields.io/badge/Bluesky-Supported-1185FE.svg)](https://bsky.app/)

**¿Qué tipo de persona es este usuario en redes sociales?** 🤔

Shameless analiza el perfil completo de un usuario en **Bluesky** (y Twitter/X) y genera un reporte detallado de su sentimiento. Proporciona un handle de usuario y obtén análisis completo con:

- ✨ Sentimiento general (positivo/negativo)
- 📊 Estadísticas detalladas (% positivos, confianza promedio)
- 🌟 Post más positivo y más negativo
- 🤖 Modelo BERT entrenado en Kaggle (87% accuracy)
- ⚡ API REST lista para producción

> 🎉 A project for **Hacktoberfest 2025 A Coruña**  
> 🤖 Pre-trained model available on [Kaggle Models](https://www.kaggle.com/models/aleselmaquinas/shameless-sentiment-analyzer)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Documentation](#-documentation)
- [Contributing](#-contributing)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## ✨ Features

### 🎯 Core Functionality

- **🦋 Bluesky Support**: Analiza usuarios de Bluesky con autenticación nativa
- **User Analysis**: Proporciona handle → Obtén perfil de sentimiento completo
- **Smart Scraping**: Recolecta automáticamente posts (usando atproto SDK oficial)
- **🤖 Pre-trained Model**: Modelo DistilBERT listo para usar desde Kaggle (~270 MB)
- **ML-Powered**: Inferencia rápida con transformers + PyTorch
- **REST API**: FastAPI con documentación interactiva (Swagger UI)

### 📊 Analysis Capabilities

- **Overall Sentiment**: ¿Es el usuario positivo, negativo o neutral?
- **Temporal Analysis**: Evolución del sentimiento a lo largo del tiempo
- **Topic Analysis**: ¿Sobre qué temas es más positivo/negativo?
- **Engagement Correlation**: Relación entre sentimiento y engagement
- **Insights**: Descubre patrones y tendencias automáticamente

### 🤖 Machine Learning

- **🎯 Pre-trained Model Ready**: DistilBERT fine-tuned on 25k samples (87% accuracy)
- **📦 One-Command Download**: Disponible en [Kaggle Models](https://www.kaggle.com/models/aleselmaquinas/shameless-sentiment-analyzer)
- **⚡ Kaggle Training**: GPU-accelerated training with T4/P100 (100% gratuito)
- **📝 Data-Agnostic**: Funciona con tweets, reviews, posts, cualquier texto
- **🔄 Version Management**: Gestión de versiones mediante variable de entorno `MODEL_VERSION`
- **🚀 Fast Inference**: ~100ms por texto en CPU, batch processing optimizado
- **💾 Compact Size**: ~270 MB (DistilBERT base + fine-tuning)

### 🎨 User Experience

- **CLI Interface**: Interfaz de línea de comandos intuitiva
- **Web UI** (Coming soon): Interface web con Streamlit
- **PDF Reports**: Reportes profesionales exportables
- **Interactive Dashboards**: Visualizaciones interactivas
- **Cache System**: Sistema de caché para análisis rápidos

---

## 🏛️ Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Data Collection Layer                                                                                                                        │
│  Bluesky (atproto) → Posts → Storage (JSON)                                                                                                    │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                   Preprocessing Layer                                                                                                                            │
│   Text Cleaning → Normalization → Tokenization                                                                                               │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                 Machine Learning Layer                                                                                                                       │
│  DistilBERT (Kaggle) → Sentiment Classification → Results                                                                             │
│  Model: v1.0 (~270 MB) | Accuracy: 87% | Inference: ~100ms                                                                           │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                                                                                                                         │
│  REST Endpoints → JSON Responses → Interactive Docs                                                                                 │
│  /api/analyze/bluesky/user/{handle}                                                                                                                      │
└──────────────────────────────────────────────────────────────┘
```

**Tech Stack:**

- **Language:** Python 3.11+
- **API Framework:** FastAPI + Uvicorn
- **ML/NLP:** transformers, torch, DistilBERT
- **Social APIs:** atproto (Bluesky), tweepy (Twitter)
- **Data:** pandas, numpy
- **Config:** pydantic-settings, python-dotenv
- **Training:** Kaggle Notebooks (GPU: T4/P100)
- **Model Storage:** Kaggle Models

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip
- Kaggle account (free)

### ⚡ 5-Minute Setup

#### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/Alesstintor/Shameless.git
cd Shameless

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install kaggle  # For downloading the model
```

#### 2. Download the Pre-trained Model

**Option A: Download from Kaggle Web (Recommended for first time)**

1. Go to: https://www.kaggle.com/models/aleselmaquinas/shameless-sentiment-analyzer
2. Click **"Download"** button
3. Extract the downloaded files
4. Copy the extracted `v1.0` folder to: `Sentiment_Analyser/data/models/v1.0`

**Option B: Using Kaggle CLI**

First, configure Kaggle CLI (one-time setup):

1. Go to https://www.kaggle.com/settings/account
2. Click **"Create New Token"** under API section
3. Download `kaggle.json`
4. Place it in:
   - **Windows**: `C:\Users\YOUR_USERNAME\.kaggle\kaggle.json`
   - **Linux/Mac**: `~/.kaggle/kaggle.json` (then run `chmod 600 ~/.kaggle/kaggle.json`)

Then download the model:

```bash
# Navigate to models directory
cd Sentiment_Analyser/data/models

# Download from Kaggle Models
# Visit the model page to find the exact instance version
# https://www.kaggle.com/models/aleselmaquinas/shameless-sentiment-analyzer
# Then use: kaggle models instances versions download <handle>/<model>/<framework>/<instance>/<version>

# Or simply download manually from the web and extract here
# The structure should be: models/v1.0/model/ and models/v1.0/tokenizer/

cd ../../..
```

**Verify the installation:**

```bash
# Check structure (replace v1.0 with your MODEL_VERSION)
ls Sentiment_Analyser/data/models/v1.0/
# Should show: model/ tokenizer/ config.json metrics.json
```

**⚠️ IMPORTANTE: Configurar permisos del modelo**

```bash
# Otorgar permisos de lectura al modelo
chmod -R 755 Sentiment_Analyser/data/models/v1.0/
```

> **Note:** The folder name should match your `MODEL_VERSION` setting in `.env`

#### 3. Configure Bluesky Credentials (Optional)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Bluesky credentials:
# BLUESKY_HANDLE=your-handle.bsky.social
# BLUESKY_PASSWORD=your-app-password
```

> **Get Bluesky App Password:** Settings → Privacy and Security → App Passwords → Create New

#### 4. Start the API

```bash
# Start the FastAPI server
uvicorn Sentiment_Analyser.api.main:app --reload
```

Visit: **http://localhost:8000/docs** for interactive API documentation

#### 5. Test It!

```bash
# Analyze sentiment for a Bluesky user
curl "http://localhost:8000/api/analyze/bluesky/user/jay.bsky.team?limit=10"
```

### 🐍 Python Usage

```python
from Sentiment_Analyser.models import SentimentAnalyzer

# Load Kaggle-trained model (version configured in .env)
analyzer = SentimentAnalyzer(
    use_kaggle_model=True,
    kaggle_model_version="v1.0"  # Or set MODEL_VERSION in .env
)

# Analyze single text
result = analyzer.analyze("I love this product!")
print(result)  # {'sentiment': 'positive', 'confidence': 0.9987, 'label': 'LABEL_1'}

# Analyze multiple texts (batch processing)
texts = ["Great experience!", "Terrible service", "Not bad"]
results = analyzer.analyze_batch(texts)
for text, result in zip(texts, results):
    print(f"{text}: {result['sentiment']} ({result['confidence']:.2%})")
```

> **Note:** To use Kaggle models, first train them in Kaggle and download locally.
> See [KAGGLE_WORKFLOW.md](KAGGLE_WORKFLOW.md) for complete instructions.

### 🎯 API Endpoints

**Analyze Bluesky User:**

```bash
GET /api/analyze/bluesky/user/{handle}?limit=10
```

**Response:**

```json
{
  "user_name": "Jay Graber",
  "user_handle": "jay.bsky.team",
  "user_avatar": "https://cdn.bsky.app/...",
  "total_analyzed": 25,
  "positive_count": 18,
  "negative_count": 7,
  "average_confidence": 0.8945,
  "most_positive": { "text": "...", "confidence": 0.9987 },
  "most_negative": { "text": "...", "confidence": 0.8654 },
  "posts": [...]
}
```

---

## 📦 Installation

### Complete Setup (Production)

```bash
# 1. Clone and create environment
git clone https://github.com/Alesstintor/Shameless.git
cd Shameless
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install kaggle

# 3. Download pre-trained model (~270 MB)
# Go to: https://www.kaggle.com/models/aleselmaquinas/shameless-sentiment-analyzer
# Click "Download" and extract to: Sentiment_Analyser/data/models/v1.0
# Note: Folder name must match MODEL_VERSION in .env (default: v1.0)

# 4. Configure environment
cp .env.example .env
# Edit .env with your Bluesky credentials and MODEL_VERSION

# 5. Start API
uvicorn Sentiment_Analyser.api.main:app --reload
```

### Development Installation

```bash
# Install with dev dependencies
pip install -r requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Run tests
pytest tests/ -v --cov
```

### Configuration

Edit `.env` with your settings:

```env
# Bluesky Credentials (Required for API)
BLUESKY_HANDLE=your-handle.bsky.social
BLUESKY_PASSWORD=your-app-password  # From Settings → App Passwords

# Model Configuration
MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english
MODEL_VERSION=v1.0  # Kaggle model version (change to v1.1, v2.0 when available)
MODEL_DEVICE=cpu  # or 'cuda' if you have GPU
MODEL_BATCH_SIZE=32

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Logging
LOG_LEVEL=INFO
```

### Troubleshooting

**Error: "Permission denied" al cargar el modelo**

Si recibes errores de permisos al intentar cargar el modelo, asegúrate de configurar los permisos correctamente:

```bash
# Otorgar permisos de lectura/escritura al directorio del modelo
chmod -R 755 Sentiment_Analyser/data/models/v1.0/
```

**Error: "Model not found at data/models/v1.0/model"**

The model files are missing. Download them:

1. Go to: https://www.kaggle.com/models/aleselmaquinas/shameless-sentiment-analyzer
2. Click **"Download"** button (you'll need a Kaggle account)
3. Extract the downloaded archive
4. Copy the folder to match your `MODEL_VERSION` in `.env`
   - If `MODEL_VERSION=v1.0`, copy to: `Sentiment_Analyser/data/models/v1.0`
   - If `MODEL_VERSION=v2.0`, copy to: `Sentiment_Analyser/data/models/v2.0`

Expected structure (for v1.0):

```
Sentiment_Analyser/data/models/v1.0/
├── model/
│   ├── config.json
│   └── model.safetensors
├── tokenizer/
│   ├── tokenizer.json
│   ├── vocab.txt
│   ├── tokenizer_config.json
│   └── special_tokens_map.json
├── config.json
└── metrics.json
```

> **Tip:** Always ensure the folder name matches the `MODEL_VERSION` variable in your `.env` file

**Error: "Bluesky integration is not configured"**

- Add your credentials to `.env`:
  ```
  BLUESKY_HANDLE=your-handle.bsky.social
  BLUESKY_PASSWORD=your-app-password
  ```
- Get App Password: Bluesky Settings → Privacy and Security → App Passwords

**Slow inference on CPU?**

- Use GPU if available: Set `MODEL_DEVICE=cuda` in `.env`
- Install CUDA-enabled PyTorch:
  ```bash
  pip install torch --index-url https://download.pytorch.org/whl/cu118
  ```

**How to upgrade to a new model version?**

When a new model version is released (e.g., v2.0):

1. Download the new version from Kaggle Models
2. Extract to: `Sentiment_Analyser/data/models/v2.0`
3. Update your `.env`:
   ```env
   MODEL_VERSION=v2.0
   ```
4. Restart the API:
   ```bash
   uvicorn Sentiment_Analyser.api.main:app --reload
   ```

You can keep multiple versions and switch between them by changing `MODEL_VERSION`!

---

## 💻 Usage

### Command Line Interface

```bash
# Collect tweets
python -m sentiment_analyser.scraper collect \
    --query "artificial intelligence" \
    --limit 1000 \
    --output data/raw/tweets.json

# Analyze sentiment
python -m sentiment_analyser.models analyze \
    --input data/raw/tweets.json \
    --output data/processed/analysis.csv
```

### Python API

```python
from sentiment_analyser.scraper import TwitterCollector, DataStorage
from sentiment_analyser.models import SentimentAnalyzer, TextPreprocessor
from sentiment_analyser.config import get_settings

# Initialize components
settings = get_settings()
collector = TwitterCollector(rate_limit=1.0)
preprocessor = TextPreprocessor()
analyzer = SentimentAnalyzer()
storage = DataStorage(settings.RAW_DATA_DIR)

# Collect data
tweets = []
for tweet in collector.search("climate change", limit=500):
    tweets.append(tweet.to_dict())

# Save raw data
storage.save_json(tweets, "climate_tweets.json")

# Preprocess
texts = [tweet['content'] for tweet in tweets]
clean_texts = preprocessor.clean_batch(texts)

# Analyze sentiment
results = analyzer.analyze_batch(clean_texts)

# Process results
for tweet, result in zip(tweets, results):
    print(f"Tweet: {tweet['content'][:50]}...")
    print(f"Sentiment: {result['sentiment']} (confidence: {result['score']:.2%})")
    print("-" * 80)
```

### Jupyter Notebook

Open the example notebook:

```bash
jupyter notebook Sentiment_Analyser/notebooks/sentiment_analysis.ipynb
```

The notebook includes:

- ✅ Complete data collection workflow
- ✅ Preprocessing examples
- ✅ Sentiment analysis
- ✅ Beautiful visualizations
- ✅ Statistical insights
- ✅ Export functionality

---

## 📁 Project Structure

```
Shameless/
├── .windsurf/                    # Windsurf IDE metadata
│   ├── architecture.md          # Architecture documentation
│   ├── context.md               # Project context and guidelines
│   └── rules.md                 # Development rules
│
├── Sentiment_Analyser/          # Main package
│   ├── config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py          # Settings with pydantic
│   │
│   ├── scraper/                 # Data collection
│   │   ├── collectors/          # Platform-specific scrapers
│   │   │   └── twitter_collector.py
│   │   └── storage/             # Data storage utilities
│   │       └── data_storage.py
│   │
│   ├── models/                  # Machine Learning
│   │   ├── preprocessing/       # Text preprocessing
│   │   │   └── text_preprocessor.py
│   │   └── inference/           # Sentiment analysis
│   │       └── sentiment_analyzer.py
│   │
│   ├── utils/                   # Shared utilities
│   │   └── logger.py            # Logging configuration
│   │
│   ├── data/                    # Data storage
│   │   ├── raw/                 # Raw scraped data
│   │   ├── processed/           # Processed datasets
│   │   └── models/              # Saved ML models
│   │
│   └── notebooks/               # Jupyter notebooks
│       └── sentiment_analysis.ipynb
│
├── tests/                       # Test suite
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── .env.example                 # Environment variables template
├── .gitignore                   # Git ignore rules
├── LICENSE                      # MIT License
└── README.md                    # This file
```

---

## 📚 Documentation

Comprehensive documentation is available in the `.windsurf/` directory:

- **[Architecture Guide](/.windsurf/rules/architecture.md)** - System architecture and design patterns
- **[Development Rules](/.windsurf/rules/rules.md)** - Coding standards and best practices
- **[Project Context](/.windsurf/rules/context.md)** - Project goals, use cases, and workflows

### Additional Resources

- [API Documentation](docs/api.md) _(coming soon)_
- [Deployment Guide](docs/deployment.md) _(coming soon)_
- [Contributing Guide](CONTRIBUTING.md) _(coming soon)_

---

## 🤝 Contributing

We welcome contributions! This project is part of **Hacktoberfest 2025**.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add type hints to all functions
- Write docstrings (Google style)
- Include unit tests for new features
- Update documentation as needed

### Good First Issues

- 🟢 Add support for Reddit scraping
- 🟢 Implement additional preprocessing options
- 🟢 Create more visualization functions
- 🟢 Add multilingual sentiment analysis
- 🟢 Improve error handling

---

## 🗺️ Roadmap

### Phase 1: MVP ✅ (Current)

- [x] Project structure and architecture
- [x] Twitter scraper with snscrape
- [x] Basic sentiment analysis (transformers)
- [x] Jupyter notebook for exploration
- [x] Documentation

### Phase 2: Core Features 🔄

- [ ] Advanced ML models (fine-tuned BERT)
- [ ] REST API with FastAPI
- [ ] Database integration (PostgreSQL)
- [ ] Docker containerization
- [ ] CI/CD pipeline

### Phase 3: Scale & Polish 📅

- [ ] Real-time processing pipeline
- [ ] Web dashboard (React)
- [ ] Model monitoring and retraining
- [ ] Multi-language support
- [ ] Cloud deployment

### Phase 4: Advanced Features 🚀

- [ ] Entity recognition
- [ ] Topic modeling
- [ ] Trend prediction
- [ ] Automated reporting
- [ ] Multi-platform support

---

## 📊 Performance

Current benchmarks (on CPU):

| Metric           | Value                  |
| ---------------- | ---------------------- |
| Scraping Speed   | ~60 tweets/min         |
| Inference Time   | ~100ms/sample          |
| Batch Processing | ~1000 samples/min      |
| Accuracy         | ~87% (SST-2 benchmark) |

---

## 🔒 Security

- ✅ No hardcoded API keys or secrets
- ✅ Environment variables for configuration
- ✅ Input sanitization
- ✅ Rate limiting on scrapers
- ✅ Regular dependency updates

**Report security issues:** Open a private security advisory on GitHub.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Hacktoberfest 2025 A Coruña** for the opportunity
- **HuggingFace** for amazing transformer models
- **snscrape** for reliable social media scraping
- All contributors who make this project better

---

<div align="center">

**Made with ❤️ for Hacktoberfest 2025**

⭐ **Star this repo** if you find it useful!

</div>
