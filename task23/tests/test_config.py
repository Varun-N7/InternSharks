from app.config import EVALUATION_THRESHOLDS


def test_evaluation_thresholds_exist():
    assert 0.0 <= EVALUATION_THRESHOLDS.relevance <= 1.0
    assert 0.0 <= EVALUATION_THRESHOLDS.groundedness <= 1.0
    assert 0.0 <= EVALUATION_THRESHOLDS.correctness <= 1.0