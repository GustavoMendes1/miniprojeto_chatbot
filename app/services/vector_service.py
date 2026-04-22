from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from app.core.config import OPENAI_API_KEY
import httpx

VECTORDB_DIR = "storage/vectordb"
Path(VECTORDB_DIR).mkdir(parents=True, exist_ok=True)

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY,
                              http_client=httpx.Client(verify=False))


def indexar_chunks(chunks):
    # Se já existe uma base, carrega e adiciona
    index_path = Path(VECTORDB_DIR) / "index.faiss"

    if index_path.exists():
        vectorstore = FAISS.load_local(
            VECTORDB_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
        vectorstore.add_documents(chunks)
    else:
        # Cria uma base nova
        vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(VECTORDB_DIR)


def buscar_chunks(pergunta: str, k: int = 4):
    index_path = Path(VECTORDB_DIR) / "index.faiss"

    if not index_path.exists():
        raise FileNotFoundError("Nenhum documento indexado ainda.")

    vectorstore = FAISS.load_local(
        VECTORDB_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore.similarity_search(pergunta, k=k)