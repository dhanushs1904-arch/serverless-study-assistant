"""Metrics and Observability Service Module
Tracks runtime application counters, latencies, and fallback frequencies.
In local mode, maintains thread-safe process metrics.
In cloud mode on AWS Lambda, outputs CloudWatch Embedded Metric Format / structured JSON.
"""

import time
import threading
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger("study_assistant.metrics")


class MetricsService:
    """Thread-safe operational telemetry collector."""

    def __init__(self):
        self._lock = threading.Lock()
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.ai_responses = 0
        self.fallback_responses = 0
        self.total_duration_ms = 0.0
        self.last_request_time: Optional[str] = None

    def record_request(
        self,
        duration_ms: float,
        success: bool = True,
        response_mode: str = "fallback"
    ) -> None:
        """Record an API request event."""
        with self._lock:
            self.total_requests += 1
            self.total_duration_ms += duration_ms
            self.last_request_time = datetime.utcnow().isoformat() + "Z"

            if success:
                self.successful_requests += 1
            else:
                self.failed_requests += 1

            if response_mode == "ai":
                self.ai_responses += 1
            else:
                self.fallback_responses += 1

        # Structured logging for CloudWatch ingest
        log_payload = {
            "event": "api_request",
            "duration_ms": round(duration_ms, 2),
            "success": success,
            "response_mode": response_mode,
            "timestamp": self.last_request_time
        }
        logger.info(f"METRICS_EVENT: {log_payload}")

    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Generate point-in-time statistics."""
        with self._lock:
            uptime = time.time() - self.start_time
            avg_duration = (
                self.total_duration_ms / self.total_requests
                if self.total_requests > 0 else 0.0
            )
            fallback_pct = (
                (self.fallback_responses / self.total_requests) * 100.0
                if self.total_requests > 0 else 0.0
            )

            return {
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "ai_responses": self.ai_responses,
                "fallback_responses": self.fallback_responses,
                "fallback_rate_pct": round(fallback_pct, 2),
                "average_duration_ms": round(avg_duration, 2),
                "uptime_seconds": round(uptime, 2),
                "last_request_timestamp": self.last_request_time
            }

    def reset_metrics(self) -> None:
        """Reset counters (used for test isolation)."""
        with self._lock:
            self.start_time = time.time()
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.ai_responses = 0
            self.fallback_responses = 0
            self.total_duration_ms = 0.0
            self.last_request_time = None


# Singleton instance
metrics_service = MetricsService()
