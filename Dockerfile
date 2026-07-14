FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY backend/requirements.txt .

# Instalar Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY backend ./app

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
