"""
Application settings loaded from environment variables.
Uses Pydantic BaseSettings for validation and type coercion.
"""

from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the AI Meeting Summarizer."""

    # ── Application ──────────────────────────────────────────────
    APP_NAME: str = "AI Meeting Summarizer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development | staging | production

    # ── Server ───────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./meeting_summarizer.db"
    DATABASE_ECHO: bool = False

    # ── JWT Authentication ───────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE-ME-IN-PRODUCTION-USE-OPENSSL-RAND-HEX-32"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── File Upload ──────────────────────────────────────────────
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 500
    ALLOWED_AUDIO_EXTENSIONS: list[str] = [
        ".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm", ".mp4", ".wma",
    ]

    # ── AI – Transcription (Faster-Whisper) ──────────────────────
    WHISPER_MODEL_SIZE: str = "base"  # tiny | base | small | medium | large-v3
    WHISPER_DEVICE: str = "cpu"  # cpu | cuda
    WHISPER_COMPUTE_TYPE: str = "int8"  # float16 | int8
    WHISPER_LANGUAGE: Optional[str] = None  # None = auto-detect

    # ── AI – Summarization (Ollama) ──────────────────────────────
    AI_PROVIDER: str = "ollama"  # ollama | openai | claude | gemini
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3"
    OLLAMA_TIMEOUT: int = 120

    # ── AI – Optional providers ──────────────────────────────────
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    CLAUDE_API_KEY: Optional[str] = None
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ── Speaker Diarization ──────────────────────────────────────
    ENABLE_DIARIZATION: bool = False
    HF_AUTH_TOKEN: Optional[str] = None  # Required for pyannote.audio

    # ── Rate Limiting ────────────────────────────────────────────
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_AUTH: str = "10/minute"

    # ── Logging ──────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json | text

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from env var — handles JSON arrays, comma-separated, or plain strings."""
        import json as _json
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                try:
                    return _json.loads(v)
                except _json.JSONDecodeError:
                    pass
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    @field_validator("UPLOAD_DIR")
    @classmethod
    def ensure_upload_dir(cls, v: str) -> str:
        Path(v).mkdir(parents=True, exist_ok=True)
        return v

    @property
    def max_upload_size_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton instance
settings = Settings()
