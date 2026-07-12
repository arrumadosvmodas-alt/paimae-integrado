# Pai&MaeIntegrado

Base tecnica inicial para um sistema de acompanhamento escolar e familiar com rotinas, notificacoes, evolucao da crianca, IA com limites de dados e auditoria.

## Stack

- Python 3.12
- FastAPI
- PostgreSQL
- SQLAlchemy 2
- Alembic
- Docker
- Pytest

## Executar

```bash
cp .env.example .env
docker compose up --build
```

Rodar migration:

```bash
make migrate
```

Gerar notificacoes de uma data:

```bash
make generate-notifications date=2026-07-13
```

Rodar testes de integracao com PostgreSQL local:

```bash
make test-integration
```

API:

- `GET http://localhost:8000/health`
- `POST http://localhost:8000/api/v1/auth/bootstrap-admin`
- `POST http://localhost:8000/api/v1/auth/login`

Aplicativo web:

- `http://localhost:5173`

## Principios do MVP

- Comecar adaptavel para uma escola especifica, sem travar multi-escola.
- Separar acesso escolar e familiar.
- Nao inventar conclusoes quando faltarem dados.
- Medir evolucao da crianca com historico auditavel.
- Preparar modelo de assinatura familiar e pacote escolar.

## Seguranca implementada

- JWT.
- Senhas com hash bcrypt.
- Escopo por escola.
- Escopo familiar por crianca.
- Auditoria de operacoes sensiveis.

## Fluxo para teste real

1. Suba o projeto com `docker compose up --build`.
2. Abra `http://localhost:5173`.
3. Crie o primeiro admin.
4. Faca login.
5. Cadastre escola, crianca, rotinas, tarefas e eventos de evolucao.
6. Gere notificacoes do dia e acompanhe conclusoes/resumos.
