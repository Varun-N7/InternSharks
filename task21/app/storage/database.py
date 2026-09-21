import sqlite3
import json

from app.config import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_runs (
            run_id TEXT PRIMARY KEY,
            goal TEXT NOT NULL,
            status TEXT NOT NULL,
            step_count INTEGER NOT NULL,
            messages TEXT NOT NULL,
            pending_action TEXT,
            execution_trace TEXT NOT NULL
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS approvals (
            action_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            tool TEXT NOT NULL,
            arguments TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def encode_json(value):
    return json.dumps(value)


def decode_json(value, default):
    if not value:
        return default

    return json.loads(value)