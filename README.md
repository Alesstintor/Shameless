# 🎭 Shameless - User Sentiment Profiler

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hacktoberfest 2025](https://img.shields.io/badge/Hacktoberfest-2025-orange.svg)](https://hacktoberfest.com/)
[![Kaggle](https://img.shields.io/badge/Kaggle-Model-blue.svg)](https://www.kaggle.com/)

**¿Qué tipo de persona es este usuario en redes sociales?** 🤔

Shameless analiza el perfil completo de un usuario en Twitter/X y genera un reporte detallado de su sentimiento. Proporciona una URL o nombre de usuario y obtén un análisis completo de personalidad basado en sus publicaciones.

> 🎉 A project for **Hacktoberfest 2025 A Coruña**

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
- **User Analysis**: Proporciona URL o username → Obtén perfil de sentimiento completo
- **Smart Scraping**: Recolecta automáticamente tweets del usuario (sin límites de API)
- **ML-Powered**: Usa modelos entrenados en Kaggle con GPU
- **Comprehensive Reports**: Genera reportes detallados con insights y visualizaciones

### 📊 Analysis Capabilities
- **Overall Sentiment**: ¿Es el usuario positivo, negativo o neutral?
- **Temporal Analysis**: Evolución del sentimiento a lo largo del tiempo
- **Topic Analysis**: ¿Sobre qué temas es más positivo/negativo?
- **Engagement Correlation**: Relación entre sentimiento y engagement
- **Insights**: Descubre patrones y tendencias automáticamente

### 🤖 Machine Learning
- **Kaggle Training**: Entrena modelos en Kaggle con GPU gratuita ⚡
- **Data-Agnostic**: Modelo funciona con tweets, reviews, cualquier texto 📝
- **Flexible Input**: Acepta 1..n textos de cualquier fuente 🎯
- **Version Control**: Gestión de versiones de modelos (v1.0, v1.1, v2.0) 📦
- **BERT-based**: Modelos de última generación (BERT, RoBERTa, DistilBERT) 🤖
- **Fast Inference**: Batch processing optimizado 🚀

### 🎨 User Experience
- **CLI Interface**: Interfaz de línea de comandos intuitiva
- **Web UI** (Coming soon): Interface web con Streamlit
- **PDF Reports**: Reportes profesionales exportables
- **Interactive Dashboards**: Visualizaciones interactivas
- **Cache System**: Sistema de caché para análisis rápidos

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Data Collection Layer                    │
│  (snscrape) → Twitter/X → Raw Data → Storage (JSON/CSV)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Preprocessing Layer                        │
│   Text Cleaning → Normalization → Feature Extraction        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Machine Learning Layer                      │
│    BERT/DistilBERT → Sentiment Classification → Results     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   Analysis & Visualization                   │
│   Jupyter Notebooks → Charts → Insights → Reports           │
└─────────────────────────────────────────────────────────────┘
```

**Tech Stack (Local - Inference Only):**
- **Language:** Python 3.9+
- **ML/NLP:** transformers, torch
- **Data:** pandas, numpy
- **Config:** pydantic, python-dotenv
- **Training:** Kaggle (GPU + Jupyter notebooks)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip or conda

### 5-Minute Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Shameless.git
cd Shameless

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Launch Jupyter Notebook
jupyter notebook Sentiment_Analyser/notebooks/sentiment_analysis.ipynb
```

### Quick Analysis with Kaggle Model

```python
from sentiment_analyser.models import SentimentAnalyzer

# Use Kaggle-trained model (data-agnostic)
analyzer = SentimentAnalyzer(use_kaggle_model=True, kaggle_model_version="v1.0")

# Analyze single text
result = analyzer.analyze("I love this product!")
print(result)  # {'sentiment': 'positive', 'score': 0.99}

# Analyze multiple texts (1..n from any source)
texts = ["Great experience!", "Terrible service", "Not bad"]
results = analyzer.analyze_batch(texts)

# Done! 🎉
```

> **Note:** To use Kaggle models, first train them in Kaggle and download locally.
> See [KAGGLE_WORKFLOW.md](KAGGLE_WORKFLOW.md) for complete instructions.

---

## 📦 Installation

### Standard Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Shameless.git
cd Shameless

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt
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

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Model configuration
MODEL_NAME=distilbert-base-uncased-finetuned-sst-2-english
MODEL_DEVICE=cpu  # or 'cuda' for GPU

# Scraper settings
SCRAPER_RATE_LIMIT=1.0

# Logging
LOG_LEVEL=INFO
```

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

- **[Architecture Guide](/.windsurf/architecture.md)** - System architecture and design patterns
- **[Development Rules](/.windsurf/rules.md)** - Coding standards and best practices
- **[Project Context](/.windsurf/context.md)** - Project goals, use cases, and workflows

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

| Metric | Value |
|--------|-------|
| Scraping Speed | ~60 tweets/min |
| Inference Time | ~100ms/sample |
| Batch Processing | ~1000 samples/min |
| Accuracy | ~87% (SST-2 benchmark) |

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
