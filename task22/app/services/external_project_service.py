from app.reliability.errors import RetryableError, NonRetryableError


# Tracks temporary failures for each project during the current process.
# First temporary_failure call fails; the next one succeeds.
temporary_failure_attempts = {}


def get_external_project_status(
    project_id: int,
    failure_mode: str = "success"
):
    """
    Simulated external project service.

    failure_mode:
    - success
    - temporary_failure
    - permanent_failure
    - timeout
    """

    if failure_mode == "success":
        return {
            "project_id": project_id,
            "external_status": "healthy",
            "source": "simulated_external_service",
        }

    if failure_mode == "temporary_failure":
        attempts = temporary_failure_attempts.get(project_id, 0) + 1
        temporary_failure_attempts[project_id] = attempts

        if attempts == 1:
            raise RetryableError(
                "Temporary external service failure"
            )

        return {
            "project_id": project_id,
            "external_status": "healthy",
            "source": "simulated_external_service",
            "recovered_after_retry": True,
        }

    if failure_mode == "permanent_failure":
        raise NonRetryableError(
            "Permanent external service failure"
        )

    if failure_mode == "timeout":
        import time

        time.sleep(10)

        return {
            "project_id": project_id,
            "external_status": "healthy",
            "source": "simulated_external_service",
        }

    raise NonRetryableError(
        f"Unknown failure mode: {failure_mode}"
    )