def build_rag_prompt(question: str, context: str) -> str:
    return f"""
You are a helpful document assistant.

Answer the user's question using ONLY the information provided in the context below.

Rules:
- Do not use outside knowledge.
- Do not invent or guess information.
- If the answer cannot be found in the context, clearly say that the answer was not found in the document.
- Keep the answer clear and concise.

Context:
{context}

Question:
{question}

Answer:
""".strip()
