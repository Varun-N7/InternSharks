import os
from dataclasses import dataclass


OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    "",
)

OPENROUTER_BASE_URL = os.getenv(
    "OPENROUTER_BASE_URL",
    "https://openrouter.ai/api/v1",
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-4o-mini",
)


@dataclass(frozen=True)
class EvaluationThresholds:
    relevance: float = 0.5
    groundedness: float = 0.5
    correctness: float = 0.5


EVALUATION_THRESHOLDS = EvaluationThresholds()