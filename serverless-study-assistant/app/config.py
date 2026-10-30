"""Configuration Management for Serverless Study Assistant
Reads settings from environment variables with safe defaults.
"""

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()


class Settings:
    """Application settings and configuration."""

    def __init__(self):
        # Application metadata
        self.APP_NAME: str = "Serverless Chatbot with MLOps Pipeline"
        self.APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
        self.APP_ENV: str = os.getenv("APP_ENV", "local")  # local, test, cloud
        self.DEBUG: bool = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
        self.PORT: int = int(os.getenv("PORT", "8000"))

        # AI Provider (Groq / LLaMA)
        self.GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
        self.GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        # Storage & Cloud Toggles
        self.AWS_STORAGE_ENABLED: bool = os.getenv("AWS_STORAGE_ENABLED", "false").lower() in ("true", "1", "yes")
        self.S3_ARTIFACTS_ENABLED: bool = os.getenv("S3_ARTIFACTS_ENABLED", "false").lower() in ("true", "1", "yes")

        # AWS Configuration
        self.AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
        self.AWS_DYNAMODB_TABLE: str = os.getenv("AWS_DYNAMODB_TABLE", "StudyAssistantRecords")
        self.AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "vit-study-assistant-artifacts-23mis0224")

        # Local Paths
        self.SQLITE_DB_PATH: str = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "data" / "study_assistant.db"))
        self.REPORTS_DIR: str = os.getenv("REPORTS_DIR", str(BASE_DIR / "data" / "reports"))
        self.EVAL_DATASET_PATH: str = os.getenv("EVAL_DATASET_PATH", str(BASE_DIR / "data" / "evaluation_dataset.json"))
        self.FRONTEND_API_BASE_URL: str = os.getenv("FRONTEND_API_BASE_URL", "http://127.0.0.1:8000")

    @property
    def is_groq_configured(self) -> bool:
        """Check if Groq API key is present."""
        return bool(self.GROQ_API_KEY and len(self.GROQ_API_KEY) > 10)

    def get_safe_status(self) -> Dict[str, Any]:
        """Return safe configuration without exposing secret keys."""
        return {
            "app_name": self.APP_NAME,
            "app_version": self.APP_VERSION,
            "environment": self.APP_ENV,
            "ai_provider": "Groq (LLaMA)" if self.is_groq_configured else "Rule-Based Fallback",
            "model_identifier": self.GROQ_MODEL if self.is_groq_configured else "heuristic-academic-v1",
            "storage_mode": "DynamoDB (Cloud)" if self.AWS_STORAGE_ENABLED else "SQLite (Local)",
            "s3_artifacts": "Enabled" if self.S3_ARTIFACTS_ENABLED else "Disabled (Local FS)",
            "aws_region": self.AWS_REGION,
            "dynamodb_table": self.AWS_DYNAMODB_TABLE if self.AWS_STORAGE_ENABLED else None,
            "s3_bucket": self.AWS_S3_BUCKET if self.S3_ARTIFACTS_ENABLED else None,
        }


# Singleton instance
settings = Settings()
