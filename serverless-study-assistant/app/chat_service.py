"""Chat Service Module
Coordinates incoming questions, AI inference / rule-based fallback,
metrics telemetry, and persistence across SQLite and DynamoDB.
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Optional
from app.config import settings
from app.schemas import ChatRequest, ChatResponse
from app.model_provider import model_provider
from app.services.metrics_service import metrics_service
from app.database.sqlite_store import sqlite_store
from app.database.dynamodb_store import dynamodb_store

logger = logging.getLogger("study_assistant.chat")


class ChatService:
    """Core chat orchestrator."""

    def process_message(self, request: ChatRequest) -> ChatResponse:
        """Process student query and return response with metadata."""
        start_time = time.time()
        conversation_id = request.conversation_id or f"conv-{uuid.uuid4().hex[:10]}"
        timestamp = datetime.utcnow().isoformat() + "Z"

        try:
            # Generate AI response or fallback
            reply, response_mode, model_id = model_provider.generate_response(
                user_message=request.message,
                topic=request.topic
            )
            duration_ms = (time.time() - start_time) * 1000.0

            # Record operational metrics
            metrics_service.record_request(
                duration_ms=duration_ms,
                success=True,
                response_mode=response_mode
            )

            # Persist conversation
            storage_recorded = False

            # 1. Local SQLite store
            try:
                sqlite_store.insert_conversation(
                    conversation_id=conversation_id,
                    user_message=request.message,
                    assistant_response=reply,
                    response_mode=response_mode,
                    model_identifier=model_id,
                    duration_ms=duration_ms,
                    status="success"
                )
                storage_recorded = True
            except Exception as e:
                logger.error(f"Failed to record conversation in SQLite: {e}")

            # 2. Cloud DynamoDB store when AWS storage is enabled
            if settings.AWS_STORAGE_ENABLED:
                try:
                    cloud_success = dynamodb_store.insert_conversation(
                        conversation_id=conversation_id,
                        user_message=request.message,
                        assistant_response=reply,
                        response_mode=response_mode,
                        model_identifier=model_id,
                        duration_ms=duration_ms,
                        status="success"
                    )
                    if cloud_success:
                        storage_recorded = True
                except Exception as e:
                    logger.error(f"Failed to record conversation in DynamoDB: {e}")

            return ChatResponse(
                reply=reply,
                response_mode=response_mode,
                model_identifier=model_id,
                duration_ms=round(duration_ms, 2),
                conversation_id=conversation_id,
                timestamp=timestamp,
                storage_recorded=storage_recorded
            )

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000.0
            metrics_service.record_request(
                duration_ms=duration_ms,
                success=False,
                response_mode="error"
            )
            logger.error(f"Error in chat processing: {exc}")
            raise exc


# Singleton instance
chat_service = ChatService()
