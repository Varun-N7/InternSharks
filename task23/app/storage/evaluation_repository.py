from datetime import datetime, timezone
from typing import Any

from app.storage.database import get_connection


def save_evaluation_run(
    run_id: str,
    suite: str,
    result: dict[str, Any],
    model: str | None = None,
    prompt_version: str | None = None,
) -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT INTO evaluation_runs (
                run_id,
                suite,
                model,
                prompt_version,
                total_cases,
                passed,
                failed,
                pass_rate,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                suite,
                model,
                prompt_version,
                result["total_cases"],
                result["passed"],
                result["failed"],
                result["pass_rate"],
                datetime.now(timezone.utc).isoformat(),
            ),
        )

        for case in result["results"]:
            connection.execute(
                """
                INSERT INTO evaluation_case_results (
                    run_id,
                    case_id,
                    question,
                    actual_answer,
                    passed,
                    keyword_match,
                    non_empty,
                    refusal,
                    latency_ms
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    case["case_id"],
                    case["question"],
                    case["actual_answer"],
                    int(case["passed"]),
                    case["scores"]["keyword_match"],
                    int(case["checks"]["non_empty"]),
                    int(case["checks"]["refusal"]),
                    case["latency_ms"],
                ),
            )

        connection.commit()

    finally:
        connection.close()


def get_evaluation_run(
    run_id: str,
) -> dict[str, Any] | None:
    connection = get_connection()

    try:
        run = connection.execute(
            """
            SELECT *
            FROM evaluation_runs
            WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()

        if run is None:
            return None

        cases = connection.execute(
            """
            SELECT
                case_id,
                question,
                actual_answer,
                passed,
                keyword_match,
                non_empty,
                refusal,
                latency_ms
            FROM evaluation_case_results
            WHERE run_id = ?
            ORDER BY id
            """,
            (run_id,),
        ).fetchall()

        return {
            "run_id": run["run_id"],
            "suite": run["suite"],
            "model": run["model"],
            "prompt_version": run["prompt_version"],
            "total_cases": run["total_cases"],
            "passed": run["passed"],
            "failed": run["failed"],
            "pass_rate": run["pass_rate"],
            "created_at": run["created_at"],
            "results": [
                {
                    "case_id": case["case_id"],
                    "question": case["question"],
                    "actual_answer": case["actual_answer"],
                    "passed": bool(case["passed"]),
                    "scores": {
                        "keyword_match": case["keyword_match"],
                    },
                    "checks": {
                        "non_empty": bool(case["non_empty"]),
                        "refusal": bool(case["refusal"]),
                    },
                    "latency_ms": case["latency_ms"],
                }
                for case in cases
            ],
        }

    finally:
        connection.close()


def get_failed_cases(
    run_id: str,
) -> list[dict[str, Any]]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                case_id,
                question,
                actual_answer,
                passed,
                keyword_match,
                non_empty,
                refusal,
                latency_ms
            FROM evaluation_case_results
            WHERE run_id = ?
              AND passed = 0
            ORDER BY id
            """,
            (run_id,),
        ).fetchall()

        return [
            {
                "case_id": row["case_id"],
                "question": row["question"],
                "actual_answer": row["actual_answer"],
                "passed": bool(row["passed"]),
                "scores": {
                    "keyword_match": row["keyword_match"],
                },
                "checks": {
                    "non_empty": bool(row["non_empty"]),
                    "refusal": bool(row["refusal"]),
                },
                "latency_ms": row["latency_ms"],
            }
            for row in rows
        ]

    finally:
        connection.close()