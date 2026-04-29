from openai import OpenAI
from app.services.vector_service import buscar_chunks
from app.core.config import OPENAI_API_KEY
import httpx


client = OpenAI(api_key=OPENAI_API_KEY,
                http_client=httpx.Client(verify=False))


def formatar_historico(history: list) -> list:
    return [
        {"role": msg["role"], "content": msg["content"]}
        for msg in history
    ]


def gerar_resposta(pergunta: str, history: list = []) -> str:

    # 1. Busca os chunks relevantes no FAISS
    chunks = buscar_chunks(pergunta)

    # 2. Monta o contexto com os chunks encontrados
    contexto = "\n\n".join([chunk.page_content for chunk in chunks])

    # 3. Monta o system prompt
    system_prompt = f"""Você é um assistente especializado em responder perguntas com base em documentos.

Use APENAS o conteúdo abaixo para responder. Se a resposta não estiver no documento, diga:
"Não encontrei essa informação no documento."

Documento:
{contexto}
"""

    # 4. Monta o histórico + pergunta atual
    mensagens = [{"role": "system", "content": system_prompt}]
    mensagens += formatar_historico(history)
    mensagens.append({"role": "user", "content": pergunta})

    # 5. Chama o OpenAI
    response = client.chat.completions.create(
        model="gpt-4o",
        max_tokens=1024,
        messages=mensagens
    )

    return response.choices[0].message.content