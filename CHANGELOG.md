# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- REST API with FastAPI
- Web dashboard
- Real-time processing pipeline
- Multi-language support
- Fine-tuned models

## [0.1.0] - 2024-10-18

### Added
- Initial project structure and architecture
- Twitter/X scraper using snscrape
  - Rate limiting support
  - Multiple search options (query, user, hashtag)
  - Data export to JSON, CSV, Parquet
- Text preprocessing module
  - URL removal
  - Mention/hashtag handling
  - Text normalization
  - Batch processing support
- Sentiment analysis with transformers
  - Pre-trained model support (BERT, DistilBERT)
  - Batch inference
  - Confidence scores
- Jupyter notebook for exploration
  - Complete analysis workflow
  - Beautiful visualizations
  - Statistical insights
- Configuration management
  - Environment variable support
  - Settings validation with Pydantic
- CLI interface
  - Scrape command
  - Analyze command
  - Rich terminal output
- Development tools
  - Docker support
  - Pre-commit hooks
  - GitHub Actions CI/CD
  - Testing framework
- Comprehensive documentation
  - README with usage examples
  - Architecture guide
  - Development rules
  - Contributing guide
  - Windsurf IDE metadata

### Infrastructure
- Python 3.9+ support
- Virtual environment setup
- Dependency management (requirements.txt)
- Development dependencies (requirements-dev.txt)
- Git workflows and hooks
- Docker containerization
- Makefile for common tasks

### Documentation
- Professional README with badges
- Architecture documentation
- API usage examples
- Contributing guidelines
- Code of conduct reference
- License (MIT)

[Unreleased]: https://github.com/yourusername/Shameless/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/yourusername/Shameless/releases/tag/v0.1.0
