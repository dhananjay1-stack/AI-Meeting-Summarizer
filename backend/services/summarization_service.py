"""
Summarization service — orchestrates AI-powered meeting summarization.
"""

import json
import logging
import time

from backend.prompts.summarize import SUMMARIZATION_PROMPT, SYSTEM_PROMPT
from backend.services.ai_provider import AIProvider, get_ai_provider

logger = logging.getLogger(__name__)


class SummarizationService:
    """Orchestrates meeting transcript summarization."""

    def __init__(self, provider: AIProvider | None = None):
        self.provider = provider or get_ai_provider()

    async def summarize(self, transcript_text: str) -> dict:
        """
        Generate a structured summary from a transcript.

        Returns:
            dict with: executive_summary, key_points, decisions,
                       action_items, keywords, ai_model, ai_provider, processing_time
        """
        start_time = time.time()

        # Truncate very long transcripts to prevent token limits
        max_chars = 30000
        if len(transcript_text) > max_chars:
            logger.warning(
                f"Transcript too long ({len(transcript_text)} chars), truncating to {max_chars}"
            )
            transcript_text = transcript_text[:max_chars] + "\n\n[Transcript truncated due to length]"

        prompt = SUMMARIZATION_PROMPT.format(transcript=transcript_text)

        try:
            raw_response = await self.provider.generate(prompt, system_prompt=SYSTEM_PROMPT)

            # Parse JSON response
            result = self._parse_response(raw_response)

            elapsed = time.time() - start_time
            result["ai_model"] = self.provider.get_model_name()
            result["ai_provider"] = self.provider.get_provider_name()
            result["processing_time"] = round(elapsed, 2)

            logger.info(
                f"Summarization complete: provider={result['ai_provider']}, "
                f"model={result['ai_model']}, time={elapsed:.1f}s"
            )

            return result

        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise

    def _parse_response(self, raw_response: str) -> dict:
        """Parse the LLM response into structured data."""
        # Try to extract JSON from the response
        text = raw_response.strip()

        # Remove markdown code fences if present
        if text.startswith("```"):
            # Find the first newline after opening fence
            start = text.index("\n") + 1 if "\n" in text else 3
            end = text.rfind("```")
            if end > start:
                text = text[start:end].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            json_start = text.find("{")
            json_end = text.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                try:
                    data = json.loads(text[json_start:json_end])
                except json.JSONDecodeError:
                    logger.warning("Failed to parse LLM response as JSON, using fallback")
                    data = self._fallback_parse(text)
            else:
                data = self._fallback_parse(text)

        # Validate required fields
        return {
            "executive_summary": data.get("executive_summary", "Not Mentioned"),
            "key_points": data.get("key_points", []),
            "decisions": data.get("decisions", []),
            "action_items": data.get("action_items", []),
            "keywords": data.get("keywords", []),
        }

    def _fallback_parse(self, text: str) -> dict:
        """Fallback parsing when JSON extraction fails."""
        return {
            "executive_summary": text[:500] if text else "Summary generation failed.",
            "key_points": [],
            "decisions": [],
            "action_items": [],
            "keywords": [],
        }
