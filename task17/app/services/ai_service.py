import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL


class InvalidAPIKeyError(Exception):
    pass


class RateLimitError(Exception):
    pass


class AIServiceError(Exception):
    pass


def generate_answer(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60,
        )
    except requests.RequestException:
        raise AIServiceError("AI service is unavailable")

    if response.status_code in (401, 403):
        raise InvalidAPIKeyError("Invalid OpenRouter API key")

    if response.status_code == 429:
        raise RateLimitError("AI service rate limit exceeded")

    if response.status_code >= 400:
        raise AIServiceError("AI model request failed")

    try:
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
    except (ValueError, KeyError, IndexError, TypeError):
        raise AIServiceError("Invalid response from AI service")

    if not answer or not answer.strip():
        raise AIServiceError("AI returned an empty response")

    return answer.strip()