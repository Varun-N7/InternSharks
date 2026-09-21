from app.storage.database import (
    get_connection,
    encode_json,
    decode_json,
)


def save_run(run):
    connection = get_connection()

    connection.execute(
        """
        INSERT OR REPLACE INTO agent_runs
        (
            run_id,
            goal,
            status,
            step_count,
            messages,
            pending_action,
            execution_trace
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run["run_id"],
            run["goal"],
            run["status"],
            run["step_count"],
            encode_json(run["messages"]),
            encode_json(run["pending_action"])
            if run.get("pending_action")
            else None,
            encode_json(run["execution_trace"]),
        ),
    )

    connection.commit()
    connection.close()


def get_run(run_id):
    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM agent_runs WHERE run_id = ?",
        (run_id,),
    ).fetchone()

    connection.close()

    if not row:
        return None

    return {
        "run_id": row["run_id"],
        "goal": row["goal"],
        "status": row["status"],
        "step_count": row["step_count"],
        "messages": decode_json(row["messages"], []),
        "pending_action": decode_json(row["pending_action"], None),
        "execution_trace": decode_json(row["execution_trace"], []),
    }