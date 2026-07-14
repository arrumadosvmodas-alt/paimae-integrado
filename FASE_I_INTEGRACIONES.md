# 🔗 Fase I — Integrações Externas

Integração com Google Classroom, Microsoft Teams, WhatsApp Business e Webhooks customizados.

---

## ✅ O que foi implementado

### 1. **Modelos de Dados**
- `Integration` — Configuração de integrações
- `IntegrationSyncLog` — Histórico de sincronizações
- `WebhookEvent` — Eventos recebidos
- `GoogleClassroomSync` — Mapeamento Google Classroom
- `MicrosoftTeamsSync` — Mapeamento Microsoft Teams
- `WhatsAppBusinessSync` — Mapeamento WhatsApp
- `WebhookSubscription` — Inscrições de webhook customizado

### 2. **Serviços de Integração**

#### **Google Classroom** (`google_classroom.py`)
```python
- get_courses()           # Listar cursos
- get_assignments()       # Listar atividades
- get_grades()           # Obter notas
- sync_classroom_data()  # Sincronizar
```

#### **Microsoft Teams** (`microsoft_teams.py`)
```python
- get_teams()            # Listar times
- get_channels()         # Listar canais
- send_message()         # Enviar mensagem
- get_assignments()      # Listar tarefas
- sync_team_data()       # Sincronizar
```

#### **WhatsApp Business** (`whatsapp.py`)
```python
- send_message()         # Enviar mensagem
- send_notification()    # Enviar notificação formatada
- mark_as_read()         # Marcar como lida
- verify_webhook()       # Verificar webhook
- handle_incoming_message() # Processar mensagem recebida
```

#### **Webhooks Customizados** (`webhook.py`)
```python
- send_event()           # Enviar evento para webhooks
- verify_webhook_signature() # Verificar assinatura
- test_webhook()         # Testar webhook
- _match_filters()       # Filtrar eventos
```

### 3. **Endpoints da API**

```
GET    /api/v1/integrations              # Listar integrações
POST   /api/v1/integrations              # Criar integração
PATCH  /api/v1/integrations/{id}         # Atualizar
DELETE /api/v1/integrations/{id}         # Deletar
POST   /api/v1/integrations/{id}/sync    # Sincronizar

GET    /api/v1/integrations/webhooks/subscriptions      # Listar webhooks
POST   /api/v1/integrations/webhooks/subscriptions      # Criar webhook
POST   /api/v1/integrations/webhooks/{id}/test         # Testar webhook
POST   /api/v1/integrations/webhooks/events            # Receber evento
```

---

## 🔐 Configuração

### Google Classroom

```bash
# 1. Google Cloud Console
# 2. Criar projeto
# 3. Ativar API Classroom
# 4. Criar Service Account
# 5. Baixar credenciais (JSON)

# .env
GOOGLE_CLASSROOM_CREDENTIALS_PATH=/path/to/credentials.json
```

### Microsoft Teams

```bash
# 1. Azure Portal
# 2. App Registration
# 3. Criar client secret
# 4. Conceder permissões

# .env
MICROSOFT_TEAMS_CLIENT_ID=your-client-id
MICROSOFT_TEAMS_CLIENT_SECRET=your-secret
MICROSOFT_TEAMS_TENANT_ID=your-tenant-id
```

### WhatsApp Business

```bash
# 1. Meta Business Manager
# 2. Criar WhatsApp Business App
# 3. Obter número de telefone ID e access token

# .env
WHATSAPP_PHONE_NUMBER_ID=your-phone-id
WHATSAPP_ACCESS_TOKEN=your-access-token
WHATSAPP_WEBHOOK_VERIFY_TOKEN=your-verify-token
```

### Webhooks Customizados

```bash
# Criar inscrição via API
POST /api/v1/integrations/webhooks/subscriptions
{
  "name": "Meu Sistema",
  "url": "https://seu-servidor.com/webhooks",
  "secret": "seu-secret-key",
  "events": ["assignment.created", "grade.updated"],
  "filters": {
    "subject": ["Matemática"]
  }
}
```

---

## 📋 Fluxo de Sincronização

```
1. Criar Integração
   └─ POST /api/v1/integrations
   └─ Guardar credentials

2. Ativar Sincronização
   └─ PATCH /api/v1/integrations/{id}
   └─ sync_enabled: true

3. Sincronizar (Manual ou Agendado)
   └─ POST /api/v1/integrations/{id}/sync
   └─ Background task inicia
   └─ Chama serviço apropriado
   └─ Cria registros no BD
   └─ Atualiza IntegrationSyncLog

4. Resultados
   └─ Verificar last_sync
   └─ Consultar sync_logs
```

---

## 🔔 Webhooks

### Eventos Disponíveis

```
assignment.created      → Atividade criada
assignment.updated      → Atividade atualizada
assignment.deleted      → Atividade deletada
grade.created          → Nota registrada
grade.updated          → Nota atualizada
interaction.created    → Interação criada
interaction.responded  → Interação respondida
student.enrolled       → Aluno inscrito
student.unenrolled     → Aluno removido
notification.sent      → Notificação enviada
```

### Payload de Webhook

```json
{
  "event": "assignment.created",
  "timestamp": "2026-07-14T10:30:00Z",
  "data": {
    "id": "assignment-123",
    "title": "Trabalho de Matemática",
    "due_date": "2026-07-20",
    "subject": "Matemática"
  }
}
```

### Headers

```
X-Webhook-Signature: hmac-sha256 da payload
X-Webhook-Event: assignment.created
Content-Type: application/json
```

---

## 📱 Integração Frontend/Mobile

### Listar Integrações

```typescript
const integrations = await api.get('/integrations');
// [
//   { id: "...", provider: "google_classroom", name: "... },
//   { id: "...", provider: "whatsapp", name: "... }
// ]
```

### Ativar Sincronização

```typescript
await api.patch(`/integrations/${integrationId}`, {
  sync_enabled: true,
  sync_interval_minutes: "30"
});
```

### Testar Webhook

```typescript
await api.post(`/integrations/webhooks/${subscriptionId}/test`);
```

---

## 🎯 Casos de Uso

### 1. Sincronizar Google Classroom

```
Professor
  ├─ Conecta Google Classroom
  ├─ Autoriza acesso
  └─ Ativa sincronização
       └─ Sistema puxa atividades
       └─ Cria StudyPlans automaticamente
```

### 2. Enviar Notificações WhatsApp

```
Interação Criada
  └─ Dispara webhook
  └─ Serviço WhatsApp envia mensagem
  └─ Responsável recebe no celular
```

### 3. Customizar com Webhook

```
Sistema Externo
  ├─ Cria atividade
  └─ POST /integrations/webhooks/events
       └─ Valida assinatura
       └─ Processa evento
       └─ Atualiza StudyPlan
```

---

## 📊 Monitoramento

### Logs de Sincronização

```
GET /api/v1/integrations/{id}/sync-logs

[
  {
    id: "...",
    status: "success",
    records_synced: "15",
    started_at: "...",
    completed_at: "..."
  }
]
```

### Eventos de Webhook

```
GET /api/v1/integrations/webhooks/events

[
  {
    id: "...",
    event_type: "assignment.created",
    processed: true,
    received_at: "..."
  }
]
```

---

## 🔄 Retry Automático

Webhooks com retry automático:
- Até 3 tentativas
- Delay: 5 segundos entre tentativas
- Timeout: 10 segundos por requisição

---

## 🚀 Próximas Melhorias

- ✅ Google Classroom integrado
- ✅ Microsoft Teams integrado
- ✅ WhatsApp Business integrado
- ✅ Webhooks customizados
- ⏳ LMS genérico (Canvas, Moodle)
- ⏳ Sincronização agendada com Celery
- ⏳ Criptografia de credentials em vault
- ⏳ Dashboard de sincronização
- ⏳ Alertas de falha de integração

---

## 📚 Arquivos Criados

```
backend/app/
├── models/integration.py           # 7 modelos
├── services/
│   ├── google_classroom.py        # Serviço Google
│   ├── microsoft_teams.py         # Serviço Teams
│   ├── whatsapp.py                # Serviço WhatsApp
│   └── webhook.py                 # Serviço Webhooks
├── api/v1/endpoints/
│   └── integrations.py            # 7 endpoints
└── schemas/integration.py          # Schemas Pydantic
```

---

**Fase I Completa! 🎉**

Próximo: Fase J — Gamificação Avançada
