import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

from dataclasses import dataclass




@dataclass(frozen=True)
class Settings:
    openrouter_api_key: str = os.getenv(
        "OPENROUTER_API_KEY",
        "",
    )

    openrouter_model: str = os.getenv(
        "OPENROUTER_MODEL",
        "",
    )

    max_image_size_mb: int = int(
        os.getenv(
            "MAX_IMAGE_SIZE_MB",
            "10",
        )
    )

    request_timeout_seconds: float = float(
        os.getenv(
            "REQUEST_TIMEOUT_SECONDS",
            "30",
        )
    )

    max_retries: int = int(
        os.getenv(
            "MAX_RETRIES",
            "1",
        )
    )


settings = Settings()