import re
from typing import Any


def normalize_text(text: str) -> str:
    """Normalize text for simple deterministic comparisons."""
    return re.sub(r"\s+", " ", text.strip().lower())


def keyword_match(
    actual_answer: str,
    expected_keywords: list[str],
) -> float:
    """
    Return the fraction of expected keywords found in the answer.

    1.0 = all keywords found
    0.0 = none found
    """
    if not expected_keywords:
        return 1.0

    actual = normalize_text(actual_answer)

    matched = sum(
        1
        for keyword in expected_keywords
        if normalize_text(keyword) in actual
    )

    return matched / len(expected_keywords)


def non_empty_check(actual_answer: str) -> bool:
    """Check that the AI returned a non-empty answer."""
    return bool(actual_answer and actual_answer.strip())


def refusal_check(
    actual_answer: str,
    should_refuse: bool,
) -> bool:
    """
    Evaluate whether the model appropriately refused unsupported information.

    For a normal case, a non-empty answer passes this check.
    For a refusal case, look for language indicating the information
    is unavailable or cannot be determined from the context.
    """
    if not should_refuse:
        return non_empty_check(actual_answer)

    answer = normalize_text(actual_answer)

    refusal_phrases = [
        "not provided",
        "not available",
        "no information",
        "cannot determine",
        "can't determine",
        "cannot be determined",
        "can't be determined",
        "unknown",
        "insufficient information",
        "not mentioned",
        "not specified",
        "do not have enough information",
    ]

    return any(phrase in answer for phrase in refusal_phrases)


def evaluate_deterministic(
    case: dict[str, Any],
    actual_answer: str,
) -> dict[str, Any]:
    """Run all deterministic checks for one evaluation case."""
    keywords = case.get("expected_keywords", [])
    should_refuse = case.get("should_refuse", False)

    keyword_score = keyword_match(actual_answer, keywords)
    non_empty = non_empty_check(actual_answer)
    refusal_passed = refusal_check(actual_answer, should_refuse)

    passed = (
        non_empty
        and keyword_score >= 1.0
        and refusal_passed
    )

    return {
        "keyword_match": keyword_score,
        "non_empty": non_empty,
        "refusal": refusal_passed,
        "passed": passed,
    }