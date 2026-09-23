import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent.parent / "evaluation.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluation_runs (
                run_id TEXT PRIMARY KEY,
                suite TEXT NOT NULL,
                model TEXT,
                prompt_version TEXT,
                total_cases INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                failed INTEGER NOT NULL,
                pass_rate REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS evaluation_case_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                case_id TEXT NOT NULL,
                question TEXT NOT NULL,
                actual_answer TEXT NOT NULL,
                passed INTEGER NOT NULL,
                keyword_match REAL NOT NULL,
                non_empty INTEGER NOT NULL,
                refusal INTEGER NOT NULL,
                latency_ms REAL NOT NULL,
                FOREIGN KEY (run_id)
                    REFERENCES evaluation_runs(run_id)
            )
            """
        )

        connection.commit()

    finally:
        connection.close()