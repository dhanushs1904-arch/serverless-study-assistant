"""Amazon S3 Artifact Storage Service Module
Manages MLOps evaluation dataset archiving and retraining simulation report uploads.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.config import settings

logger = logging.getLogger("study_assistant.s3")


class S3ArtifactService:
    """Handles S3 object storage for educational MLOps pipeline artifacts."""

    def __init__(self):
        self.bucket_name = settings.AWS_S3_BUCKET
        self.region = settings.AWS_REGION
        self._s3_client = None

    def _get_client(self):
        """Lazily initialize boto3 S3 client."""
        if self._s3_client is None:
            try:
                self._s3_client = boto3.client("s3", region_name=self.region)
            except Exception as e:
                logger.error(f"Failed to initialize S3 client: {e}")
                self._s3_client = None
        return self._s3_client

    def upload_artifact(
        self,
        local_file_path: str,
        s3_key: str,
        content_type: str = "application/json",
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Uploads a file to the configured S3 bucket with private ACL.
        Returns s3:// URI on success or None on failure.
        """
        if not settings.S3_ARTIFACTS_ENABLED:
            logger.info("S3 artifact storage disabled in settings. Skipping cloud upload.")
            return None

        client = self._get_client()
        if not client:
            logger.warning("S3 client not available. Skipping cloud upload.")
            return None

        extra_args: Dict[str, Any] = {
            "ContentType": content_type,
            "ServerSideEncryption": "AES256"  # Enforce at-rest encryption
        }
        if metadata:
            extra_args["Metadata"] = metadata

        try:
            logger.info(f"Uploading artifact {local_file_path} to s3://{self.bucket_name}/{s3_key}")
            client.upload_file(
                Filename=str(local_file_path),
                Bucket=self.bucket_name,
                Key=s3_key,
                ExtraArgs=extra_args
            )
            s3_uri = f"s3://{self.bucket_name}/{s3_key}"
            logger.info(f"Successfully uploaded: {s3_uri}")
            return s3_uri
        except NoCredentialsError:
            logger.error("AWS credentials not found. S3 upload skipped.")
            return None
        except ClientError as e:
            logger.error(f"S3 ClientError: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {e}")
            return None

    def upload_evaluation_dataset(self, dataset_path: str) -> Optional[str]:
        """Upload benchmark evaluation dataset to S3."""
        filename = Path(dataset_path).name
        s3_key = f"datasets/{filename}"
        return self.upload_artifact(
            local_file_path=dataset_path,
            s3_key=s3_key,
            content_type="application/json",
            metadata={"dataset-type": "academic-evaluation-benchmark"}
        )

    def upload_retrain_report(self, report_path: str, run_id: str) -> Optional[str]:
        """Upload an MLOps retraining simulation report to S3."""
        filename = Path(report_path).name
        extension = Path(report_path).suffix
        content_type = "application/json" if extension == ".json" else "text/markdown"
        s3_key = f"mlops-reports/{run_id}/{filename}"
        return self.upload_artifact(
            local_file_path=report_path,
            s3_key=s3_key,
            content_type=content_type,
            metadata={"mlops-run-id": run_id}
        )


# Singleton instance
s3_service = S3ArtifactService()
