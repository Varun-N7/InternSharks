import json

from app.storage.database import get_connection
from app.reliability.idempotency import (
    arguments_hash,
)


def create_execution_record(
    run_id,
    action_id,
    tool,
    idempotency_key,
    arguments,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO action_execution (
            action_id,
            run_id,
            tool,
            idempotency_key,
            arguments,
            status,
            attempt_count,
            last_failure,
            previous_result,
            arguments_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            action_id,
            run_id,
            tool,
            idempotency_key,
            json.dumps(arguments),
            "pending",
            0,
            None,
            None,
            arguments_hash(arguments),
        ),
    )

    connection.commit()
    connection.close()


def get_execution_record(action_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM action_execution
        WHERE action_id = ?
        """,
        (action_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if not row:
        return None

    return dict(row)


def get_execution_by_idempotency_key(
    idempotency_key,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM action_execution
        WHERE idempotency_key = ?
        """,
        (idempotency_key,),
    )

    row = cursor.fetchone()

    connection.close()

    if not row:
        return None

    return dict(row)


def update_attempt(
    action_id,
    attempt_count,
    last_failure=None,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE action_execution
        SET
            attempt_count = ?,
            last_failure = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE action_id = ?
        """,
        (
            attempt_count,
            last_failure,
            action_id,
        ),
    )

    connection.commit()
    connection.close()


def save_success(
    action_id,
    attempt_count,
    result,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE action_execution
        SET
            status = ?,
            attempt_count = ?,
            last_failure = NULL,
            previous_result = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE action_id = ?
        """,
        (
            "executed",
            attempt_count,
            json.dumps(result),
            action_id,
        ),
    )

    connection.commit()
    connection.close()


def save_failure(
    action_id,
    attempt_count,
    error,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE action_execution
        SET
            status = ?,
            attempt_count = ?,
            last_failure = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE action_id = ?
        """,
        (
            "failed",
            attempt_count,
            str(error),
            action_id,
        ),
    )

    connection.commit()
    connection.close()


def save_retrying(
    action_id,
    attempt_count,
    error,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE action_execution
        SET
            status = ?,
            attempt_count = ?,
            last_failure = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE action_id = ?
        """,
        (
            "retrying",
            attempt_count,
            str(error),
            action_id,
        ),
    )

    connection.commit()
    connection.close()


def mark_executed(
    action_id,
    result=None,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE action_execution
        SET
            status = ?,
            previous_result = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE action_id = ?
        """,
        (
            "executed",
            json.dumps(result)
            if result is not None
            else None,
            action_id,
        ),
    )

    connection.commit()
    connection.close()