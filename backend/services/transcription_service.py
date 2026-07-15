"""
Transcription service — supports Groq Whisper API (cloud) and local Faster-Whisper.
"""

import logging
import time
from pathlib import Path
from typing import Optional

import httpx

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Audio transcription using Groq API (primary) or local Faster-Whisper (fallback)."""

    def __init__(self):
        self._local_model = None

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> dict:
        """
        Transcribe an audio file.
        Uses Groq Whisper API if GROQ_API_KEY is set, otherwise falls back to local model.

        Returns:
            dict with keys: full_text, segments, language, confidence, duration_seconds
        """
        # Prefer Groq cloud API (works on Render free tier)
        if settings.GROQ_API_KEY:
            return await self._transcribe_groq(audio_path, language)

        # Fallback: local faster-whisper
        return await self._transcribe_local(audio_path, language)

    async def _transcribe_groq(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> dict:
        """Transcribe using Groq's Whisper API (free tier, cloud-based)."""
        start_time = time.time()
        file_path = Path(audio_path)

        logger.info(f"Transcribing with Groq Whisper API: {file_path.name}")

        async with httpx.AsyncClient(timeout=300) as client:
            with open(file_path, "rb") as audio_file:
                files = {"file": (file_path.name, audio_file, "audio/mpeg")}
                data = {
                    "model": settings.GROQ_WHISPER_MODEL,
                    "response_format": "verbose_json",
                }
                if language:
                    data["language"] = language

                response = await client.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {settings.GROQ_API_KEY}"},
                    files=files,
                    data=data,
                )
                response.raise_for_status()
                result = response.json()

        elapsed = time.time() - start_time
        full_text = result.get("text", "")
        detected_lang = result.get("language", "en")
        duration = result.get("duration", 0)

        # Parse segments from verbose_json response
        segments = []
        for seg in result.get("segments", []):
            segments.append({
                "start": round(seg.get("start", 0), 2),
                "end": round(seg.get("end", 0), 2),
                "text": seg.get("text", "").strip(),
            })

        logger.info(
            f"Groq transcription complete: language={detected_lang}, "
            f"duration={duration:.1f}s, processing_time={elapsed:.1f}s, "
            f"segments={len(segments)}"
        )

        return {
            "full_text": full_text,
            "segments": segments,
            "language": detected_lang,
            "confidence": 0.95,  # Groq doesn't return confidence; Whisper-large-v3 is high quality
            "duration_seconds": int(duration),
            "processing_time": round(elapsed, 2),
        }

    async def _transcribe_local(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> dict:
        """Transcribe using local Faster-Whisper model."""
        start_time = time.time()
        model = self._get_local_model()

        lang = language or settings.WHISPER_LANGUAGE

        try:
            segments_generator, info = model.transcribe(
                audio_path,
                language=lang,
                beam_size=5,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                ),
            )

            segments = []
            full_text_parts = []

            for segment in segments_generator:
                seg_data = {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip(),
                }
                segments.append(seg_data)
                full_text_parts.append(segment.text.strip())

            full_text = " ".join(full_text_parts)
            elapsed = time.time() - start_time

            logger.info(
                f"Local transcription complete: language={info.language}, "
                f"duration={info.duration:.1f}s, "
                f"processing_time={elapsed:.1f}s, "
                f"segments={len(segments)}"
            )

            return {
                "full_text": full_text,
                "segments": segments,
                "language": info.language,
                "confidence": round(info.language_probability, 4),
                "duration_seconds": int(info.duration),
                "processing_time": round(elapsed, 2),
            }

        except Exception as e:
            logger.error(f"Local transcription failed: {e}")
            raise

    def _get_local_model(self):
        """Lazy-load the local Whisper model."""
        if self._local_model is None:
            try:
                from faster_whisper import WhisperModel

                logger.info(
                    f"Loading Whisper model: {settings.WHISPER_MODEL_SIZE} "
                    f"on {settings.WHISPER_DEVICE} ({settings.WHISPER_COMPUTE_TYPE})"
                )
                self._local_model = WhisperModel(
                    settings.WHISPER_MODEL_SIZE,
                    device=settings.WHISPER_DEVICE,
                    compute_type=settings.WHISPER_COMPUTE_TYPE,
                )
                logger.info("Whisper model loaded successfully.")
            except ImportError:
                raise RuntimeError(
                    "Transcription is not available: 'faster-whisper' is not installed "
                    "and no GROQ_API_KEY is configured. Either install faster-whisper "
                    "or set GROQ_API_KEY for cloud transcription (free at https://console.groq.com)."
                )
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
        return self._local_model


# Singleton
transcription_service = TranscriptionService()
