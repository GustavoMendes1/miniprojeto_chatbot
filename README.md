# 📄 RAG API — Chat com PDF

Assistente conversacional que responde perguntas com base no conteúdo de documentos PDF, utilizando RAG (Retrieval-Augmented Generation).

---

## 🧠 Como funciona

```
Upload PDF → Extração de texto → Chunks → Embeddings → FAISS
                                                           ↓
                                          Pergunta → Busca semântica
                                                           ↓
                                               Contexto + GPT-4o → Resposta
```

---

## 🗂 Estrutura do projeto

```
rag-api/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       ├── upload.py
│   │       └── chat.py
│   ├── core/
│   │   └── config.py
│   ├── services/
│   │   ├── pdf_service.py
│   │   ├── vector_service.py
│   │   └── rag_service.py
│   └── models/
│       └── chat.py
│
├── frontend/
│   └── app.py
│
├── storage/
│   ├── pdfs/
│   └── vectordb/
│
├── .env
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalação

**1. Clone o repositório**
```bash
git clone https://github.com/GustavoMendes1/miniprojeto_chatbot.git
cd miniprojeto_chatbot
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**
```bash
cp .env.example .env
```

Edite o `.env` com sua chave da OpenAI:
```env
OPENAI_API_KEY=sua_chave_aqui
```

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
| Swagger | http://localhost:8000/docs |
| Frontend | http://localhost:7860 |

---

## 🔌 Rotas da API

### `POST /api/upload`
Recebe um PDF, extrai o texto, divide em chunks e indexa no FAISS.

**Request:** `multipart/form-data`
```
file: arquivo.pdf
```

**Response:**
```json
{
  "filename": "arquivo.pdf",
  "status": "indexado",
  "chunks": 42
}
```

---

### `POST /api/chat`
Recebe uma pergunta e retorna a resposta com base no documento indexado.

**Request:**
```json
{
  "question": "O que é o produto X?",
  "history": [
    { "role": "user", "content": "pergunta anterior" },
    { "role": "assistant", "content": "resposta anterior" }
  ]
}
```

**Response:**
```json
{
  "answer": "O produto X é..."
}
```

---

## 🛠 Stack

| Tecnologia | Função |
|---|---|
| FastAPI | Framework da API |
| Uvicorn | Servidor ASGI |
| pdfplumber | Extração de texto do PDF |
| LangChain | Orquestração do pipeline RAG |
| FAISS | Vector store local |
| OpenAI | Embeddings + GPT-4o |
| Gradio | Interface web |
| python-dotenv | Variáveis de ambiente |

---

## 🔒 Segurança

- Nunca suba o arquivo `.env` para o repositório
- O `.gitignore` já está configurado para ignorá-lo
- Sempre use o `.env.example` como referência com valores fictícios