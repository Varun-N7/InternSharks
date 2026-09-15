from fastapi import FastAPI

from app.routes.rag import router as rag_router


app = FastAPI(
    title="RAG Document Chat API",
    description="Simple RAG API using FastAPI, FAISS, Hugging Face embeddings, and OpenRouter.",
    version="1.0.0",
)


app.include_router(rag_router)


@app.get("/")
def root():
    return {
        "message": "API is running"
    }