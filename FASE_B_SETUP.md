# 🚀 Fase B — Setup de APIs

Este documento descreve como configurar as APIs externas necessárias para a Fase B (Upload, OCR e Processamento com IA).

## 📋 Requisitos

- **Google Cloud Vision API** — Para OCR (extração de texto)
- **Google Gemini API** — Para análise de conteúdo e geração de planos

Ambas são fornecidas pelo Google Cloud Platform e têm níveis gratuitos disponíveis.

---

## 🔑 Google Cloud Vision API (OCR)

### Passo 1: Criar Projeto no Google Cloud

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto (ou use um existente)
3. Anote o **Project ID**

### Passo 2: Habilitar Vision API

1. No Console, vá para **APIs & Services** → **Library**
2. Busque por "Cloud Vision API"
3. Clique e selecione **Enable**

### Passo 3: Criar Service Account

1. Vá para **APIs & Services** → **Credentials**
2. Clique em **Create Credentials** → **Service Account**
3. Preencha os detalhes:
   - **Service account name**: `paimae-vision`
   - **Service account ID**: auto-preenchido
4. Clique em **Create and Continue**
5. Conceda permissão: **Cloud Vision API User** (ou role mais simples)
6. Clique em **Continue** e depois **Done**

### Passo 4: Criar Chave API

1. Na lista de Service Accounts, clique no que foi criado
2. Vá para **Keys** → **Add Key** → **Create new key**
3. Escolha **JSON**
4. Salve o arquivo JSON localmente
5. Este JSON contém a chave privada (não compartilhe!)

### Passo 5: Configurar Variável de Ambiente

Para usar a Vision API, você pode:

**Opção A (Recomendada):** Definir variável de ambiente
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

**Opção B:** Usar chave diretamente no `.env`
```
GOOGLE_VISION_API_KEY=seu-api-key-json-em-base64
```

---

## 🤖 Google Gemini API (LLM)

### Passo 1: Obter Chave de API

1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Clique em **Create API Key**
3. Escolha seu projeto Google Cloud
4. Copie a chave gerada

### Passo 2: Configurar no `.env`

```bash
# backend/.env
GOOGLE_GEMINI_API_KEY=sua-chave-aqui
```

**Nota:** Esta é uma chave pública (não é sensível como a Vision). A Vision usa autenticação de serviço, Gemini usa chave de API simples.

---

## 💾 Supabase Storage (Armazenamento de Arquivos)

Se já tem Supabase configurado:

```bash
# backend/.env
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anonima
SUPABASE_BUCKET=paimae-storage
```

Se não tem, veja [Documentação Supabase](https://supabase.com/docs/guides/storage/quickstart).

---

## 🧪 Testar a Configuração

### 1. Instalar Dependências

```bash
cd backend
pip install -e ".[dev]"
```

### 2. Iniciar Servidor

```bash
uvicorn app.main:app --reload
```

### 3. Testar Upload

```bash
# Com cURL
curl -X POST "http://localhost:8000/materials/{material_id}/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/path/to/book.pdf"

# Resposta esperada (202 Accepted):
{
  "status": "processing_initiated",
  "message": "Arquivo recebido. Processamento em andamento...",
  "material_id": "uuid-aqui",
  "details": {
    "status": "success",
    "message": "Livro processado com sucesso",
    ...
  }
}
```

### 4. Consultar Status

```bash
curl -X GET "http://localhost:8000/materials/{material_id}/processing-status" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Resposta esperada:
{
  "material_id": "uuid",
  "status": "ok",
  "processing_status": "completed",
  "file_url": "https://...",
  "error": null,
  "ai_analysis": {
    "subject": "Português",
    "proficiency_level": "Fundamental 1",
    ...
  }
}
```

---

## 📦 Endpoints da Fase B

### Upload de Livro
```
POST /materials/{material_id}/upload
Content-Type: multipart/form-data

Form Data:
- file: <PDF ou imagem do livro>

Response: 202 Accepted
```

### Consultar Status
```
GET /materials/{material_id}/processing-status

Response: 200 OK
{
  "processing_status": "pending|processing|completed|failed",
  "ai_analysis": {...}
}
```

### Gerar Plano de Estudos
```
POST /materials/{material_id}/generate-study-plan?child_id={child_id}

Response: 200 OK
{
  "study_plan": "Plano estruturado em Markdown..."
}
```

### Gerar Interação
```
POST /materials/{material_id}/generate-interaction?child_id={child_id}&chapter=Cap1&theme=Vogais&recipient_type=child

Response: 200 OK
{
  "interaction": "Mensagem personalizada para criança..."
}
```

---

## ⚙️ Configuração Avançada

### Limites de Requisição

- **Google Vision API**: ~1000 requisições/mês gratuitas (depois paga ~$1.50/1000)
- **Google Gemini API**: ~60 requisições/minuto, ilimitado com plano pago
- **Supabase Storage**: 1GB gratuito, depois ~$0.06/GB

### Fallback Simulado

Se as APIs não estiverem configuradas, o sistema fornece respostas simuladas para testes:

- OCR simula extração de texto (pedagógico)
- Gemini simula análise estruturada (JSON válido)
- Interações simuladas funcionam normalmente

Isso permite desenvolver e testar sem APIs reais configuradas.

---

## 🐛 Troubleshooting

### Erro: "Google Vision API key não configurada"

**Solução:** Verifique se `GOOGLE_VISION_API_KEY` ou `GOOGLE_APPLICATION_CREDENTIALS` está configurado.

### Erro: "Arquivo muito grande"

**Limite:** 50 MB por arquivo. Comprima ou use versão reduzida do PDF.

### OCR retorna texto vazio

**Causas:**
1. Imagem com muita compressão
2. Texto manuscrito (Vision API não reconhece bem)
3. Idioma não suportado (Vision suporta +100 idiomas)

**Solução:** Use PDFs de texto (não scaneado) ou imagens de alta qualidade.

### Gemini retorna erro de rate limit

**Solução:** Aguarde alguns minutos ou configure filas com Celery (próxima fase).

---

## 📚 Referências

- [Google Cloud Vision API Docs](https://cloud.google.com/vision/docs)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Supabase Storage Docs](https://supabase.com/docs/guides/storage)

---

## ✅ Checklist de Setup

- [ ] Projeto Google Cloud criado
- [ ] Vision API habilitada
- [ ] Service Account criado com chave JSON
- [ ] Gemini API key obtida
- [ ] `.env` preenchido com chaves
- [ ] Supabase configurado (opcional)
- [ ] Dependências Python instaladas (`pip install -e .`)
- [ ] Servidor iniciado e respondendo
- [ ] Teste de upload bem-sucedido

---

## 🚀 Próxima Etapa

Após configurar Fase B:
- ✅ Sistema pode fazer upload de livros
- ✅ OCR extrai texto automaticamente
- ✅ IA analisa estrutura pedagógica
- ✅ Planos de estudos são gerados
- ✅ Interações personalizadas são criadas

**Próximo:** Fase C — Orquestração Pedagógica (agendamento automático de interações).
