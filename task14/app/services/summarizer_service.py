import json

import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.prompts.summarizer_prompt import SYSTEM_PROMPT, USER_PROMPT


def summarize_text(text: str, summary_type: str):

    prompt = USER_PROMPT.format(
        text=text,
        summary_type=summary_type,
    )

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": OPENROUTER_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0,
"response_format": {
    "type": "json_object"
},
        },
        timeout=60,
    )

    if response.status_code == 401:
        raise ValueError("Invalid OpenRouter API key")

    if response.status_code == 429:
        raise ValueError("OpenRouter rate limit reached")

    if response.status_code >= 400:
        raise ValueError("OpenRouter AI service failed")

    data = response.json()

    content = data["choices"][0]["message"]["content"]

    return json.loads(content)
