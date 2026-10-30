"""Standalone CLI Script: Simulate MLOps Retraining
Can be run via:
    python scripts/simulate_retraining.py
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.mlops_service import mlops_service


def main():
    print("=" * 70)
    print("SERVERLESS CHATBOT WITH MLOps PIPELINE - RETRAINING SIMULATION")
    print("Student: Dhanush S (23MIS0224) | VIT | Agile Development Process & DevOps")
    print("Faculty: Prof. Arun Kumar")
    print("=" * 70)

    try:
        print("\n[1/4] Loading academic evaluation benchmark dataset...")
        result = mlops_service.run_simulation(
            trigger_reason="CLI simulation run for academic viva evaluation"
        )

        print("\n[2/4] Evaluation Completed Successfully!")
        print(f"  - Run ID: {result['run_id']}")
        print(f"  - Previous Model Version: {result['previous_version']}")
        print(f"  - New Model Version:      {result['new_version']}")
        print(f"  - Benchmark Samples:      {result['dataset_samples_evaluated']}")

        m = result["metrics"]
        print("\n[3/4] Evaluation Metrics:")
        print(f"  - Benchmark Accuracy:  {m['benchmark_accuracy'] * 100:.1f}%")
        print(f"  - Average Precision:   {m['average_precision']:.3f}")
        print(f"  - Average Recall:      {m['average_recall']:.3f}")
        print(f"  - F1-Score:            {m['average_f1_score']:.3f}")

        print("\n[4/4] Artifact Delivery & Storage Status:")
        print(f"  - Local Report Path:   {result['artifact_report_path']}")
        print(f"  - S3 Upload Enabled:   {result['s3_uploaded']}")
        if result['s3_uploaded']:
            print(f"  - S3 Bucket:           {result['s3_bucket']}")
        print(f"  - DynamoDB Logged:     {result['dynamodb_recorded']}")

        print("\n" + "=" * 70)
        print("SIMULATION SUCCESSFUL: Pipeline artifacts generated and version updated.")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
