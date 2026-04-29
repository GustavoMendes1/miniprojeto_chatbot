from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pdfplumber

def extrair_texto(file_path: str) -> str:
    texto = ""
    with pdfplumber.open(file_path) as pdf:
        for pagina in pdf.pages:
            texto += pagina.extract_text() or ""
    return texto

def dividir_em_chunks(texto: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.create_documents([texto])