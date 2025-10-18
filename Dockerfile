# Multi-stage Dockerfile for Shameless Sentiment Analyser

# Stage 1: Base image with Python
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create app directory
WORKDIR /app

# Stage 2: Dependencies
FROM base as dependencies

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application
FROM base as application

# Copy Python dependencies from previous stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code
COPY Sentiment_Analyser/ ./Sentiment_Analyser/
COPY setup.py .
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Install the package
RUN pip install -e .

# Create necessary directories
RUN mkdir -p \
    /app/Sentiment_Analyser/data/raw \
    /app/Sentiment_Analyser/data/processed \
    /app/Sentiment_Analyser/data/models \
    /app/logs

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port for API (when implemented)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sentiment_analyser; print('OK')" || exit 1

# Default command
CMD ["python", "-m", "sentiment_analyser"]
