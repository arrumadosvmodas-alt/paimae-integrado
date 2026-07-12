# Arquitetura

## Backend

- FastAPI com rotas versionadas em `/api/v1`.
- PostgreSQL como banco principal.
- SQLAlchemy 2 para ORM.
- Alembic para migrations.
- JWT para autenticacao.

## Seguranca

- `admin`: acesso global.
- usuario escolar: acesso limitado a propria escola.
- responsavel familiar: acesso limitado as criancas vinculadas em `child_guardians`.
- auditoria automatica em operacoes sensiveis.

As listagens de rotinas, notificacoes, tarefas e vinculos familiares usam escopo derivado do usuario autenticado. Chamadas sem `child_id` nao devem retornar dados globais fora do papel `admin`.
