import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str = os.getenv("OPENROUTER_API_KEY", "")
    openrouter_model: str = os.getenv(
        "OPENROUTER_MODEL",
        "demo-model",
    )
    log_ai_content: bool = os.getenv(
        "LOG_AI_CONTENT",
        "false",
    ).lower() == "true"
    slow_request_threshold_ms: float = float(
        os.getenv(
            "SLOW_REQUEST_THRESHOLD_MS",
            "3000",
        )
    )
    prompt_version: str = os.getenv(
        "PROMPT_VERSION",
        "assistant_v1",
    )
    database_path: str = os.getenv(
        "DATABASE_PATH",
        "observability.db",
    )


settings = Settings()


MODEL_PRICING = {
    "demo-model": {
        "input_per_million": 0.50,
        "output_per_million": 1.50,
    },
}


def get_model_pricing(model: str) -> dict[str, float]:
    return MODEL_PRICING.get(
        model,
        {
            "input_per_million": 0.0,
            "output_per_million": 0.0,
        },
    )