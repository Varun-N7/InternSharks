import json

from pydantic import BaseModel, ConfigDict, ValidationError


class EvaluationAnswer(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    confidence: float


def validate_structured_response(
    response: str,
) -> EvaluationAnswer:
    """
    Validate an AI response against the required
    evaluation JSON schema.
    """

    try:
        data = json.loads(response)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Invalid JSON response"
        ) from exc

    try:
        return EvaluationAnswer.model_validate(data)
    except ValidationError as exc:
        raise ValueError(
            "Invalid structured response"
        ) from exc