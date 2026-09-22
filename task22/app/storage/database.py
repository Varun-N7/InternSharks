import json
import sqlite3

from app.config import DATABASE_PATH


def get_connection():
    connection = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False
    )
    connection.row_factory = sqlite3.Row
    return connection


def encode_json(value):
    return json.dumps(value)


def decode_json(value, default=None):
    if value is None:
        return default

    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS agent_runs (
            run_id TEXT PRIMARY KEY,
            goal TEXT NOT NULL,
            status TEXT NOT NULL,
            step_count INTEGER DEFAULT 0,
            messages TEXT DEFAULT '[]',
            pending_action TEXT,
            execution_trace TEXT DEFAULT '[]',
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS approvals (
            action_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            tool TEXT NOT NULL,
            arguments TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS action_execution (
            action_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            tool TEXT NOT NULL,
            arguments TEXT,
            idempotency_key TEXT,
            arguments_hash TEXT,
            status TEXT,
            attempt_count INTEGER DEFAULT 0,
            last_failure TEXT,
            previous_result TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )

    # ---------------------------------------------------------
    # Task 22 migration support
    # ---------------------------------------------------------
    # If the database was created by Task 21, some newer
    # Task 22 columns may not exist yet.
    # Add them without deleting existing data.

    cursor.execute("PRAGMA table_info(agent_runs)")
    agent_run_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    migrations = {
        "messages": "ALTER TABLE agent_runs ADD COLUMN messages TEXT DEFAULT '[]'",
        "pending_action": "ALTER TABLE agent_runs ADD COLUMN pending_action TEXT",
        "execution_trace": "ALTER TABLE agent_runs ADD COLUMN execution_trace TEXT DEFAULT '[]'",
        "step_count": "ALTER TABLE agent_runs ADD COLUMN step_count INTEGER DEFAULT 0",
        "created_at": "ALTER TABLE agent_runs ADD COLUMN created_at TEXT",
        "updated_at": "ALTER TABLE agent_runs ADD COLUMN updated_at TEXT",
    }

    for column, sql in migrations.items():
        if column not in agent_run_columns:
            cursor.execute(sql)

    # Make sure action_execution has all Task 22 fields too.
    cursor.execute("PRAGMA table_info(action_execution)")
    execution_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    execution_migrations = {
        "arguments": "ALTER TABLE action_execution ADD COLUMN arguments TEXT",
        "idempotency_key": "ALTER TABLE action_execution ADD COLUMN idempotency_key TEXT",
        "arguments_hash": "ALTER TABLE action_execution ADD COLUMN arguments_hash TEXT",
        "attempt_count": "ALTER TABLE action_execution ADD COLUMN attempt_count INTEGER DEFAULT 0",
        "last_failure": "ALTER TABLE action_execution ADD COLUMN last_failure TEXT",
        "previous_result": "ALTER TABLE action_execution ADD COLUMN previous_result TEXT",
        "created_at": "ALTER TABLE action_execution ADD COLUMN created_at TEXT",
        "updated_at": "ALTER TABLE action_execution ADD COLUMN updated_at TEXT",
    }

    for column, sql in execution_migrations.items():
        if column not in execution_columns:
            cursor.execute(sql)

    connection.commit()
    connection.close()