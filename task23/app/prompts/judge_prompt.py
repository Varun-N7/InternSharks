SYSTEM_PROMPT = """
You are an evaluation judge for a grounded question-answering system.

Evaluate the supplied answer using ONLY the supplied context.

Return JSON only, with exactly these fields:

{
  "groundedness": 0.0,
  "relevance": 0.0,
  "reason": "short explanation"
}

Rules:

- groundedness measures whether the answer is supported by the context.
- relevance measures whether the answer directly addresses the question.
- Scores must be between 0.0 and 1.0.
- Do not reward information that is not supported by the context.
- Do not invent facts.
- Keep the reason concise.
""".strip()


def build_prompt(
    question: str,
    context: str,
    answer: str,
) -> str:
    return f"""
Question:
{question}

Context:
{context}

Answer:
{answer}

Evaluate the answer according to the rules.
Return JSON only.
""".strip()