import json
import sqlite3
from datetime import datetime, timezone

from utils.paths import DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def insert_pending(
    model_name: str,
    dataset: str,
    algorithm: str,
    train_size: float,
    target_column: str,
) -> int:
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO training_results (
            model_name, dataset, algorithm, train_size, target_column, status
        ) VALUES (?, ?, ?, ?, ?, 'pending')
        """,
        (model_name, dataset, algorithm, train_size, target_column),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def mark_done(
    result_id: int,
    mae: float,
    rmse: float,
    r2: float,
    metrics: dict,
    model_path: str,
    feature_columns: list[str],
) -> None:
    conn = get_connection()
    conn.execute(
        """
        UPDATE training_results
        SET status = 'done',
            mae = ?,
            rmse = ?,
            r2 = ?,
            metrics_json = ?,
            model_path = ?,
            feature_columns = ?,
            finished_at = ?
        WHERE id = ?
        """,
        (
            mae,
            rmse,
            r2,
            json.dumps(metrics),
            model_path,
            json.dumps(feature_columns),
            _now(),
            result_id,
        ),
    )
    conn.commit()
    conn.close()


def mark_failed(result_id: int, error_message: str) -> None:
    conn = get_connection()
    conn.execute(
        """
        UPDATE training_results
        SET status = 'failed',
            error_message = ?,
            finished_at = ?
        WHERE id = ?
        """,
        (error_message, _now(), result_id),
    )
    conn.commit()
    conn.close()


def model_name_exists(model_name: str) -> bool:
    conn = get_connection()
    row = conn.execute(
        "SELECT 1 FROM training_results WHERE model_name = ? LIMIT 1",
        (model_name,),
    ).fetchone()
    conn.close()
    return row is not None


def fetch_results(status: str | None = None) -> list[dict]:
    conn = get_connection()
    if status:
        rows = conn.execute(
            """
            SELECT * FROM training_results
            WHERE status = ?
            ORDER BY id DESC
            """,
            (status,),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM training_results ORDER BY id DESC"
        ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_result(result_id: int) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM training_results WHERE id = ?",
        (result_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def fetch_model_by_name(model_name: str) -> dict | None:
    conn = get_connection()
    row = conn.execute(
        """
        SELECT * FROM training_results
        WHERE model_name = ? AND status = 'done'
        ORDER BY id DESC
        LIMIT 1
        """,
        (model_name,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
