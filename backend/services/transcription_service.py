"""
Transcription service using Faster-Whisper.
"""

import logging
import time
from typing import Optional

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class TranscriptionService:
    """Audio transcription using Faster-Whisper."""

    def __init__(self):
        self._model = None

    def _get_model(self):
        """Lazy-load the Whisper model."""
        if self._model is None:
            try:
                from faster_whisper import WhisperModel

                logger.info(
                    f"Loading Whisper model: {settings.WHISPER_MODEL_SIZE} "
                    f"on {settings.WHISPER_DEVICE} ({settings.WHISPER_COMPUTE_TYPE})"
                )
                self._model = WhisperModel(
                    settings.WHISPER_MODEL_SIZE,
                    device=settings.WHISPER_DEVICE,
                    compute_type=settings.WHISPER_COMPUTE_TYPE,
                )
                logger.info("Whisper model loaded successfully.")
            except ImportError:
                logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
                raise
            except Exception as e:
                logger.error(f"Failed to load Whisper model: {e}")
                raise
        return self._model

    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
    ) -> dict:
        """
        Transcribe an audio file.

        Returns:
            dict with keys: full_text, segments, language, confidence, duration_seconds
        """
        start_time = time.time()
        model = self._get_model()

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

            # Collect segments
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
                f"Transcription complete: language={info.language}, "
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
            logger.error(f"Transcription failed: {e}")
            raise


# Singleton
transcription_service = TranscriptionService()
