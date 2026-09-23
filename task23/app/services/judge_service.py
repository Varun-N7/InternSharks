import json
import time
from dataclasses import dataclass

import httpx

from app.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_BASE_URL,
    OPENROUTER_MODEL,
)
from app.prompts.judge_prompt import (
    SYSTEM_PROMPT,
    build_prompt,
)


@dataclass
class JudgeResult:
    groundedness: float
    relevance: float
    reason: str
    model: str
    latency_ms: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None


class JudgeService:
    def __init__(
        self,
        model: str = OPENROUTER_MODEL,
        api_key: str = OPENROUTER_API_KEY,
        base_url: str = OPENROUTER_BASE_URL,
    ):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def evaluate(
        self,
        question: str,
        context: str,
        answer: str,
    ) -> JudgeResult:

        if not self.api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not configured"
            )

        user_prompt = build_prompt(
            question,
            context,
            answer,
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
                        "content": SYSTEM_PROMPT,
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
                "Judge response contained no choices"
            )

        content = (
            choices[0]
            .get("message", {})
            .get("content")
        )

        if not isinstance(content, str):
            raise RuntimeError(
                "Judge response contained no content"
            )

        result = self._parse_result(content)

        usage = payload.get("usage") or {}

        result.model = payload.get(
            "model",
            self.model,
        )

        result.latency_ms = latency_ms
        result.input_tokens = usage.get(
            "prompt_tokens"
        )
        result.output_tokens = usage.get(
            "completion_tokens"
        )
        result.total_tokens = usage.get(
            "total_tokens"
        )
        result.cost_usd = usage.get("cost")

        return result

    @staticmethod
    def _parse_result(content: str) -> JudgeResult:
        content = content.strip()

        # Handle accidental markdown fences.
        if content.startswith("```"):
            lines = content.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Judge returned invalid JSON"
            ) from exc

        groundedness = data.get("groundedness")
        relevance = data.get("relevance")
        reason = data.get("reason")

        if not isinstance(groundedness, (int, float)):
            raise RuntimeError(
                "Judge groundedness is invalid"
            )

        if not isinstance(relevance, (int, float)):
            raise RuntimeError(
                "Judge relevance is invalid"
            )

        if not isinstance(reason, str):
            raise RuntimeError(
                "Judge reason is invalid"
            )

        groundedness = float(groundedness)
        relevance = float(relevance)

        if not 0.0 <= groundedness <= 1.0:
            raise RuntimeError(
                "Judge groundedness must be between 0 and 1"
            )

        if not 0.0 <= relevance <= 1.0:
            raise RuntimeError(
                "Judge relevance must be between 0 and 1"
            )

        return JudgeResult(
            groundedness=groundedness,
            relevance=relevance,
            reason=reason,
            model="",
            latency_ms=0.0,
        )