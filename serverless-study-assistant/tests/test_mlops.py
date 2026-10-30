"""MLOps Pipeline Simulation Tests
"""

import json
from pathlib import Path
from fastapi.testclient import TestClient
from app.services.mlops_service import mlops_service
from app.config import settings


def test_evaluation_dataset_structure():
    """Verify evaluation dataset contains required metadata and valid samples."""
    dataset = mlops_service.load_evaluation_dataset()
    assert "dataset_metadata" in dataset
    assert "samples" in dataset
    samples = dataset["samples"]
    assert len(samples) >= 10

    for s in samples:
        assert "id" in s
        assert "question" in s
        assert "expected_keywords" in s
        assert len(s["expected_keywords"]) >= 2
        assert "category" in s


def test_evaluate_single_sample():
    """Test evaluation logic for keyword matching and F1 computation."""
    sample = {
        "id": "test-sample-01",
        "category": "Agile",
        "question": "What is Scrum and Sprint?",
        "expected_keywords": ["scrum", "sprint"]
    }
    result = mlops_service.evaluate_sample(sample)
    assert result["id"] == "test-sample-01"
    assert result["keyword_recall"] >= 0.5
    assert result["f1_score"] > 0


def test_mlops_run_simulation(tmp_path):
    """Test end-to-end MLOps retraining simulation."""
    mlops_service.reports_dir = tmp_path
    result = mlops_service.run_simulation(trigger_reason="Pytest automated unit test")

    assert result["status"] == "completed"
    assert "mlops-run-" in result["run_id"]
    assert result["dataset_samples_evaluated"] >= 10
    assert "metrics" in result
    assert result["metrics"]["benchmark_accuracy"] > 0

    # Verify report files were generated on filesystem
    report_json = Path(result["artifact_report_path"])
    assert report_json.exists()

    with open(report_json, "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data["run_id"] == result["run_id"]
        assert "evaluation_metrics" in data


def test_mlops_api_endpoint(client: TestClient):
    """Test POST /api/mlops/retrain-simulation endpoint."""
    payload = {"trigger_reason": "API endpoint unit test"}
    response = client.post("/api/mlops/retrain-simulation", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "run_id" in data
    assert "new_version" in data
    assert data["dataset_samples_evaluated"] >= 10
    assert "benchmark_accuracy" in data["metrics"]
