"""Pytest Configuration and Fixtures
Student: Dhanush S (23MIS0224) | VIT
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Set test environment flags before importing application modules
os.environ["APP_ENV"] = "test"
os.environ["AWS_STORAGE_ENABLED"] = "false"
os.environ["S3_ARTIFACTS_ENABLED"] = "false"
os.environ["GROQ_API_KEY"] = ""  # Default to fallback mode for tests

from fastapi.testclient import TestClient
from app.main import app
from app.config import settings
from app.database.sqlite_store import SQLiteStore
from app.services.metrics_service import metrics_service


@pytest.fixture(autouse=True)
def reset_test_state(tmp_path):
    """Isolate each test with clean temp database and reset metrics."""
    test_db = tmp_path / "test_study_assistant.db"
    settings.SQLITE_DB_PATH = str(test_db)
    # Re-initialize store with new test DB
    from app.database import sqlite_store as store_mod
    store_mod.sqlite_store = SQLiteStore(str(test_db))

    metrics_service.reset_metrics()
    yield


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client
