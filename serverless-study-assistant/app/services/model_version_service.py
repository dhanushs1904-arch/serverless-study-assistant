"""Model Version Tracking Service Module
Maintains audit trail of application versions, AI model configurations,
and MLOps retraining pipeline milestones.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.config import settings
from app.database.sqlite_store import sqlite_store
from app.database.dynamodb_store import dynamodb_store

logger = logging.getLogger("study_assistant.model_version")


class ModelVersionService:
    """Manages version lineage and deployment records."""

    def __init__(self):
        self.current_version = "v1.0.0-baseline"
        self.last_change_reason = "Initial project deployment for VIT Agile/DevOps coursework"
        self.last_updated = datetime.utcnow().isoformat() + "Z"
        self.mlops_pipeline_stage = "Production-Serving"

    def get_current_version_info(self) -> Dict[str, Any]:
        """Fetch active model version details."""
        # Query local SQLite store for latest record
        try:
            latest = sqlite_store.get_latest_model_version()
            if latest:
                self.current_version = latest.get("record_version", self.current_version)
                self.last_change_reason = latest.get("change_reason", self.last_change_reason)
                self.last_updated = latest.get("last_updated", self.last_updated)
        except Exception as e:
            logger.warning(f"Could not read model version from SQLite: {e}")

        provider_name = "Groq (LLaMA)" if settings.is_groq_configured else "Rule-Based Fallback"
        model_name = settings.GROQ_MODEL if settings.is_groq_configured else "heuristic-academic-v1"

        return {
            "application_version": settings.APP_VERSION,
            "model_provider": provider_name,
            "model_identifier": model_name,
            "record_version": self.current_version,
            "change_reason": self.last_change_reason,
            "last_updated": self.last_updated,
            "mlops_pipeline_stage": self.mlops_pipeline_stage
        }

    def register_new_version(
        self,
        new_version: str,
        reason: str,
        pipeline_stage: str = "Retrained-Candidate",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Records a new version increment following MLOps retraining simulation."""
        self.current_version = new_version
        self.last_change_reason = reason
        self.last_updated = datetime.utcnow().isoformat() + "Z"
        self.mlops_pipeline_stage = pipeline_stage

        # Persist locally in SQLite
        sqlite_store.update_model_version(
            record_version=new_version,
            change_reason=reason,
            metadata=metadata
        )

        # Persist in DynamoDB if cloud mode enabled
        if settings.AWS_STORAGE_ENABLED:
            dynamodb_store.insert_model_version(
                record_version=new_version,
                change_reason=reason,
                metadata=metadata
            )

        logger.info(f"Model version updated to {new_version}: {reason}")
        return self.get_current_version_info()


# Singleton instance
model_version_service = ModelVersionService()
