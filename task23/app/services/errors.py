class AIServiceError(Exception):
    """Base AI provider error."""


class AIConfigurationError(AIServiceError):
    """Missing or invalid provider configuration."""


class AIProviderError(AIServiceError):
    """Provider returned an unsuccessful response."""


class AIResponseError(AIServiceError):
    """Provider returned an unusable response."""