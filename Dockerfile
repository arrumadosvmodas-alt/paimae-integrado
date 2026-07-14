FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar código do backend (pyproject.toml define as dependências)
COPY backend/ ./

# Instalar a aplicação em modo de produção (sem editable -e e sem pacotes dev)
RUN pip install --no-cache-dir .

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Roda as migrations e inicia a aplicação
CMD ["sh", "start.sh"]
