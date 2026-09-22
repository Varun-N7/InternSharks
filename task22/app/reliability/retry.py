import time

from app.reliability.errors import is_retryable_error


def calculate_backoff(
    base_delay,
    retry_number,
):
    return base_delay * (
        2 ** retry_number
    )


def execute_with_retry(
    function,
    max_retries=3,
    base_delay=1,
    on_retry=None,
    on_attempt=None,
):
    """
    Execute a function with controlled retries.

    max_retries represents the maximum number
    of total attempts.

    Example:
        max_retries=3

        Attempt 1
        Attempt 2
        Attempt 3
    """

    attempt = 0

    while attempt < max_retries:

        attempt += 1

        if on_attempt:
            on_attempt(
                attempt=attempt,
            )

        try:
            result = function()

            return {
                "success": True,
                "result": result,
                "attempt_count": attempt,
                "retryable": False,
                "retries_exhausted": False,
            }

        except Exception as error:

            retryable = is_retryable_error(
                error
            )

            if not retryable:
                return {
                    "success": False,
                    "error": str(error),
                    "attempt_count": attempt,
                    "retryable": False,
                    "retries_exhausted": False,
                }

            if attempt >= max_retries:
                return {
                    "success": False,
                    "error": str(error),
                    "attempt_count": attempt,
                    "retryable": True,
                    "retries_exhausted": True,
                }

            delay = calculate_backoff(
                base_delay,
                attempt - 1,
            )

            if on_retry:
                on_retry(
                    attempt=attempt,
                    next_attempt=attempt + 1,
                    delay=delay,
                    error=str(error),
                )

            if delay > 0:
                time.sleep(delay)

    return {
        "success": False,
        "error": "Retry execution failed",
        "attempt_count": attempt,
        "retryable": True,
        "retries_exhausted": True,
    }