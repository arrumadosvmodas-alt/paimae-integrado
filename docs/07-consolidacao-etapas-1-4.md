# Consolidacao das Etapas 1 a 4

Data: 2026-07-13

## Escopo aprovado

Esta consolidacao corrige e estabiliza as etapas ja implementadas antes de avancar para relatorios, metricas, LGPD e piloto de 7 dias.

A etapa 7 permanece fora do escopo ate que as correcoes abaixo estejam validadas.

## Etapa 1: Interacoes familiares

- Mantido o fluxo de registros diarios com sugestoes de interacao familiar.
- Reforcada a regra de que responsaveis familiares visualizam apenas dados ativos e vinculados a crianca.
- Ponto pendente para evolucao futura: criar retorno/status da familia sobre cada sugestao, caso o piloto mostre necessidade.

## Etapa 2: Consulta real ISBN

- A consulta ISBN deixa de gravar automaticamente material no banco.
- O endpoint de consulta passa a preencher dados para revisao do usuario.
- A persistencia fica no cadastro/edicao de material pedagogico.
- Removido uso de contexto SSL sem verificacao.

## Etapa 3: Fluxo escolar e permissoes

- Roles escolares padronizados para `school_admin` e `teacher`.
- `admin`, `school_admin` e `teacher` podem operar fluxos escolares autorizados.
- `guardian` permanece restrito aos vinculos em `child_guardians`.
- Usuario inativo nao deve conseguir autenticar nem usar token ativo.

## Etapa 4: Edicao e inativacao segura

- Inativacao/reativacao deixa de usar toggle ambiguo.
- Endpoints passam a receber status explicito por payload: `{ "is_active": true/false }`.
- Operacoes de status registram auditoria com estado anterior e novo estado.
- Frontend pede confirmacao antes de alterar status.

## Validacoes executadas

- Sintaxe Python dos endpoints alterados.
- Build do frontend com TypeScript e Vite.

## Validacao pendente

- Suite de testes backend completa depende da instalacao do driver `psycopg` e de PostgreSQL de teste disponivel.