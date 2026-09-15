import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.prompts.chat_prompt import SYSTEM_PROMPT


class InvalidAPIKeyError(Exception):
    pass


class RateLimitError(Exception):
    pass


class AIServiceError(Exception):
    pass


def get_ai_response(messages):

    try:
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
                    *messages,
                ],
                "temperature": 0.7,
            },
            timeout=60,
        )

    except requests.RequestException:
        raise AIServiceError("OpenRouter AI service failed")

    if response.status_code == 401:
        raise InvalidAPIKeyError("Invalid OpenRouter API key")

    if response.status_code == 429:
        raise RateLimitError("OpenRouter rate limit reached")

    if response.status_code >= 400:
        raise AIServiceError("OpenRouter AI service failed")

    try:
        data = response.json()
        content = data["choices"][0]["message"]["content"]

        if not content or not content.strip():
            raise AIServiceError("Empty AI response")

        return content.strip()

    except (ValueError, KeyError, IndexError, TypeError):
        raise AIServiceError("Invalid AI response")