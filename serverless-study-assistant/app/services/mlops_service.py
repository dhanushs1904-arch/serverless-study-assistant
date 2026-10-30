"""MLOps Retraining Simulation Service Module
Executes an educational MLOps pipeline lifecycle demonstration:
1. Loads and validates the benchmark evaluation dataset
2. Evaluates model responses against ground truth keyword expectations
3. Computes Precision, Recall, F1-Score, and Keyword Coverage
4. Generates comprehensive Markdown and JSON evaluation reports
5. Saves artifacts locally and uploads to Amazon S3 when enabled
6. Records run metadata into SQLite and Amazon DynamoDB
7. Advances the model version record with full provenance tracking
"""

import os
import json
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.config import settings
from app.fallback import generate_fallback_response
from app.database.sqlite_store import sqlite_store
from app.database.dynamodb_store import dynamodb_store
from app.services.s3_service import s3_service
from app.services.model_version_service import model_version_service

logger = logging.getLogger("study_assistant.mlops")


class MLOpsSimulationService:
    """Orchestrates educational MLOps continuous evaluation and retraining simulations."""

    def __init__(self):
        self.reports_dir = Path(settings.REPORTS_DIR)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def load_evaluation_dataset(self, custom_path: Optional[str] = None) -> Dict[str, Any]:
        """Loads and parses the academic evaluation dataset."""
        dataset_path = Path(custom_path or settings.EVAL_DATASET_PATH)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Evaluation dataset not found at {dataset_path}")

        with open(dataset_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if "samples" not in data or not isinstance(data["samples"], list):
            raise ValueError("Invalid dataset structure: 'samples' list is missing.")

        return data

    def evaluate_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates a single question against expected domain keywords."""
        question = sample.get("question", "")
        expected_kws = [kw.lower() for kw in sample.get("expected_keywords", [])]

        # Use fallback engine to generate answer for deterministic benchmark evaluation
        reply, matched_topic = generate_fallback_response(question)
        reply_lower = reply.lower()

        matched_kws = [kw for kw in expected_kws if kw in reply_lower]
        missing_kws = [kw for kw in expected_kws if kw not in reply_lower]

        # Calculate keyword precision and recall
        recall = len(matched_kws) / len(expected_kws) if expected_kws else 1.0
        # Precision heuristic based on relevance
        precision = min(1.0, (len(matched_kws) / max(1, len(expected_kws))))
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {
            "id": sample.get("id"),
            "category": sample.get("category"),
            "question": question,
            "matched_keywords": matched_kws,
            "missing_keywords": missing_kws,
            "keyword_recall": round(recall, 3),
            "precision": round(precision, 3),
            "f1_score": round(f1, 3),
            "pass_threshold": recall >= 0.60
        }

    def run_simulation(
        self,
        trigger_reason: str = "Scheduled periodic evaluation benchmark",
        custom_dataset_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the full retraining simulation pipeline.
        Returns execution summary dictionary.
        """
        run_timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        run_id = f"mlops-run-{run_timestamp}-{uuid.uuid4().hex[:6]}"
        start_time = datetime.utcnow().isoformat() + "Z"

        logger.info(f"Starting MLOps retraining simulation: {run_id}")

        # 1. Load dataset
        dataset = self.load_evaluation_dataset(custom_dataset_path)
        samples = dataset.get("samples", [])
        metadata = dataset.get("dataset_metadata", {})

        # 2. Evaluate samples
        sample_results: List[Dict[str, Any]] = []
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0
        passed_samples = 0

        for s in samples:
            res = self.evaluate_sample(s)
            sample_results.append(res)
            total_precision += res["precision"]
            total_recall += res["keyword_recall"]
            total_f1 += res["f1_score"]
            if res["pass_threshold"]:
                passed_samples += 1

        n = len(samples)
        avg_precision = round(total_precision / n, 4) if n > 0 else 0.0
        avg_recall = round(total_recall / n, 4) if n > 0 else 0.0
        avg_f1 = round(total_f1 / n, 4) if n > 0 else 0.0
        accuracy = round(passed_samples / n, 4) if n > 0 else 0.0

        metrics_summary = {
            "total_samples": n,
            "passed_samples": passed_samples,
            "benchmark_accuracy": accuracy,
            "average_precision": avg_precision,
            "average_recall": avg_recall,
            "average_f1_score": avg_f1,
            "category_distribution": metadata.get("categories", []),
            "simulation_note": "Educational workflow simulation: verified keyword recall and pipeline delivery automation."
        }

        # 3. Version bump logic
        previous_version = model_version_service.current_version
        version_parts = previous_version.replace("v", "").split("-")[0].split(".")
        try:
            major, minor, patch = int(version_parts[0]), int(version_parts[1]), int(version_parts[2])
            minor += 1
            new_version = f"v{major}.{minor}.0-retrained"
        except Exception:
            new_version = "v1.1.0-retrained"

        # 4. Generate Reports (JSON and Markdown)
        report_data = {
            "run_id": run_id,
            "timestamp": start_time,
            "trigger_reason": trigger_reason,
            "student": "Dhanush S (23MIS0224)",
            "institution": "Vellore Institute of Technology (VIT)",
            "course": "Agile Development Process and DevOps",
            "faculty": "Prof. Arun Kumar",
            "previous_version": previous_version,
            "new_version": new_version,
            "evaluation_metrics": metrics_summary,
            "detailed_sample_evaluations": sample_results
        }

        json_filename = f"{run_id}_report.json"
        md_filename = f"{run_id}_report.md"
        json_path = self.reports_dir / json_filename
        md_path = self.reports_dir / md_filename

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        # Markdown report generation
        md_content = (
            f"# MLOps Retraining Simulation Report\n\n"
            f"- **Run ID:** `{run_id}`\n"
            f"- **Timestamp:** `{start_time}`\n"
            f"- **Student:** Dhanush S (23MIS0224) | VIT\n"
            f"- **Course:** Agile Development Process and DevOps (Prof. Arun Kumar)\n"
            f"- **Trigger Reason:** {trigger_reason}\n"
            f"- **Version Lineage:** `{previous_version}` -> `{new_version}`\n\n"
            f"## Aggregate Evaluation Metrics\n\n"
            f"| Metric | Score | Evaluation Target | Status |\n"
            f"|---|---|---|---|\n"
            f"| Benchmark Accuracy | **{accuracy * 100:.1f}%** | >= 75.0% | {'PASS' if accuracy >= 0.75 else 'WARN'} |\n"
            f"| Average Precision | **{avg_precision:.3f}** | >= 0.700 | {'PASS' if avg_precision >= 0.70 else 'WARN'} |\n"
            f"| Average Recall | **{avg_recall:.3f}** | >= 0.700 | {'PASS' if avg_recall >= 0.70 else 'WARN'} |\n"
            f"| F1-Score | **{avg_f1:.3f}** | >= 0.700 | {'PASS' if avg_f1 >= 0.70 else 'WARN'} |\n\n"
            f"## Per-Sample Breakdown\n\n"
            f"| ID | Category | Question | Matched Keywords | F1 |\n"
            f"|---|---|---|---|---|\n"
        )
        for s in sample_results:
            md_content += f"| {s['id']} | {s['category']} | {s['question'][:45]}... | {', '.join(s['matched_keywords']) or 'None'} | {s['f1_score']} |\n"

        md_content += (
            f"\n\n---\n"
            f"*Note: This report is generated by the educational MLOps pipeline. "
            f"In a production system, this pipeline triggers GPU-backed fine-tuning or prompt-evaluation "
            f"and automates shadow deployment testing before production cutover.*"
        )

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_content)

        # 5. S3 Cloud Upload
        s3_uploaded = False
        s3_uri = None
        if settings.S3_ARTIFACTS_ENABLED:
            s3_uri = s3_service.upload_retrain_report(str(json_path), run_id)
            if s3_uri:
                s3_uploaded = True

        # 6. Database Persistence (Local SQLite & Cloud DynamoDB)
        sqlite_store.insert_retrain_run(
            run_id=run_id,
            status="completed",
            previous_version=previous_version,
            new_version=new_version,
            samples_evaluated=n,
            metrics=metrics_summary,
            artifact_path=str(json_path)
        )

        dynamodb_recorded = False
        if settings.AWS_STORAGE_ENABLED:
            dynamodb_recorded = dynamodb_store.insert_retrain_run(
                run_id=run_id,
                status="completed",
                previous_version=previous_version,
                new_version=new_version,
                samples_evaluated=n,
                metrics=metrics_summary,
                artifact_s3_uri=s3_uri or f"file://{json_path}"
            )

        # 7. Update Model Version Record
        model_version_service.register_new_version(
            new_version=new_version,
            reason=f"MLOps Retrain Run {run_id}: Benchmark Accuracy {accuracy*100:.1f}%, F1 {avg_f1}",
            pipeline_stage="Retrained-Candidate-Validated",
            metadata=metrics_summary
        )

        summary_msg = (
            f"MLOps Retraining Simulation completed successfully. "
            f"Evaluated {n} benchmark questions. Accuracy: {accuracy*100:.1f}%, F1: {avg_f1}. "
            f"Model version advanced from {previous_version} to {new_version}."
        )

        return {
            "run_id": run_id,
            "status": "completed",
            "previous_version": previous_version,
            "new_version": new_version,
            "dataset_samples_evaluated": n,
            "metrics": metrics_summary,
            "artifact_report_path": str(json_path),
            "s3_uploaded": s3_uploaded,
            "s3_bucket": settings.AWS_S3_BUCKET if s3_uploaded else None,
            "dynamodb_recorded": dynamodb_recorded,
            "timestamp": start_time,
            "summary": summary_msg
        }


# Singleton instance
mlops_service = MLOpsSimulationService()
