# Seguranca e Autorizacao

## Roles

| Role | Escopo |
| --- | --- |
| `admin` | Acesso administrativo global. |
| `school_admin` | Dados vinculados a propria escola. |
| `teacher` | Dados vinculados a propria escola. |
| `guardian` | Criancas vinculadas em `child_guardians`. |

## Vinculo responsavel-crianca

O controle familiar fica em `child_guardians`.

Campos principais:

- `can_view`: permite visualizar dados da crianca.
- `can_manage_routine`: permite criar/alterar rotinas da crianca.
- `can_mark_notifications`: permite marcar notificacoes como lidas/concluidas.

## Regras aplicadas

- Listagens sem `child_id` sao sempre limitadas pelo escopo do usuario.
- Responsavel familiar nao acessa criancas fora dos seus vinculos.
- Usuario escolar nao acessa dados de outra escola.
- Operacoes sensiveis registram `audit_logs`.
- Resumo de IA registra auditoria e retorna `insufficient_data` quando houver poucos eventos.

## Testes

O CI sobe PostgreSQL e executa testes de integracao cobrindo:

- bootstrap do primeiro admin;
- login JWT;
- criacao de escola, crianca e responsavel;
- listagem de criancas limitada ao vinculo familiar;
- bloqueio de criacao de rotina quando `can_manage_routine=false`.

## Pendencias para producao

- Rotacionar `JWT_SECRET_KEY` por ambiente seguro.
- Adicionar refresh token ou sessao curta com renovacao controlada.
- Criar rate limiting para login.
- Adicionar politicas LGPD para retencao, exportacao e exclusao de dados.
- Adicionar testes de integracao com PostgreSQL real no CI.
