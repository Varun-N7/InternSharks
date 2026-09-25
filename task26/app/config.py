import os

from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


class Settings:
    app_name: str = os.getenv(
        "APP_NAME",
        "Task 26 - Async AI Jobs",
    )

    worker_count: int = int(
        os.getenv(
            "WORKER_COUNT",
            "2",
        )
    )

    processing_delay_seconds: float = float(
        os.getenv(
            "PROCESSING_DELAY_SECONDS",
            "2",
        )
    )

    # OpenRouter configuration
    openrouter_api_key: str = os.getenv(
        "OPENROUTER_API_KEY",
        "",
    )

    openrouter_base_url: str = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1",
    )

    openrouter_model: str = os.getenv(
        "OPENROUTER_MODEL",
        "google/gemini-2.0-flash-001",
    )


settings = Settings()