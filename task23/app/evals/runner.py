import time
from pathlib import Path
from typing import Any, Callable
import json

from app.evals.semantic import evaluate_semantic_baseline
from app.services.judge_service import JudgeService


def evaluate_answer(
    question: str,
    context: str,
    answer: str,
    judge: JudgeService | None = None,
) -> dict[str, Any]:
    deterministic = evaluate_semantic_baseline(
        question=question,
        context=context,
        answer=answer,
    )

    report: dict[str, Any] = {
        "question": question,
        "context": context,
        "answer": answer,
        "deterministic": deterministic,
        "judge": None,
    }

    if judge is not None:
        judge_result = judge.evaluate(
            question=question,
            context=context,
            answer=answer,
        )

        report["judge"] = {
            "groundedness": judge_result.groundedness,
            "relevance": judge_result.relevance,
            "reason": judge_result.reason,
            "model": judge_result.model,
            "latency_ms": judge_result.latency_ms,
            "input_tokens": judge_result.input_tokens,
            "output_tokens": judge_result.output_tokens,
            "total_tokens": judge_result.total_tokens,
            "cost_usd": judge_result.cost_usd,
        }

    return report


def summarize_evaluation(
    report: dict[str, Any],
) -> dict[str, Any]:
    deterministic = report.get("deterministic", {})
    judge = report.get("judge")

    summary = {
        "deterministic_groundedness": deterministic.get(
            "groundedness"
        ),
        "deterministic_relevance": deterministic.get(
            "relevance"
        ),
        "judge_available": judge is not None,
    }

    if judge is not None:
        summary.update(
            {
                "judge_groundedness": judge.get(
                    "groundedness"
                ),
                "judge_relevance": judge.get(
                    "relevance"
                ),
                "judge_reason": judge.get(
                    "reason"
                ),
            }
        )

    return summary


def run_evaluation(
    answer_provider: Callable[[dict[str, Any]], str],
) -> dict[str, Any]:
    dataset_path = (
        Path(__file__).resolve().parents[1]
        / "datasets"
        / "rag_basic.json"
    )

    with dataset_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        cases = json.load(file)

    results = []

    for case in cases:
        start = time.perf_counter()

        actual_answer = answer_provider(case)

        latency_ms = (
            time.perf_counter() - start
        ) * 1000

        question = case["question"]

        keywords = case.get("keywords", [])

        answer_lower = actual_answer.lower()

        if keywords:
            matched = sum(
                1
                for keyword in keywords
                if keyword.lower() in answer_lower
            )

            keyword_match = matched / len(keywords)
        else:
            keyword_match = 0.0

        non_empty = bool(
            actual_answer.strip()
        )

        refusal = any(
            phrase in answer_lower
            for phrase in (
                "not provided",
                "not available",
                "i don't know",
                "don't know",
                "cannot answer",
                "can't answer",
            )
        )

        should_refuse = case.get(
            "should_refuse",
            False,
        )

        if should_refuse:
            passed = non_empty and refusal
        else:
            passed = (
                non_empty
                and keyword_match >= 0.5
            )

        results.append(
            {
                "case_id": case["id"],
                "question": question,
                "actual_answer": actual_answer,
                "passed": passed,
                "scores": {
                    "keyword_match": keyword_match,
                },
                "checks": {
                    "non_empty": non_empty,
                    "refusal": refusal,
                },
                "latency_ms": latency_ms,
            }
        )

    total_cases = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    failed = total_cases - passed

    return {
        "total_cases": total_cases,
        "passed": passed,
        "failed": failed,
        "pass_rate": (
            passed / total_cases
            if total_cases
            else 0.0
        ),
        "results": results,
    }