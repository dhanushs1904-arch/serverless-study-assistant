"""FastAPI Application Entry Point
Serverless Study Assistant with MLOps Pipeline
Student: Dhanush S (23MIS0224) | VIT | Agile Development Process and DevOps
Faculty: Prof. Arun Kumar
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.config import settings
from app.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    MetricsResponse,
    ModelVersionResponse,
    RetrainSimulationRequest,
    RetrainSimulationResponse,
)
from app.chat_service import chat_service
from app.services.metrics_service import metrics_service
from app.services.model_version_service import model_version_service
from app.services.mlops_service import mlops_service
from app.database.sqlite_store import sqlite_store

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("study_assistant.api")

app = FastAPI(
    title="Serverless Chatbot with MLOps Pipeline API",
    description=(
        "Academic Study Assistant backend demonstrating FastAPI, AWS Serverless architecture "
        "(Lambda, API Gateway, DynamoDB, S3, CloudWatch), and MLOps delivery automation. "
        "Built for Vellore Institute of Technology (VIT) Agile & DevOps course evaluation."
    ),
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler for request payload validation errors."""
    clean_errors = []
    for err in exc.errors():
        clean_errors.append({
            "loc": [str(loc_item) for loc_item in err.get("loc", [])],
            "msg": str(err.get("msg", "")),
            "type": str(err.get("type", ""))
        })
    logger.warning(f"Validation error on {request.url.path}: {clean_errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request payload. Please verify input length and required fields.",
            "details": clean_errors
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Fallback handler for uncaught server errors."""
    logger.error(f"Unhandled error on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred processing your request."
        }
    )


@app.get("/", tags=["General"])
def root_endpoint() -> Dict[str, Any]:
    """Root metadata and verification endpoint."""
    return {
        "project": "Serverless Chatbot with MLOps Pipeline",
        "student": "Dhanush S (23MIS0224)",
        "institution": "Vellore Institute of Technology (VIT)",
        "course": "Agile Development Process and DevOps",
        "faculty": "Prof. Arun Kumar",
        "status": "operational",
        "version": settings.APP_VERSION,
        "docs_url": "/docs",
        "cloud_services": [
            "Amazon S3",
            "AWS Lambda",
            "Amazon API Gateway",
            "Amazon DynamoDB",
            "Amazon CloudWatch"
        ]
    }


@app.get("/api/health", response_model=HealthResponse, tags=["Observability"])
def health_check() -> HealthResponse:
    """System health check and configuration audit."""
    safe_status = settings.get_safe_status()
    return HealthResponse(
        status="healthy",
        app_name=safe_status["app_name"],
        app_version=safe_status["app_version"],
        environment=safe_status["environment"],
        storage_mode=safe_status["storage_mode"],
        ai_provider=safe_status["ai_provider"],
        model_identifier=safe_status["model_identifier"],
        timestamp=datetime.utcnow().isoformat() + "Z"
    )


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Primary chat endpoint.
    Processes student question through Groq AI (LLaMA) or rule-based fallback,
    records operational telemetry, and persists interaction.
    """
    try:
        response = chat_service.process_message(request)
        return response
    except Exception as e:
        logger.error(f"Chat execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chatbot processing error."
        )


@app.get("/api/metrics", response_model=MetricsResponse, tags=["Observability"])
def get_metrics() -> MetricsResponse:
    """Retrieve runtime telemetry, request counts, latencies, and fallback rates."""
    snapshot = metrics_service.get_metrics_snapshot()
    return MetricsResponse(**snapshot)


@app.get("/api/model-version", response_model=ModelVersionResponse, tags=["MLOps"])
def get_model_version() -> ModelVersionResponse:
    """Retrieve current model version, lineage, change reason, and pipeline stage."""
    info = model_version_service.get_current_version_info()
    return ModelVersionResponse(**info)


@app.post("/api/mlops/retrain-simulation", response_model=RetrainSimulationResponse, tags=["MLOps"])
def retrain_simulation(request: RetrainSimulationRequest) -> RetrainSimulationResponse:
    """
    Executes an educational MLOps retraining simulation:
    - Benchmarks evaluation dataset questions against expected domain keywords
    - Computes precision, recall, and F1 scores
    - Increments model version record
    - Emits and archives Markdown/JSON reports
    - Uploads artifacts to S3 and logs run to DynamoDB when cloud toggled
    """
    try:
        result = mlops_service.run_simulation(
            trigger_reason=request.trigger_reason or "Manual faculty demo trigger",
            custom_dataset_path=request.dataset_path
        )
        return RetrainSimulationResponse(**result)
    except Exception as e:
        logger.error(f"MLOps retraining simulation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"MLOps simulation error: {str(e)}"
        )


@app.get("/api/conversations", tags=["Inspection"])
def inspect_conversations(limit: int = 25) -> List[Dict[str, Any]]:
    """Inspect stored conversation records from local SQLite."""
    return sqlite_store.get_recent_conversations(limit=limit)


@app.get("/api/mlops/runs", tags=["Inspection"])
def inspect_retrain_runs(limit: int = 10) -> List[Dict[str, Any]]:
    """Inspect recent MLOps simulation runs and metrics from local SQLite."""
    return sqlite_store.get_recent_retrain_runs(limit=limit)
