from app.config import get_model_pricing


def calculate_cost(
    model: str,
    prompt_tokens: int | None,
    completion_tokens: int | None,
) -> float | None:
    if (
        prompt_tokens is None
        or completion_tokens is None
    ):
        return None

    pricing = get_model_pricing(model)

    input_cost = (
        prompt_tokens
        / 1_000_000
        * pricing["input_per_million"]
    )

    output_cost = (
        completion_tokens
        / 1_000_000
        * pricing["output_per_million"]
    )

    return round(
        input_cost + output_cost,
        8,
    )