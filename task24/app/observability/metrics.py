from statistics import mean


def percentile(
    values: list[float],
    percentage: float,
) -> float:
    if not values:
        return 0.0

    values = sorted(values)

    if len(values) == 1:
        return float(values[0])

    position = (
        percentage
        / 100
        * (len(values) - 1)
    )

    lower = int(position)
    upper = min(
        lower + 1,
        len(values) - 1,
    )

    fraction = position - lower

    return (
        values[lower]
        + (
            values[upper]
            - values[lower]
        )
        * fraction
    )


def calculate_metrics(
    traces: list[dict],
) -> dict:
    total = len(traces)

    successful = sum(
        trace["status"] == "success"
        for trace in traces
    )

    failed = sum(
        trace["status"] == "failed"
        for trace in traces
    )

    timeout = sum(
        trace["status"] == "timeout"
        for trace in traces
    )

    latencies = [
        float(trace["total_duration_ms"])
        for trace in traces
    ]

    total_tokens = sum(
        trace["total_tokens"] or 0
        for trace in traces
    )

    total_cost = sum(
        trace["estimated_cost_usd"] or 0
        for trace in traces
    )

    by_model: dict[str, dict] = {}

    for trace in traces:
        model = trace["model"] or "unknown"

        if model not in by_model:
            by_model[model] = {
                "requests": 0,
                "successful": 0,
                "failed": 0,
                "average_latency_ms": 0.0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
            }

        data = by_model[model]

        data["requests"] += 1

        if trace["status"] == "success":
            data["successful"] += 1

        if trace["status"] in {
            "failed",
            "timeout",
            "rate_limited",
        }:
            data["failed"] += 1

        data["total_tokens"] += (
            trace["total_tokens"] or 0
        )

        data["total_cost_usd"] += (
            trace["estimated_cost_usd"] or 0
        )

    for model, data in by_model.items():
        model_latencies = [
            float(trace["total_duration_ms"])
            for trace in traces
            if (trace["model"] or "unknown") == model
        ]

        data["average_latency_ms"] = round(
            mean(model_latencies),
            3,
        ) if model_latencies else 0.0

        data["total_cost_usd"] = round(
            data["total_cost_usd"],
            8,
        )

    return {
        "total_requests": total,
        "successful_requests": successful,
        "failed_requests": failed,
        "timeout_requests": timeout,
        "average_latency_ms": round(
            mean(latencies),
            3,
        ) if latencies else 0.0,
        "p50_latency_ms": round(
            percentile(latencies, 50),
            3,
        ),
        "p95_latency_ms": round(
            percentile(latencies, 95),
            3,
        ),
        "total_tokens": total_tokens,
        "total_cost_usd": round(
            total_cost,
            8,
        ),
        "by_model": by_model,
    }