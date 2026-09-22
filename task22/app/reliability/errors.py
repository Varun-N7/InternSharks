class RetryableError(Exception):
    """An error that may succeed if the operation is retried."""


class NonRetryableError(Exception):
    """An error that should not be retried."""


def is_retryable_error(error):
    if isinstance(error, RetryableError):
        return True

    if isinstance(error, NonRetryableError):
        return False

    return False


def classify_error(error):
    if isinstance(error, RetryableError):
        return "retryable"

    if isinstance(error, NonRetryableError):
        return "non_retryable"

    return "non_retryable"