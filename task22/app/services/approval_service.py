import uuid

from app.storage.database import get_connection
from app.reliability.idempotency import (
    build_idempotency_key,
)
from app.storage.action_repository import (
    create_execution_record,
    get_execution_record,
    get_execution_by_idempotency_key,
    mark_executed as mark_execution_executed,
)


def create_action(
    run_id,
    tool,
    arguments,
):
    action_id = "action_" + uuid.uuid4().hex[:10]

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO approvals (
            action_id,
            run_id,
            tool,
            arguments,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            action_id,
            run_id,
            tool,
            __import__("json").dumps(arguments),
            "pending",
        ),
    )

    connection.commit()
    connection.close()

    idempotency_key = build_idempotency_key(
        run_id,
        action_id,
    )

    create_execution_record(
        run_id=run_id,
        action_id=action_id,
        tool=tool,
        idempotency_key=idempotency_key,
        arguments=arguments,
    )

    return action_id


def get_action(action_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM approvals
        WHERE action_id = ?
        """,
        (action_id,),
    )

    row = cursor.fetchone()

    connection.close()

    if not row:
        return None

    data = dict(row)

    try:
        data["arguments"] = __import__(
            "json"
        ).loads(data["arguments"])
    except Exception:
        data["arguments"] = {}

    return data


def get_execution(action_id):
    return get_execution_record(action_id)


def get_execution_by_key(idempotency_key):
    return get_execution_by_idempotency_key(
        idempotency_key
    )


def mark_approved(action_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE approvals
        SET status = ?
        WHERE action_id = ?
        """,
        (
            "approved",
            action_id,
        ),
    )

    connection.commit()
    connection.close()


def mark_rejected(action_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE approvals
        SET status = ?
        WHERE action_id = ?
        """,
        (
            "rejected",
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
        UPDATE approvals
        SET status = ?
        WHERE action_id = ?
        """,
        (
            "executed",
            action_id,
        ),
    )

    connection.commit()
    connection.close()

    mark_execution_executed(
        action_id,
        result=result,
    )