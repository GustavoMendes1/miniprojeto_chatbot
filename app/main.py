from fastapi import FastAPI
from app.api.routes import upload
from app.api.routes import chat

app = FastAPI(title="RAG API")

app.include_router(upload.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok"}