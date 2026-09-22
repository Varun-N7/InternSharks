from app.reliability.errors import RetryableError


def execute_with_timeout(function, timeout_seconds):
    """
    Execute a function with a maximum allowed time.

    A real timeout is treated as retryable.
    Exceptions raised by the function itself are propagated
    unchanged so retry.py can classify them correctly.
    """

    result = {
        "completed": False,
        "value": None,
        "error": None,
    }

    def target():
        try:
            result["value"] = function()
        except Exception as error:
            result["error"] = error
        finally:
            result["completed"] = True

    import threading

    thread = threading.Thread(target=target)
    thread.daemon = True
    thread.start()
    thread.join(timeout_seconds)

    # The function is still running after the timeout.
    if not result["completed"]:
        raise RetryableError(
            f"Operation timed out after {timeout_seconds} seconds"
        )


    if result["error"] is not None:
        raise result["error"]

    return result["value"]