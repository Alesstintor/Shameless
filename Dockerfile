# Dockerfile simplificado para Shameless Sentiment Analyser
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY Sentiment_Analyser/ ./Sentiment_Analyser/
COPY frontend/ ./frontend/
COPY setup.py pyproject.toml README.md LICENSE ./

# Instalar el paquete en modo editable
RUN pip install -e .

# IMPORTANTE: Copiar el modelo ML pre-entrenado al contenedor
# Asegúrate de tener el modelo descargado en tu máquina local en:
# ./Sentiment_Analyser/data/models/v1.0/
# Si no existe, el contenedor funcionará pero sin análisis de sentimiento
COPY Sentiment_Analyser/data/models/ ./Sentiment_Analyser/data/models/

# Crear directorios necesarios
RUN mkdir -p \
    /app/Sentiment_Analyser/data/raw \
    /app/Sentiment_Analyser/data/processed \
    /app/logs

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Exponer puerto
EXPOSE 8000

# Health check simple
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Comando por defecto: levantar FastAPI
CMD ["uvicorn", "Sentiment_Analyser.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
