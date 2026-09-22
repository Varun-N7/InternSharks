import pytest

from app.reliability.errors import (
    RetryableError,
    NonRetryableError,
)
from app.reliability.retry import execute_with_retry
from app.reliability.timeout import execute_with_timeout


def test_retryable_failure_then_success():
    attempts = {"count": 0}

    def operation():
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise RetryableError("Temporary failure")

        return "success"

    result = execute_with_retry(
        operation,
        max_retries=3,
        base_delay=0,
    )

    assert result["success"] is True
    assert result["result"] == "success"
    assert result["attempt_count"] == 3


def test_non_retryable_failure_does_not_retry():
    attempts = {"count": 0}

    def operation():
        attempts["count"] += 1
        raise NonRetryableError("Employee not found")

    result = execute_with_retry(
        operation,
        max_retries=3,
        base_delay=0,
    )

    assert result["success"] is False
    assert result["retryable"] is False
    assert result["attempt_count"] == 1


def test_retry_exhaustion():
    attempts = {"count": 0}

    def operation():
        attempts["count"] += 1
        raise RetryableError("Service unavailable")

    result = execute_with_retry(
        operation,
        max_retries=3,
        base_delay=0,
    )

    assert result["success"] is False
    assert result["retryable"] is True
    assert result["retries_exhausted"] is True
    assert result["attempt_count"] == 3


def test_timeout():
    import time

    def slow_operation():
        time.sleep(2)
        return "finished"

    with pytest.raises(RetryableError):
        execute_with_timeout(
            slow_operation,
            timeout_seconds=0.1,
        )
def test_openrouter_retryable_failure(monkeypatch):
    from app.agent import runner
    from app.reliability.errors import RetryableError

    attempts = {"count": 0}

    def fake_openrouter_call(messages):
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise RetryableError("OpenRouter temporary failure")

        return {
            "role": "assistant",
            "content": "success",
        }

    monkeypatch.setattr(
        runner,
        "openrouter_call",
        fake_openrouter_call,
    )

    result = runner.call_openrouter_with_retry([])

    assert result["success"] is True
    assert result["attempt_count"] == 3
    assert result["result"]["content"] == "success"