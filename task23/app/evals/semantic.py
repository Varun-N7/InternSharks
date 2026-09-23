import re
from typing import Any


STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "was",
    "were",
    "and",
    "or",
    "but",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "by",
    "from",
    "uses",
    "use",
    "using",
    "has",
    "have",
    "does",
    "do",
    "project",
}


WORD_NORMALIZATION = {
    "manages": "manage",
    "managed": "manage",
    "managing": "manage",
    "uses": "use",
    "used": "use",
    "using": "use",
    "projects": "project",
}


def _normalize_token(token: str) -> str:
    return WORD_NORMALIZATION.get(token, token)


def _tokens(text: str) -> set[str]:
    raw_tokens = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        text.lower(),
    )

    return {
        _normalize_token(token)
        for token in raw_tokens
        if token not in STOP_WORDS
    }


def groundedness_score(
    answer: str,
    context: str,
) -> float:
    """
    Deterministic lexical groundedness baseline.

    This is intentionally simple. The final Task 23 semantic
    evaluation will use the LLM judge.
    """

    answer_tokens = _tokens(answer)
    context_tokens = _tokens(context)

    if not answer_tokens:
        return 0.0

    supported = answer_tokens & context_tokens
    unsupported = answer_tokens - context_tokens

    if not unsupported:
        return 1.0

    score = len(supported) / (
        len(supported) + 2 * len(unsupported)
    )

    return round(score, 4)


def relevance_score(
    question: str,
    answer: str,
) -> float:
    """
    Deterministic lexical relevance baseline.
    """

    question_tokens = _tokens(question)
    answer_tokens = _tokens(answer)

    if not question_tokens or not answer_tokens:
        return 0.0

    matched = question_tokens & answer_tokens

    return round(
        len(matched) / len(question_tokens),
        4,
    )


def evaluate_semantic_baseline(
    question: str,
    context: str,
    answer: str,
) -> dict[str, Any]:
    groundedness = groundedness_score(
        answer,
        context,
    )

    relevance = relevance_score(
        question,
        answer,
    )

    return {
        "groundedness": groundedness,
        "relevance": relevance,
    }