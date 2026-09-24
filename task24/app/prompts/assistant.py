import json
from typing import Any

from app.storage.database import get_connection


def save_trace(trace: dict[str, Any]) -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            INSERT OR REPLACE INTO traces (
                trace_id,
                request_type,
                model,
                prompt_version,
                status,
                start_time,
                end_time,
                total_duration_ms,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                estimated_cost_usd,
                error_category,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trace["trace_id"],
                trace["request_type"],
                trace["model"],
                trace["prompt_version"],
                trace["status"],
                trace["start_time"],
                trace["end_time"],
                trace["total_duration_ms"],
                trace["prompt_tokens"],
                trace["completion_tokens"],
                trace["total_tokens"],
                trace["estimated_cost_usd"],
                trace["error_category"],
                trace["error_message"],
            ),
        )

        connection.execute(
            """
            DELETE FROM spans
            WHERE trace_id = ?
            """,
            (trace["trace_id"],),
        )

        for span in trace["spans"]:
            connection.execute(
                """
                INSERT INTO spans (
                    span_id,
                    trace_id,
                    name,
                    status,
                    duration_ms,
                    attributes
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    span["span_id"],
                    span["trace_id"],
                    span["name"],
                    span["status"],
                    span["duration_ms"],
                    json.dumps(
                        span.get("attributes", {})
                    ),
                ),
            )

        connection.commit()

    finally:
        connection.close()


def _trace_from_row(
    connection,
    row,
) -> dict[str, Any]:
    spans = connection.execute(
        """
        SELECT
            span_id,
            trace_id,
            name,
            status,
            duration_ms,
            attributes
        FROM spans
        WHERE trace_id = ?
        ORDER BY id
        """,
        (row["trace_id"],),
    ).fetchall()

    return {
        "trace_id": row["trace_id"],
        "request_type": row["request_type"],
        "model": row["model"],
        "prompt_version": row["prompt_version"],
        "status": row["status"],
        "start_time": row["start_time"],
        "end_time": row["end_time"],
        "total_duration_ms": row["total_duration_ms"],
        "prompt_tokens": row["prompt_tokens"],
        "completion_tokens": row["completion_tokens"],
        "total_tokens": row["total_tokens"],
        "estimated_cost_usd": row["estimated_cost_usd"],
        "error_category": row["error_category"],
        "error_message": row["error_message"],
        "spans": [
            {
                "span_id": span["span_id"],
                "trace_id": span["trace_id"],
                "name": span["name"],
                "status": span["status"],
                "duration_ms": span["duration_ms"],
                "attributes": (
                    json.loads(span["attributes"])
                    if span["attributes"]
                    else {}
                ),
            }
            for span in spans
        ],
    }


def get_trace(
    trace_id: str,
) -> dict[str, Any] | None:
    connection = get_connection()

    try:
        row = connection.execute(
            """
            SELECT *
            FROM traces
            WHERE trace_id = ?
            """,
            (trace_id,),
        ).fetchone()

        if row is None:
            return None

        return _trace_from_row(
            connection,
            row,
        )

    finally:
        connection.close()


def list_traces(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    model: str | None = None,
    prompt_version: str | None = None,
) -> dict[str, Any]:
    page = max(page, 1)
    page_size = min(
        max(page_size, 1),
        100,
    )

    conditions = []
    parameters: list[Any] = []

    if status:
        conditions.append("status = ?")
        parameters.append(status)

    if model:
        conditions.append("model = ?")
        parameters.append(model)

    if prompt_version:
        conditions.append("prompt_version = ?")
        parameters.append(prompt_version)

    where = ""

    if conditions:
        where = "WHERE " + " AND ".join(conditions)

    connection = get_connection()

    try:
        total = connection.execute(
            f"""
            SELECT COUNT(*)
            FROM traces
            {where}
            """,
            parameters,
        ).fetchone()[0]

        offset = (page - 1) * page_size

        rows = connection.execute(
            f"""
            SELECT *
            FROM traces
            {where}
            ORDER BY start_time DESC
            LIMIT ? OFFSET ?
            """,
            [
                *parameters,
                page_size,
                offset,
            ],
        ).fetchall()

        results = [
            _trace_from_row(
                connection,
                row,
            )
            for row in rows
        ]

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "results": results,
        }

    finally:
        connection.close()


def get_failed_traces(
    error_category: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    return list_traces(
        page=page,
        page_size=page_size,
        status=None,
    ) if error_category is None else _get_failures_by_category(
        error_category,
        page,
        page_size,
    )


def _get_failures_by_category(
    error_category: str,
    page: int,
    page_size: int,
) -> dict[str, Any]:
    connection = get_connection()

    try:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size

        total = connection.execute(
            """
            SELECT COUNT(*)
            FROM traces
            WHERE error_category = ?
            """,
            (error_category,),
        ).fetchone()[0]

        rows = connection.execute(
            """
            SELECT *
            FROM traces
            WHERE error_category = ?
            ORDER BY start_time DESC
            LIMIT ? OFFSET ?
            """,
            (
                error_category,
                page_size,
                offset,
            ),
        ).fetchall()

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "results": [
                _trace_from_row(
                    connection,
                    row,
                )
                for row in rows
            ],
        }

    finally:
        connection.close()


def get_slow_traces(
    threshold_ms: float,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, Any]:
    connection = get_connection()

    try:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size

        total = connection.execute(
            """
            SELECT COUNT(*)
            FROM traces
            WHERE total_duration_ms >= ?
            """,
            (threshold_ms,),
        ).fetchone()[0]

        rows = connection.execute(
            """
            SELECT *
            FROM traces
            WHERE total_duration_ms >= ?
            ORDER BY total_duration_ms DESC
            LIMIT ? OFFSET ?
            """,
            (
                threshold_ms,
                page_size,
                offset,
            ),
        ).fetchall()

        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "results": [
                _trace_from_row(
                    connection,
                    row,
                )
                for row in rows
            ],
        }

    finally:
        connection.close()


def get_all_traces() -> list[dict[str, Any]]:
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT *
            FROM traces
            ORDER BY start_time ASC
            """
        ).fetchall()

        return [
            _trace_from_row(
                connection,
                row,
            )
            for row in rows
        ]

    finally:
        connection.close()