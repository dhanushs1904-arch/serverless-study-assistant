"""SQLite Local Database Service
Manages local persistence for conversations, model versions, and MLOps simulation runs.
"""

import os
import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger("study_assistant.sqlite")


class SQLiteStore:
    """Thread-safe SQLite database manager for local execution."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        # Ensure parent directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize_tables()

    def get_connection(self) -> sqlite3.Connection:
        """Create a connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def initialize_tables(self) -> None:
        """Initialize database schema with parameterized setup."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    response_mode TEXT NOT NULL,
                    model_identifier TEXT NOT NULL,
                    duration_ms REAL NOT NULL,
                    status TEXT NOT NULL
                )
            """)

            # Model versions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS model_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    application_version TEXT NOT NULL,
                    model_provider TEXT NOT NULL,
                    model_identifier TEXT NOT NULL,
                    record_version TEXT NOT NULL UNIQUE,
                    change_reason TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    metadata_json TEXT
                )
            """)

            # Retrain runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS retrain_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL UNIQUE,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    previous_version TEXT NOT NULL,
                    new_version TEXT NOT NULL,
                    samples_evaluated INTEGER NOT NULL,
                    metrics_json TEXT NOT NULL,
                    artifact_path TEXT NOT NULL
                )
            """)

            # Seed initial model version if table is empty
            cursor.execute("SELECT COUNT(*) as count FROM model_versions")
            if cursor.fetchone()["count"] == 0:
                cursor.execute("""
                    INSERT INTO model_versions (
                        application_version, model_provider, model_identifier,
                        record_version, change_reason, last_updated, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    settings.APP_VERSION,
                    "Groq (LLaMA)" if settings.is_groq_configured else "Rule-Based Fallback",
                    settings.GROQ_MODEL if settings.is_groq_configured else "heuristic-academic-v1",
                    "v1.0.0-baseline",
                    "Initial project deployment for VIT Agile/DevOps coursework",
                    datetime.utcnow().isoformat() + "Z",
                    json.dumps({"stage": "baseline", "benchmarked": False})
                ))

            conn.commit()
            logger.info(f"SQLite database initialized at {self.db_path}")

    def insert_conversation(
        self,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        response_mode: str,
        model_identifier: str,
        duration_ms: float,
        status: str = "success"
    ) -> int:
        """Insert a conversation record using parameterized SQL."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO conversations (
                    conversation_id, timestamp, user_message,
                    assistant_response, response_mode, model_identifier,
                    duration_ms, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                conversation_id,
                timestamp,
                user_message,
                assistant_response,
                response_mode,
                model_identifier,
                duration_ms,
                status
            ))
            conn.commit()
            return cursor.lastrowid

    def get_recent_conversations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent conversation records for inspection."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_latest_model_version(self) -> Dict[str, Any]:
        """Retrieve the current active model version record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM model_versions ORDER BY id DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {
                "application_version": settings.APP_VERSION,
                "model_provider": "Rule-Based Fallback",
                "model_identifier": "heuristic-academic-v1",
                "record_version": "v1.0.0-baseline",
                "change_reason": "Default fallback",
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }

    def update_model_version(
        self,
        record_version: str,
        change_reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Record a new model version after retraining or configuration update."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO model_versions (
                    application_version, model_provider, model_identifier,
                    record_version, change_reason, last_updated, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                settings.APP_VERSION,
                "Groq (LLaMA)" if settings.is_groq_configured else "Rule-Based Fallback",
                settings.GROQ_MODEL if settings.is_groq_configured else "heuristic-academic-v1",
                record_version,
                change_reason,
                timestamp,
                json.dumps(metadata or {})
            ))
            conn.commit()

    def insert_retrain_run(
        self,
        run_id: str,
        status: str,
        previous_version: str,
        new_version: str,
        samples_evaluated: int,
        metrics: Dict[str, Any],
        artifact_path: str
    ) -> None:
        """Record an MLOps retraining simulation execution."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO retrain_runs (
                    run_id, timestamp, status, previous_version,
                    new_version, samples_evaluated, metrics_json, artifact_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                timestamp,
                status,
                previous_version,
                new_version,
                samples_evaluated,
                json.dumps(metrics),
                artifact_path
            ))
            conn.commit()

    def get_recent_retrain_runs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent retraining simulation runs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM retrain_runs ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                item["metrics"] = json.loads(item["metrics_json"])
                results.append(item)
            return results


# Global singleton instance for local storage
sqlite_store = SQLiteStore()
