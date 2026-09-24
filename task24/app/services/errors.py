class AIServiceError(Exception):
    def __init__(
        self,
        message: str,
        category: str = "AI_ERROR",
        status: str = "failed",
    ):
        super().__init__(message)
        self.category = category
        self.status = status


class OpenRouterTimeoutError(AIServiceError):
    def __init__(self, message: str = "OpenRouter request timed out"):
        super().__init__(
            message,
            category="OPENROUTER_TIMEOUT",
            status="timeout",
        )


class OpenRouterRateLimitError(AIServiceError):
    def __init__(self, message: str = "OpenRouter rate limit"):
        super().__init__(
            message,
            category="OPENROUTER_RATE_LIMIT",
            status="rate_limited",
        )


class OpenRouterError(AIServiceError):
    def __init__(self, message: str = "OpenRouter request failed"):
        super().__init__(
            message,
            category="OPENROUTER_ERROR",
            status="failed",
        )