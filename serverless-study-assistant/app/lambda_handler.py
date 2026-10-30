"""AWS Lambda Handler Module
Adapts the FastAPI application for serverless execution behind Amazon API Gateway
using Mangum ASGI adapter.
"""

import os
import logging
from mangum import Mangum
from app.main import app

# Set up logging for CloudWatch ingestion
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize Mangum handler
# lifespan="off" is recommended for Lambda to eliminate startup delay overhead
handler = Mangum(app, lifespan="off")


def lambda_handler(event, context):
    """
    Entry point for AWS Lambda invocations from Amazon API Gateway HTTP API or REST API.
    Logs invocation context and dispatches to FastAPI app.
    """
    logger.info("Lambda invocation received", extra={
        "aws_request_id": getattr(context, "aws_request_id", "local-test-id"),
        "function_name": getattr(context, "function_name", "study-assistant-backend"),
        "http_method": event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method"),
        "path": event.get("path") or event.get("rawPath")
    })

    response = handler(event, context)
    return response
