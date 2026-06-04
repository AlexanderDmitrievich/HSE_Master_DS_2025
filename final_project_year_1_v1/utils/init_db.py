"""Инициализация SQLite. Запуск из корня проекта: python utils/init_db.py"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sqlite3

from utils.paths import DB_PATH


def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS training_results")
    conn.execute(
        """
        CREATE TABLE training_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            dataset TEXT NOT NULL,
            algorithm TEXT NOT NULL,
            train_size REAL NOT NULL,
            target_column TEXT NOT NULL,
            status TEXT NOT NULL,
            mae REAL,
            rmse REAL,
            r2 REAL,
            metrics_json TEXT,
            model_path TEXT,
            feature_columns TEXT,
            error_message TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            finished_at TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_training_status ON training_results(status)"
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_training_model_name ON training_results(model_name)"
    )
    conn.commit()
    conn.close()
    print(f"База инициализирована: {DB_PATH}")


if __name__ == "__main__":
    init_db()
