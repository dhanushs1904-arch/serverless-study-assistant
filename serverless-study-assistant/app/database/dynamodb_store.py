"""Amazon DynamoDB Service Module
Handles cloud persistence for StudyAssistantRecords table.
PK: Entity Category / Partition Key
SK: Timestamp or Unique Entity ID
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger("study_assistant.dynamodb")


def _convert_floats_to_decimals(obj: Any) -> Any:
    """DynamoDB requires Decimal for floating point numbers."""
    if isinstance(obj, float):
        return Decimal(str(round(obj, 4)))
    elif isinstance(obj, dict):
        return {k: _convert_floats_to_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_floats_to_decimals(i) for i in obj]
    return obj


class DynamoDBStore:
    """Manages Amazon DynamoDB operations for cloud deployment."""

    def __init__(self):
        self.table_name = settings.AWS_DYNAMODB_TABLE
        self.region = settings.AWS_REGION
        self._table = None

    def _get_table(self):
        """Lazily initialize boto3 DynamoDB table resource."""
        if self._table is None:
            try:
                dynamodb = boto3.resource("dynamodb", region_name=self.region)
                self._table = dynamodb.Table(self.table_name)
            except Exception as e:
                logger.error(f"Failed to connect to DynamoDB table {self.table_name}: {e}")
                self._table = None
        return self._table

    def insert_conversation(
        self,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        response_mode: str,
        model_identifier: str,
        duration_ms: float,
        status: str = "success"
    ) -> bool:
        """
        Record category: CONVERSATION
        PK: CONVERSATION#{conversation_id}
        SK: {timestamp}
        """
        table = self._get_table()
        if not table:
            logger.warning("DynamoDB table resource unavailable. Skipping cloud write.")
            return False

        timestamp = datetime.utcnow().isoformat() + "Z"
        item = {
            "PK": f"CONVERSATION#{conversation_id}",
            "SK": timestamp,
            "EntityType": "CONVERSATION",
            "ConversationId": conversation_id,
            "Timestamp": timestamp,
            "UserMessage": user_message,
            "AssistantResponse": assistant_response,
            "ResponseMode": response_mode,
            "ModelIdentifier": model_identifier,
            "DurationMs": Decimal(str(round(duration_ms, 2))),
            "Status": status,
            "TTL": int(datetime.utcnow().timestamp()) + (90 * 86400)  # 90-day retention
        }

        try:
            table.put_item(Item=item)
            logger.info(f"DynamoDB: Saved conversation {conversation_id} to {self.table_name}")
            return True
        except ClientError as e:
            logger.error(f"DynamoDB ClientError in insert_conversation: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error writing conversation to DynamoDB: {e}")
            return False

    def insert_model_version(
        self,
        record_version: str,
        change_reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record category: MODEL_VERSION
        PK: MODEL_VERSION
        SK: {record_version}
        """
        table = self._get_table()
        if not table:
            return False

        timestamp = datetime.utcnow().isoformat() + "Z"
        item = {
            "PK": "MODEL_VERSION",
            "SK": record_version,
            "EntityType": "MODEL_VERSION",
            "RecordVersion": record_version,
            "ApplicationVersion": settings.APP_VERSION,
            "ModelProvider": "Groq (LLaMA)" if settings.is_groq_configured else "Rule-Based Fallback",
            "ModelIdentifier": settings.GROQ_MODEL if settings.is_groq_configured else "heuristic-academic-v1",
            "ChangeReason": change_reason,
            "Timestamp": timestamp,
            "Metadata": _convert_floats_to_decimals(metadata or {})
        }

        try:
            table.put_item(Item=item)
            logger.info(f"DynamoDB: Saved model version {record_version}")
            return True
        except Exception as e:
            logger.error(f"Failed to write model version to DynamoDB: {e}")
            return False

    def insert_retrain_run(
        self,
        run_id: str,
        status: str,
        previous_version: str,
        new_version: str,
        samples_evaluated: int,
        metrics: Dict[str, Any],
        artifact_s3_uri: str
    ) -> bool:
        """
        Record category: RETRAIN_RUN
        PK: RETRAIN_RUN
        SK: {run_id}
        """
        table = self._get_table()
        if not table:
            return False

        timestamp = datetime.utcnow().isoformat() + "Z"
        item = {
            "PK": "RETRAIN_RUN",
            "SK": run_id,
            "EntityType": "RETRAIN_RUN",
            "RunId": run_id,
            "Status": status,
            "PreviousVersion": previous_version,
            "NewVersion": new_version,
            "SamplesEvaluated": samples_evaluated,
            "Metrics": _convert_floats_to_decimals(metrics),
            "ArtifactS3Uri": artifact_s3_uri,
            "Timestamp": timestamp
        }

        try:
            table.put_item(Item=item)
            logger.info(f"DynamoDB: Saved retrain run {run_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to write retrain run to DynamoDB: {e}")
            return False

    def insert_metric_snapshot(self, metrics: Dict[str, Any]) -> bool:
        """
        Record category: METRIC
        PK: METRICS_SNAPSHOT
        SK: {timestamp}
        """
        table = self._get_table()
        if not table:
            return False

        timestamp = datetime.utcnow().isoformat() + "Z"
        item = {
            "PK": "METRICS_SNAPSHOT",
            "SK": timestamp,
            "EntityType": "METRIC",
            "Timestamp": timestamp,
            "Metrics": _convert_floats_to_decimals(metrics)
        }

        try:
            table.put_item(Item=item)
            return True
        except Exception as e:
            logger.error(f"Failed to record metric snapshot to DynamoDB: {e}")
            return False


# Singleton instance
dynamodb_store = DynamoDBStore()
