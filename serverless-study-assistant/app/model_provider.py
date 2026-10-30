"""Model Provider Service
Integrates with the Groq API using LLaMA models.
Provides resilient error handling, timeouts, and automatic fallback dispatch.
"""

import logging
from typing import Tuple, Optional
from app.config import settings
from app.fallback import generate_fallback_response

logger = logging.getLogger("study_assistant.model_provider")

# Academic persona system prompt
ACADEMIC_SYSTEM_PROMPT = (
    "You are an expert academic tutor and study assistant for engineering and computer science students "
    "at Vellore Institute of Technology (VIT). Your explanations should be precise, pedagogically structured, "
    "academically rigorous, and easy to understand. Structure complex topics with clear definitions, "
    "architectural explanations, bullet points, and key exam/viva tips where appropriate. "
    "Maintain an encouraging, professional, and educational tone."
)


class ModelProvider:
    """Handles external AI calls with fallback resilience."""

    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self._client = None

    def _get_client(self):
        """Lazily initialize the Groq client if key is configured."""
        if self._client is None and settings.is_groq_configured:
            try:
                from groq import Groq
                self._client = Groq(api_key=settings.GROQ_API_KEY, timeout=12.0)
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self._client = None
        return self._client

    def generate_response(self, user_message: str, topic: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Generates an academic response.
        Returns:
            (reply_text, response_mode ['ai' or 'fallback'], model_identifier)
        """
        # If no API key configured, seamlessly route to rule-based fallback
        if not settings.is_groq_configured:
            logger.info("Groq API key not configured. Routing to rule-based fallback engine.")
            reply, _ = generate_fallback_response(user_message)
            return reply, "fallback", "heuristic-academic-v1"

        client = self._get_client()
        if not client:
            logger.warning("Groq client unavailable. Routing to fallback.")
            reply, _ = generate_fallback_response(user_message)
            return reply, "fallback", "heuristic-academic-v1"

        try:
            logger.info(f"Invoking Groq API model: {self.model}")
            messages = [
                {"role": "system", "content": ACADEMIC_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ]

            completion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
            )

            choice = completion.choices[0] if completion.choices else None
            if not choice or not choice.message or not choice.message.content:
                raise ValueError("Received empty response payload from model provider.")

            content = choice.message.content.strip()
            return content, "ai", self.model

        except Exception as exc:
            # Handle rate limits, timeouts, connection errors gracefully
            logger.error(f"AI Provider error ({type(exc).__name__}): {exc}. Invoking fallback.")
            reply, _ = generate_fallback_response(user_message)
            # Append clear note about provider error fallback
            fallback_with_notice = (
                f"{reply}\n\n"
                f"> *[Notice: Switched to Rule-Based Fallback due to temporary AI service condition ({type(exc).__name__})]*"
            )
            return fallback_with_notice, "fallback", "heuristic-academic-v1"


# Singleton instance
model_provider = ModelProvider()
