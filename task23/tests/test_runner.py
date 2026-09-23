from dataclasses import dataclass

from app.evals.runner import (
    evaluate_answer,
    summarize_evaluation,
)


@dataclass
class FakeJudgeResult:
    groundedness: float = 0.9
    relevance: float = 0.8
    reason: str = "Supported answer."
    model: str = "fake-model"
    latency_ms: float = 12.5
    input_tokens: int = 100
    output_tokens: int = 25
    total_tokens: int = 125
    cost_usd: float = 0.001


class FakeJudge:
    def evaluate(
        self,
        question: str,
        context: str,
        answer: str,
    ):
        return FakeJudgeResult()


def test_evaluate_without_judge():
    report = evaluate_answer(
        question="Who manages Project Nova?",
        context="Project Nova is managed by Arun.",
        answer="Arun manages Project Nova.",
    )

    assert report["question"] == (
        "Who manages Project Nova?"
    )

    assert report["answer"] == (
        "Arun manages Project Nova."
    )

    assert report["judge"] is None

    assert (
        report["deterministic"]["groundedness"]
        > 0.5
    )


def test_evaluate_with_judge():
    report = evaluate_answer(
        question="Who manages Project Nova?",
        context="Project Nova is managed by Arun.",
        answer="Arun manages Project Nova.",
        judge=FakeJudge(),
    )

    assert report["judge"] is not None

    assert (
        report["judge"]["groundedness"]
        == 0.9
    )

    assert (
        report["judge"]["relevance"]
        == 0.8
    )

    assert (
        report["judge"]["reason"]
        == "Supported answer."
    )

    assert (
        report["judge"]["model"]
        == "fake-model"
    )

    assert (
        report["judge"]["total_tokens"]
        == 125
    )


def test_summarize_without_judge():
    report = evaluate_answer(
        question="Who manages Project Nova?",
        context="Project Nova is managed by Arun.",
        answer="Arun manages Project Nova.",
    )

    summary = summarize_evaluation(report)

    assert (
        summary["deterministic_groundedness"]
        > 0.5
    )

    assert (
        summary["judge_available"]
        is False
    )


def test_summarize_with_judge():
    report = evaluate_answer(
        question="Who manages Project Nova?",
        context="Project Nova is managed by Arun.",
        answer="Arun manages Project Nova.",
        judge=FakeJudge(),
    )

    summary = summarize_evaluation(report)

    assert (
        summary["deterministic_groundedness"]
        > 0.5
    )

    assert (
        summary["deterministic_relevance"]
        >= 0.0
    )

    assert (
        summary["judge_available"]
        is True
    )

    assert (
        summary["judge_groundedness"]
        == 0.9
    )

    assert (
        summary["judge_relevance"]
        == 0.8
    )

    assert (
        summary["judge_reason"]
        == "Supported answer."
    )