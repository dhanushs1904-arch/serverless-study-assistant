"""AWS Services Integration Tests (Using Mocks)
Validates S3, DynamoDB, Lambda, API Gateway events, and CloudWatch telemetry
without requiring real AWS credentials or incur cloud costs.
"""

import json
from unittest.mock import MagicMock, patch
import pytest
from app.config import settings
from app.services.s3_service import s3_service
from app.database.dynamodb_store import dynamodb_store
from app.lambda_handler import lambda_handler


def test_s3_upload_mock(tmp_path):
    """Test Amazon S3 artifact upload using mocked boto3 S3 client."""
    test_artifact = tmp_path / "sample_eval.json"
    test_artifact.write_text(json.dumps({"test": "data"}))

    mock_client = MagicMock()
    mock_client.upload_file.return_value = None

    with patch.object(settings, "S3_ARTIFACTS_ENABLED", True):
        with patch.object(s3_service, "_get_client", return_value=mock_client):
            uri = s3_service.upload_artifact(
                local_file_path=str(test_artifact),
                s3_key="mlops-reports/test.json",
                content_type="application/json"
            )

            assert uri == f"s3://{settings.AWS_S3_BUCKET}/mlops-reports/test.json"
            mock_client.upload_file.assert_called_once()


def test_dynamodb_insert_mock():
    """Test Amazon DynamoDB item insertion using mocked boto3 Table resource."""
    mock_table = MagicMock()
    mock_table.put_item.return_value = {"ResponseMetadata": {"HTTPStatusCode": 200}}

    with patch.object(settings, "AWS_STORAGE_ENABLED", True):
        with patch.object(dynamodb_store, "_get_table", return_value=mock_table):
            success = dynamodb_store.insert_conversation(
                conversation_id="conv-aws-test-01",
                user_message="What is AWS Lambda?",
                assistant_response="AWS Lambda is a serverless compute service.",
                response_mode="fallback",
                model_identifier="heuristic-academic-v1",
                duration_ms=32.4
            )

            assert success is True
            mock_table.put_item.assert_called_once()
            call_args = mock_table.put_item.call_args[1]["Item"]
            assert call_args["PK"] == "CONVERSATION#conv-aws-test-01"
            assert call_args["EntityType"] == "CONVERSATION"


def test_lambda_handler_api_gateway_health_event():
    """Test AWS Lambda handler with synthetic Amazon API Gateway HTTP API event."""
    # Synthetic API Gateway v2 event payload for GET /api/health
    event = {
        "version": "2.0",
        "routeKey": "GET /api/health",
        "rawPath": "/api/health",
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "host": "api.studyassistant.vit.ac.in",
            "user-agent": "Mozilla/5.0"
        },
        "requestContext": {
            "http": {
                "method": "GET",
                "path": "/api/health",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1"
            }
        },
        "isBase64Encoded": False
    }

    class MockContext:
        aws_request_id = "aws-req-test-9999"
        function_name = "vit-study-assistant-backend"

    response = lambda_handler(event, MockContext())
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert body["status"] == "healthy"
    assert "app_name" in body


def test_lambda_handler_api_gateway_chat_event():
    """Test AWS Lambda handler with synthetic Amazon API Gateway POST /api/chat event."""
    event = {
        "version": "2.0",
        "routeKey": "POST /api/chat",
        "rawPath": "/api/chat",
        "rawQueryString": "",
        "headers": {
            "content-type": "application/json"
        },
        "requestContext": {
            "http": {
                "method": "POST",
                "path": "/api/chat",
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1"
            }
        },
        "body": json.dumps({"message": "What is Agile Scrum?"}),
        "isBase64Encoded": False
    }

    class MockContext:
        aws_request_id = "aws-req-test-chat-01"
        function_name = "vit-study-assistant-backend"

    response = lambda_handler(event, MockContext())
    assert response["statusCode"] == 200

    body = json.loads(response["body"])
    assert "reply" in body
    assert body["response_mode"] in ["ai", "fallback"]
