import sqlite3

from app.config import settings


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(
        settings.database_path,
        check_same_thread=False,
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS traces (
                trace_id TEXT PRIMARY KEY,
                request_type TEXT NOT NULL,
                model TEXT,
                prompt_version TEXT,
                status TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_duration_ms REAL NOT NULL,
                prompt_tokens INTEGER,
                completion_tokens INTEGER,
                total_tokens INTEGER,
                estimated_cost_usd REAL,
                error_category TEXT,
                error_message TEXT
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS spans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                span_id TEXT NOT NULL,
                trace_id TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                attributes TEXT,
                FOREIGN KEY(trace_id)
                    REFERENCES traces(trace_id)
            )
            """
        )

        connection.commit()

    finally:
        connection.close()