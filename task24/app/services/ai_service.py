import time

import httpx

from app.config import settings
from app.observability.pricing import calculate_cost
from app.observability.tracing import Trace
from app.services.errors import (
    OpenRouterError,
    OpenRouterRateLimitError,
    OpenRouterTimeoutError,
)


class AIService:
    def __init__(self):
        self.model = settings.openrouter_model

    def ask(
        self,
        message: str,
        trace: Trace,
    ) -> str:
        trace.model = self.model
        trace.prompt_version = settings.prompt_version

        prompt_span = trace.start_span(
            "prompt_build"
        )

        prompt = (
            "You are a helpful assistant.\n\n"
            f"User: {message}"
        )

        prompt_span.set_attribute(
            "prompt_length",
            len(prompt),
        )

        prompt_span.finish()

        if not settings.openrouter_api_key:
            llm_span = trace.start_span(
                "openrouter_call"
            )

            time.sleep(0.01)

            response = (
                f"Demo response for: {message}"
            )

            trace.prompt_tokens = len(prompt.split())
            trace.completion_tokens = len(response.split())
            trace.total_tokens = (
                trace.prompt_tokens + trace.completion_tokens
            )

            trace.estimated_cost_usd = calculate_cost(
                self.model,
                trace.prompt_tokens,
                trace.completion_tokens,
            )

            llm_span.set_attribute(
                "mock",
                True,
            )
            llm_span.finish()

            return response

        llm_span = trace.start_span(
            "openrouter_call"
        )

        try:
            response = httpx.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": (
                        f"Bearer "
                        f"{settings.openrouter_api_key}"
                    ),
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                },
                timeout=30.0,
            )

            if response.status_code == 429:
                raise OpenRouterRateLimitError()

            if response.status_code >= 400:
                raise OpenRouterError(
                    f"OpenRouter returned "
                    f"{response.status_code}"
                )

            payload = response.json()

            usage = payload.get(
                "usage"
            ) or {}

            trace.prompt_tokens = usage.get(
                "prompt_tokens"
            )

            trace.completion_tokens = usage.get(
                "completion_tokens"
            )

            trace.total_tokens = usage.get(
                "total_tokens"
            )

            if trace.total_tokens is None:
                if (
                    trace.prompt_tokens is not None
                    and trace.completion_tokens is not None
                ):
                    trace.total_tokens = (
                        trace.prompt_tokens
                        + trace.completion_tokens
                    )

            trace.estimated_cost_usd = (
                calculate_cost(
                    self.model,
                    trace.prompt_tokens,
                    trace.completion_tokens,
                )
            )

            llm_span.finish()

            return payload["choices"][0][
                "message"
            ]["content"]

        except httpx.TimeoutException as exc:
            llm_span.finish("timeout")
            raise OpenRouterTimeoutError() from exc

        except httpx.HTTPError as exc:
            llm_span.finish("failed")
            raise OpenRouterError(
                str(exc)
            ) from exc

        except (
            OpenRouterTimeoutError,
            OpenRouterRateLimitError,
            OpenRouterError,
        ):
            raise