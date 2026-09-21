from app.storage.database import get_connection


def save_action(action_id, run_id, tool, arguments, status="pending"):
    connection = get_connection()

    import json

    connection.execute(
        """
        INSERT OR REPLACE INTO approvals
        (
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
            json.dumps(arguments),
            status,
        ),
    )

    connection.commit()
    connection.close()


def get_action(action_id):
    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM approvals WHERE action_id = ?",
        (action_id,),
    ).fetchone()

    connection.close()

    if not row:
        return None

    import json

    return {
        "action_id": row["action_id"],
        "run_id": row["run_id"],
        "tool": row["tool"],
        "arguments": json.loads(row["arguments"]),
        "status": row["status"],
    }


def update_action_status(action_id, status):
    connection = get_connection()

    connection.execute(
        """
        UPDATE approvals
        SET status = ?
        WHERE action_id = ?
        """,
        (status, action_id),
    )

    connection.commit()
    connection.close()