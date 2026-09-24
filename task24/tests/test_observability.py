from app.observability.metrics import (
    calculate_metrics,
    percentile,
)
from app.observability.spans import Span
from app.observability.tracing import Trace
from app.observability.pricing import calculate_cost


def test_trace_id_generated():
    trace = Trace()

    assert trace.trace_id.startswith(
        "trace_"
    )


def test_multiple_spans_same_trace():
    trace = Trace()

    first = trace.start_span(
        "prompt_build"
    )
    first.finish()

    second = trace.start_span(
        "retrieval"
    )
    second.finish()

    third = trace.start_span(
        "openrouter_call"
    )
    third.finish()

    assert len(trace.spans) == 3

    assert all(
        span.trace_id == trace.trace_id
        for span in trace.spans
    )


def test_duration_recorded():
    trace = Trace()

    span = trace.start_span(
        "test"
    )

    duration = span.finish()

    trace.finish()

    assert duration >= 0
    assert trace.total_duration_ms >= 0


def test_cost_calculation():
    cost = calculate_cost(
        "demo-model",
        1_000_000,
        1_000_000,
    )

    assert cost == 2.0


def test_missing_token_usage():
    cost = calculate_cost(
        "demo-model",
        None,
        None,
    )

    assert cost is None


def test_percentiles():
    values = [
        100,
        200,
        300,
        400,
        500,
    ]

    assert percentile(
        values,
        50,
    ) == 300

    assert percentile(
        values,
        95,
    ) == 480


def test_metrics_aggregation():
    traces = [
        {
            "status": "success",
            "model": "model-a",
            "total_duration_ms": 100,
            "total_tokens": 10,
            "estimated_cost_usd": 0.1,
        },
        {
            "status": "failed",
            "model": "model-a",
            "total_duration_ms": 200,
            "total_tokens": 20,
            "estimated_cost_usd": 0.2,
        },
        {
            "status": "success",
            "model": "model-b",
            "total_duration_ms": 300,
            "total_tokens": 30,
            "estimated_cost_usd": 0.3,
        },
    ]

    result = calculate_metrics(
        traces
    )

    assert result[
        "total_requests"
    ] == 3

    assert result[
        "successful_requests"
    ] == 2

    assert result[
        "failed_requests"
    ] == 1

    assert result[
        "total_tokens"
    ] == 60

    assert "model-a" in result[
        "by_model"
    ]

    assert "model-b" in result[
        "by_model"
    ]


def test_trace_failure():
    trace = Trace()

    trace.finish(
        status="timeout",
        error_category=(
            "OPENROUTER_TIMEOUT"
        ),
        error_message=(
            "OpenRouter request timed out"
        ),
    )

    result = trace.to_dict()

    assert result["status"] == "timeout"

    assert (
        result["error_category"]
        == "OPENROUTER_TIMEOUT"
    )


def test_prompt_version_and_model():
    trace = Trace()

    trace.model = "demo-model"
    trace.prompt_version = (
        "assistant_v1"
    )

    assert trace.model == "demo-model"

    assert (
        trace.prompt_version
        == "assistant_v1"
    )


def test_span_attributes():
    trace = Trace()

    span = trace.start_span(
        "prompt_build"
    )

    span.set_attribute(
        "prompt_length",
        25,
    )

    span.finish()

    assert (
        span.attributes[
            "prompt_length"
        ]
        == 25
    )