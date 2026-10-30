"""Standalone CLI Script: Export Operational & Academic Summary Report
Can be run via:
    python scripts/export_report.py
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.sqlite_store import sqlite_store
from app.services.metrics_service import metrics_service
from app.services.model_version_service import model_version_service
from app.config import settings


def main():
    print("=" * 70)
    print("SERVERLESS CHATBOT WITH MLOps PIPELINE - SYSTEM AUDIT EXPORTER")
    print("Student: Dhanush S (23MIS0224) | VIT | Agile Development Process & DevOps")
    print("=" * 70)

    metrics = metrics_service.get_metrics_snapshot()
    version = model_version_service.get_current_version_info()
    convs = sqlite_store.get_recent_conversations(limit=5)
    runs = sqlite_store.get_recent_retrain_runs(limit=3)

    summary = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "student": "Dhanush S (23MIS0224)",
        "course": "Agile Development Process and DevOps",
        "institution": "Vellore Institute of Technology (VIT)",
        "configuration": settings.get_safe_status(),
        "runtime_metrics": metrics,
        "active_model_version": version,
        "total_conversations_recorded": len(convs),
        "recent_retrain_runs": runs
    }

    output_dir = Path(settings.REPORTS_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file = output_dir / "latest_system_audit_summary.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nAudit summary generated successfully at: {out_file}")
    print(f"- Total Requests Processed: {metrics['total_requests']}")
    print(f"- Successful Requests:       {metrics['successful_requests']}")
    print(f"- Fallback Responses:       {metrics['fallback_responses']}")
    print(f"- Current Model Version:    {version['record_version']}")
    print(f"- AI Provider Mode:         {version['model_provider']}")
    print("=" * 70)


if __name__ == "__main__":
    main()
