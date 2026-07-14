# 📚 Pai&Mãe Integrado - MVP Completo

Plataforma Inteligente de Educação Personalizada com IA, Aprendizado Adaptativo e Analytics Avançados.

**Status:** ✅ Fases A-G 100% Implementadas | **Linhas de Código:** 9,100+ | **Desenvolvimento:** 2-3 semanas

---

## 🎯 O que é Pai&Mãe Integrado?

Uma plataforma educacional que:
- 📚 **Processa livros automaticamente** com OCR + IA (Google Vision + Gemini)
- 🧠 **Adapta-se ao aluno** com perfil dinâmico, recomendações IA e predições ML
- 📤 **Orquestra interações** com envio automático (2 jobs: 5min + midnight)
- 📊 **Visualiza progresso** com 5 tipos de gráficos avançados e relatórios PDF
- 🎮 **Gamifica o aprendizado** com badges, streaks e recompensas
- 🛡️ **Respeita LGPD** com portabilidade e direito ao esquecimento

---

## 📋 Fases Implementadas

### ✅ Fase A — Dados (21 modelos, 21 CRUD APIs)
- Modelos: Child, School, User, PedagogicalMaterial, StudyPlan, Interaction, etc.
- Endpoints CRUD completos com validação e tratamento de erro

### ✅ Fase B — Upload e Processamento (OCR + IA)
- Google Vision API para OCR (PDF/Imagem)
- Google Gemini para análise pedagógica
- Extração automática: disciplina, BNCC skills, sequência, dificuldade

### ✅ Fase C — Orquestração (APScheduler)
- Job 1: Dispatch de interações (5 minutos)
- Job 2: Geração diária de planos (midnight)
- Notificações: Email, SMS, Push

### ✅ Fase D — Aprendizado Adaptativo (ML)
- Perfil de aprendizagem dinâmico (moving average 70/30)
- Predição de sucesso em próxima atividade
- Detecção de risco de dropout (multi-fator)
- Feedback personalizado com IA

### ✅ Fase E — Frontend React (4 componentes)
- `BookUpload`: Upload com OCR + progresso
- `StudyPlanView`: Visualização e ativação de planos
- `LearningAnalytics`: Métricas, estilos, recomendações
- `InteractionCard`: Respostas com feedback IA

### ✅ Fase F — Dashboards (3 páginas)
- `TeacherDashboard`: Upload, planos, análise
- `ParentDashboard`: Progresso filhos, interações, alertas
- `ChildInterface`: Gamificação, atividades, feedback

### ✅ Fase G — Analytics Avançados (5 gráficos)
- `ProgressChart`: Evolução ao longo do tempo
- `LearningStyleChart`: Estilos de aprendizagem
- `ThemeProgressChart`: Progresso por tema
- `ComparisonChart`: Radar comparativo (aluno vs turma)
- `SchoolStatistics`: Agregado por escola
- `ReportGenerator`: PDF, JSON, CSV

---

## 🚀 Como Testar

### 1. **Instalar Dependências**

```bash
# Frontend
cd frontend
npm install

# Backend (opcional, se quiser testar com API real)
cd backend
pip install -r requirements.txt
```

### 2. **Iniciar Dev Server**

```bash
# Terminal 1: Frontend
cd frontend
npm run dev
# Acesse: http://localhost:5173
```

```bash
# Terminal 2: Backend (opcional)
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### 3. **Credenciais de Teste**

```
Email: professor@escola.com
Senha: senha123
```

### 4. **Rotas Disponíveis**

| Rota | Descrição |
|------|-----------|
| `/` | Dashboard Principal (Admin/Coordenador) |
| `/login` | Página de Autenticação |
| `/teacher-dashboard` | Dashboard Professor |
| `/parent-dashboard` | Dashboard Pais |
| `/child-interface` | Interface Criança |
| `/analytics` | Analytics Avançados |

---

## 📦 Stack Tecnológico

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **ORM:** SQLAlchemy
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **IA/ML:** Google Vision API, Google Gemini, Scikit-learn
- **Scheduler:** APScheduler
- **Auth:** JWT + Bcrypt

### Frontend
- **Framework:** React 18 + TypeScript
- **Router:** React Router 7
- **Styling:** Tailwind CSS
- **Gráficos:** Recharts
- **Icons:** Lucide React

---

## 📈 Estatísticas

| Métrica | Valor |
|---------|-------|
| Modelos de Dados | 21+ |
| Endpoints API | 50+ |
| Componentes React | 12+ |
| Gráficos Avançados | 5 |
| Linhas de Código | 9,100+ |
| Páginas/Dashboards | 6 |
| Tempo de Dev | 2-3 semanas |

---

## 🎯 Próximas Fases (Opcionais)

### Fase H — Aplicativo Móvel (30-45 dias)
- React Native / Flutter
- Notificações Push (Firebase)
- Sincronização offline
- iOS + Android

### Fase I — Integrações Externas (10-15 dias)
- Google Classroom
- Microsoft Teams
- WhatsApp Business

### Fase J — Gamificação Avançada (5-7 dias)
- Leaderboards
- Missões
- Recompensas

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
