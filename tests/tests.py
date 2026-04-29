import pytest
from unittest.mock import patch, MagicMock


# ─────────────────────────────────────────
# pdf_service
# ─────────────────────────────────────────

class TestPdfService:

    @patch("pdfplumber.open")
    def test_extrair_texto_sucesso(self, mock_pdf):
        pagina = MagicMock()
        pagina.extract_text.return_value = "Texto da página"
        mock_pdf.return_value.__enter__.return_value.pages = [pagina]

        from app.services.pdf_service import extrair_texto
        resultado = extrair_texto("fake.pdf")

        assert resultado == "Texto da página"

    @patch("pdfplumber.open")
    def test_extrair_texto_pagina_vazia(self, mock_pdf):
        pagina = MagicMock()
        pagina.extract_text.return_value = None
        mock_pdf.return_value.__enter__.return_value.pages = [pagina]

        from app.services.pdf_service import extrair_texto
        resultado = extrair_texto("fake.pdf")

        assert resultado == ""

    def test_dividir_em_chunks_retorna_lista(self):
        from app.services.pdf_service import dividir_em_chunks
        texto = "palavra " * 300
        chunks = dividir_em_chunks(texto)

        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_dividir_em_chunks_tamanho(self):
        from app.services.pdf_service import dividir_em_chunks
        texto = "palavra " * 300
        chunks = dividir_em_chunks(texto)

        for chunk in chunks:
            assert len(chunk.page_content) <= 600


# ─────────────────────────────────────────
# vector_service
# ─────────────────────────────────────────

class TestVectorService:

    @patch("app.services.vector_service.FAISS")
    @patch("app.services.vector_service.Path.exists", return_value=False)
    def test_indexar_chunks_cria_novo(self, mock_exists, mock_faiss):
        mock_store = MagicMock()
        mock_faiss.from_documents.return_value = mock_store

        from app.services.vector_service import indexar_chunks
        chunks = [MagicMock()]
        indexar_chunks(chunks)

        mock_faiss.from_documents.assert_called_once()

    @patch("app.services.vector_service.FAISS")
    @patch("app.services.vector_service.Path.exists", return_value=True)
    def test_indexar_chunks_adiciona_existente(self, mock_exists, mock_faiss):
        mock_store = MagicMock()
        mock_faiss.load_local.return_value = mock_store

        from app.services.vector_service import indexar_chunks
        chunks = [MagicMock()]
        indexar_chunks(chunks)

        mock_store.add_documents.assert_called_once_with(chunks)

    @patch("app.services.vector_service.FAISS")
    @patch("app.services.vector_service.Path.exists", return_value=True)
    def test_buscar_chunks_retorna_resultados(self, mock_exists, mock_faiss):
        mock_store = MagicMock()
        mock_store.similarity_search.return_value = ["chunk1", "chunk2"]
        mock_faiss.load_local.return_value = mock_store

        from app.services.vector_service import buscar_chunks
        resultado = buscar_chunks("qual é o produto?")

        assert len(resultado) == 2

    @patch("app.services.vector_service.Path.exists", return_value=False)
    def test_buscar_chunks_sem_index_levanta_erro(self, mock_exists):
        from app.services.vector_service import buscar_chunks

        with pytest.raises(FileNotFoundError):
            buscar_chunks("pergunta qualquer")


# ─────────────────────────────────────────
# rag_service
# ─────────────────────────────────────────

class TestRagService:

    @patch("app.services.rag_service.buscar_chunks")
    @patch("app.services.rag_service.client")
    def test_gerar_resposta_sucesso(self, mock_client, mock_buscar):
        chunk = MagicMock()
        chunk.page_content = "conteúdo do documento"
        mock_buscar.return_value = [chunk]

        mock_resposta = MagicMock()
        mock_resposta.choices[0].message.content = "Resposta gerada"
        mock_client.chat.completions.create.return_value = mock_resposta

        from app.services.rag_service import gerar_resposta
        resposta = gerar_resposta("O que é isso?")

        assert resposta == "Resposta gerada"

    @patch("app.services.rag_service.buscar_chunks")
    @patch("app.services.rag_service.client")
    def test_gerar_resposta_com_historico(self, mock_client, mock_buscar):
        chunk = MagicMock()
        chunk.page_content = "conteúdo"
        mock_buscar.return_value = [chunk]

        mock_resposta = MagicMock()
        mock_resposta.choices[0].message.content = "Resposta"
        mock_client.chat.completions.create.return_value = mock_resposta

        history = [
            {"role": "user", "content": "pergunta anterior"},
            {"role": "assistant", "content": "resposta anterior"}
        ]

        from app.services.rag_service import gerar_resposta
        gerar_resposta("nova pergunta", history)

        call_args = mock_client.chat.completions.create.call_args
        mensagens = call_args.kwargs["messages"]
        roles = [m["role"] for m in mensagens]

        assert "user" in roles
        assert "assistant" in roles


# ─────────────────────────────────────────
# rotas
# ─────────────────────────────────────────

class TestRotaUpload:

    def test_upload_arquivo_invalido(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post(
            "/api/upload",
            files={"file": ("test.txt", b"conteudo", "text/plain")}
        )

        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    @patch("app.services.pdf_service.pdfplumber.open")
    @patch("app.services.vector_service.FAISS")
    @patch("app.services.vector_service.Path.exists", return_value=False)
    def test_upload_pdf_sucesso(self, mock_exists, mock_faiss, mock_pdf):
        from fastapi.testclient import TestClient
        from app.main import app

        pagina = MagicMock()
        pagina.extract_text.return_value = "texto extraído do pdf"
        mock_pdf.return_value.__enter__.return_value.pages = [pagina]
        mock_faiss.from_documents.return_value = MagicMock()

        client = TestClient(app)
        response = client.post(
            "/api/upload",
            files={"file": ("test.pdf", b"%PDF conteudo", "application/pdf")}
        )

        assert response.status_code == 200
        assert response.json()["status"] == "indexado"


class TestRotaChat:

    @patch("app.services.rag_service.buscar_chunks")
    @patch("app.services.rag_service.client")
    def test_chat_sucesso(self, mock_client, mock_buscar):
        from fastapi.testclient import TestClient
        from app.main import app

        chunk = MagicMock()
        chunk.page_content = "conteúdo"
        mock_buscar.return_value = [chunk]

        mock_resposta = MagicMock()
        mock_resposta.choices[0].message.content = "Resposta do assistente"
        mock_client.chat.completions.create.return_value = mock_resposta

        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={"question": "O que é isso?", "history": []}
        )

        assert response.status_code == 200
        assert response.json()["answer"] == "Resposta do assistente"

    def test_chat_pergunta_vazia(self):
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.post(
            "/api/chat",
            json={"question": "   ", "history": []}
        )

        assert response.status_code == 400