#!/usr/bin/env bash
# Encerra o script em caso de erro
set -e

echo "Executando migrations do banco de dados (Alembic)..."
alembic upgrade head

echo "Iniciando aplicação FastAPI com Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
