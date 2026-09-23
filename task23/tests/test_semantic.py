from app.evals.semantic import (
    evaluate_semantic_baseline,
    groundedness_score,
    relevance_score,
)


def test_grounded_answer_scores_high():
    score = groundedness_score(
        "Arun manages Project Nova.",
        "Project Nova is managed by Arun.",
    )

    assert score > 0.5


def test_unsupported_answer_scores_low():
    score = groundedness_score(
        "Project Nova uses PostgreSQL.",
        "Project Nova is managed by Arun and uses FastAPI.",
    )

    assert score < 0.5


def test_relevant_answer_scores_high():
    score = relevance_score(
        "Who manages Project Nova?",
        "Arun manages Project Nova.",
    )

    assert score > 0.5


def test_irrelevant_answer_scores_low():
    score = relevance_score(
        "Who manages Project Nova?",
        "Project Orion uses Django.",
    )

    assert score < 0.5


def test_semantic_baseline_returns_both_scores():
    result = evaluate_semantic_baseline(
        question="What framework does Project Nova use?",
        context="Project Nova uses FastAPI.",
        answer="Project Nova uses FastAPI.",
    )

    assert "groundedness" in result
    assert "relevance" in result
    assert result["groundedness"] > 0
    assert result["relevance"] > 0