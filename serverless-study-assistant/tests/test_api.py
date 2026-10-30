"""API Endpoint Tests for FastAPI Application
"""

import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """Test root status and project metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["student"] == "Dhanush S (23MIS0224)"
    assert data["institution"] == "Vellore Institute of Technology (VIT)"
    assert "Amazon S3" in data["cloud_services"]
    assert "AWS Lambda" in data["cloud_services"]


def test_health_endpoint(client: TestClient):
    """Test /api/health endpoint structure and status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "app_version" in data
    assert "storage_mode" in data
    assert "ai_provider" in data
    assert "timestamp" in data


def test_metrics_endpoint(client: TestClient):
    """Test /api/metrics baseline retrieval."""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "successful_requests" in data
    assert "average_duration_ms" in data
    assert "fallback_rate_pct" in data
    assert "uptime_seconds" in data


def test_metrics_counter_increment(client: TestClient):
    """Verify that calling /api/chat increments operational counters."""
    # Send a valid chat request
    payload = {"message": "Explain what Agile Scrum is"}
    chat_resp = client.post("/api/chat", json=payload)
    assert chat_resp.status_code == 200

    metrics_resp = client.get("/api/metrics")
    assert metrics_resp.status_code == 200
    metrics_data = metrics_resp.json()
    assert metrics_data["total_requests"] >= 1
    assert metrics_data["successful_requests"] >= 1


def test_model_version_endpoint(client: TestClient):
    """Test /api/model-version endpoint."""
    response = client.get("/api/model-version")
    assert response.status_code == 200
    data = response.json()
    assert "record_version" in data
    assert "application_version" in data
    assert "model_provider" in data
    assert "model_identifier" in data
    assert "change_reason" in data


def test_chat_empty_message_validation(client: TestClient):
    """Test that empty string message returns HTTP 422."""
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422
    data = response.json()
    assert "Validation Error" in data.get("error", "")


def test_chat_whitespace_only_validation(client: TestClient):
    """Test that whitespace-only message returns HTTP 422."""
    response = client.post("/api/chat", json={"message": "    \n\t   "})
    assert response.status_code == 422


def test_chat_missing_message_field(client: TestClient):
    """Test that payload without 'message' returns HTTP 422."""
    response = client.post("/api/chat", json={"wrong_field": "hello"})
    assert response.status_code == 422


def test_chat_message_too_long_validation(client: TestClient):
    """Test that message exceeding 2000 chars returns HTTP 422."""
    long_msg = "A" * 2050
    response = client.post("/api/chat", json={"message": long_msg})
    assert response.status_code == 422
