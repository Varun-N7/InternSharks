import pytest

from app.services.ai_service import AIService


def test_missing_api_key_fails():
    service = AIService(api_key="")

    with pytest.raises(
        RuntimeError,
        match="OPENROUTER_API_KEY",
    ):
        service.answer(
            question="Who manages Project Nova?",
            context="Project Nova is managed by Arun.",
            prompt_version="v1",
        )


def test_invalid_prompt_version_fails():
    service = AIService(api_key="fake-key")

    with pytest.raises(
        ValueError,
        match="Unsupported prompt version",
    ):
        service.answer(
            question="Who manages Project Nova?",
            context="Project Nova is managed by Arun.",
            prompt_version="v3",
        )