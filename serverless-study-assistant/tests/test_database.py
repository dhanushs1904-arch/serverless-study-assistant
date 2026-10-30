"""SQLite Database Persistence Tests
"""

import os
from pathlib import Path
from app.database.sqlite_store import SQLiteStore


def test_sqlite_table_initialization(tmp_path):
    """Test that SQLite initializes tables without errors."""
    db_file = tmp_path / "test_init.db"
    store = SQLiteStore(str(db_file))
    assert Path(db_file).exists()

    latest = store.get_latest_model_version()
    assert latest is not None
    assert latest["record_version"] == "v1.0.0-baseline"


def test_sqlite_insert_and_retrieve_conversation(tmp_path):
    """Test inserting and retrieving conversation records."""
    db_file = tmp_path / "test_conv.db"
    store = SQLiteStore(str(db_file))

    row_id = store.insert_conversation(
        conversation_id="conv-test-101",
        user_message="Explain virtual memory paging",
        assistant_response="Virtual memory paging maps virtual pages to physical frames.",
        response_mode="fallback",
        model_identifier="heuristic-academic-v1",
        duration_ms=45.2,
        status="success"
    )
    assert row_id > 0

    records = store.get_recent_conversations(limit=10)
    assert len(records) == 1
    rec = records[0]
    assert rec["conversation_id"] == "conv-test-101"
    assert rec["user_message"] == "Explain virtual memory paging"
    assert rec["response_mode"] == "fallback"
    assert rec["duration_ms"] == 45.2


def test_sqlite_model_version_update(tmp_path):
    """Test updating and reading active model version."""
    db_file = tmp_path / "test_version.db"
    store = SQLiteStore(str(db_file))

    store.update_model_version(
        record_version="v1.1.0-retrained-eval",
        change_reason="Retrained with 12 benchmark samples",
        metadata={"accuracy": 0.85}
    )

    latest = store.get_latest_model_version()
    assert latest["record_version"] == "v1.1.0-retrained-eval"
    assert "Retrained with 12 benchmark samples" in latest["change_reason"]


def test_sqlite_retrain_run_record(tmp_path):
    """Test recording and retrieving MLOps simulation runs."""
    db_file = tmp_path / "test_retrain.db"
    store = SQLiteStore(str(db_file))

    store.insert_retrain_run(
        run_id="mlops-test-999",
        status="completed",
        previous_version="v1.0.0-baseline",
        new_version="v1.1.0-retrained",
        samples_evaluated=12,
        metrics={"accuracy": 0.91, "f1_score": 0.88},
        artifact_path="/data/reports/mlops-test-999_report.json"
    )

    runs = store.get_recent_retrain_runs(limit=5)
    assert len(runs) == 1
    assert runs[0]["run_id"] == "mlops-test-999"
    assert runs[0]["metrics"]["accuracy"] == 0.91
