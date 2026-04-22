# 📄 RAG API — Chat com contexto de PDF

> Assistente conversacional que responde perguntas com base no conteúdo de documentos PDF, utilizando a técnica de RAG (Retrieval-Augmented Generation).

Em vez de responder com base apenas no treinamento geral de um modelo de linguagem, este projeto busca informações em documentos específicos enviados pelo usuário e formula respostas fundamentadas nesse conteúdo.

---

## 📑 Índice

- [Como funciona](#-como-funciona)
- [Tecnologias utilizadas](#-tecnologias-utilizadas)
- [Configuração do ambiente](#-configuração-do-ambiente)
- [Rodando o projeto](#-rodando-o-projeto)
- [Exemplos de uso](#-exemplos-de-uso)
- [Testes automatizados](#-testes-automatizados)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Limitações e próximos passos](#-limitações-e-próximos-passos)
- [Créditos](#-créditos)
- [Licença](#-licença)

---

## 🧠 Como funciona

```
Upload PDF
    ↓
Extração de texto (pdfplumber)
    ↓
Divisão em chunks (LangChain RecursiveCharacterTextSplitter)
    ↓
Geração de embeddings (OpenAI text-embedding-ada-002)
    ↓
Armazenamento vetorial (FAISS)
    ↓
Pergunta do usuário → Busca semântica → Top-K chunks relevantes
    ↓
Prompt com contexto → GPT-4o → Resposta baseada no documento
```

---

## 🛠 Tecnologias utilizadas

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.8+ | Linguagem principal |
| FastAPI | latest | Framework da API REST |
| Uvicorn | latest | Servidor ASGI |
| pdfplumber | latest | Extração de texto de PDFs |
| LangChain | latest | Orquestração do pipeline RAG |
| FAISS | latest | Vector store local |
| OpenAI API | latest | Embeddings + GPT-4o para geração de respostas |
| Gradio | latest | Interface web do frontend |
| python-dotenv | latest | Gerenciamento de variáveis de ambiente |
| pytest | latest | Testes automatizados |

### Modelos de IA utilizados
- **text-embedding-ada-002** — geração de embeddings dos chunks e das perguntas
- **GPT-4o** — geração das respostas com base no contexto recuperado

### Assistentes de código
- **Claude (Anthropic)** — utilizado como assistente durante o desenvolvimento para estruturação do projeto, revisão de código e resolução de erros

---

## ⚙️ Configuração do ambiente

### Pré-requisitos
- Python 3.8 ou superior
- Conta na [OpenAI](https://platform.openai.com) com uma API key ativa

### 1. Clone o repositório

```bash
git clone https://github.com/GustavoMendes1/miniprojeto_chatbot.git
cd miniprojeto_chatbot
```

### 2. Crie e ative o ambiente virtual

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com sua chave:

```env
OPENAI_API_KEY=sua_chave_aqui
```

> ⚠️ Nunca suba o arquivo `.env` para o repositório. Ele já está no `.gitignore`.

---

## 🚀 Rodando o projeto

Abra dois terminais:

**Terminal 1 — Backend**
```bash
uvicorn app.main:app --reload
```

**Terminal 2 — Frontend**
```bash
python frontend/app.py
```

| Serviço | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger (documentação interativa) | http://localhost:8000/docs |
| Frontend Gradio | http://localhost:7860 |

---

## 💡 Exemplos de uso

### Via Frontend (Gradio)

1. Acesse `http://localhost:7860`
2. Na aba **Upload**, selecione um PDF e clique em **Enviar PDF**
3. Aguarde a confirmação de indexação
4. Na aba **Chat**, faça perguntas sobre o documento

### Via API (curl)

**Upload de PDF:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@seu_documento.pdf"
```

**Resposta esperada:**
```json
{
  "filename": "seu_documento.pdf",
  "status": "indexado",
  "chunks": 42
}
```

**Pergunta ao assistente:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Qual é o objetivo principal do documento?",
    "history": []
  }'
```

**Resposta esperada:**
```json
{
  "answer": "Com base no documento, o objetivo principal é..."
}
```

**Pergunta com histórico (follow-up):**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Pode explicar melhor?",
    "history": [
      { "role": "user", "content": "Qual é o objetivo principal?" },
      { "role": "assistant", "content": "O objetivo principal é..." }
    ]
  }'
```

### Via Swagger

Acesse `http://localhost:8000/docs` para testar todas as rotas diretamente no navegador, sem precisar de curl ou Postman.

---

## 🧪 Testes automatizados

### Instalação das dependências de teste

```bash
pip install pytest httpx
```

### Rodando os testes

```bash
pytest tests/ -v
```

### O que é testado

| Módulo | Testes |
|---|---|
| `pdf_service` | Extração de texto, página vazia, divisão em chunks |
| `vector_service` | Indexar novo, indexar existente, buscar chunks, erro sem índice |
| `rag_service` | Geração de resposta simples, geração com histórico |
| `routes/upload` | Arquivo inválido, upload com sucesso |
| `routes/chat` | Resposta com sucesso, pergunta vazia |

> Todos os testes utilizam `MagicMock` para simular chamadas à API da OpenAI, sem gerar custos reais.

---

## 🗂 Estrutura do projeto

```
rag-api/
├── app/
│   ├── main.py                  # Entrada da aplicação
│   ├── api/
│   │   └── routes/
│   │       ├── upload.py        # POST /api/upload
│   │       └── chat.py          # POST /api/chat
│   ├── core/
│   │   └── config.py            # Variáveis de ambiente
│   ├── services/
│   │   ├── pdf_service.py       # Extração e chunking do PDF
│   │   ├── vector_service.py    # Indexação e busca no FAISS
│   │   └── rag_service.py       # Orquestração RAG + chamada ao GPT
│   └── models/
│       └── chat.py              # Schemas Pydantic
│
├── frontend/
│   └── app.py                   # Interface Gradio
│
├── tests/
│   └── test_services.py         # Testes automatizados
│
├── storage/
│   ├── pdfs/                    # PDFs enviados
│   └── vectordb/                # Índice FAISS persistido
│
├── .env                         # Variáveis locais (não versionado)
├── .env.example                 # Modelo do .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚠️ Limitações e próximos passos

### Limitações atuais

- **Um documento por vez** — o sistema não diferencia perguntas entre múltiplos PDFs indexados simultaneamente
- **Sem autenticação** — a API não possui controle de acesso
- **Armazenamento local** — o índice FAISS e os PDFs ficam salvos localmente, sem suporte a ambientes distribuídos
- **Sem feedback de relevância** — o sistema não informa se os chunks encontrados eram realmente relevantes para a pergunta

### Próximos passos

- [ ] Suporte a múltiplos documentos com identificação por `document_id`
- [ ] Autenticação via JWT na API
- [ ] Migração para um vector store hospedado (ex: Pinecone, Weaviate)
- [ ] Endpoint `GET /documents` para listar PDFs indexados
- [ ] Endpoint `DELETE /documents/:id` para remover documentos
- [ ] Deploy via Docker
- [ ] Suporte a outros formatos além de PDF (`.docx`, `.txt`)
- [ ] Avaliação de qualidade das respostas com métricas RAG (faithfulness, relevance)

---

## 👤 Créditos

Desenvolvido por [Gustavo Mendes](https://github.com/GustavoMendes1) como miniprojeto de estudo sobre RAG (Retrieval-Augmented Generation).

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.