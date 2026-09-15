import uuid

from app.prompts.rag_prompt import build_rag_prompt
from app.services.ai_service import generate_answer
from app.services.embedding_service import embedding_service
from app.storage.vector_store import vector_store
from app.utils.file_parser import extract_text
from app.utils.text_chunker import chunk_text


def upload_document(file_name: str, file_content: bytes):
    text = extract_text(file_name, file_content)

    chunks = chunk_text(text)

    embeddings = embedding_service.create_embeddings(chunks)

    document_id = uuid.uuid4().hex

    vector_store.add_document(
        document_id=document_id,
        file_name=file_name,
        chunks=chunks,
        embeddings=embeddings,
    )

    return {
        "document_id": document_id,
        "file_name": file_name,
        "chunks_created": len(chunks),
    }


def ask_question(
    document_id: str,
    question: str,
    top_k: int = 3,
):
    if not vector_store.document_exists(document_id):
        raise ValueError("Document not found")

    question_embedding = embedding_service.create_embeddings(
        [question]
    )[0]

    relevant_chunks = vector_store.search(
        document_id=document_id,
        query_embedding=question_embedding,
        top_k=top_k,
    )

    if not relevant_chunks:
        raise ValueError("No relevant information found")

    context = "\n\n---\n\n".join(relevant_chunks)

    prompt = build_rag_prompt(
        question=question,
        context=context,
    )

    answer = generate_answer(prompt)

    return {
        "document_id": document_id,
        "question": question,
        "answer": answer,
    }


def get_document(document_id: str):
    document = vector_store.get_document(document_id)

    if not document:
        raise ValueError("Document not found")

    return {
        "document_id": document_id,
        "file_name": document["file_name"],
        "chunks_created": len(document["chunks"]),
    }