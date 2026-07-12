FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copia o código completo para dentro do container
COPY . /app

# Instala a aplicação em modo de produção (sem editable -e e sem pacotes dev)
RUN pip install --no-cache-dir .

