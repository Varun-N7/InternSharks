from app.evals.deterministic import (
    evaluate_deterministic,
    keyword_match,
    non_empty_check,
    refusal_check,
)


def test_keyword_match_pass():
    score = keyword_match(
        "Project Nova is managed by Arun.",
        ["Arun"],
    )

    assert score == 1.0


def test_keyword_match_fail():
    score = keyword_match(
        "Project Nova uses FastAPI.",
        ["Arun"],
    )

    assert score == 0.0


def test_multiple_keywords():
    score = keyword_match(
        "Project Orion is managed by Priya and uses Django.",
        ["Priya", "Django"],
    )

    assert score == 1.0


def test_non_empty_pass():
    assert non_empty_check("Arun") is True


def test_non_empty_fail():
    assert non_empty_check("") is False


def test_refusal_pass():
    assert refusal_check(
        "The database information is not provided in the context.",
        True,
    ) is True


def test_refusal_fail():
    assert refusal_check(
        "Project Nova uses PostgreSQL.",
        True,
    ) is False


def test_normal_case_deterministic_evaluation():
    case = {
        "id": "eval_001",
        "expected_keywords": ["Arun"],
        "should_refuse": False,
    }

    result = evaluate_deterministic(
        case,
        "The project manager is Arun.",
    )

    assert result["keyword_match"] == 1.0
    assert result["non_empty"] is True
    assert result["refusal"] is True
    assert result["passed"] is True


def test_refusal_case_deterministic_evaluation():
    case = {
        "id": "eval_002",
        "expected_keywords": [],
        "should_refuse": True,
    }

    result = evaluate_deterministic(
        case,
        "The database information is not provided.",
    )

    assert result["keyword_match"] == 1.0
    assert result["refusal"] is True
    assert result["passed"] is True