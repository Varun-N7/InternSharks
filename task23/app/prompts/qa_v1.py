SYSTEM_PROMPT = """
You are a question-answering assistant.

Answer the user's question using only the supplied context.
Do not invent facts.
If the context does not contain enough information, clearly say that
the information is not provided.
Keep answers concise and factual.
""".strip()


def build_prompt(question: str, context: str) -> str:
    return f"""
Context:
{context}

Question:
{question}

Answer using only the context above.
""".strip()