.PHONY: help install install-dev clean test lint format docker-build docker-up docker-down notebook

help:
	@echo "Available commands:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development dependencies"
	@echo "  clean         - Remove build artifacts and cache"
	@echo "  test          - Run tests with coverage"
	@echo "  lint          - Run linters (flake8, mypy)"
	@echo "  format        - Format code with black and isort"
	@echo "  docker-build  - Build Docker images"
	@echo "  docker-up     - Start Docker containers"
	@echo "  docker-down   - Stop Docker containers"
	@echo "  notebook      - Start Jupyter notebook"

install:
	pip install -r requirements.txt
	pip install -e .

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .
	pre-commit install

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	@echo "✅ Cleanup complete"

test:
	@echo "Running tests..."
	pytest tests/ -v --cov --cov-report=term-missing --cov-report=html
	@echo "✅ Tests complete. Coverage report in htmlcov/index.html"

lint:
	@echo "Running linters..."
	flake8 Sentiment_Analyser/ --max-line-length=100 --extend-ignore=E203,W503
	mypy Sentiment_Analyser/ --ignore-missing-imports
	@echo "✅ Linting complete"

format:
	@echo "Formatting code..."
	black Sentiment_Analyser/ --line-length=100
	isort Sentiment_Analyser/ --profile=black --line-length=100
	@echo "✅ Formatting complete"

docker-build:
	@echo "Building Docker images..."
	docker-compose build
	@echo "✅ Docker build complete"

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d
	@echo "✅ Containers started"
	@echo "Jupyter: http://localhost:8888"
	@echo "API: http://localhost:8000"

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down
	@echo "✅ Containers stopped"

notebook:
	@echo "Starting Jupyter notebook..."
	jupyter notebook Sentiment_Analyser/notebooks/

# Quick start for development
dev-setup: install-dev
	@echo "Setting up development environment..."
	cp -n .env.example .env || true
	@echo "✅ Development setup complete!"
	@echo "Edit .env file with your configuration"

# Run the scraper
scrape:
	@echo "Running scraper..."
	python -m sentiment_analyser.cli scrape --help

# Run analysis
analyze:
	@echo "Running analysis..."
	python -m sentiment_analyser.cli analyze --help
