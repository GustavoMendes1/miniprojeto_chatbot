from fastapi import APIRouter, HTTPException
from app.models.chat import ChatRequest, ChatResponse
from app.services.rag_service import gerar_resposta

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Pergunta não pode ser vazia")

    try:
        history = [msg.model_dump() for msg in request.history]
        answer = gerar_resposta(request.question, history)
        return ChatResponse(answer=answer)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Nenhum documento indexado. Faça upload de um PDF primeiro.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))