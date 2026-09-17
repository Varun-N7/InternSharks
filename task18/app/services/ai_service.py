import requests

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from app.prompts.assistant_prompt import TOOLS


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(messages, use_tools=True):

    if not OPENROUTER_API_KEY:
        raise ValueError("OpenRouter API key is not configured")

    if not OPENROUTER_MODEL:
        raise ValueError("OpenRouter model is not configured")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": OPENROUTER_MODEL,
        "messages": messages
    }

    if use_tools:
        data["tools"] = TOOLS
        data["tool_choice"] = "auto"
    else:
        data["tool_choice"] = "none"

    try:
        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=data,
            timeout=30
        )

    except requests.RequestException:
        raise ValueError("Could not connect to OpenRouter")

    if response.status_code == 401:
        raise ValueError("Invalid OpenRouter API key")

    if response.status_code == 429:
        raise ValueError("OpenRouter rate limit reached")

    if response.status_code >= 400:
        raise ValueError("OpenRouter request failed")

    try:
        result = response.json()
    except ValueError:
        raise ValueError("Invalid response from OpenRouter")

    if "choices" not in result or not result["choices"]:
        raise ValueError("Invalid AI response")

    return result