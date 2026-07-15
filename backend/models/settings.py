"""
User settings model for per-user preferences.
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base, UUIDMixin, utc_now


class UserSettings(UUIDMixin, Base):
    """Per-user configuration preferences."""

    __tablename__ = "user_settings"

    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    default_ai_provider: Mapped[str] = mapped_column(String(20), default="ollama", nullable=False)
    default_whisper_model: Mapped[str] = mapped_column(String(20), default="base", nullable=False)
    enable_diarization: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_export_format: Mapped[str] = mapped_column(String(10), default="pdf", nullable=False)
    theme: Mapped[str] = mapped_column(String(10), default="dark", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    # Relationship
    user = relationship("User", back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings user={self.user_id} theme={self.theme}>"
