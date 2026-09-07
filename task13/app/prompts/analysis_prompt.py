ANALYSIS_PROMPT = """
Analyze the user's text and return a structured JSON object.

The JSON must contain exactly these fields:

{{
    "summary": "A concise summary of the text",
    "category": "One of: blocker, update, request, question, other",
    "priority": "One of: low, medium, high",
    "sentiment": "One of: positive, neutral, negative",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Rules:
- Return valid JSON only.
- Do not include markdown.
- Do not include explanations outside the JSON.
- Keep the summary concise.
- Choose the most appropriate category.
- Keywords should be short and relevant.

Text to analyze:
{text}
"""