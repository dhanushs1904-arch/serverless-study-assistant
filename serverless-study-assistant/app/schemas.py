"""Pydantic Request and Response Schemas for API Validation
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Incoming user chat message payload."""
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The student query or academic topic to explain"
    )
    conversation_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional conversation identifier for message thread tracking"
    )
    topic: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Academic subject area (e.g. Agile, DevOps, OS, DBMS, Networks)"
    )

    @field_validator("message")
    @classmethod
    def validate_message_not_empty(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Message cannot be blank or contain only whitespace.")
        return trimmed


class ChatResponse(BaseModel):
    """Outgoing chat response payload."""
    reply: str
    response_mode: str = Field(..., description="'ai' (Groq/LLaMA) or 'fallback' (Rule-Based)")
    model_identifier: str
    duration_ms: float
    conversation_id: str
    timestamp: str
    storage_recorded: bool = Field(default=False, description="Whether the record was saved to SQLite/DynamoDB")


class HealthResponse(BaseModel):
    """Health check response schema."""
    status: str = "healthy"
    app_name: str
    app_version: str
    environment: str
    storage_mode: str
    ai_provider: str
    model_identifier: str
    timestamp: str


class MetricsResponse(BaseModel):
    """Operational metrics response schema."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    ai_responses: int
    fallback_responses: int
    fallback_rate_pct: float
    average_duration_ms: float
    uptime_seconds: float
    last_request_timestamp: Optional[str] = None


class ModelVersionResponse(BaseModel):
    """Model version tracking response schema."""
    application_version: str
    model_provider: str
    model_identifier: str
    record_version: str
    change_reason: str
    last_updated: str
    mlops_pipeline_stage: str


class RetrainSimulationRequest(BaseModel):
    """Trigger payload for MLOps retraining simulation."""
    trigger_reason: Optional[str] = Field(
        default="Scheduled periodic evaluation benchmark",
        max_length=200
    )
    dataset_path: Optional[str] = Field(
        default=None,
        max_length=300
    )


class RetrainSimulationResponse(BaseModel):
    """Result of educational MLOps retraining simulation."""
    run_id: str
    status: str
    previous_version: str
    new_version: str
    dataset_samples_evaluated: int
    metrics: Dict[str, Any]
    artifact_report_path: str
    s3_uploaded: bool
    s3_bucket: Optional[str] = None
    dynamodb_recorded: bool
    timestamp: str
    summary: str
