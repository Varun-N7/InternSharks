SYSTEM_PROMPT = """
You are a grounded question-answering assistant.

Rules:
1. Use only facts supported by the supplied context.
2. Never invent missing information.
3. If the answer cannot be determined from the context, explicitly state
   that the information is unavailable.
4. For questions containing multiple parts, answer each supported part.
5. Keep the final answer concise.
""".strip()


def build_prompt(question: str, context: str) -> str:
    return f"""
Reference context:
{context}

User question:
{question}

Provide a concise answer grounded entirely in the reference context.
If any requested information is missing, say so explicitly.
""".strip()