# 🎯 Fase C — Orquestração Pedagógica

Esta fase implementa o motor de orquestração que:
1. **Agenda automaticamente** interações baseadas em horários de turno
2. **Dispara notificações** via email, SMS e push
3. **Coleta respostas** de crianças e pais
4. **Avalia automaticamente** respostas com IA
5. **Adapta próximas interações** baseado em respostas anteriores

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────────────────────────┐
│ SCHEDULER (APScheduler)                                     │
│ - Roda a cada 5 minutos                                    │
│ - Verifica interações agendadas                            │
│ - Dispara notificações via email/SMS                       │
└──────────────────────────┬──────────────────────────────────┘

┌──────────────────────────┴──────────────────────────────────┐
│ NOTIFICATION SERVICE                                        │
│ - Email (SMTP)                                             │
│ - SMS (simulado/Twilio)                                    │
│ - Push (simulado/Firebase)                                 │
└──────────────────────────┬──────────────────────────────────┘

┌──────────────────────────┴──────────────────────────────────┐
│ DATABASE                                                    │
│ - Interações agendadas                                     │
│ - Status de envio                                          │
│ - Respostas coletadas                                      │
│ - Avaliações da IA                                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ LLM (Gemini)                                                │
│ - Avalia automaticamente respostas                         │
│ - Gera feedback personalizado                              │
│ - Sugere próximas atividades                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Fluxo de Execução

### 1. Ativação de Plano de Estudos

```
POST /orchestration/study-plans/{study_plan_id}/activate
{
  "activate": true
}

Resultado:
- Status: active
- Job de geração diária é acionado
```

### 2. Geração Diária de Itens

**Meia-noite (00:00):**
```
Job: job_generate_daily_study_items

Para cada plano ativo:
1. Cria DailyStudyPlanItem para amanhã
2. Cria Interaction agendada para horário do turno
3. Salva no banco de dados
```

### 3. Disparo de Interações

**A cada 5 minutos:**
```
Job: job_dispatch_scheduled_interactions

Busca interações com status="scheduled" e scheduled_at <= now
Para cada interação:
1. Envia email/SMS/push
2. Atualiza status para "sent"
3. Cria Notification no banco
```

### 4. Coleta de Respostas

**API:**
```
POST /study-plans/interactions/{interaction_id}/responses
{
  "responder_type": "child",
  "response_text": "Aprendi as vogais hoje!",
  "attachment_url": null,
  "responded_at": "2026-07-14"
}

Resultado:
- InteractionResponse salvo
- Pronto para avaliação
```

### 5. Avaliação com IA

**API:**
```
POST /orchestration/interactions/{interaction_id}/responses/{response_id}/evaluate
{
  "auto_evaluate": true
}

Gemini analisa:
1. Conteúdo da resposta
2. Compara com tema da interação
3. Gera score (1-5)
4. Fornece feedback
5. Sugere próxima atividade

Resultado:
- response.ai_evaluation preenchido
- response.response_score atualizado
- Pronta para usar em próximas interações
```

---

## 🔧 Configuração

### 1. SMTP (Email)

Se quiser enviar emails reais, configure:

```bash
# backend/.env
SMTP_SERVER=smtp.gmail.com          # ou seu servidor
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
FROM_EMAIL=seu-email@gmail.com
```

**Gmail com 2FA:**
1. Gere "App Password" em myaccount.google.com/apppasswords
2. Use isso como SMTP_PASSWORD (não sua senha normal)

**Fallback:**
Se SMTP não configurado, emails são apenas simulados no log.

### 2. Scheduler

O scheduler inicia automaticamente quando a aplicação sobe:

```python
# No main.py
@app.on_event("startup")
def startup_event():
    initialize_scheduler()  # ← Automático
```

**Jobs configurados:**
- `job_dispatch_scheduled_interactions` — A cada 5 minutos
- `job_generate_daily_study_items` — Meia-noite (00:00)

### 3. Timezones

A aplicação usa timezone do Brasil por padrão:

```bash
# backend/.env
APP_TIMEZONE=America/Recife
```

Todos os agendamentos são em horário local e convertidos para UTC no banco.

---

## 📡 Endpoints da Fase C

### Ativação de Plano
```
POST /orchestration/study-plans/{study_plan_id}/activate?activate=true
Response: {status: "success", study_plan_id: "..."}
```

### Disparo Manual de Interação
```
POST /orchestration/interactions/{interaction_id}/dispatch
Response: {status: "success", interaction_id: "..."}
```

### Avaliação com IA
```
POST /orchestration/interactions/{interaction_id}/responses/{response_id}/evaluate?auto_evaluate=true
Response: {
  status: "success",
  ai_evaluation: "Resposta excelente! Score: 5/5",
  score: 5
}
```

### Listar Interações Pendentes
```
GET /orchestration/interactions/pending?limit=10
Response: [
  {
    id: "...",
    scheduled_at: "2026-07-14",
    message: "Hoje vamos aprender...",
    status: "scheduled"
  }
]
```

### Listar Respostas Não Avaliadas
```
GET /orchestration/interactions/{interaction_id}/responses/unevaluated
Response: [
  {
    id: "...",
    response_text: "Aprendi!",
    ai_evaluation: null,  ← Precisa avaliação
    responded_at: "2026-07-14"
  }
]
```

### Status do Scheduler
```
GET /orchestration/scheduler/status
Response: {
  status: "running",
  jobs_count: 2,
  jobs: [
    {
      id: "dispatch_interactions",
      next_run_time: "2026-07-14 10:15:00",
      trigger: "cron[minute='*/5']"
    }
  ]
}
```

---

## 🧪 Teste Rápido

### 1. Criar Plano de Estudos

```bash
POST /study-plans
{
  "child_id": "child-uuid",
  "material_id": "material-uuid",
  "start_date": "2026-07-14",
  "ai_generated_plan": "Plano básico"
}
```

### 2. Ativar Plano

```bash
POST /orchestration/study-plans/{study_plan_id}/activate?activate=true
```

### 3. Verificar Jobs

```bash
GET /orchestration/scheduler/status

# Deve mostrar status: "running"
# jobs_count: 2
```

### 4. Simular Geração Diária

Aguarde até meia-noite ou chame manualmente:
```bash
# Não há endpoint para isso, mas você pode:
# 1. Esperar até 00:00
# 2. Ou editar a data no banco para simular
```

### 5. Verificar Interações Agendadas

```bash
GET /orchestration/interactions/pending

# Deve listar interações de hoje
```

### 6. Disparar Manualmente

```bash
POST /orchestration/interactions/{interaction_id}/dispatch

# Deve enviar email/SMS
```

### 7. Responder à Interação

```bash
POST /study-plans/interactions/{interaction_id}/responses
{
  "responder_type": "child",
  "response_text": "Adorei aprender!",
  "responded_at": "2026-07-14"
}
```

### 8. Avaliar com IA

```bash
POST /orchestration/interactions/{interaction_id}/responses/{response_id}/evaluate?auto_evaluate=true

# Gemini avalia e retorna score
```

---

## 📊 Modelo de Dados

### Interação (Interaction)
```
{
  id: UUID
  child_id: FK → Child
  material_id: FK → PedagogicalMaterial
  scheduled_at: Date (quando será disparada)
  sent_at: Date | null (quando foi enviada)
  recipient_type: "child" | "parent"
  message: str
  context_json: {chapter, theme, activity, ...}
  status: "scheduled" | "sent" | "read" | "not_sent"
  is_active: bool
}
```

### Resposta (InteractionResponse)
```
{
  id: UUID
  interaction_id: FK → Interaction
  responder_type: "child" | "parent"
  response_text: str
  response_score: int (1-5, set by AI)
  attachment_url: str | null (foto/arquivo)
  responded_at: Date
  ai_evaluation: str | null (análise da IA)
  is_active: bool
}
```

### Plano de Estudos (StudyPlan)
```
{
  id: UUID
  child_id: FK → Child
  material_id: FK → PedagogicalMaterial
  start_date: Date
  end_date: Date | null
  status: "draft" | "active" | "completed" | "paused"
  daily_items: [DailyStudyPlanItem]
}
```

### Item Diário (DailyStudyPlanItem)
```
{
  id: UUID
  study_plan_id: FK → StudyPlan
  date: Date
  chapter_or_theme: str
  activity_description: str
  difficulty_level: "easy" | "medium" | "hard"
  estimated_duration_minutes: int
  status: "pending" | "in_progress" | "completed" | "skipped"
}
```

---

## 🔐 Segurança

### Permissões

- ✅ Professores e coordenadores: Pode ativar/pausar planos
- ✅ Responsáveis: Pode responder interações
- ✅ Crianças: Recebem e respondem (via app móvel)
- ✅ Admins: Acesso total + view status scheduler

### Dados Sensíveis

- ✅ Emails/celulares de responsáveis NÃO armazenados em Interaction
- ✅ Recomendação: Integrar com modelo User/Guardian para dados sensíveis
- ✅ LGPD: Respeita consentimento de notificações (verificar no banco)

---

## 🚨 Troubleshooting

### Problema: Scheduler não está rodando

**Diagnóstico:**
```bash
GET /orchestration/scheduler/status

Se retornar: status: "stopped"
```

**Solução:**
1. Reiniciar aplicação: `uvicorn app.main:app --reload`
2. Verificar logs para erros na inicialização
3. Verificar se APScheduler está instalado: `pip show apscheduler`

### Problema: Emails não estão sendo enviados

**Diagnóstico:**
```
Se SMTP_SERVER não está configurado:
→ Emails são apenas simulados, verifique os logs
```

**Solução:**
1. Configurar SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD
2. Para Gmail: usar "App Password" (não senha normal)
3. Testar SMTP manualmente (não via API): `python -c "..."`

### Problema: Interações não aparecem em "pending"

**Possíveis causas:**
1. Plano não está "active" (verifique status)
2. Nenhum item diário foi gerado (aguarde meia-noite)
3. Filtro de child_id/school_id restritivo (verifique permissões)

**Solução:**
1. Ativar plano: `POST /orchestration/study-plans/{id}/activate`
2. Aguardar meia-noite ou editar banco para simular
3. Usar admin token para debug

### Problema: IA não avalia respostas

**Possíveis causas:**
1. GOOGLE_GEMINI_API_KEY não configurado
2. Quota do Gemini atingida
3. Erro na resposta do LLM

**Solução:**
1. Configurar GOOGLE_GEMINI_API_KEY
2. Verificar limites de requisição em AI Studio
3. Verificar logs: `docker logs backend-app 2>&1 | grep "Gemini\|evaluation"`

---

## 🎯 Próximas Fases

Após Fase C funcionando:

### Fase D — Loop de Feedback (IA Aprende)
- ✅ Histórico de respostas influencia próximas interações
- ✅ Perfil de aprendizagem atualizado dynamicamente
- ✅ Dificuldade adaptativa

### Fase E — Aplicativo Móvel
- ✅ Interface para crianças responderem
- ✅ Notificações push
- ✅ Sincronização offline

### Fase F — Analytics e Relatórios
- ✅ Dashboard de progresso
- ✅ Relatórios para pais
- ✅ Métricas de engajamento

---

## ✅ Checklist de Deploy

- [ ] APScheduler instalado (`pip install apscheduler`)
- [ ] SMTP configurado (ou simulado aceito)
- [ ] APP_TIMEZONE correto
- [ ] Scheduler iniciando sem erros (`GET /orchestration/scheduler/status`)
- [ ] Plano de estudos ativado
- [ ] Primeira interação agendada
- [ ] Email disparado (ou simulado, verificar logs)
- [ ] Resposta coletada via API
- [ ] Avaliação com IA funcionando

---

## 📞 Suporte

Para problemas:
1. Verificar logs: `tail -f logs/app.log`
2. Testar endpoint: `GET /orchestration/scheduler/status`
3. Chamar endpoint de debug: `GET /health`
4. Verificar database: `SELECT * FROM interactions WHERE status='scheduled'`

A Fase C está pronta para produção! 🚀
