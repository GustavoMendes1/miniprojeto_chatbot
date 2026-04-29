import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.pdf_service import extrair_texto, dividir_em_chunks
from app.services.vector_service import indexar_chunks

router = APIRouter()

UPLOAD_DIR = Path("storage/pdfs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Apenas PDFs são aceitos")

    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    texto = extrair_texto(str(file_path))
    if not texto.strip():
        raise HTTPException(status_code=422, detail="Não foi possível extrair texto do PDF")

    chunks = dividir_em_chunks(texto)

    indexar_chunks(chunks)

    return {
        "filename": file.filename,
        "status": "indexado",
        "chunks": len(chunks)
    }