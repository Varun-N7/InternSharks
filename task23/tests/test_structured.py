import pytest

from app.evals.structured import (
    validate_structured_response,
)


def test_valid_structured_response():
    result = validate_structured_response(
        """
        {
            "answer": "Arun",
            "confidence": 0.9
        }
        """
    )

    assert result.answer == "Arun"
    assert result.confidence == 0.9


def test_missing_field_fails():
    with pytest.raises(
        ValueError,
        match="Invalid structured response",
    ):
        validate_structured_response(
            """
            {
                "answer": "Arun"
            }
            """
        )


def test_wrong_field_type_fails():
    with pytest.raises(
        ValueError,
        match="Invalid structured response",
    ):
        validate_structured_response(
            """
            {
                "answer": "Arun",
                "confidence": "high"
            }
            """
        )


def test_extra_field_fails():
    with pytest.raises(
        ValueError,
        match="Invalid structured response",
    ):
        validate_structured_response(
            """
            {
                "answer": "Arun",
                "confidence": 0.9,
                "extra": "unexpected"
            }
            """
        )


def test_invalid_json_fails():
    with pytest.raises(
        ValueError,
        match="Invalid JSON response",
    ):
        validate_structured_response(
            "this is not json"
        )