import time
from dataclasses import dataclass

import httpx

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)
from app.prompts.qa_v1 import (
    SYSTEM_PROMPT as V1_SYSTEM_PROMPT,
    build_prompt as build_v1_prompt,
)
from app.prompts.qa_v2 import (
    SYSTEM_PROMPT as V2_SYSTEM_PROMPT,
    build_prompt as build_v2_prompt,
)


@dataclass
class AIResponse:
    answer: str
    model: str
    prompt_version: str
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None


class AIService:
    def __init__(
        self,
        model: str = OPENROUTER_MODEL,
        api_key: str = OPENROUTER_API_KEY,
        base_url: str = OPENROUTER_BASE_URL,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def answer(
        self,
        question: str,
        context: str,
        prompt_version: str = "v1",
    ) -> AIResponse:

        if prompt_version == "v1":
            system_prompt = V1_SYSTEM_PROMPT
            user_prompt = build_v1_prompt(
                question,
                context,
            )

        elif prompt_version == "v2":
            system_prompt = V2_SYSTEM_PROMPT
            user_prompt = build_v2_prompt(
                question,
                context,
            )

        else:
            raise ValueError(
                f"Unsupported prompt version: {prompt_version}"
            )

        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured"
            )

        started = time.perf_counter()

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                "temperature": 0,
            },
            timeout=60.0,
        )

        latency_ms = round(
            (time.perf_counter() - started) * 1000,
            2,
        )

        response.raise_for_status()

        payload = response.json()

        choices = payload.get("choices", [])

        if not choices:
            raise RuntimeError(
                "OpenRouter response contained no choices"
            )

        message = choices[0].get("message", {})
        answer = message.get("content")

        if not isinstance(answer, str) or not answer.strip():
            raise RuntimeError(
                "OpenRouter returned an empty answer"
            )

        usage = payload.get("usage") or {}

        input_tokens = usage.get("prompt_tokens")
        output_tokens = usage.get("completion_tokens")
        total_tokens = usage.get("total_tokens")

        cost_usd = usage.get("cost")

        return AIResponse(
            answer=answer.strip(),
            model=payload.get("model", self.model),
            prompt_version=prompt_version,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost_usd=cost_usd,
        )